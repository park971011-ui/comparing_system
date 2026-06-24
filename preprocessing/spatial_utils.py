"""
공간단위 통합(areal interpolation) 공통 유틸 — 8강에서 다룬 문제의 해결책.

구역계(boundary)나 등시간권(isochrone) polygon은 SGIS 집계구 경계와 일치하지 않는다.
집계구가 polygon 경계에 걸칠 경우, "교차면적/집계구 전체면적" 비율로 인구·종사자를
비례 배분해 합산한다 (단순 포함/제외 방식이 아님).

이 모듈은 04_population_overlay.py(등시간권 x 집계구)와
06_socio_demo.py(구역계 x 집계구) 양쪽에서 동일하게 재사용한다 — 두 분석의
공간단위 통합 방법이 달라지면 "동일 기준 비교"가 깨지므로 반드시 공유 함수로 유지할 것.
"""
import geopandas as gpd


def areal_weighted_sum(
    census: gpd.GeoDataFrame, clip_polygon: gpd.GeoDataFrame, value_cols: list[str]
) -> dict:
    """census 의 value_cols 를 clip_polygon 영역 기준으로 면적가중 합산.

    census, clip_polygon 은 동일한 평면(미터 단위) CRS 여야 정확한 면적비가 나온다
    (EPSG:5179 권장). census 에는 사전에 'geometry' 와 각 value_cols 가 있어야 한다.
    """
    census = census.copy()
    census["_full_area"] = census.geometry.area
    inter = gpd.overlay(census, clip_polygon[["geometry"]], how="intersection")
    inter["_weight"] = inter.geometry.area / inter["_full_area"]
    return {col: float((inter[col] * inter["_weight"]).sum()) for col in value_cols}
