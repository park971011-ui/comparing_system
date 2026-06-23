"""
등시간권 × SGIS 집계구 면적가중 결합 — 도달가능 인구/종사자 산출, 누적접근성곡선.

입력:
  preprocessing/outputs/isochrone_{region}_30_60.geojson
  data_raw/sgis/{region}_census_units.geojson (집계구 + 인구/종사자 속성)

출력:
  stats_summary.json 의 accessibility 섹션
  preprocessing/outputs/accessibility_curve.json (0~60분, 5분 단위)

방법(공간단위 통합): 집계구가 등시간권 경계에 걸칠 경우 교차면적/집계구면적 비율로
인구·종사자를 비례 배분(areal interpolation)한다. 보고서 "분석 방법" 절에 동일 서술 필요.
"""
import geopandas as gpd


def areal_weighted_sum(isochrone: gpd.GeoDataFrame, census: gpd.GeoDataFrame, value_cols: list[str]) -> dict:
    inter = gpd.overlay(census, isochrone[["geometry"]], how="intersection")
    inter["weight"] = inter.geometry.area / inter["geometry_area_full"]
    return {col: float((inter[col] * inter["weight"]).sum()) for col in value_cols}


def main():
    raise NotImplementedError("Phase 1 SGIS 수집 + Phase 3 등시간권 완료 후 구현")


if __name__ == "__main__":
    main()
