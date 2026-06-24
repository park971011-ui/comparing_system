"""
등시간권(Isochrone) 분석 — 핵심역 기준 30/60분 도달가능 폴리곤 산출.

입력: subway_network/network/{nodes,links}.tsv
출력: preprocessing/outputs/isochrone_{region}_30_60.geojson
      각 polygon feature 에 region, minutes(30|60) 속성

방법:
  1. nodes/links.tsv 로드, T(분석 기준시점)로 begin/effective_begin cutoff 적용
  2. scipy.sparse.csgraph.dijkstra 로 핵심역(CORE_STATIONS) 기준 전역 최단시간 계산
  3. 도달 노드에 보행 버퍼(WALK_BUFFER_M) 적용 후 union → 폴리곤화
  4. 30분 / 60분 cutoff 로 두 폴리곤 생성
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from shapely.ops import unary_union

NETWORK_DIR = "../subway_network/network"
# 분석 기준시점: subway_network 데이터셋의 cutoff("현재")와 동일하게 맞춤 (opening.tsv 참고).
# 7호선 청라연장(2029~2033 예정)은 이 시점에 미개통이라 데이터셋에도 없음 → 자동 제외됨.
T = "2026-05-04"
WALK_BUFFER_M = 500
CUTOFFS_SEC = {30: 30 * 60, 60: 60 * 60}

# Phase 0 확정 (2026-06-24):
#   판교: 신분당선/경강선 판교역 (둘 다 같은 광장 앞 환승역, 신분당선을 핵심역으로 채택 —
#         2011 최초 개통, 강남 직결로 판교테크노밸리 입지 가치를 만든 노선)
#   청라: 공항철도 청라국제도시역 (2014-06-21 개통, 현재 유일하게 운영 중인 역.
#         7호선 청라연장은 2029년 이후 예정으로 본 분석 시점에는 미개통)
CORE_STATIONS = {
    "pangyo": {"statnm": "판교", "linenm": "신분당선"},
    "cheongna": {"statnm": "청라국제도시", "linenm": "공항철도"},
}


def load_active_network(t: str):
    nodes = pd.read_csv(f"{NETWORK_DIR}/nodes.tsv", sep="\t", encoding="utf-8")
    links = pd.read_csv(f"{NETWORK_DIR}/links.tsv", sep="\t", encoding="utf-8")
    nodes_eff = nodes["effective_begin"].where(nodes["effective_begin"].fillna("") != "", nodes["begin"])
    active_nodes = nodes[nodes_eff <= t].copy()
    active_ids = set(active_nodes["id"])
    active_links = links[
        (links["begin"] <= t)
        & links["fromNode"].isin(active_ids)
        & links["toNode"].isin(active_ids)
    ].copy()
    return active_nodes.reset_index(drop=True), active_links.reset_index(drop=True)


def build_csr(nodes: pd.DataFrame, links: pd.DataFrame) -> tuple[csr_matrix, dict]:
    """links 의 fromNode/toNode 는 nodes.id (전역, 비연속) 를 참조하므로
    active_nodes 의 행 순서(0..n-1)로 재매핑한 뒤 CSR 을 만든다."""
    id_map = {old: new for new, old in enumerate(nodes["id"])}
    n = len(nodes)
    u = links["fromNode"].map(id_map).to_numpy()
    v = links["toNode"].map(id_map).to_numpy()
    src = np.concatenate([u, v])
    dst = np.concatenate([v, u])
    cost = np.concatenate([links["timeFT"].to_numpy(), links["timeTF"].to_numpy()]).astype(np.float64)
    return csr_matrix((cost, (src, dst)), shape=(n, n)), id_map


def isochrone_for_region(region: str, nodes: pd.DataFrame, A: csr_matrix, id_map: dict) -> dict:
    cfg = CORE_STATIONS[region]
    row = nodes[(nodes["statnm"] == cfg["statnm"]) & (nodes["linenm"] == cfg["linenm"])]
    if len(row) == 0:
        raise ValueError(f"핵심역을 찾을 수 없음: {region} {cfg}")
    src_idx = id_map[row.iloc[0]["id"]]

    dist_sec = dijkstra(A, indices=src_idx)
    nodes = nodes.copy()
    nodes["dist_sec"] = dist_sec

    polygons = {}
    reach_counts = {}
    for minutes, cutoff_sec in CUTOFFS_SEC.items():
        reach = nodes[(nodes["dist_sec"] >= 0) & (nodes["dist_sec"] < cutoff_sec)]
        reach_counts[minutes] = len(reach)
        pts = gpd.GeoSeries(
            gpd.points_from_xy(reach["x_5179"], reach["y_5179"]), crs="EPSG:5179"
        )
        buffered = pts.buffer(WALK_BUFFER_M)
        polygons[minutes] = unary_union(buffered.to_list())

    gdf = gpd.GeoDataFrame(
        {"region": [region] * len(polygons), "minutes": list(polygons.keys())},
        geometry=list(polygons.values()),
        crs="EPSG:5179",
    ).to_crs(epsg=4326)
    gdf.to_file(f"outputs/isochrone_{region}_30_60.geojson", driver="GeoJSON")

    print(f"[{region}] 핵심역={cfg['statnm']}({cfg['linenm']}) 도달역수: {reach_counts}")
    return reach_counts


def main():
    nodes, links = load_active_network(T)
    print(f"활성 노드 {len(nodes)}/{len(nodes)}, 활성 링크 {len(links)} (cutoff={T})")
    A, id_map = build_csr(nodes, links)

    summary = {}
    for region in CORE_STATIONS:
        summary[region] = isochrone_for_region(region, nodes, A, id_map)

    import json

    with open("outputs/isochrone_reach_counts.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
