# 프로젝트 플랜 — 판교테크노밸리 vs 청라국제업무지구

## 0. 확정된 전제
- 기준 지역: 판교테크노밸리 (제1판교만, 제2판교 제외 — 조성 시점·경계 명확성 확보)
- 비교 지역: 인천 청라국제업무지구
- 핵심역: 판교역(신분당선/경강선) vs 청라국제도시역(공항철도, 2027 개통 예정 → **현재 시점 기준 미개통이면 검암역 등 대체 핵심역 검토 필요, §1에서 확정**)
- 기술 스택: React + Vite + MapLibre GL JS / deck.gl, GitHub Pages 배포
- 전처리: Python (pandas, geopandas, networkx/scipy.sparse)
- 제공 데이터: `subway_network/network/{nodes,links}.tsv` 활용 (dijkstra, scipy.sparse.csgraph)

## 1. Phase 0 — 범위 확정 (선행 필수, 착수 전 의사결정)
- [ ] 청라국제업무지구 구역계 정의: 인천경제자유구역청 지구단위계획 고시문에서 "국제업무용지" 블록 경계 좌표 확보, 면적 산출
- [ ] 판교테크노밸리 구역계 정의: 판교테크노밸리 사업지구 경계(성남시 고시) 확보, 면적 산출 — 두 지역 면적 차이가 클 경우 비교 방법(면적 정규화 등) 명시
- [ ] "실패/저조" 근거 자료 수집: 청라 업무용지 공실률·미매각 통계, 언론보도, 인천경제청 감사자료 등 3건 이상 스크랩 (출처·날짜 기록)
- [ ] 핵심역 확정: 청라국제도시역 운영 여부 확인 (subway_network nodes.tsv의 begin/effective_begin 확인) → 미개통이면 대체역 또는 "2027 개통 후 시나리오"를 별도 분석으로 추가
- [ ] 기준연도/기준월 확정 (예: 2025년 12월 또는 가장 최신 공개 통계 시점) — 모든 지표 동일 기준 적용

## 2. Phase 1 — 데이터 수집
| 데이터 | 소스 | 담당 작업 |
|---|---|---|
| 집계구 인구·종사자 | SGIS 통계지리정보서비스 (Open API) | API 키 발급, 두 구역 + 등시간권 범위 집계구 조회 |
| 토지이용계획(용도지역) | VWorld 토지이용계획정보 API/다운로드 | 두 구역 polygon 추출 |
| 건축물대장 | 건축HUB API | 구역 내 건축물 목록 + 주용도·연면적·용적률 |
| 도로망 | OSM (Overpass API 또는 osmnx) | 두 구역 도로 네트워크 추출, 도로율·밀도 산출 |
| 지하철망 | 제공된 subway_network.zip | 그대로 사용 (이미 그래프 구축됨) |
| 버스정류장(보조) | 국토교통부 정류장 정보 | 구역 내 정류장 밀도 |

- [ ] 각 API 키 발급 (SGIS, VWorld, 건축HUB)
- [ ] `data_raw/` 폴더에 원본 저장, 모든 다운로드 스크립트는 재현 가능하게 저장

## 3. Phase 2 — 전처리 (Python)
디렉토리 구조 제안:
```
preprocessing/
├── 01_define_boundary.py      # 두 구역 경계 GeoJSON 생성 + 면적 계산
├── 02_landuse.py               # 용도지역·건축물대장 → 구역 내 클리핑, LUM 엔트로피, 평균 용적률
├── 03_isochrone.py             # dijkstra(subway network) → 30/60분 등시간권 폴리곤(컨벡스헐 또는 역세권 버퍼 유니온)
├── 04_population_overlay.py    # 등시간권 polygon × SGIS 집계구 면적가중 결합 → 인구/종사자 합산
├── 05_road_network.py          # OSM 도로망 → 도로율·밀도
├── 06_socio_demo.py            # 구역 내 집계구 인구·종사자·직주비
└── outputs/                    # 모든 산출물 GeoJSON/JSON (시스템에서 바로 로드)
```
핵심 산출물(시스템 입력용 정적 파일):
- `boundary_pangyo.geojson`, `boundary_cheongna.geojson`
- `landuse_pangyo.geojson`, `landuse_cheongna.geojson` (용도지역/건축물 주용도 속성 포함)
- `isochrone_pangyo_30_60.geojson`, `isochrone_cheongna_30_60.geojson`
- `accessibility_curve.json` (0~60분, 5분 단위 도달인구/종사자)
- `stats_summary.json` (두 지역 전 지표 한 곳에 모음 — 시스템 통계 패널과 보고서 수치의 단일 소스)

> 원칙: **보고서의 모든 수치는 `stats_summary.json`에서 나온다.** 보고서와 시스템 수치 불일치 감점을 원천 차단.

## 4. Phase 3 — 등시간권 분석 (핵심)
- [ ] nodes/links.tsv 로드, `effective_begin` 기준으로 분석 시점 cutoff 적용
- [ ] scipy.sparse.csgraph.dijkstra로 핵심역 기준 전역 SSSP 계산
- [ ] 도달 노드(역)에 보행 버퍼(예: 500m) 적용해 면적 폴리곤화 (역세권 유니온 또는 보로노이+컨벡스헐)
- [ ] SGIS 집계구와 면적가중 overlay → 30분/60분 도달 인구·종사자
- [ ] 0~60분 5분 간격 누적 접근성 곡선 산출
- [ ] 두 지역 동일 방법론으로 산출 후 격차 시점/구간 식별

## 5. Phase 4 — 시스템 개발 (React + Vite + MapLibre)
```
system/
├── src/
│   ├── components/
│   │   ├── MapView.tsx          # 두 지역 토글/사이드바이사이드, 용도 컬러맵, 클릭 속성 팝업
│   │   ├── IsochroneLayer.tsx   # 30/60분 슬라이더, 폴리곤 표출 + 인구·종사자 라벨
│   │   ├── StatsPanel.tsx       # 비교 표 + 파이/바 차트 + 누적접근성곡선 (Chart.js/recharts)
│   │   └── RegionToggle.tsx
│   ├── data/                    # Phase 2 출력 GeoJSON/JSON 복사
│   └── App.tsx
├── vite.config.ts (base: '/repo-name/')
└── .github/workflows/deploy.yml  # GitHub Actions → Pages 자동 배포
```
필수기능 체크리스트(§4 매핑):
- [ ] 지도 시각화: 경계+건축물/필지 컬러맵, 지역 전환 또는 side-by-side
- [ ] 등시간권 레이어: 30/60분 슬라이더 + 인구·종사자 수치 동시 표시
- [ ] 통계 패널: 토지이용/교통/인구사회 비교 표+차트, 누적접근성곡선
- [ ] 클릭 상호작용: 필지/건축물 속성 팝업

## 6. Phase 5 — 분석 해석 & 성공요인 도출
- [ ] 3개 영역(토지이용/교통/인구사회) 수치표 완성
- [ ] "차이 → 원인" 해석 메모 작성 (왜 그 차이가 나는지, 상관/인과 구분)
- [ ] 성공요인 3가지 이상 도출, 각각 수치로 근거 제시
- [ ] 한계 서술 (구역계 비대칭, 집계구 통합 오차, 인과추론 한계 등)

## 7. Phase 6 — 보고서 작성 (A4 10매 이내)
구성: 서론 → 분석방법(시공간범위·단위 명시) → 비교분석(토지/교통/인구) → 성공요인 → 한계 → 부록(시스템 URL, 저장소 URL, 데이터 출처, AI 활용내역)
- [ ] 모든 표/그림에 "시스템 OO화면 근거" 캡션 명시
- [ ] AI 활용 문단 작성 (도구명, 활용범위)
- [ ] PDF 변환 전 분량(11pt, 10매) 점검

## 8. Phase 7 — 제출 준비
- [ ] GitHub repo public 전환, README(데이터 출처/기준월/재현 절차) 완성
- [ ] GitHub Pages 배포 확인 (실제 URL 접속 테스트, 모바일/속도 점검)
- [ ] 보고서 PDF 최종 수치 ↔ 시스템 수치 1:1 대조
- [ ] LMS 제출 (저장소 URL, Pages URL, PDF)

## 다음 액션
Phase 0의 의사결정(구역계 출처 확보, 청라역 개통여부 확인, 기준월 확정)이 먼저 끝나야 API 호출 범위가 정해짐 → 바로 시작할지, 또는 저장소/디렉토리 스캐폴딩(Phase 4 폴더 구조)부터 만들지 알려주시면 진행하겠습니다.
