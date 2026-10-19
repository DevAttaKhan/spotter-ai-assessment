import type { RiskLevel, RouteId } from "./types";

export const LEVEL_LABEL = {
  low: "Low",
  moderate: "Moderate",
  high: "High",
  severe: "Severe",
  no_travel: "No travel",
  unknown: "No forecast",
} as const satisfies Record<RiskLevel, string>;

export const LEVEL_COLOR = {
  low: "#3f7d4e",
  moderate: "#b8860b",
  high: "#d86b12",
  severe: "#c2332b",
  no_travel: "#1c1917",
  unknown: "#a8a29e",
} as const satisfies Record<RiskLevel, string>;

export const ROUTE_COLOR = {
  "route-a": "#1d4e89",
  "route-b": "#0f766e",
  "route-c": "#9a3412",
} as const satisfies Record<RouteId, string>;

export const ROUTE_NAMES = {
  "route-a": "Route A",
  "route-b": "Route B",
  "route-c": "Route C",
} as const satisfies Record<RouteId, string>;
