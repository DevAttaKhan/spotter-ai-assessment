import { useEffect, useRef, useState } from "react";
import { GeoJSONSource, LngLatBounds, Map, NavigationControl, Popup, setWorkerUrl } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { MapFocus, RouteId, TripPlan } from "@/domain/types";
import { isRouteId } from "@/domain/types";
import { fetchMapKey } from "@/lib/api";
import { formatInches, formatWhen, formatWind } from "@/lib/format";
import { When } from "react-if";
import { checkpointsToGeoJSON, corridorToGeoJSON, routesToGeoJSON } from "./mapData";
import { MapLegend } from "./MapLegend";

setWorkerUrl("/maplibre-gl-worker.mjs");

const emptyCollection: GeoJSON.FeatureCollection = { type: "FeatureCollection", features: [] };

type LayerClickEvent = {
  features?: Array<{
    properties?: GeoJSON.GeoJsonProperties;
    geometry: GeoJSON.Geometry;
  }>;
};

type MapViewProps = {
  plan: TripPlan | null;
  selectedId: RouteId | null;
  hourIndex: number;
  showHeat: boolean;
  focus: MapFocus | null;
  onSelectRoute: (routeId: RouteId) => void;
};

type MapSnapshot = {
  plan: TripPlan | null;
  selectedId: RouteId | null;
  hourIndex: number;
  showHeat: boolean;
};

const setGeoJSON = (map: Map, sourceId: string, data: GeoJSON.GeoJSON) => {
  const source = map.getSource(sourceId);
  if (!(source instanceof GeoJSONSource)) {
    return;
  }
  void source.setData(data);
};

const readMeasure = (value: unknown): number | null => {
  if (value === "" || value === null || value === undefined) {
    return null;
  }
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
};

const addLayers = (map: Map) => {
  map.addSource("corridor", { type: "geojson", data: emptyCollection });
  map.addLayer({
    id: "corridor-heat",
    type: "heatmap",
    source: "corridor",
    paint: {
      "heatmap-weight": ["interpolate", ["linear"], ["get", "score"], 0, 0, 1, 0.2, 5, 1],
      "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 3, 0.55, 8, 1.3],
      "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 3, 14, 6, 32, 10, 46],
      "heatmap-opacity": 0.72,
      "heatmap-color": [
        "interpolate",
        ["linear"],
        ["heatmap-density"],
        0,
        "rgba(0,0,0,0)",
        0.15,
        "rgba(63,125,78,0.55)",
        0.4,
        "rgba(184,134,11,0.7)",
        0.6,
        "rgba(216,107,18,0.8)",
        0.8,
        "rgba(194,51,43,0.88)",
        1,
        "rgba(28,25,23,0.92)",
      ],
    },
  });

  map.addSource("routes", { type: "geojson", data: emptyCollection });
  map.addLayer({
    id: "route-line",
    type: "line",
    source: "routes",
    filter: ["!=", ["get", "selected"], true],
    layout: { "line-cap": "round", "line-join": "round" },
    paint: {
      "line-color": ["get", "color"],
      "line-width": 3,
      "line-opacity": 0.55,
    },
  });
  map.addLayer({
    id: "route-line-selected",
    type: "line",
    source: "routes",
    filter: ["==", ["get", "selected"], true],
    layout: { "line-cap": "round", "line-join": "round" },
    paint: {
      "line-color": ["get", "color"],
      "line-width": 5,
      "line-opacity": 0.95,
    },
  });

  map.addSource("checkpoints", { type: "geojson", data: emptyCollection });
  map.addLayer({
    id: "checkpoint-circle",
    type: "circle",
    source: "checkpoints",
    paint: {
      "circle-color": ["get", "color"],
      "circle-radius": ["case", ["==", ["get", "selected"], true], 6, 3.5],
      "circle-stroke-color": "#ffffff",
      "circle-stroke-width": 1,
    },
  });
};

export const MapView = ({ plan, selectedId, hourIndex, showHeat, focus, onSelectRoute }: MapViewProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<Map | null>(null);
  const popupRef = useRef<Popup | null>(null);
  const fittedRef = useRef<TripPlan | null>(null);
  const onSelectRef = useRef(onSelectRoute);
  const dataRef = useRef<MapSnapshot>({ plan, selectedId, hourIndex, showHeat });
  const [mapNote, setMapNote] = useState("Loading map…");

  onSelectRef.current = onSelectRoute;
  dataRef.current = { plan, selectedId, hourIndex, showHeat };

  const applyRef = useRef<() => void>(() => undefined);
  applyRef.current = () => {
    const map = mapRef.current;
    if (!map?.getSource("routes")) {
      return;
    }
    const current = dataRef.current;
    const routes = current.plan?.routes ?? [];
    setGeoJSON(map, "routes", routesToGeoJSON(routes, current.selectedId));
    setGeoJSON(map, "checkpoints", checkpointsToGeoJSON(routes, current.selectedId));
    setGeoJSON(map, "corridor", corridorToGeoJSON(current.plan?.corridor, current.hourIndex, current.showHeat));

    if (current.plan && fittedRef.current !== current.plan && routes.length) {
      fittedRef.current = current.plan;
      const bounds = new LngLatBounds();
      routes.forEach((route) => {
        route.geometry.forEach(([lon, lat]) => bounds.extend([lon, lat]));
      });
      if (!bounds.isEmpty()) {
        map.fitBounds(bounds, { padding: 48, duration: 500, maxZoom: 9 });
      }
    }
  };

  useEffect(() => {
    let cancelled = false;
    let map: Map | undefined;
    let observer: ResizeObserver | undefined;

    const handleRouteClick = (event: LayerClickEvent) => {
      const routeId = event.features?.[0]?.properties?.id;
      if (isRouteId(routeId)) {
        onSelectRef.current(routeId);
      }
    };

    const handleCheckpointClick = (event: LayerClickEvent) => {
      const feature = event.features?.[0];
      if (!feature || feature.geometry.type !== "Point" || !map) {
        return;
      }
      const props = feature.properties ?? {};
      const timeZone = dataRef.current.plan?.timezone || "UTC";
      const root = document.createElement("div");
      root.className = "text-sm";
      const title = document.createElement("p");
      title.className = "font-medium";
      title.textContent = `${String(props.title ?? "Checkpoint")} · mile ${String(props.mile ?? "")}`;
      const when = document.createElement("p");
      when.textContent = formatWhen(typeof props.eta === "string" ? props.eta : null, timeZone);
      const weather = document.createElement("p");
      weather.textContent = `${formatWind(readMeasure(props.wind))} wind, ${formatInches(readMeasure(props.rain))} rain, ${formatInches(readMeasure(props.snow))} snow`;
      root.append(title, when, weather);
      if (typeof props.factors === "string" && props.factors) {
        const factors = document.createElement("p");
        factors.textContent = `Set by ${props.factors}`;
        root.append(factors);
      }
      const [lon, lat] = feature.geometry.coordinates;
      popupRef.current?.remove();
      popupRef.current = new Popup({ closeButton: true, maxWidth: "240px" })
        .setLngLat([lon, lat])
        .setDOMContent(root)
        .addTo(map);
    };

    const setCursor = (cursor: string) => {
      map?.getCanvas().style.setProperty("cursor", cursor);
    };

    fetchMapKey()
      .then((mapKey) => {
        const container = containerRef.current;
        if (cancelled || !container) {
          return;
        }
        if (!mapKey) {
          setMapNote("The map key is missing. Set STADIA_API_KEY and reload.");
          return;
        }
        map = new Map({
          container,
          style: `https://tiles.stadiamaps.com/styles/alidade_smooth.json?api_key=${mapKey}`,
          center: [-98.5, 39.5],
          zoom: 3.4,
        });
        map.addControl(new NavigationControl(), "top-right");
        observer = new ResizeObserver(() => map?.resize());
        observer.observe(container);
        map.on("load", () => {
          if (!map) {
            return;
          }
          addLayers(map);
          map.on("click", "route-line", handleRouteClick);
          map.on("click", "route-line-selected", handleRouteClick);
          map.on("click", "checkpoint-circle", handleCheckpointClick);
          map.on("mouseenter", "route-line", () => setCursor("pointer"));
          map.on("mouseenter", "route-line-selected", () => setCursor("pointer"));
          map.on("mouseleave", "route-line", () => setCursor(""));
          map.on("mouseleave", "route-line-selected", () => setCursor(""));
          map.on("mouseenter", "checkpoint-circle", () => setCursor("pointer"));
          map.on("mouseleave", "checkpoint-circle", () => setCursor(""));
          mapRef.current = map;
          setMapNote("");
          applyRef.current();
        });
        map.on("error", () => {
          if (map && !map.loaded()) {
            setMapNote("The basemap did not load. Check the Stadia key and allowed domains.");
          }
        });
      })
      .catch(() => {
        if (!cancelled) {
          setMapNote("Could not reach the server for the map key.");
        }
      });

    return () => {
      cancelled = true;
      observer?.disconnect();
      popupRef.current?.remove();
      map?.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    applyRef.current();
  }, [plan, selectedId, hourIndex, showHeat]);

  useEffect(() => {
    if (!focus || !mapRef.current) {
      return;
    }
    mapRef.current.easeTo({
      center: [focus.lon, focus.lat],
      zoom: Math.max(mapRef.current.getZoom(), 7),
      duration: 450,
    });
  }, [focus]);

  return (
    <div className="relative flex min-h-0 flex-1 flex-col">
      <div ref={containerRef} className="min-h-0 w-full flex-1" role="region" aria-label="Route map" />
      <When condition={mapNote}>
        <p className="pointer-events-none absolute top-4 left-4 max-w-xs rounded-xl border border-line bg-surface/95 px-3.5 py-2.5 text-sm shadow-lg backdrop-blur-sm">
          {mapNote}
        </p>
      </When>
      <MapLegend />
    </div>
  );
};
