"""
토지이용 분석 — 용도지역 구성비, 건축물 주용도 구성비, LUM 혼합도, 평균 용적률.

방법론 (2026-06-24):
1. VWorld 연속지적도(LP_PA_CBND_BUBUN) 를 구역경계(boundary_*.geojson) polygon 으로
   GetFeature 조회 → 경계와 교차하는 필지(PNU) 목록을 얻는다.
2. PNU(19자리: 시군구5+법정동5+토지구분1+본번4+부번4)를 디코딩해 (sigunguCd, bjdongCd) 별로
   묶고, 건축HUB getBrTitleInfo 를 법정동 단위로 호출(페이지네이션)한 뒤
   (bjdongCd, bun, ji, platGbCd) 키로 필지 목록과 매칭 — 이 매칭이 "구역계 밖 필지를
   섞지 않는" 공간단위 통합 처리다 (boundary 자체가 근사치라는 한계는 PLAN.md §1-2 에 별도 명시).
3. VWorld 용도지역지구(LT_C_UQ111) 를 동일 polygon 으로 조회해 필지 단위 용도지역 속성을 얻는다.
4. 매칭된 건축물의 주용도(mainPurpsCdNm)별 연면적(totArea) 합 → 구성비, LUM 엔트로피, 평균 용적률.

출력: preprocessing/outputs/landuse_{region}.json, landuse_{region}_buildings.geojson
"""
import json
import math
import time

import geopandas as gpd
import pandas as pd
import requests

from config import (
    BUILDING_HUB_API_KEY,
    BUILDING_HUB_BASE_URL,
    VWORLD_API_KEY,
    VWORLD_DATA_URL,
    VWORLD_DOMAIN,
    VWORLD_LAYER_USE_ZONE_URBAN,
)

OUT_DIR = "outputs"
PARCEL_LAYER = "LP_PA_CBND_BUBUN"


def _polygon_wkt(boundary: gpd.GeoDataFrame) -> str:
    wkt_str = boundary.geometry.iloc[0].wkt
    return wkt_str.replace("POLYGON (", "POLYGON(").replace(" (", "(")


def fetch_vworld_features(layer: str, polygon_wkt: str, size: int = 1000) -> list[dict]:
    r = requests.get(
        VWORLD_DATA_URL,
        params={
            "service": "data", "version": "2.0", "request": "GetFeature",
            "data": layer, "key": VWORLD_API_KEY, "domain": VWORLD_DOMAIN,
            "format": "json", "size": size, "geomFilter": polygon_wkt,
            "geometry": "true", "crs": "EPSG:4326",
        },
        timeout=30,
    )
    d = r.json()["response"]
    if d["status"] != "OK":
        raise RuntimeError(f"VWorld error: {d.get('error')}")
    return d["result"]["featureCollection"]["features"]


def decode_pnu(pnu: str) -> dict:
    return {
        "sigunguCd": pnu[0:5],
        "bjdongCd": pnu[5:10],
        "platGbCd": "0" if pnu[10] == "1" else "1",  # PNU 1=일반/2=산 -> 건축HUB 0=일반/1=산
        "bun": pnu[11:15],
        "ji": pnu[15:19],
    }


def fetch_buildings_for_dong(sigungu_cd: str, bjdong_cd: str) -> pd.DataFrame:
    """API가 numOfRows 요청값을 무시하고 서버 측에서 100건으로 강제 캡하므로,
    실제 응답의 numOfRows/totalCount 를 기준으로 페이지 수를 계산해 끝까지 순회한다."""
    rows = []
    page = 1
    while True:
        r = requests.get(
            f"{BUILDING_HUB_BASE_URL}/getBrTitleInfo",
            params={
                "sigunguCd": sigungu_cd, "bjdongCd": bjdong_cd,
                "numOfRows": 100, "pageNo": page, "_type": "json",
                "serviceKey": BUILDING_HUB_API_KEY,
            },
            timeout=30,
        )
        body = r.json()["response"]["body"]
        items = body.get("items")
        if not items:
            break
        item_list = items["item"] if isinstance(items["item"], list) else [items["item"]]
        rows.extend(item_list)
        page_size = int(body["numOfRows"])
        total_count = int(body["totalCount"])
        if page * page_size >= total_count:
            break
        page += 1
        time.sleep(0.2)
    return pd.DataFrame(rows)


def landuse_for_region(region: str) -> dict:
    boundary = gpd.read_file(f"{OUT_DIR}/boundary_{region}.geojson")
    polygon_wkt = _polygon_wkt(boundary)

    # 1) 경계와 교차하는 필지(PNU) 목록
    parcels = fetch_vworld_features(PARCEL_LAYER, polygon_wkt)
    parcel_keys = set()
    dong_set = set()
    for p in parcels:
        d = decode_pnu(p["properties"]["pnu"])
        parcel_keys.add((d["bjdongCd"], d["platGbCd"], d["bun"], d["ji"]))
        dong_set.add((d["sigunguCd"], d["bjdongCd"]))
    print(f"[{region}] 경계 교차 필지 {len(parcels)}개, 관련 법정동 {len(dong_set)}개")

    # 2) 관련 법정동의 건축물대장을 모두 받아 필지 키로 필터링
    all_buildings = []
    for sigungu_cd, bjdong_cd in dong_set:
        df = fetch_buildings_for_dong(sigungu_cd, bjdong_cd)
        if df.empty:
            continue
        df["_key"] = list(zip(df["bjdongCd"], df["platGbCd"], df["bun"], df["ji"]))
        matched = df[df["_key"].isin(parcel_keys)]
        all_buildings.append(matched)
    buildings = pd.concat(all_buildings, ignore_index=True) if all_buildings else pd.DataFrame()
    print(f"[{region}] 매칭된 건축물(표제부 레코드) {len(buildings)}개")

    # 3) 용도지역(필지 단위) 구성비 — 필지 면적 대신 필지 수 비율로 근사(면적 속성 미제공 레이어)
    zoning = fetch_vworld_features(VWORLD_LAYER_USE_ZONE_URBAN, polygon_wkt)
    zoning_counts: dict[str, int] = {}
    for z in zoning:
        uname = z["properties"].get("uname", "미분류")
        zoning_counts[uname] = zoning_counts.get(uname, 0) + 1
    zoning_total = sum(zoning_counts.values()) or 1
    zoning_ratio = {k: round(v / zoning_total, 4) for k, v in zoning_counts.items()}

    # 4) 건축물 주용도 구성비 (연면적 기준) + LUM 엔트로피 + 평균 용적률
    usage_ratio = {}
    lum_entropy = 0.0
    avg_far = None
    if not buildings.empty:
        buildings["totArea"] = pd.to_numeric(buildings["totArea"], errors="coerce").fillna(0)
        buildings["platArea"] = pd.to_numeric(buildings["platArea"], errors="coerce").fillna(0)
        buildings["mainPurpsCdNm"] = buildings["mainPurpsCdNm"].replace("", "미분류").fillna("미분류")

        area_by_purpose = buildings.groupby("mainPurpsCdNm")["totArea"].sum()
        total_area = area_by_purpose.sum()
        if total_area > 0:
            usage_ratio = {k: round(v / total_area, 4) for k, v in area_by_purpose.items()}
            k = (area_by_purpose > 0).sum()
            if k > 1:
                shares = area_by_purpose[area_by_purpose > 0] / total_area
                lum_entropy = round(float(-(shares * shares.apply(math.log)).sum() / math.log(k)), 4)

        plat_area_sum = buildings.drop_duplicates("mgmBldrgstPk")["platArea"].sum()
        if plat_area_sum > 0:
            avg_far = round(float(total_area / plat_area_sum), 4)

    # 5) 공지(미건축) 비율 — 경계 교차 필지 중 건축물대장 매칭이 전혀 없는 필지의 비율
    built_keys = set(zip(buildings["bjdongCd"], buildings["platGbCd"], buildings["bun"], buildings["ji"])) if not buildings.empty else set()
    vacant_lot_ratio = round(1 - len(built_keys) / len(parcel_keys), 4) if parcel_keys else None

    result = {
        "region": region,
        "parcel_count": len(parcels),
        "building_record_count": len(buildings),
        "vacant_lot_ratio": vacant_lot_ratio,
        "zoning_ratio": zoning_ratio,
        "usage_ratio": usage_ratio,
        "lum_entropy": lum_entropy,
        "avg_far": avg_far,
    }
    with open(f"{OUT_DIR}/landuse_{region}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[{region}] {result}")
    return result


def main():
    for region in ("pangyo", "cheongna"):
        landuse_for_region(region)


if __name__ == "__main__":
    main()
