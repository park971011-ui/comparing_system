import { useEffect, useRef } from "react";
import maplibregl, { Map as MapLibreMap } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

type Region = "pangyo" | "cheongna";

interface MapViewProps {
  region: Region;
  isochroneMinutes: 30 | 60;
}

const REGION_CENTER: Record<Region, [number, number]> = {
  pangyo: [127.1086, 37.4019],
  cheongna: [126.6286, 37.5326],
};

export default function MapView({ region, isochroneMinutes }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;
    mapRef.current = new maplibregl.Map({
      container: mapContainer.current,
      style: "https://demotiles.maplibre.org/style.json",
      center: REGION_CENTER[region],
      zoom: 13,
    });
    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    mapRef.current?.flyTo({ center: REGION_CENTER[region] });
    // TODO: 등시간권(isochroneMinutes)·건축물 컬러맵 layer 갱신, 클릭 popup 바인딩
  }, [region, isochroneMinutes]);

  return <div ref={mapContainer} style={{ width: "100%", height: "100%" }} />;
}
