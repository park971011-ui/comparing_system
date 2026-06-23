type Region = "pangyo" | "cheongna";
type ViewMode = "toggle" | "side-by-side";

interface RegionToggleProps {
  region: Region;
  viewMode: ViewMode;
  onRegionChange: (region: Region) => void;
  onViewModeChange: (mode: ViewMode) => void;
}

export default function RegionToggle({
  region,
  viewMode,
  onRegionChange,
  onViewModeChange,
}: RegionToggleProps) {
  return (
    <div className="region-toggle">
      <button disabled={viewMode === "side-by-side"} onClick={() => onRegionChange("pangyo")} aria-pressed={region === "pangyo"}>
        판교테크노밸리
      </button>
      <button disabled={viewMode === "side-by-side"} onClick={() => onRegionChange("cheongna")} aria-pressed={region === "cheongna"}>
        청라국제업무지구
      </button>
      <label>
        <input
          type="checkbox"
          checked={viewMode === "side-by-side"}
          onChange={(e) => onViewModeChange(e.target.checked ? "side-by-side" : "toggle")}
        />
        나란히 보기
      </label>
    </div>
  );
}
