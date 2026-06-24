"""
등시간권 × SGIS 면적가중 결합 — 0~60분(5분 간격) 누적 도달가능 인구/종사자 곡선.

방법론 (2026-06-24):
구역계(06_socio_demo.py)와 달리 등시간권은 수도권 전역을 덮어 집계구 단위로 전부
받으면 API 호출이 수천 건이 된다. 따라서 이 분석은 **시군구 단위**(coarser)로 수행한다
— 보고서에는 §3-3(구역 내 인구사회, 집계구 단위)과 본 분석(등시간권, 시군구 단위)의
공간단위가 다르다는 점과 그 이유를 반드시 명시할 것 (강령이 요구하는 "공간단위 명시").

절차:
1. 03_isochrone.py 의 dist_sec 를 재사용해 0,5,...,60분 cutoff 폴리곤을 생성.
2. 60분 폴리곤의 bbox 로 SGIS boundary/userarea.geojson(cd=2, 시군구)을 한 번 조회.
3. 매칭된 시군구(adm_cd 5자리)마다 stats/population.json 으로 인구/종사자 합계를 가져와
   geometry 와 결합 (전역 캐시로 두 지역이 공유하는 시군구 중복 호출 방지).
4. 각 cutoff 폴리곤과 spatial_utils.areal_weighted_sum() 으로 결합해 누적 곡선 산출.

출력: preprocessing/outputs/accessibility_curve.json
"""
import importlib.util
import json

import geopandas as gpd
import pandas as pd
import requests

from config import SGIS_AUTH_URL, SGIS_CONSUMER_KEY, SGIS_CONSUMER_SECRET
from spatial_utils import areal_weighted_sum

spec = importlib.util.spec_from_file_location("isochrone_mod", "03_isochrone.py")
isochrone_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(isochrone_mod)

OUT_DIR = "outputs"
MINUTE_STEPS = list(range(5, 65, 5))  # 5,10,...,60
STATS_YEAR = "2023"
_pop_cache: dict[str, dict] = {}


def get_token() -> str:
    r = requests.get(SGIS_AUTH_URL, params={"consumer_key": SGIS_CONSUMER_KEY, "consumer_secret": SGIS_CONSUMER_SECRET})
    return r.json()["result"]["accessToken"]


def fetch_sgg_in_bbox(token: str, bounds_5179: tuple) -> gpd.GeoDataFrame:
    minx, miny, maxx, maxy = bounds_5179
    r = requests.get(
        "https://sgisapi.kostat.go.kr/OpenAPI3/boundary/userarea.geojson",
        params={"accessToken": token, "cd": "2", "minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy},
        timeout=30,
    ).json()
    rows = []
    for f in r["features"]:
        adm_cd = f["properties"]["adm_cd"]
        if adm_cd not in _pop_cache:
            pop = requests.get(
                "https://sgisapi.kostat.go.kr/OpenAPI3/stats/population.json",
                params={"accessToken": token, "year": STATS_YEAR, "adm_cd": adm_cd}, timeout=30,
            ).json()
            _pop_cache[adm_cd] = pop["result"][0] if pop.get("result") else None
        pop_row = _pop_cache[adm_cd]
        if not pop_row:
            continue
        from shapely.geometry import shape
        rows.append({
            "adm_cd": adm_cd,
            "tot_ppltn": float(pop_row.get("tot_ppltn", 0) or 0),
            "employee_cnt": float(pop_row.get("employee_cnt", 0) or 0),
            "geometry": shape(f["geometry"]),
        })
    return gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:5179")


def main():
    token = get_token()
    nodes, links = isochrone_mod.load_active_network(isochrone_mod.T)
    A, id_map = isochrone_mod.build_csr(nodes, links)

    curve = {m: {} for m in MINUTE_STEPS}
    for region in isochrone_mod.CORE_STATIONS:
        dist_sec = isochrone_mod.dist_sec_for_region(region, nodes, A, id_map)

        sixty_poly, _ = isochrone_mod.polygon_for_cutoff(nodes, dist_sec, 60 * 60)
        sgg = fetch_sgg_in_bbox(token, sixty_poly.bounds)
        print(f"[{region}] 60분권 bbox 내 시군구 {len(sgg)}개 매칭")

        for minutes in MINUTE_STEPS:
            poly, reach_n = isochrone_mod.polygon_for_cutoff(nodes, dist_sec, minutes * 60)
            poly_gdf = gpd.GeoDataFrame({"geometry": [poly]}, crs="EPSG:5179")
            agg = areal_weighted_sum(sgg, poly_gdf, ["tot_ppltn", "employee_cnt"])
            curve[minutes][region] = {
                "population": round(agg["tot_ppltn"], 1),
                "workers": round(agg["employee_cnt"], 1),
                "station_count": reach_n,
            }
        print(f"[{region}] 60분 도달 인구={curve[60][region]['population']}, 종사자={curve[60][region]['workers']}")

    with open(f"{OUT_DIR}/accessibility_curve.json", "w", encoding="utf-8") as f:
        json.dump(curve, f, ensure_ascii=False, indent=2)
    print(f"저장됨: {OUT_DIR}/accessibility_curve.json")


if __name__ == "__main__":
    main()
