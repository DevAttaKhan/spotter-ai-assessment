import type { TripPlan, TripRequest } from "@/domain/types";

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

export const planTrip = async (payload: TripRequest): Promise<TripPlan> => {
  const response = await fetch("/api/plan/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body: unknown = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = isRecord(body) && typeof body.error === "string" ? body.error : "The plan could not be built.";
    throw new Error(message);
  }
  if (!isRecord(body) || !Array.isArray(body.routes)) {
    throw new Error("The plan response was not usable.");
  }
  return body as TripPlan;
};

export const fetchMapKey = async (): Promise<string> => {
  const response = await fetch("/api/config/");
  if (!response.ok) {
    return "";
  }
  const body: unknown = await response.json();
  if (!isRecord(body) || typeof body.map_key !== "string") {
    return "";
  }
  return body.map_key;
};
