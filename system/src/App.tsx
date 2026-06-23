import { useState } from "react";
import MapView from "./components/MapView";
import IsochroneLayer from "./components/IsochroneLayer";
import StatsPanel from "./components/StatsPanel";
import RegionToggle from "./components/RegionToggle";
import "./App.css";

type Region = "pangyo" | "cheongna";
type ViewMode = "toggle" | "side-by-side";

function App() {
  const [region, setRegion] = useState<Region>("pangyo");
  const [viewMode, setViewMode] = useState<ViewMode>("toggle");
  const [minutes, setMinutes] = useState<30 | 60>(30);

  return (
    <div className="app-layout">
      <header>
        <h1>판교테크노밸리 vs 청라국제업무지구 비교분석</h1>
        <RegionToggle
          region={region}
          viewMode={viewMode}
          onRegionChange={setRegion}
          onViewModeChange={setViewMode}
        />
      </header>

      <main className="map-area">
        {viewMode === "toggle" ? (
          <MapView region={region} isochroneMinutes={minutes} />
        ) : (
          <div className="side-by-side">
            <MapView region="pangyo" isochroneMinutes={minutes} />
            <MapView region="cheongna" isochroneMinutes={minutes} />
          </div>
        )}
        <IsochroneLayer minutes={minutes} onChange={setMinutes} />
      </main>

      <aside className="stats-area">
        <StatsPanel pangyo={{}} cheongna={{}} accessibilityCurve={[]} />
      </aside>
    </div>
  );
}

export default App;
