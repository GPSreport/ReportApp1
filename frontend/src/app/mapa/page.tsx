"use client";

import dynamic from "next/dynamic";
import useSWR from "swr";
import { Header } from "@/components/layout/Header";
import { ReporteResponse, reportesService } from "@/services/reportes";
import { SpinnerOverlay, Alert } from "@/components/ui";

// Leaflet solo funciona en el cliente
const MapClient = dynamic(
  () => import("@/components/map/MapClient").then((m) => m.MapClient),
  { ssr: false, loading: () => <SpinnerOverlay message="Cargando mapa..." /> }
);

export default function MapaPage() {
  // SWR con polling de 1 minuto, se detiene cuando la pestaña está oculta
  const { data: reports = [], isLoading, error } = useSWR<ReporteResponse[]>(
    "reportes",
    () => reportesService.obtenerReportes(),
    {
      refreshInterval: 60_000, // 1 minuto
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
    }
  );

  return (
    <>
      <Header
        title="Mapa"
        description="Visualización interactiva de reportes en el mapa"
      />
      <div className="flex flex-col gap-6 p-6">
        {isLoading ? (
          <div className="h-96">
            <SpinnerOverlay message="Cargando reportes..." />
          </div>
        ) : error ? (
          <Alert variant="destructive" title="Error">
            {error instanceof Error ? error.message : "Error cargando reportes"}
          </Alert>
        ) : reports.length === 0 ? (
          <Alert variant="default" title="Sin reportes">
            No hay reportes para mostrar en el mapa.
          </Alert>
        ) : (
          <div className="h-[calc(100vh-220px)]">
            <MapClient reports={reports} />
          </div>
        )}
      </div>
    </>
  );
}
