import { useEffect, useRef } from "react";
import maplibregl, { Map as MapLibreMap } from "maplibre-gl";
import type { FeatureCollection } from "geojson";
import "maplibre-gl/dist/maplibre-gl.css";

type Region = "pangyo" | "cheongna";

interface MapViewProps {
  region: Region;
  isochroneMinutes: 30 | 60;
  isochroneData: FeatureCollection;
}

const REGION_CENTER: Record<Region, [number, number]> = {
  pangyo: [127.1086, 37.4019],
  cheongna: [126.6286, 37.5326],
};

const ISO_SOURCE_ID = "isochrone";
const ISO_FILL_LAYER_ID = "isochrone-fill";
const ISO_LINE_LAYER_ID = "isochrone-line";

export default function MapView({ region, isochroneMinutes, isochroneData }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: "https://demotiles.maplibre.org/style.json",
      center: REGION_CENTER[region],
      zoom: 12,
    });
    mapRef.current = map;

    map.on("load", () => {
      map.addSource(ISO_SOURCE_ID, { type: "geojson", data: isochroneData });
      map.addLayer({
        id: ISO_FILL_LAYER_ID,
        type: "fill",
        source: ISO_SOURCE_ID,
        filter: ["==", ["get", "minutes"], isochroneMinutes],
        paint: { "fill-color": "#2563eb", "fill-opacity": 0.18 },
      });
      map.addLayer({
        id: ISO_LINE_LAYER_ID,
        type: "line",
        source: ISO_SOURCE_ID,
        filter: ["==", ["get", "minutes"], isochroneMinutes],
        paint: { "line-color": "#1d4ed8", "line-width": 1.5 },
      });
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    map.flyTo({ center: REGION_CENTER[region], zoom: 12 });
    const source = map.getSource(ISO_SOURCE_ID) as maplibregl.GeoJSONSource | undefined;
    source?.setData(isochroneData);
    // TODO: 토지이용/건축물 컬러맵 layer 추가, 클릭 popup 바인딩 (Phase 1 데이터 수신 후)
  }, [region, isochroneData]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.getLayer(ISO_FILL_LAYER_ID)) return;
    map.setFilter(ISO_FILL_LAYER_ID, ["==", ["get", "minutes"], isochroneMinutes]);
    map.setFilter(ISO_LINE_LAYER_ID, ["==", ["get", "minutes"], isochroneMinutes]);
  }, [isochroneMinutes]);

  return <div ref={mapContainer} style={{ width: "100%", height: "100%" }} />;
}
