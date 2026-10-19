import { LEVEL_COLOR, LEVEL_LABEL } from "@/domain/risk";
import type { RiskLevel } from "@/domain/types";

type RiskPillProps = {
  level: RiskLevel;
};

export const RiskPill = ({ level }: RiskPillProps) => {
  const label = LEVEL_LABEL[level] || "Unknown";
  return (
    <span
      className="inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-semibold tracking-wide text-white"
      style={{ backgroundColor: LEVEL_COLOR[level] || LEVEL_COLOR.unknown }}
    >
      {label}
    </span>
  );
};
