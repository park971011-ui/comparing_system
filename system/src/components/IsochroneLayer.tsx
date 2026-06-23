interface IsochroneLayerProps {
  minutes: 30 | 60;
  onChange: (minutes: 30 | 60) => void;
  reachablePopulation?: number;
  reachableWorkers?: number;
}

export default function IsochroneLayer({
  minutes,
  onChange,
  reachablePopulation,
  reachableWorkers,
}: IsochroneLayerProps) {
  return (
    <div className="isochrone-control">
      <label>
        등시간권:
        <input
          type="range"
          min={30}
          max={60}
          step={30}
          value={minutes}
          onChange={(e) => onChange(Number(e.target.value) as 30 | 60)}
        />
        {minutes}분
      </label>
      <div className="isochrone-stats">
        <span>도달 인구: {reachablePopulation?.toLocaleString() ?? "-"}</span>
        <span>도달 종사자: {reachableWorkers?.toLocaleString() ?? "-"}</span>
      </div>
    </div>
  );
}
