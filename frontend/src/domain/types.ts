export type RiskLevel = "low" | "moderate" | "high" | "severe" | "no_travel" | "unknown";

export type RouteId = "route-a" | "route-b" | "route-c";

export type SampleMiles = 10 | 25 | 50;

export type TripRequest = {
  origin: string;
  destination: string;
  departure: string;
  load_weight_lb: number;
  sample_miles: SampleMiles;
};

export type Checkpoint = {
  lat: number;
  lon: number;
  mile: number;
  stretch_miles: number;
  eta: string;
  wind_mph: number | null;
  rain_in_hr: number | null;
  snow_in_hr: number | null;
  level: RiskLevel;
  factors: string[];
};

export type RouteSummary = {
  low_miles: number;
  moderate_miles: number;
  high_miles: number;
  severe_miles: number;
  no_travel_miles: number;
  average_risk: number | null;
};

export type RouteOption = {
  id: RouteId;
  name: string;
  rank: number;
  recommended: boolean;
  distance_miles: number;
  duration_seconds: number;
  has_toll: boolean;
  has_highway: boolean;
  geometry: [number, number][];
  checkpoints: Checkpoint[];
  summary: RouteSummary;
};

export type CorridorPoint = {
  lat: number;
  lon: number;
  scores: Array<number | null>;
};

export type Corridor = {
  hours: string[];
  points: CorridorPoint[];
};

export type Place = {
  label: string;
  lat: number;
  lon: number;
  timezone?: string;
};

export type TripPlan = {
  origin: Place;
  destination: Place;
  departure: string;
  timezone: string;
  load_weight_lb: number;
  sample_miles: SampleMiles;
  recommended_route_id: RouteId | null;
  routes: RouteOption[];
  corridor: Corridor;
  note: string | null;
};

export type MapFocus = {
  lon: number;
  lat: number;
  key: string;
};

export const isRouteId = (value: unknown): value is RouteId =>
  value === "route-a" || value === "route-b" || value === "route-c";
