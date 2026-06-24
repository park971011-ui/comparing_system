import { useEffect, useRef } from "react";
import maplibregl, { Map as MapLibreMap } from "maplibre-gl";
import type { FeatureCollection } from "geojson";
import "maplibre-gl/dist/maplibre-gl.css";

type Region = "pangyo" | "cheongna";

interface MapViewProps {
  region: Region;
  isochroneMinutes: 30 | 60;
  isochroneData: FeatureCollection;
  boundaryData: FeatureCollection;
  parcelData: FeatureCollection;
}

// 핵심역 실측 좌표 (subway_network/network/nodes.tsv 확인, PLAN.md §1-1)
const REGION_CENTER: Record<Region, [number, number]> = {
  pangyo: [127.11116, 37.39457],
  cheongna: [126.62465, 37.55649],
};

const ISO_SOURCE_ID = "isochrone";
const ISO_FILL_LAYER_ID = "isochrone-fill";
const ISO_LINE_LAYER_ID = "isochrone-line";
const BOUNDARY_SOURCE_ID = "boundary";
const BOUNDARY_LINE_LAYER_ID = "boundary-line";
const PARCEL_SOURCE_ID = "parcels";
const PARCEL_FILL_LAYER_ID = "parcels-fill";
const PARCEL_LINE_LAYER_ID = "parcels-line";

// 건축물 주용도별 색상 — 범례는 StatsPanel/legend 컴포넌트에서 동일 매핑 사용
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const USAGE_COLOR_MATCH: any[] = [
  "match",
  ["get", "mainPurpsCdNm"],
  "업무시설", "#2563eb",
  "공동주택", "#f59e0b",
  "교육연구시설", "#10b981",
  "판매시설", "#a855f7",
  "숙박시설", "#ec4899",
  "제1종근린생활시설", "#fbbf24",
  "제2종근린생활시설", "#fcd34d",
  "자동차관련시설", "#64748b",
  "창고시설", "#78716c",
  "운동시설", "#06b6d4",
  "운수시설", "#0ea5e9",
  "종교시설", "#f43f5e",
  /* 기타/미분류(공지 포함) */ "#d1d5db",
];

export default function MapView({ region, isochroneMinutes, isochroneData, boundaryData, parcelData }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const popupRef = useRef<maplibregl.Popup | null>(null);

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
      map.addSource(PARCEL_SOURCE_ID, { type: "geojson", data: parcelData });
      map.addLayer({
        id: PARCEL_FILL_LAYER_ID,
        type: "fill",
        source: PARCEL_SOURCE_ID,
        paint: { "fill-color": USAGE_COLOR_MATCH as never, "fill-opacity": 0.75 },
      });
      map.addLayer({
        id: PARCEL_LINE_LAYER_ID,
        type: "line",
        source: PARCEL_SOURCE_ID,
        paint: { "line-color": "#374151", "line-width": 0.5 },
      });

      map.addSource(ISO_SOURCE_ID, { type: "geojson", data: isochroneData });
      map.addLayer({
        id: ISO_FILL_LAYER_ID,
        type: "fill",
        source: ISO_SOURCE_ID,
        filter: ["==", ["get", "minutes"], isochroneMinutes],
        paint: { "fill-color": "#2563eb", "fill-opacity": 0.1 },
      });
      map.addLayer({
        id: ISO_LINE_LAYER_ID,
        type: "line",
        source: ISO_SOURCE_ID,
        filter: ["==", ["get", "minutes"], isochroneMinutes],
        paint: { "line-color": "#1d4ed8", "line-width": 1.5 },
      });

      map.addSource(BOUNDARY_SOURCE_ID, { type: "geojson", data: boundaryData });
      map.addLayer({
        id: BOUNDARY_LINE_LAYER_ID,
        type: "line",
        source: BOUNDARY_SOURCE_ID,
        paint: { "line-color": "#dc2626", "line-width": 2.5, "line-dasharray": [2, 1] },
      });

      map.on("click", PARCEL_FILL_LAYER_ID, (e) => {
        const f = e.features?.[0];
        if (!f) return;
        const p = f.properties as Record<string, string | number | null>;
        popupRef.current?.remove();
        popupRef.current = new maplibregl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(
            `<div style="font-size:12px;line-height:1.5">
              <b>지번 ${p.jibun ?? "-"}</b><br/>
              용도지역: ${p.uname ?? "-"}<br/>
              주용도: ${p.mainPurpsCdNm ?? "미건축(공지)"}<br/>
              연면적: ${p.totArea ? Number(p.totArea).toLocaleString() + "㎡" : "-"}<br/>
              대지면적: ${p.platArea ? Number(p.platArea).toLocaleString() + "㎡" : "-"}<br/>
              용적률: ${p.far ?? "-"}<br/>
              층수: ${p.grndFlrCnt ?? "-"}
            </div>`
          )
          .addTo(map);
      });
      map.on("mouseenter", PARCEL_FILL_LAYER_ID, () => { map.getCanvas().style.cursor = "pointer"; });
      map.on("mouseleave", PARCEL_FILL_LAYER_ID, () => { map.getCanvas().style.cursor = ""; });
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
    popupRef.current?.remove();
    (map.getSource(PARCEL_SOURCE_ID) as maplibregl.GeoJSONSource | undefined)?.setData(parcelData);
    (map.getSource(ISO_SOURCE_ID) as maplibregl.GeoJSONSource | undefined)?.setData(isochroneData);
    (map.getSource(BOUNDARY_SOURCE_ID) as maplibregl.GeoJSONSource | undefined)?.setData(boundaryData);
  }, [region, isochroneData, boundaryData, parcelData]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.getLayer(ISO_FILL_LAYER_ID)) return;
    map.setFilter(ISO_FILL_LAYER_ID, ["==", ["get", "minutes"], isochroneMinutes]);
    map.setFilter(ISO_LINE_LAYER_ID, ["==", ["get", "minutes"], isochroneMinutes]);
  }, [isochroneMinutes]);

  return <div ref={mapContainer} style={{ width: "100%", height: "100%" }} />;
}
