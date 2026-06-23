"""
도로망 지표 — 도로율, 도로망 밀도(km/km2), 고속도로 IC까지 거리.

입력: OSM (osmnx 로 구역 bbox 또는 polygon 기준 도로망 추출)
출력: stats_summary.json 의 road_network 섹션
"""
import osmnx as ox
import geopandas as gpd


def road_density(boundary: gpd.GeoDataFrame) -> dict:
    polygon = boundary.to_crs(epsg=4326).geometry.unary_union
    graph = ox.graph_from_polygon(polygon, network_type="drive")
    edges = ox.graph_to_gdfs(graph, nodes=False)
    area_km2 = boundary.to_crs(epsg=5179).geometry.area.sum() / 1e6
    total_length_km = edges.to_crs(epsg=5179).geometry.length.sum() / 1000
    return {"road_density_km_per_km2": total_length_km / area_km2}


def main():
    raise NotImplementedError("Phase 0 경계 확정 후 구현")


if __name__ == "__main__":
    main()
