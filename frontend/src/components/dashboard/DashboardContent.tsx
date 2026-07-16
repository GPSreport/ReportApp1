"use client";

import { useEffect, useState } from "react";
import { StatCard } from "./StatCard";
import { RecentReports } from "./RecentReports";
import { reportesService, ReporteResponse, StatsResponse } from "@/services/reportes";
import { SpinnerOverlay, Alert } from "@/components/ui";

export function DashboardContent() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [reports, setReports] = useState<ReporteResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      reportesService.obtenerStats(),
      reportesService.obtenerReportes(),
    ])
      .then(([s, r]) => {
        setStats(s);
        setReports(r.slice(0, 5)); // 5 más recientes
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : "Error cargando datos");
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <SpinnerOverlay message="Cargando dashboard..." />;

  if (error) {
    return (
      <div className="p-6">
        <Alert variant="destructive" title="Error">
          {error}
        </Alert>
      </div>
    );
  }

  const lastReport = stats?.ultimo_reporte
    ? new Date(stats.ultimo_reporte).toLocaleDateString("es-CO", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "Sin datos";

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* KPI Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          label="Total reportes"
          value={stats?.total_reportes ?? 0}
          icon={
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="h-6 w-6"
            >
              <path
                fillRule="evenodd"
                d="M6.75 2.25A.75.75 0 017.5 3v1.5h9V3A.75.75 0 0118 3v1.5h.75a3 3 0 013 3v11.25a3 3 0 01-3 3H5.25a3 3 0 01-3-3V7.5a3 3 0 013-3H6V3a.75.75 0 01.75-.75zm13.5 9a1.5 1.5 0 00-1.5-1.5H5.25a1.5 1.5 0 00-1.5 1.5v7.5a1.5 1.5 0 001.5 1.5h13.5a1.5 1.5 0 001.5-1.5v-7.5z"
                clipRule="evenodd"
              />
            </svg>
          }
          description="Reportes geolocalizados"
        />
        <StatCard
          label="Último reporte"
          value={lastReport}
          icon={
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="h-6 w-6"
            >
              <path
                fillRule="evenodd"
                d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zM12.75 6a.75.75 0 00-1.5 0v6c0 .414.336.75.75.75h4.5a.75.75 0 000-1.5h-3.75V6z"
                clipRule="evenodd"
              />
            </svg>
          }
          description="Fecha del reporte más reciente"
        />
        <StatCard
          label="Reportes hoy"
          value="—"
          icon={
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="h-6 w-6"
            >
              <path d="M18.375 12.739h-7.735V2.25a1.5 1.5 0 00-1.5-1.5h-1.5a.75.75 0 00-.75.75v18.489a3.75 3.75 0 013.75 3.75h6.235a3 3 0 003-3v-7.5zM8.25 21.75a2.25 2.25 0 002.25-2.25V9a2.25 2.25 0 00-2.25-2.25H4.5a.75.75 0 00-.75.75v12a3 3 0 003 3h2.25z" />
            </svg>
          }
          description="Pendiente de implementar"
        />
      </div>

      {/* Reportes recientes */}
      <RecentReports reports={reports} />
    </div>
  );
}
