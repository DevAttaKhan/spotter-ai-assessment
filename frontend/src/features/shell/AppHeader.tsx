import type { TripPlan } from "@/domain/types";
import { Else, If, Then } from "react-if";

type AppHeaderProps = {
  plan: TripPlan | null;
};

export const AppHeader = ({ plan }: AppHeaderProps) => (
  <header className="flex items-center justify-between gap-4 border-b border-line bg-surface px-4 py-3 sm:px-5">
    <div className="flex items-center gap-3">
      <span
        className="font-display flex h-9 w-9 items-center justify-center rounded-xl bg-ink text-lg leading-none text-white"
        aria-hidden="true"
      >
        R
      </span>
      <div>
        <h1 className="font-display text-[1.35rem] leading-none font-medium tracking-tight">Route check</h1>
        <p className="mt-1 text-xs text-muted">Weather along the haul, then the shorter drive.</p>
      </div>
    </div>
    <If condition={plan !== null}>
      <Then>
        <p className="hidden max-w-xs text-right text-sm sm:block">
          <span className="font-medium">{plan?.origin.label}</span>
          <span className="text-muted"> to </span>
          <span className="font-medium">{plan?.destination.label}</span>
          <span className="mt-0.5 block text-xs text-muted">{plan?.timezone.replaceAll("_", " ")}</span>
        </p>
      </Then>
      <Else>
        <p className="hidden text-xs text-muted md:block">Up to three truck routes</p>
      </Else>
    </If>
  </header>
);
