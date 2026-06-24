import { useEffect, useState } from "react";
import type { FeatureCollection } from "geojson";
import MapView from "./components/MapView";
import IsochroneLayer from "./components/IsochroneLayer";
import StatsPanel from "./components/StatsPanel";
import RegionToggle from "./components/RegionToggle";
import "./App.css";

type Region = "pangyo" | "cheongna";
type ViewMode = "toggle" | "side-by-side";
type ReachCounts = Record<Region, Record<"30" | "60", number>>;

const EMPTY_FC: FeatureCollection = { type: "FeatureCollection", features: [] };

function App() {
  const [region, setRegion] = useState<Region>("pangyo");
  const [viewMode, setViewMode] = useState<ViewMode>("toggle");
  const [minutes, setMinutes] = useState<30 | 60>(30);
  const [isochroneData, setIsochroneData] = useState<Record<Region, FeatureCollection>>({
    pangyo: EMPTY_FC,
    cheongna: EMPTY_FC,
  });
  const [reachCounts, setReachCounts] = useState<ReachCounts | null>(null);

  useEffect(() => {
    const base = import.meta.env.BASE_URL;
    Promise.all([
      fetch(`${base}data/isochrone_pangyo_30_60.geojson`).then((r) => r.json()),
      fetch(`${base}data/isochrone_cheongna_30_60.geojson`).then((r) => r.json()),
      fetch(`${base}data/isochrone_reach_counts.json`).then((r) => r.json()),
    ]).then(([pangyo, cheongna, counts]) => {
      setIsochroneData({ pangyo, cheongna });
      setReachCounts(counts);
    });
  }, []);

  const reachableStations = reachCounts?.[region]?.[String(minutes) as "30" | "60"];

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
          <MapView region={region} isochroneMinutes={minutes} isochroneData={isochroneData[region]} />
        ) : (
          <div className="side-by-side">
            <MapView region="pangyo" isochroneMinutes={minutes} isochroneData={isochroneData.pangyo} />
            <MapView region="cheongna" isochroneMinutes={minutes} isochroneData={isochroneData.cheongna} />
          </div>
        )}
        <IsochroneLayer minutes={minutes} onChange={setMinutes} reachableStations={reachableStations} />
      </main>

      <aside className="stats-area">
        <StatsPanel pangyo={{}} cheongna={{}} accessibilityCurve={[]} />
      </aside>
    </div>
  );
}

export default App;
