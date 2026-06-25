// 건축물 주용도별 색상 — MapView(지도 컬러맵)와 MapLegend(범례)가 동일 매핑을 공유.
export const USAGE_COLORS: [string, string][] = [
  ["업무시설", "#2563eb"],
  ["공동주택", "#f59e0b"],
  ["교육연구시설", "#10b981"],
  ["판매시설", "#a855f7"],
  ["숙박시설", "#ec4899"],
  ["제1종근린생활시설", "#fbbf24"],
  ["제2종근린생활시설", "#fcd34d"],
  ["자동차관련시설", "#64748b"],
  ["창고시설", "#78716c"],
  ["운동시설", "#06b6d4"],
  ["운수시설", "#0ea5e9"],
  ["종교시설", "#f43f5e"],
];

export const USAGE_OTHER_COLOR = "#d1d5db"; // 기타/미분류(공지 포함)

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const USAGE_COLOR_MATCH: any[] = [
  "match",
  ["get", "mainPurpsCdNm"],
  ...USAGE_COLORS.flat(),
  USAGE_OTHER_COLOR,
];
