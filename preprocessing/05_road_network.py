"""
도로망 지표 — 도로율, 도로망 밀도(km/km2), 고속도로 IC까지 거리.

입력: OSM (osmnx 로 구역 bbox 또는 polygon 기준 도로망 추출) — API 키 불필요.
출력: stats_summary.json 의 road_network 섹션

주의: 현재는 config.py의 approx_bbox_4326 (임시 bbox)로 동작 검증만 한다.
정식 경계 polygon(보존 출처: PLAN.md §1-2) 확보 후 graph_from_polygon 으로 교체할 것.
"""
import json

import osmnx as ox
from shapely.geometry import box

from config import REGIONS

OUT_DIR = "outputs"


def road_density_for_bbox(bbox_4326: tuple) -> dict:
    min_lon, min_lat, max_lon, max_lat = bbox_4326
    polygon = box(min_lon, min_lat, max_lon, max_lat)
    graph = ox.graph_from_polygon(polygon, network_type="drive")
    edges = ox.graph_to_gdfs(graph, nodes=False)

    edges_5179 = edges.set_crs(epsg=4326).to_crs(epsg=5179)
    total_length_km = edges_5179.geometry.length.sum() / 1000

    area_km2 = (
        __import__("geopandas")
        .GeoSeries([polygon], crs=4326)
        .to_crs(epsg=5179)
        .area.sum()
        / 1e6
    )

    return {
        "edge_count": len(edges),
        "total_length_km": round(total_length_km, 2),
        "bbox_area_km2": round(area_km2, 3),
        "road_density_km_per_km2": round(total_length_km / area_km2, 2),
    }


def main():
    results = {}
    for region, cfg in REGIONS.items():
        print(f"[{region}] OSM 도로망 다운로드 중 (임시 bbox)...")
        results[region] = road_density_for_bbox(cfg["approx_bbox_4326"])
        print(f"[{region}] {results[region]}")

    with open(f"{OUT_DIR}/road_network_smoketest.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"저장됨: {OUT_DIR}/road_network_smoketest.json")


if __name__ == "__main__":
    main()
