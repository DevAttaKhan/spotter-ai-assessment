import type { Feature, FeatureCollection, LineString, Point } from "geojson";
import { LEVEL_COLOR, LEVEL_LABEL, ROUTE_COLOR } from "@/domain/risk";
import type { Checkpoint, Corridor, RouteOption } from "@/domain/types";

type RouteProperties = {
  id: string;
  selected: boolean;
  color: string;
};

type CheckpointProperties = {
  routeId: string;
  selected: boolean;
  level: string;
  color: string;
  title: string;
  eta: string;
  mile: number;
  wind: number | "";
  rain: number | "";
  snow: number | "";
  factors: string;
};

export const routesToGeoJSON = (
  routes: RouteOption[] | undefined,
  selectedId: string | null,
): FeatureCollection<LineString, RouteProperties> => ({
  type: "FeatureCollection",
  features: (routes ?? []).map(
    (route): Feature<LineString, RouteProperties> => ({
      type: "Feature",
      properties: {
        id: route.id,
        selected: route.id === selectedId,
        color: ROUTE_COLOR[route.id] || "#44403c",
      },
      geometry: {
        type: "LineString",
        coordinates: route.geometry,
      },
    }),
  ),
});

export const checkpointsToGeoJSON = (
  routes: RouteOption[] | undefined,
  selectedId: string | null,
): FeatureCollection<Point, CheckpointProperties> => ({
  type: "FeatureCollection",
  features: (routes ?? []).flatMap((route) =>
    route.checkpoints.map(
      (checkpoint): Feature<Point, CheckpointProperties> => ({
        type: "Feature",
        properties: checkpointProperties(route.id, route.id === selectedId, checkpoint),
        geometry: {
          type: "Point",
          coordinates: [checkpoint.lon, checkpoint.lat],
        },
      }),
    ),
  ),
});

const checkpointProperties = (
  routeId: string,
  selected: boolean,
  checkpoint: Checkpoint,
): CheckpointProperties => ({
  routeId,
  selected,
  level: checkpoint.level,
  color: LEVEL_COLOR[checkpoint.level] || LEVEL_COLOR.unknown,
  title: LEVEL_LABEL[checkpoint.level] || "Unknown",
  eta: checkpoint.eta,
  mile: checkpoint.mile,
  wind: checkpoint.wind_mph ?? "",
  rain: checkpoint.rain_in_hr ?? "",
  snow: checkpoint.snow_in_hr ?? "",
  factors: (checkpoint.factors || []).join(", "),
});

export const corridorToGeoJSON = (
  corridor: Corridor | undefined,
  hourIndex: number,
  showHeat: boolean,
): FeatureCollection<Point, { score: number }> => {
  if (!showHeat || !corridor) {
    return { type: "FeatureCollection", features: [] };
  }
  const features: Feature<Point, { score: number }>[] = [];
  for (const point of corridor.points) {
    const score = point.scores[hourIndex];
    if (!score) {
      continue;
    }
    features.push({
      type: "Feature",
      properties: { score },
      geometry: {
        type: "Point",
        coordinates: [point.lon, point.lat],
      },
    });
  }
  return { type: "FeatureCollection", features };
};
