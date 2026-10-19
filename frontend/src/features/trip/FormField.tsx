import type { ReactNode } from "react";
import { When } from "react-if";

type FormFieldProps = {
  id: string;
  label: string;
  hint?: string;
  children: ReactNode;
};

export const fieldClass =
  "h-10 w-full rounded-lg border border-line bg-canvas px-3 text-sm text-ink outline-none transition placeholder:text-muted/80 focus:border-accent focus:bg-surface focus:ring-4 focus:ring-accent/10";

export const FormField = ({ id, label, hint, children }: FormFieldProps) => (
  <div className="flex flex-col gap-1.5">
    <label className="text-[13px] font-medium" htmlFor={id}>
      {label}
    </label>
    {children}
    <When condition={hint}>
      <p className="text-xs leading-4 text-muted">{hint}</p>
    </When>
  </div>
);
