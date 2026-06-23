import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface StatsPanelProps {
  // TODO: stats_summary.json 타입 정의 후 교체
  pangyo: Record<string, unknown>;
  cheongna: Record<string, unknown>;
  accessibilityCurve: { minute: number; pangyo: number; cheongna: number }[];
}

export default function StatsPanel({ accessibilityCurve }: StatsPanelProps) {
  return (
    <div className="stats-panel">
      <h3>누적 접근성 곡선 (도달 종사자수)</h3>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={accessibilityCurve}>
          <XAxis dataKey="minute" label={{ value: "분", position: "insideBottom" }} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="pangyo" name="판교" stroke="#2563eb" />
          <Line type="monotone" dataKey="cheongna" name="청라" stroke="#dc2626" />
        </LineChart>
      </ResponsiveContainer>

      <h3>토지이용 / 인구사회 비교</h3>
      {/* TODO: stats_summary.json 로드 후 BarChart로 용도지역 구성비, 종사자수 등 비교 */}
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={[]}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="pangyo" name="판교" fill="#2563eb" />
          <Bar dataKey="cheongna" name="청라" fill="#dc2626" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
