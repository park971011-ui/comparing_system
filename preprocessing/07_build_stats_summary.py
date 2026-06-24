"""
모든 전처리 산출물을 stats_summary.json 하나로 통합 — 보고서·시스템 수치의 단일 소스(PLAN.md 원칙).
"""
import json

OUT_DIR = "outputs"


def load(name):
    with open(f"{OUT_DIR}/{name}", encoding="utf-8") as f:
        return json.load(f)


def main():
    reach_counts = load("isochrone_reach_counts.json")
    summary = {}
    for region in ("pangyo", "cheongna"):
        landuse = load(f"landuse_{region}.json")
        summary[region] = {
            "landuse": landuse,
            "transport": {"isochrone_reachable_stations": reach_counts[region]},
            "socio_demo": "pending (Phase 1 SGIS 집계구 수집 대기)",
        }
    with open(f"{OUT_DIR}/stats_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"저장됨: {OUT_DIR}/stats_summary.json")


if __name__ == "__main__":
    main()
