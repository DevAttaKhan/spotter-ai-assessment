import { ROUTE_COLOR } from "@/domain/risk";
import type { RouteId, RouteOption } from "@/domain/types";
import { formatDrive, formatMiles } from "@/lib/format";
import { When } from "react-if";
import { RouteMetrics } from "./RouteMetrics";

type RouteCardProps = {
  route: RouteOption;
  selected: boolean;
  onSelect: (routeId: RouteId) => void;
};

export const RouteCard = ({ route, selected, onSelect }: RouteCardProps) => {
  const handleSelect = () => onSelect(route.id);
  const cardClass = selected
    ? "border-accent bg-surface shadow-sm ring-4 ring-accent/10"
    : "border-line bg-surface hover:border-ink/15";

  return (
    <button
      type="button"
      className={`relative w-full overflow-hidden rounded-xl border px-3.5 py-3 pl-4 text-left transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${cardClass}`}
      aria-pressed={selected}
      onClick={handleSelect}
    >
      <span className="absolute inset-y-0 left-0 w-1" style={{ backgroundColor: ROUTE_COLOR[route.id] }} aria-hidden="true" />
      <div className="flex items-start justify-between gap-2">
        <span className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: ROUTE_COLOR[route.id] }} aria-hidden="true" />
          <span className="font-semibold">{route.name}</span>
        </span>
        <When condition={route.recommended}>
          <span className="rounded-full bg-signal-soft px-2 py-0.5 text-[10px] font-semibold tracking-wide text-signal uppercase">
            Recommended
          </span>
        </When>
      </div>
      <p className="mt-1.5 text-sm tabular-nums text-muted">
        {formatMiles(route.distance_miles)} · {formatDrive(route.duration_seconds)}
      </p>
      <RouteMetrics summary={route.summary} />
      <When condition={route.has_toll || route.has_highway}>
        <p className="mt-2 flex flex-wrap gap-1.5 text-[11px] text-muted">
          <When condition={route.has_highway}>
            <span className="rounded-full bg-canvas px-2 py-0.5">Highways</span>
          </When>
          <When condition={route.has_toll}>
            <span className="rounded-full bg-canvas px-2 py-0.5">Tolls</span>
          </When>
        </p>
      </When>
    </button>
  );
};
