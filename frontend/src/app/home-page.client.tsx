"use client";

import { Header } from "@/components/layout/Header";
import { ArchitectureSummaryCard } from "@/components/presentation/architecture-summary-card";
import { useArchitectureSummary } from "@/hooks/use-architecture-summary";

export function HomePageClient() {
  const summary = useArchitectureSummary();

  return (
    <>
      <Header
        title="Inicio"
        description="Bienvenido al sistema de reportes GPS"
      />

      <div className="flex flex-col gap-6 p-6">
        <ArchitectureSummaryCard summary={summary} />
      </div>
    </>
  );
}
