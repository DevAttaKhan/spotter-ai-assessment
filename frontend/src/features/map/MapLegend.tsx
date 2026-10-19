import { LEVEL_COLOR, LEVEL_LABEL, ROUTE_COLOR, ROUTE_NAMES } from "@/domain/risk";
import type { RiskLevel, RouteId } from "@/domain/types";

const routeEntries = Object.entries(ROUTE_COLOR) as [RouteId, string][];
const levelEntries = Object.entries(LEVEL_LABEL) as [RiskLevel, string][];

export const MapLegend = () => (
  <div className="pointer-events-none absolute bottom-3 left-3 max-w-[calc(100%-4.5rem)] rounded-2xl border border-line/80 bg-surface/95 px-2.5 py-2 text-[11px] shadow-lg backdrop-blur-md lg:bottom-4 lg:max-w-[280px] lg:px-3 lg:py-2.5">
    <ul className="flex flex-wrap gap-x-2.5 gap-y-1 lg:hidden">
      {routeEntries.map(([id, color]) => (
        <li key={id} className="flex items-center gap-1.5">
          <span className="inline-block h-1 w-3.5 rounded-full" style={{ backgroundColor: color }} />
          {ROUTE_NAMES[id]}
        </li>
      ))}
      {levelEntries.map(([level, label]) => (
        <li key={level} className="flex items-center gap-1.5">
          <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: LEVEL_COLOR[level] }} />
          {label}
        </li>
      ))}
    </ul>
    <div className="hidden lg:block">
      <p className="text-[10px] font-semibold tracking-[0.14em] text-muted uppercase">Routes</p>
      <ul className="mt-1.5 flex flex-wrap gap-x-3 gap-y-1">
        {routeEntries.map(([id, color]) => (
          <li key={id} className="flex items-center gap-1.5">
            <span className="inline-block h-1 w-4 rounded-full" style={{ backgroundColor: color }} />
            {ROUTE_NAMES[id]}
          </li>
        ))}
      </ul>
      <p className="mt-2.5 text-[10px] font-semibold tracking-[0.14em] text-muted uppercase">Checkpoint risk</p>
      <ul className="mt-1.5 grid grid-cols-2 gap-x-3 gap-y-1">
        {levelEntries.map(([level, label]) => (
          <li key={level} className="flex items-center gap-1.5">
            <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: LEVEL_COLOR[level] }} />
            {label}
          </li>
        ))}
      </ul>
    </div>
  </div>
);
