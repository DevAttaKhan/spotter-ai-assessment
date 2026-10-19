import type { RouteSummary } from "@/domain/types";
import { formatMiles } from "@/lib/format";

type RouteMetricsProps = {
  summary: RouteSummary;
};

export const RouteMetrics = ({ summary }: RouteMetricsProps) => {
  const items = [
    { label: "Blocked", value: formatMiles(summary.no_travel_miles) },
    { label: "Severe", value: formatMiles(summary.severe_miles) },
    { label: "High", value: formatMiles(summary.high_miles) },
    { label: "Average", value: summary.average_risk ?? "–" },
  ];

  return (
    <dl className="mt-3 grid grid-cols-4 gap-1.5">
      {items.map((item) => (
        <div key={item.label} className="rounded-lg bg-canvas px-2 py-1.5">
          <dt className="text-[10px] font-medium tracking-wide text-muted uppercase">{item.label}</dt>
          <dd className="mt-0.5 text-xs font-semibold tabular-nums">{item.value}</dd>
        </div>
      ))}
    </dl>
  );
};
