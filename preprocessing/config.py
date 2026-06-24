"""공통 설정 — API 키 로드, 두 지역의 확정된 구역계/핵심역 상수 (PLAN.md §1 참고)."""
import os

from dotenv import load_dotenv

load_dotenv()

SGIS_CONSUMER_KEY = os.getenv("SGIS_CONSUMER_KEY")
SGIS_CONSUMER_SECRET = os.getenv("SGIS_CONSUMER_SECRET")
VWORLD_API_KEY = os.getenv("VWORLD_API_KEY")
BUILDING_HUB_API_KEY = os.getenv("BUILDING_HUB_API_KEY")

# SGIS 통계지리정보서비스 — 검증된 인증 엔드포인트 (2026-06-24, accessToken 발급 확인).
# kostat.go.kr 도메인은 mods.go.kr 로 302 리다이렉트됨 — requests 는 기본적으로 따라가므로 문제 없음.
SGIS_AUTH_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/auth/authentication.json"

# 건축HUB 건축물대장정보 서비스 (공공데이터포털 id=15134735) — 검증된 base URL.
# 주의: data.go.kr 문서/예제에 흔히 나오는 "BldRgstService_v2"는 404/500 오류가 남.
# 올바른 경로는 "BldRgstHubService" (2026-06-24, getBrTitleInfo 로 실키 검증 완료).
BUILDING_HUB_BASE_URL = "http://apis.data.go.kr/1613000/BldRgstHubService"
BUILDING_HUB_OPERATIONS = {
    "basis_oulin": "getBrBasisOulnInfo",      # 기본개요
    "recap_title": "getBrRecapTitleInfo",      # 총괄표제부
    "title": "getBrTitleInfo",                 # 표제부
    "floor_oulin": "getBrFlrOulnInfo",         # 층별개요
    "atch_jibun": "getBrAtchJibunInfo",        # 부속지번
    "expos_pubuse_area": "getBrExposPubuseAreaInfo",  # 전유공용면적
    "wclf": "getBrWclfInfo",                   # 오수정화시설
    "hsprc": "getBrHsprcInfo",                 # 주택가격
    "expos": "getBrExposInfo",                 # 전유부
    "jijigu": "getBrJijiguInfo",               # 지역지구구역
}

# VWorld 2D데이터 API(용도지역지구 - 국토계획법) — 검증 완료 (2026-06-24, 판교역 좌표로 "준주거지역" 확인).
# 주의: 데이터API는 지도/검색API와 달리 "domain" 파라미터(키 발급 시 등록한 서비스 URL)를
# 반드시 같이 보내야 함 — 빠뜨리면 키가 멀쩡해도 INCORRECT_KEY 오류가 난다.
VWORLD_DATA_URL = "https://api.vworld.kr/req/data"
VWORLD_DOMAIN = "https://park971011-ui.github.io/comparing_system/"  # 인증키 발급 시 등록한 서비스 URL
# LT_C_UQ111 = 도시지역. 다른 용도지역(관리/농림/자연환경보전 등)은 VWorld API레퍼런스의
# "용도지역지구(국토계획법)" 카테고리에서 레이어 코드를 추가로 확인할 것.
VWORLD_LAYER_USE_ZONE_URBAN = "LT_C_UQ111"

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
