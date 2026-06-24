"""
인구사회 분석 — 구역계(boundary_*.geojson) 내 집계구 인구·가구·종사자·사업체, 직주비.

방법론 (2026-06-24):
1. SGIS addr/stage.json 으로 사전에 확인한 관련 행정동(8자리 adm_cd) 목록에 대해
   - boundary/statsarea.geojson(adm_cd=행정동) → 집계구 polygon (EPSG:5179, 14자리 집계구 adm_cd)
   - stats/population.json(adm_cd=행정동, low_search=1, year) → 집계구별 인구/가구/사업체/종사자
   를 adm_cd 키로 결합한다.
2. 공간단위 통합: 구역계와 집계구 경계가 불일치하므로 spatial_utils.areal_weighted_sum() 으로
   면적가중 비례배분한다 (04_population_overlay.py 와 동일 방법, PLAN.md 참고).

관련 행정동 목록은 02_landuse.py 에서 확인한 경계 교차 법정동을 참고해 사전에 수동 확정
(행정동/법정동 코드체계가 달라 자동 매핑하지 않음 — 동명 기준 수동 확인, 아래 RELATED_DONGS).

출력: preprocessing/outputs/socio_demo_{region}.json
"""
import json

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import shape

from config import SGIS_AUTH_URL, SGIS_CONSUMER_KEY, SGIS_CONSUMER_SECRET
from spatial_utils import areal_weighted_sum

OUT_DIR = "outputs"
STATS_YEAR = "2023"  # SGIS 인구통계 최신 공개 연도 (Phase 1 확정값과 일치시킬 것)

# 02_landuse.py 의 경계 교차 법정동(VWorld PNU 기준)을 동명으로 대조해 확정한 SGIS 행정동코드.
RELATED_DONGS = {
    "pangyo": ["31023740", "31023760", "31023750", "31023680"],  # 삼평동/백현동/판교동/운중동
    "cheongna": ["23080740", "23080780", "23080790"],  # 청라1동/2동/3동
}

NUMERIC_FIELDS = ["tot_ppltn", "tot_family", "employee_cnt", "corp_cnt"]


def get_token() -> str:
    r = requests.get(SGIS_AUTH_URL, params={"consumer_key": SGIS_CONSUMER_KEY, "consumer_secret": SGIS_CONSUMER_SECRET})
    return r.json()["result"]["accessToken"]


def fetch_census_units(token: str, adm_cd_8: str) -> gpd.GeoDataFrame:
    boundary_resp = requests.get(
        "https://sgisapi.kostat.go.kr/OpenAPI3/boundary/statsarea.geojson",
        params={"accessToken": token, "adm_cd": adm_cd_8}, timeout=30,
    ).json()
    pop_resp = requests.get(
        "https://sgisapi.kostat.go.kr/OpenAPI3/stats/population.json",
        params={"accessToken": token, "year": STATS_YEAR, "adm_cd": adm_cd_8, "low_search": "1"}, timeout=30,
    ).json()

    geoms = {f["properties"]["adm_cd"]: shape(f["geometry"]) for f in boundary_resp["features"]}
    pop_df = pd.DataFrame(pop_resp["result"])
    pop_df["geometry"] = pop_df["adm_cd"].map(geoms)
    pop_df = pop_df.dropna(subset=["geometry"])

    for col in NUMERIC_FIELDS:
        pop_df[col] = pd.to_numeric(pop_df[col], errors="coerce").fillna(0)

    return gpd.GeoDataFrame(pop_df, geometry="geometry", crs="EPSG:5179")


def socio_demo_for_region(region: str) -> dict:
    token = get_token()
    parts = [fetch_census_units(token, adm) for adm in RELATED_DONGS[region]]
    census = pd.concat(parts, ignore_index=True)
    census = gpd.GeoDataFrame(census, geometry="geometry", crs="EPSG:5179")

    boundary = gpd.read_file(f"{OUT_DIR}/boundary_{region}.geojson").to_crs(epsg=5179)

    agg = areal_weighted_sum(census, boundary, NUMERIC_FIELDS)
    population = agg["tot_ppltn"]
    workers = agg["employee_cnt"]

    result = {
        "region": region,
        "stats_year": STATS_YEAR,
        "population": round(population, 1),
        "households": round(agg["tot_family"], 1),
        "workers": round(workers, 1),
        "firms": round(agg["corp_cnt"], 1),
        "job_housing_ratio": round(workers / population, 4) if population else None,
        "census_unit_count": len(census),
    }
    with open(f"{OUT_DIR}/socio_demo_{region}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[{region}] {result}")
    return result


def main():
    for region in RELATED_DONGS:
        socio_demo_for_region(region)


if __name__ == "__main__":
    main()
