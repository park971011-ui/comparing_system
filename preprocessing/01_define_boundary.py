"""
구역계 정의 — 판교테크노밸리 / 청라국제업무지구 경계 GeoJSON 생성.

방법론 (2026-06-25, 시간 제약상 임시 채택):
국토부 NSDI/UPIS 지구단위계획구역 API는 data.go.kr 별도 활용신청이 필요해
1~2일 승인 대기가 발생하고, UPIS 단독 사이트는 서비스 종료됐다(eum.go.kr로 통합).
정식 결정도면(좌표) 확보 전까지, PLAN.md §1-2에 명시된 "공식 면적 수치"에 맞춘
**면적-일치 근사 사각형**을 핵심역 인근에 배치해 임시 경계로 쓴다.

- 판교테크노밸리: 661,157㎡, 신분당선 판교역(127.11116, 37.39457) 북쪽 삼평동 일원.
  법적 근거(확인됨): 성남시 고시 제2025-6호(2025.1.6) "성남 도시관리계획(지구단위계획:
  분당지구, 판교지구 등) 결정(변경) 고시" — 단 변경분만 수록된 문서라 결정도면 좌표는
  미포함. 경계 형상은 eum.go.kr 이음지도 실측 확인(2026-06-25, 분당구 삼평동 일대)으로
  시각 검증함(스크린샷 PLAN.md 작업 기록 참고).
- 청라국제업무지구: 278,000㎡(가+나구역), 공항철도 청라국제도시역(126.62465, 37.55649) 인근.
  IFEZ 지구단위계획 청라국제도시 국제업무지구(plan_se=C03015) 면적 수치만 확인, 정식
  결정고시 번호는 미확인 (Phase 0 잔여 TODO — eum.go.kr seq=519197 은 무관한 고시로
  판명되어 인용 취소함).

주의: 이 polygon은 정식 결정도면 좌표가 아니라 "면적-일치 근사치"다. 보고서에는
"경계 형상은 면적 기준 근사이며, 법적 근거 고시번호는 위 표와 같이 확인했으나 결정도면
좌표 자체는 미확보"임을 명시할 것. 정식 polygon 확보 시 이 스크립트를 교체한다.

출력: preprocessing/outputs/boundary_pangyo.geojson, boundary_cheongna.geojson
      각 properties 에 area_m2(목표 면적), actual_area_m2(생성된 polygon 실제 면적),
      source, is_approximate=True 기록.
"""
import json

import geopandas as gpd
from shapely.affinity import rotate
from shapely.geometry import box, mapping
from shapely.ops import transform
from pyproj import Transformer

OUT_DIR = "outputs"

# 핵심역 실제 좌표 (subway_network/network/nodes.tsv 확인, WGS84)
CORE_STATION_LATLON = {
    "pangyo": (127.11116, 37.39457),       # 신분당선 판교역
    "cheongna": (126.62465, 37.55649),     # 공항철도 청라국제도시역
}

# 핵심역 기준 중심 오프셋(미터, east/north) — 업무단지가 역에서 떨어진 방향 보정용 추정치.
CENTER_OFFSET_M = {
    "pangyo": (250, 600),       # 판교테크노밸리는 역 북쪽 삼평동 일원
    "cheongna": (-300, -400),   # 청라업무단지(가/나구역)는 역 서남쪽 인근으로 보고된 위치
}

REGIONS = {
    "pangyo": {"area_m2": 661_157, "rect_ratio": 1.8, "rotation_deg": 15,
               "source": "성남시 판교지구 지구단위계획 특별계획구역(2004.12 지정) 공식 면적"},
    "cheongna": {"area_m2": 278_000, "rect_ratio": 1.3, "rotation_deg": -10,
                 "source": "IFEZ 지구단위계획 청라국제도시 국제업무지구(가+나구역) 공식 면적"},
}

to_5179 = Transformer.from_crs("EPSG:4326", "EPSG:5179", always_xy=True)
to_4326 = Transformer.from_crs("EPSG:5179", "EPSG:4326", always_xy=True)


def make_boundary(region: str) -> gpd.GeoDataFrame:
    cfg = REGIONS[region]
    lon, lat = CORE_STATION_LATLON[region]
    sx, sy = to_5179.transform(lon, lat)
    dx, dy = CENTER_OFFSET_M[region]
    cx, cy = sx + dx, sy + dy

    area = cfg["area_m2"]
    ratio = cfg["rect_ratio"]
    h = (area / ratio) ** 0.5
    w = ratio * h

    rect = box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    rect = rotate(rect, cfg["rotation_deg"], origin=(cx, cy))

    rect_4326 = transform(lambda x, y: to_4326.transform(x, y), rect)

    gdf = gpd.GeoDataFrame(
        {
            "region": [region],
            "area_m2": [area],
            "actual_area_m2": [round(rect.area, 1)],
            "source": [cfg["source"]],
            "is_approximate": [True],
            "note": ["면적-일치 근사 사각형. 정식 지구단위계획 고시 경계 아님 (PLAN.md §1-2 참고)"],
        },
        geometry=[rect_4326],
        crs="EPSG:4326",
    )
    return gdf


def main():
    for region in REGIONS:
        gdf = make_boundary(region)
        out_path = f"{OUT_DIR}/boundary_{region}.geojson"
        gdf.to_file(out_path, driver="GeoJSON")
        row = gdf.iloc[0]
        print(f"[{region}] 목표면적={row['area_m2']}㎡ 실제생성면적={row['actual_area_m2']}㎡ -> {out_path}")


if __name__ == "__main__":
    main()
