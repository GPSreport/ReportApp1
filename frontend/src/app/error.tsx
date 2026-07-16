"use client";

import Link from "next/link";
import { Button } from "@/components/ui/Button";

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function ErrorPage({ error, reset }: ErrorPageProps) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-6 px-4 text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-red-50">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          className="h-10 w-10 text-red-400"
        >
          <path
            fillRule="evenodd"
            d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 3.249-2.598 3.249H4.645c-2.309 0-3.752-1.249-2.598-3.249L9.4 3.003zM12 8.25a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0112 8.25zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z"
            clipRule="evenodd"
          />
        </svg>
      </div>
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-bold text-neutral-900">Error</h1>
        <h2 className="text-lg font-semibold text-neutral-700">
          Algo salió mal
        </h2>
        <p className="text-sm text-neutral-500">
          {error.message || "Ha ocurrido un error inesperado."}
        </p>
      </div>
      <div className="flex gap-3">
        <Button variant="outline" onClick={() => reset()}>
          Reintentar
        </Button>
        <Link href="/">
          <Button variant="default">Volver al inicio</Button>
        </Link>
      </div>
    </div>
  );
}
