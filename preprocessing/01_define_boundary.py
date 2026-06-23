"""
구역계 정의 — 판교테크노밸리 / 청라국제업무지구 경계 GeoJSON 생성.

입력: 지구단위계획 고시 경계 좌표 (data_raw/boundary/*.geojson 또는 직접 좌표 입력)
출력: preprocessing/outputs/boundary_pangyo.geojson, boundary_cheongna.geojson
      각 GeoJSON properties 에 area_m2, source, source_date 기록.

TODO(Phase 0):
- 판교테크노밸리 사업지구 경계 출처 확보 (성남시 고시)
- 청라국제업무지구(국제업무용지) 경계 출처 확보 (인천경제자유구역청 지구단위계획 고시)
"""
import geopandas as gpd

OUT_DIR = "preprocessing/outputs"


def load_boundary(path: str, name: str, source: str, source_date: str) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    gdf = gdf.to_crs(epsg=5179)
    gdf["area_m2"] = gdf.geometry.area
    gdf["name"] = name
    gdf["source"] = source
    gdf["source_date"] = source_date
    return gdf.to_crs(epsg=4326)


def main():
    raise NotImplementedError("Phase 0 경계 출처 확보 후 구현")


if __name__ == "__main__":
    main()
