import type { ChangeEvent } from "react";
import { formatWhen } from "@/lib/format";

type HeatmapSliderProps = {
  hours?: string[];
  hourIndex: number;
  timeZone?: string;
  showHeat: boolean;
  onHourChange: (hour: number) => void;
  onToggleHeat: (show: boolean) => void;
};

export const HeatmapSlider = ({
  hours,
  hourIndex,
  timeZone,
  showHeat,
  onHourChange,
  onToggleHeat,
}: HeatmapSliderProps) => {
  const max = Math.max((hours?.length || 1) - 1, 0);
  const label = hours?.[hourIndex] ? formatWhen(hours[hourIndex], timeZone) : "–";

  const handleHourChange = (event: ChangeEvent<HTMLInputElement>) => {
    onHourChange(Number(event.target.value));
  };

  const handleToggle = (event: ChangeEvent<HTMLInputElement>) => {
    onToggleHeat(event.target.checked);
  };

  return (
    <div className="border-t border-line bg-surface px-4 py-3.5">
      <div className="flex items-center justify-between gap-4">
        <label className="inline-flex items-center gap-2 text-sm font-medium" htmlFor="show-heat">
          <input
            id="show-heat"
            className="size-4 accent-accent"
            type="checkbox"
            checked={showHeat}
            onChange={handleToggle}
          />
          Corridor forecast
        </label>
        <p className="text-right">
          <span className="block text-sm font-semibold tabular-nums">+{hourIndex}h</span>
          <span className="block text-xs text-muted tabular-nums">{label}</span>
        </p>
      </div>
      <input
        className="forecast-range mt-3"
        type="range"
        min={0}
        max={max}
        step={1}
        value={Math.min(hourIndex, max)}
        disabled={!hours?.length}
        aria-label="Forecast hour"
        aria-valuetext={label}
        onChange={handleHourChange}
      />
      <p className="mt-2 hidden text-[11px] leading-4 text-muted sm:block">
        0–48 hours from now, in {timeZone || "origin"} time. Dragging does not reload weather.
      </p>
    </div>
  );
};
