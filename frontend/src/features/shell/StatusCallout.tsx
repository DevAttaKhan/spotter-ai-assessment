import type { ReactNode } from "react";

type StatusCalloutProps = {
  tone: "error" | "note";
  children: ReactNode;
};

export const StatusCallout = ({ tone, children }: StatusCalloutProps) => {
  const toneClass =
    tone === "error"
      ? "border-red-200 bg-red-50 text-red-900"
      : "border-signal/20 bg-signal-soft text-ink";

  return (
    <p className={`mx-4 mb-3 rounded-lg border px-3 py-2 text-sm leading-5 ${toneClass}`} role={tone === "error" ? "alert" : "status"}>
      {children}
    </p>
  );
};
