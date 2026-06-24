import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface RegionLanduse {
  parcel_count: number;
  building_record_count: number;
  vacant_lot_ratio: number | null;
  usage_ratio: Record<string, number>;
  lum_entropy: number;
  avg_far: number | null;
}

interface RegionSocioDemo {
  population: number;
  households: number;
  workers: number;
  firms: number;
  job_housing_ratio: number | null;
  stats_year: string;
}

interface RegionStats {
  landuse: RegionLanduse;
  transport: { isochrone_reachable_stations: Record<"30" | "60", number> };
  socio_demo: RegionSocioDemo;
}

interface AccessibilityPoint {
  population: number;
  workers: number;
  station_count: number;
}

interface StatsPanelProps {
  pangyo?: RegionStats;
  cheongna?: RegionStats;
  accessibilityCurve?: Record<string, { pangyo: AccessibilityPoint; cheongna: AccessibilityPoint }>;
}

const USAGE_LABELS = ["업무시설", "공동주택", "교육연구시설", "판매시설", "숙박시설"];

export default function StatsPanel({ pangyo, cheongna, accessibilityCurve }: StatsPanelProps) {
  if (!pangyo || !cheongna) {
    return <div className="stats-panel">데이터 로딩 중...</div>;
  }

  const curveData = accessibilityCurve
    ? Object.entries(accessibilityCurve)
        .map(([minute, v]) => ({
          minute: Number(minute),
          판교: v.pangyo.workers,
          청라: v.cheongna.workers,
        }))
        .sort((a, b) => a.minute - b.minute)
    : [];

  const usageChartData = USAGE_LABELS.map((name) => ({
    name,
    판교: Math.round((pangyo.landuse.usage_ratio[name] ?? 0) * 1000) / 10,
    청라: Math.round((cheongna.landuse.usage_ratio[name] ?? 0) * 1000) / 10,
  }));

  const metricsRows: [string, string | number, string | number][] = [
    ["30분 도달역수", pangyo.transport.isochrone_reachable_stations["30"], cheongna.transport.isochrone_reachable_stations["30"]],
    ["60분 도달역수", pangyo.transport.isochrone_reachable_stations["60"], cheongna.transport.isochrone_reachable_stations["60"]],
    ["평균 용적률(FAR)", pangyo.landuse.avg_far ?? "-", cheongna.landuse.avg_far ?? "-"],
    ["공지(미건축) 비율", pangyo.landuse.vacant_lot_ratio ?? "-", cheongna.landuse.vacant_lot_ratio ?? "-"],
    ["토지이용 혼합도(LUM)", pangyo.landuse.lum_entropy, cheongna.landuse.lum_entropy],
    ["매칭 건축물 레코드 수", pangyo.landuse.building_record_count, cheongna.landuse.building_record_count],
    ["인구(구역 내, 면적가중)", Math.round(pangyo.socio_demo.population), Math.round(cheongna.socio_demo.population)],
    ["종사자수(구역 내, 면적가중)", Math.round(pangyo.socio_demo.workers), Math.round(cheongna.socio_demo.workers)],
    ["사업체수", Math.round(pangyo.socio_demo.firms), Math.round(cheongna.socio_demo.firms)],
    ["직주비(종사자/인구)", pangyo.socio_demo.job_housing_ratio ?? "-", cheongna.socio_demo.job_housing_ratio ?? "-"],
  ];

  return (
    <div className="stats-panel">
      <h3>누적 접근성 곡선 — 도달 종사자수 (시군구 단위 면적가중)</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={curveData}>
          <XAxis dataKey="minute" label={{ value: "분", position: "insideBottom" }} tick={{ fontSize: 10 }} />
          <YAxis tick={{ fontSize: 10 }} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="판교" stroke="#2563eb" dot={false} />
          <Line type="monotone" dataKey="청라" stroke="#dc2626" dot={false} />
        </LineChart>
      </ResponsiveContainer>

      <h3>토지이용 비교 — 건축물 주용도 구성비 (%)</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={usageChartData}>
          <XAxis dataKey="name" tick={{ fontSize: 10 }} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="판교" fill="#2563eb" />
          <Bar dataKey="청라" fill="#dc2626" />
        </BarChart>
      </ResponsiveContainer>

      <h3>핵심 지표 비교</h3>
      <table className="metrics-table">
        <thead>
          <tr>
            <th>지표</th>
            <th>판교</th>
            <th>청라</th>
          </tr>
        </thead>
        <tbody>
          {metricsRows.map(([label, p, c]) => (
            <tr key={label}>
              <td>{label}</td>
              <td>{p}</td>
              <td>{c}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="stats-note">
        ※ 경계는 공식 면적 기준 근사 폴리곤(PLAN.md §1-2). 인구·종사자는 SGIS 집계구
        ({pangyo.socio_demo.stats_year}년)를 면적가중 비례배분(areal interpolation)해 산출.
      </p>
    </div>
  );
}
