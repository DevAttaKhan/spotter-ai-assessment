import type { Checkpoint } from "@/domain/types";
import { formatInches, formatWhen, formatWind } from "@/lib/format";
import { When } from "react-if";
import { RiskPill } from "./RiskPill";

type CheckpointRowProps = {
  checkpoint: Checkpoint;
  timeZone?: string;
  onFocus: (checkpoint: Checkpoint) => void;
};

export const CheckpointRow = ({ checkpoint, timeZone, onFocus }: CheckpointRowProps) => {
  const handleFocus = () => onFocus(checkpoint);
  const factorText = checkpoint.factors.length ? checkpoint.factors.join(", ") : "";

  return (
    <li>
      <button
        type="button"
        className="flex w-full items-start justify-between gap-3 rounded-lg px-2 py-2 text-left text-sm transition hover:bg-canvas focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        onClick={handleFocus}
      >
        <span className="tabular-nums">
          <span className="block font-semibold">{checkpoint.mile} mi</span>
          <span className="mt-0.5 block text-xs text-muted">{formatWhen(checkpoint.eta, timeZone)}</span>
        </span>
        <span className="text-right text-xs tabular-nums text-muted">
          <RiskPill level={checkpoint.level} />
          <span className="mt-1 block">
            {formatWind(checkpoint.wind_mph)} · {formatInches(checkpoint.rain_in_hr)} rain
          </span>
          <span className="block">{formatInches(checkpoint.snow_in_hr)} snow</span>
          <When condition={factorText}>
            <span className="mt-0.5 block text-ink/70">from {factorText}</span>
          </When>
        </span>
      </button>
    </li>
  );
};
