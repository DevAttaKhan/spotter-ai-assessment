import type { RouteId, RouteOption } from "@/domain/types";
import { PanelLabel } from "@/features/shell/PanelLabel";
import { Else, If, Then } from "react-if";
import { RouteCard } from "./RouteCard";

type RouteListProps = {
  routes?: RouteOption[];
  selectedId: RouteId | null;
  onSelect: (routeId: RouteId) => void;
};

export const RouteList = ({ routes, selectedId, onSelect }: RouteListProps) => {
  const count = routes?.length ?? 0;

  return (
    <div className="px-4 pb-4">
      <PanelLabel title="Routes" detail={count ? `${count} returned` : undefined} />
      <If condition={count === 0}>
        <Then>
          <div className="mt-3 rounded-xl border border-dashed border-line px-4 py-6 text-center">
            <p className="text-sm font-medium">No routes yet</p>
            <p className="mt-1 text-xs leading-5 text-muted">Compare a trip. The best balance is marked first.</p>
          </div>
        </Then>
        <Else>
          <div className="mt-3 flex flex-col gap-2">
            {routes?.map((route) => (
              <RouteCard key={route.id} route={route} selected={route.id === selectedId} onSelect={onSelect} />
            ))}
          </div>
        </Else>
      </If>
    </div>
  );
};
