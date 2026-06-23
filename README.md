# 판교테크노밸리 vs 청라국제업무지구 비교분석 시스템

수도권 업무지구 성공요인을 토지이용·교통망(등시간권)·인구사회 데이터로 비교분석하는
정적 웹 시스템 (GitHub Pages 배포) 및 전처리 파이프라인.

## 폴더 구조
```
.
├── PLAN.md                  프로젝트 전체 플랜 (Phase 0~7)
├── subway_network/          제공 데이터 — 수도권 지하철 네트워크 그래프 (README 참고)
├── data_raw/                원본 다운로드 데이터 (SGIS/VWorld/건축HUB/OSM) — git 미추적
├── preprocessing/           Python 전처리 스크립트 (01~06) + outputs/ (GeoJSON/JSON 산출물)
├── system/                  React + Vite + MapLibre 정적 웹앱 (GitHub Pages 배포 대상)
└── .github/workflows/       GitHub Pages 자동 배포 워크플로
```

## 데이터 출처 및 기준 시점
| 데이터 | 출처 | 기준 시점 |
|---|---|---|
| 집계구 인구·종사자 | SGIS 통계지리정보서비스 | TODO (Phase 0에서 확정) |
| 용도지역 | VWorld 토지이용계획정보 | TODO |
| 건축물대장 | 건축HUB | TODO |
| 도로망 | OpenStreetMap | TODO (다운로드 시점) |
| 지하철 네트워크 | 자체 제작 (`subway_network/`, 2026-05-05 export) | 분석 시점 cutoff는 `03_isochrone.py`의 `T` 변수 |

## 재현 방법
```powershell
# 1. 전처리
cd preprocessing
pip install -r requirements.txt
python 01_define_boundary.py
python 02_landuse.py
python 03_isochrone.py
python 04_population_overlay.py
python 05_road_network.py
python 06_socio_demo.py
# 산출물은 preprocessing/outputs/ 에 생성 → system/src/data/ 로 복사

# 2. 시스템 로컬 실행
cd ../system
npm install
npm run dev
```

## 배포
`main` 브랜치의 `system/` 변경 시 GitHub Actions(`.github/workflows/deploy.yml`)가
자동으로 빌드 후 GitHub Pages에 배포한다. 저장소 Settings → Pages → Source를
"GitHub Actions"로 설정해야 한다. `system/vite.config.ts`의 `base`를 실제 저장소 이름으로 맞출 것.

## 현재 상태
스캐폴딩 단계 — Phase 0(구역계·기준시점 확정)이 끝나야 전처리 스크립트의 TODO를
채울 수 있다. 자세한 단계별 계획은 [PLAN.md](PLAN.md) 참고.
