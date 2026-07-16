"use client";

import type { SelectHTMLAttributes } from "react";
import { forwardRef } from "react";

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  hint?: string;
  options: SelectOption[];
  placeholder?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { label, error, hint, options, placeholder, className = "", id, ...props },
  ref
) {
  const selectId = id ?? label?.toLowerCase().replace(/\s+/g, "-");

  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label
          htmlFor={selectId}
          className="text-sm font-medium text-neutral-700"
        >
          {label}
        </label>
      )}
      <select
        ref={ref}
        id={selectId}
        className={[
          "h-10 w-full rounded-lg border bg-white px-3 text-sm text-neutral-900",
          "focus:outline-none focus:ring-2 focus:ring-offset-0",
          "transition-colors cursor-pointer",
          error
            ? "border-red-500 focus:border-red-500 focus:ring-red-500"
            : "border-neutral-300 focus:border-neutral-900 focus:ring-neutral-900",
          props.disabled ? "cursor-not-allowed bg-neutral-50 opacity-50" : "",
          className,
        ].join(" ")}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {hint && !error && (
        <p className="text-xs text-neutral-500">{hint}</p>
      )}
      {error && (
        <p className="text-xs text-red-600">{error}</p>
      )}
    </div>
  );
});
