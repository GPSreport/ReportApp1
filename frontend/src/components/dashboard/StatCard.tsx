"use client";

import type { ReactNode } from "react";
import { memo } from "react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: ReactNode;
  description?: string;
  variant?: "default" | "primary";
}

export const StatCard = memo(function StatCard({
  label,
  value,
  icon,
  description,
  variant = "default",
}: StatCardProps) {
  return (
    <div
      className={[
        "flex items-start gap-4 rounded-xl border p-5",
        variant === "primary"
          ? "border-neutral-900 bg-neutral-900 text-white"
          : "border-neutral-200 bg-white text-neutral-900",
      ].join(" ")}
    >
      <div
        className={[
          "flex h-12 w-12 shrink-0 items-center justify-center rounded-xl",
          variant === "primary"
            ? "bg-white/10 text-white"
            : "bg-neutral-100 text-neutral-600",
        ].join(" ")}
      >
        {icon}
      </div>
      <div className="flex flex-col gap-1">
        <p
          className={[
            "text-sm font-medium",
            variant === "primary" ? "text-white/70" : "text-neutral-500",
          ].join(" ")}
        >
          {label}
        </p>
        <p className="text-3xl font-bold tracking-tight">{value}</p>
        {description && (
          <p
            className={[
              "text-xs",
              variant === "primary" ? "text-white/50" : "text-neutral-400",
            ].join(" ")}
          >
            {description}
          </p>
        )}
      </div>
    </div>
  );
});
