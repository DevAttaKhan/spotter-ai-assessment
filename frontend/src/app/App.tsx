import { useState } from "react";
import { When } from "react-if";
import type { Checkpoint, MapFocus, RouteId, TripPlan, TripRequest } from "@/domain/types";
import { HeatmapSlider } from "@/features/map/HeatmapSlider";
import { MapView } from "@/features/map/MapView";
import { CheckpointList } from "@/features/routes/CheckpointList";
import { RouteList } from "@/features/routes/RouteList";
import { AppHeader } from "@/features/shell/AppHeader";
import { StatusCallout } from "@/features/shell/StatusCallout";
import { TripForm } from "@/features/trip/TripForm";
import { planTrip } from "@/lib/api";

export const App = () => {
  const [plan, setPlan] = useState<TripPlan | null>(null);
  const [selectedId, setSelectedId] = useState<RouteId | null>(null);
  const [hourIndex, setHourIndex] = useState(0);
  const [showHeat, setShowHeat] = useState(true);
  const [focus, setFocus] = useState<MapFocus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (form: TripRequest) => {
    setLoading(true);
    setError("");
    try {
      const next = await planTrip(form);
      setPlan(next);
      setSelectedId(next.recommended_route_id || next.routes[0]?.id || null);
      setHourIndex(0);
      setFocus(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "The plan could not be built.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectRoute = (routeId: RouteId) => {
    setSelectedId(routeId);
  };

  const handleFocusCheckpoint = (checkpoint: Checkpoint) => {
    setFocus({
      lon: checkpoint.lon,
      lat: checkpoint.lat,
      key: `${checkpoint.mile}-${checkpoint.lat}`,
    });
  };

  const selected = plan?.routes.find((route) => route.id === selectedId) ?? null;

  return (
    <div className="flex h-screen flex-col overflow-hidden font-sans text-ink">
      <AppHeader plan={plan} />
      <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
        <aside className="max-h-[38vh] w-full shrink-0 overflow-y-auto border-b border-line bg-surface lg:max-h-none lg:w-[400px] lg:border-r lg:border-b-0">
          <TripForm loading={loading} onSubmit={handleSubmit} />
          <When condition={error}>
            <StatusCallout tone="error">{error}</StatusCallout>
          </When>
          <When condition={plan?.note}>
            <StatusCallout tone="note">{plan?.note}</StatusCallout>
          </When>
          <RouteList routes={plan?.routes} selectedId={selectedId} onSelect={handleSelectRoute} />
          <CheckpointList route={selected} timeZone={plan?.timezone} onFocus={handleFocusCheckpoint} />
        </aside>
        <section className="flex min-h-0 min-w-0 flex-1 flex-col p-3 lg:p-4">
          <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-line bg-surface shadow-[0_1px_2px_rgba(20,32,43,0.04),0_12px_32px_rgba(20,32,43,0.06)]">
            <MapView
              plan={plan}
              selectedId={selectedId}
              hourIndex={hourIndex}
              showHeat={showHeat}
              focus={focus}
              onSelectRoute={handleSelectRoute}
            />
            <HeatmapSlider
              hours={plan?.corridor?.hours}
              hourIndex={hourIndex}
              timeZone={plan?.timezone}
              showHeat={showHeat}
              onHourChange={setHourIndex}
              onToggleHeat={setShowHeat}
            />
          </div>
        </section>
      </div>
      <footer className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 border-t border-line bg-surface px-4 py-2 text-[11px] text-muted sm:px-5">
        <span>
          Weather data by{" "}
          <a className="underline decoration-line underline-offset-2 hover:text-ink" href="https://open-meteo.com/" target="_blank" rel="noreferrer">
            Open-Meteo
          </a>
        </span>
        <span>Routes and map tiles by Stadia Maps, © OpenStreetMap contributors.</span>
      </footer>
    </div>
  );
};
