"""
인구사회 분석 — 구역계(boundary_*.geojson) 내 집계구 인구·가구·종사자·사업체, 직주비.

입력: data_raw/sgis/{region}_census_units.geojson (인구), data_raw/sgis/{region}_business.geojson (종사자/사업체)
출력: stats_summary.json 의 socio_demo 섹션

공간단위 통합: 구역계와 집계구 경계가 일치하지 않으므로 단순 합산(sum)이 아니라
spatial_utils.areal_weighted_sum() 으로 면적가중 비례배분한다 — 04_population_overlay.py
(등시간권 x 집계구)와 동일한 방법을 재사용해 두 분석의 처리 기준을 통일한다.

직주비 = 종사자수 / 상주인구
"""
import geopandas as gpd

from spatial_utils import areal_weighted_sum


def summarize_region(
    boundary: gpd.GeoDataFrame, census: gpd.GeoDataFrame, business: gpd.GeoDataFrame
) -> dict:
    """boundary, census, business 는 모두 EPSG:5179(미터) 로 변환된 상태로 전달할 것."""
    pop = areal_weighted_sum(census, boundary, ["population", "households"])
    biz = areal_weighted_sum(business, boundary, ["workers", "firm_count"])

    population = pop["population"]
    return {
        "population": population,
        "households": pop["households"],
        "workers": biz["workers"],
        "firms": biz["firm_count"],
        "job_housing_ratio": biz["workers"] / population if population else None,
    }


def main():
    raise NotImplementedError("Phase 1 SGIS 수집 후 구현")


if __name__ == "__main__":
    main()
