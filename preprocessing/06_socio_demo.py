"""
인구사회 분석 — 구역 내 집계구 인구·가구·종사자·사업체, 직주비.

입력: data_raw/sgis/{region}_census_units.geojson, data_raw/sgis/{region}_business.geojson
출력: stats_summary.json 의 socio_demo 섹션

직주비 = 종사자수 / 상주인구
"""
import geopandas as gpd


def summarize_region(census: gpd.GeoDataFrame, business: gpd.GeoDataFrame) -> dict:
    population = float(census["population"].sum())
    households = float(census["households"].sum())
    workers = float(business["workers"].sum())
    firms = int(business["firm_count"].sum())
    return {
        "population": population,
        "households": households,
        "workers": workers,
        "firms": firms,
        "job_housing_ratio": workers / population if population else None,
    }


def main():
    raise NotImplementedError("Phase 1 SGIS 수집 후 구현")


if __name__ == "__main__":
    main()
