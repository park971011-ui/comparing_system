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
T = "2026-05-04"  # TODO(Phase 0): 분석 기준시점 확정
WALK_BUFFER_M = 500
CUTOFFS_SEC = {30: 30 * 60, 60: 60 * 60}

CORE_STATIONS = {
    "pangyo": {"statnm": "판교", "linenm": None},  # TODO: linenm 확정 (신분당선/경강선)
    "cheongna": {"statnm": None, "linenm": None},  # TODO(Phase 0): 청라국제도시역 개통여부 확인 후 확정
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


def build_csr(nodes: pd.DataFrame, links: pd.DataFrame) -> csr_matrix:
    n = len(nodes)
    u = links["fromNode"].to_numpy()
    v = links["toNode"].to_numpy()
    src = np.concatenate([u, v])
    dst = np.concatenate([v, u])
    cost = np.concatenate([links["timeFT"].to_numpy(), links["timeTF"].to_numpy()]).astype(np.float64)
    return csr_matrix((cost, (src, dst)), shape=(n, n))


def isochrone_for_region(region: str):
    raise NotImplementedError("CORE_STATIONS 확정(Phase 0) 후 구현")


def main():
    for region in CORE_STATIONS:
        isochrone_for_region(region)


if __name__ == "__main__":
    main()
