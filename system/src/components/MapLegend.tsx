import { USAGE_COLORS, USAGE_OTHER_COLOR } from "../usageColors";

export default function MapLegend() {
  return (
    <div className="map-legend">
      <div className="map-legend-title">건축물 주용도</div>
      {USAGE_COLORS.map(([name, color]) => (
        <div className="map-legend-row" key={name}>
          <span className="map-legend-swatch" style={{ backgroundColor: color }} />
          <span>{name}</span>
        </div>
      ))}
      <div className="map-legend-row">
        <span className="map-legend-swatch" style={{ backgroundColor: USAGE_OTHER_COLOR }} />
        <span>기타/미건축(공지)</span>
      </div>
    </div>
  );
}
