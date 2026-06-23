"""공통 설정 — API 키 로드, 두 지역의 확정된 구역계/핵심역 상수 (PLAN.md §1 참고)."""
import os

from dotenv import load_dotenv

load_dotenv()

SGIS_CONSUMER_KEY = os.getenv("SGIS_CONSUMER_KEY")
SGIS_CONSUMER_SECRET = os.getenv("SGIS_CONSUMER_SECRET")
VWORLD_API_KEY = os.getenv("VWORLD_API_KEY")
BUILDING_HUB_API_KEY = os.getenv("BUILDING_HUB_API_KEY")

# Phase 0 확정 (PLAN.md §1)
REGIONS = {
    "pangyo": {
        "name_kr": "판교테크노밸리(제1판교)",
        "expected_area_m2": 661_157,
        "boundary_source": "성남시 판교지구 지구단위계획 (특별계획구역, 2004.12 지정)",
        "core_station": {"statnm": "판교", "linenm": "신분당선"},
        "approx_bbox_4326": (127.095, 37.392, 127.122, 37.408),  # (min_lon, min_lat, max_lon, max_lat) 임시 — 정식 경계 확보 전 OSM 테스트용
    },
    "cheongna": {
        "name_kr": "청라국제업무지구",
        "expected_area_m2": 278_000,
        "boundary_source": "IFEZ 지구단위계획 청라국제도시 국제업무지구 (plan_se=C03015), 토지이음 고시 eum.go.kr seq=519197",
        "core_station": {"statnm": "청라국제도시", "linenm": "공항철도"},
        "approx_bbox_4326": (126.615, 37.525, 126.640, 37.540),  # 임시 bbox
    },
}

ISOCHRONE_CUTOFF_DATE = "2026-05-04"
