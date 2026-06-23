"""
구역계 정의 — 판교테크노밸리 / 청라국제업무지구 경계 GeoJSON 생성.

입력: 지구단위계획 고시 경계 좌표 (data_raw/boundary/*.geojson 또는 직접 좌표 입력)
출력: preprocessing/outputs/boundary_pangyo.geojson, boundary_cheongna.geojson
      각 GeoJSON properties 에 area_m2, source, source_date 기록.

Phase 0 확정 (PLAN.md §1-2 참고):
- 판교테크노밸리(제1판교): 판교지구 특별계획구역(2004.12 지정), 면적 661,157㎡
  출처: 성남시 판교지구 지구단위계획 (고시번호 TODO — eum.go.kr 원문 확인 필요)
- 청라국제업무지구: 가구역(144,000㎡)+나구역(134,000㎡) = 278,000㎡
  출처: IFEZ 지구단위계획 청라국제도시 국제업무지구(plan_se=C03015),
        토지이음 고시 eum.go.kr seq=519197 (정확한 고시번호·일자 TODO)

TODO: 위 출처에서 실제 경계 polygon 좌표(GeoJSON/도면) 다운로드 후 EXPECTED_AREA_M2 와
대조 검증 (오차 5% 이내 권장). 좌표 확보 전까지는 area_m2 만 PLAN.md 수치로 하드코딩.
"""
import geopandas as gpd

OUT_DIR = "preprocessing/outputs"

EXPECTED_AREA_M2 = {
    "pangyo": 661_157,
    "cheongna": 278_000,
}


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
