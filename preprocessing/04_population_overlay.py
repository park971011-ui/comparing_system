"""
등시간권 × SGIS 집계구 면적가중 결합 — 도달가능 인구/종사자 산출, 누적접근성곡선.

입력:
  preprocessing/outputs/isochrone_{region}_30_60.geojson
  data_raw/sgis/{region}_census_units.geojson (집계구 + 인구/종사자 속성)

출력:
  stats_summary.json 의 accessibility 섹션
  preprocessing/outputs/accessibility_curve.json (0~60분, 5분 단위)

공간단위 통합: spatial_utils.areal_weighted_sum() 사용 (06_socio_demo.py 와 동일 방법 공유).
누적 접근성 곡선을 만들려면 03_isochrone.py 를 5분 간격 cutoff(0,5,...,60)로 반복 실행해
각 간격의 polygon 을 만들고 이 함수에 통과시키면 된다.
"""
import geopandas as gpd

from spatial_utils import areal_weighted_sum


def main():
    raise NotImplementedError(
        "Phase 1 SGIS 집계구 수집 후 구현 — areal_weighted_sum(census_5179, isochrone_5179, "
        "['population','workers']) 형태로 호출"
    )


if __name__ == "__main__":
    main()
