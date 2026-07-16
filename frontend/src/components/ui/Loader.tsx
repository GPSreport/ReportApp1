interface LoaderProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const SIZE_CLASSES = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-8 w-8",
};

export function Loader({ size = "md", className = "" }: LoaderProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      className={`animate-spin text-neutral-400 ${SIZE_CLASSES[size]} ${className}`}
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  );
}

interface SpinnerOverlayProps {
  message?: string;
}

export function SpinnerOverlay({ message = "Cargando..." }: SpinnerOverlayProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12">
      <Loader size="lg" />
      <p className="text-sm text-neutral-500">{message}</p>
    </div>
  );
}
