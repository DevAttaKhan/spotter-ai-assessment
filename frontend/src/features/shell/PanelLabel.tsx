import { When } from "react-if";

type PanelLabelProps = {
  title: string;
  detail?: string;
};

export const PanelLabel = ({ title, detail }: PanelLabelProps) => (
  <div className="flex items-baseline justify-between gap-3">
    <h2 className="text-[11px] font-semibold tracking-[0.16em] text-muted uppercase">{title}</h2>
    <When condition={detail}>
      <span className="text-xs text-muted">{detail}</span>
    </When>
  </div>
);
