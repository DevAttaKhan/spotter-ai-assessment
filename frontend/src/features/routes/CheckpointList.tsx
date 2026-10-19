import type { Checkpoint, RouteOption } from "@/domain/types";
import { PanelLabel } from "@/features/shell/PanelLabel";
import { CheckpointRow } from "./CheckpointRow";

type CheckpointListProps = {
  route: RouteOption | null;
  timeZone?: string;
  onFocus: (checkpoint: Checkpoint) => void;
};

export const CheckpointList = ({ route, timeZone, onFocus }: CheckpointListProps) => {
  if (!route) {
    return null;
  }

  return (
    <div className="border-t border-line px-4 py-4">
      <PanelLabel title={`${route.name} checkpoints`} detail="Select to center" />
      <ul className="mt-2 max-h-72 overflow-y-auto">
        {route.checkpoints.map((checkpoint) => (
          <CheckpointRow
            key={`${checkpoint.mile}-${checkpoint.lat}`}
            checkpoint={checkpoint}
            timeZone={timeZone}
            onFocus={onFocus}
          />
        ))}
      </ul>
    </div>
  );
};
