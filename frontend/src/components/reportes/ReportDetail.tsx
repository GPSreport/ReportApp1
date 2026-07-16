"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { reportesService, ReporteResponse } from "@/services/reportes";
import { Card, CardHeader, CardBody, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { SpinnerOverlay, Alert } from "@/components/ui";
import { formatDateLong, TipoBadge } from "@/lib/app-utils";

interface ReportDetailProps {
  reportId: number;
}

export function ReportDetail({ reportId }: ReportDetailProps) {
  const [report, setReport] = useState<ReporteResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    reportesService
      .obtenerReportes()
      .then((reports) => {
        const found = reports.find((r) => r.id === reportId);
        if (found) setReport(found);
        else setError("Reporte no encontrado");
      })
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Error cargando reporte")
      )
      .finally(() => setLoading(false));
  }, [reportId]);

  if (loading) return <SpinnerOverlay message="Cargando reporte..." />;

  if (error || !report)
    return (
      <div className="p-6">
        <Alert variant="destructive" title="Error">
          {error ?? "Reporte no encontrado"}
        </Alert>
        <div className="mt-4">
          <Link href="/reportes">
            <Button variant="outline" size="sm">
              ← Volver a reportes
            </Button>
          </Link>
        </div>
      </div>
    );

  const imageUrl = report.foto_base64
    ? `/backend/${report.foto_base64}`
    : null;

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Back button */}
      <Link href="/reportes">
        <Button variant="ghost" size="sm">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4">
            <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
          Volver a reportes
        </Button>
      </Link>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Image */}
        <Card>
          <CardHeader>
            <h2 className="text-base font-semibold">Fotografía</h2>
          </CardHeader>
          <CardBody>
            {imageUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={imageUrl}
                alt={`Reporte #${report.id}`}
                className="h-auto w-full rounded-lg object-cover"
                style={{ maxHeight: "400px" }}
              />
            ) : (
              <div className="flex h-48 items-center justify-center rounded-lg bg-neutral-50 text-neutral-400 text-sm">
                Sin imagen
              </div>
            )}
          </CardBody>
        </Card>

        {/* Details */}
        <div className="flex flex-col gap-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-base font-semibold">
                  Reporte #{report.id}
                </h2>
                <TipoBadge tipo={report.tipo_reporte} />
              </div>
            </CardHeader>
            <CardBody className="flex flex-col gap-4">
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
                  Descripción
                </p>
                <p className="mt-1 text-sm text-neutral-700">
                  {report.descripcion || "Sin descripción"}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
                    Latitud
                  </p>
                  <p className="mt-1 font-mono text-sm text-neutral-700">
                    {report.latitud.toFixed(8)}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
                    Longitud
                  </p>
                  <p className="mt-1 font-mono text-sm text-neutral-700">
                    {report.longitud.toFixed(8)}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
                  Fecha del reporte
                </p>
                <p className="mt-1 text-sm text-neutral-700">
                  {formatDateLong(report.timestamp)}
                </p>
              </div>

              {/* Event dates if applicable */}
              {(report.fecha_inicio_evento || report.fecha_fin_evento) && (
                <div className="grid grid-cols-2 gap-4">
                  {report.fecha_inicio_evento && (
                    <div>
                      <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
                        Inicio del evento
                      </p>
                      <p className="mt-1 text-sm text-neutral-700">
                        {formatDateLong(report.fecha_inicio_evento)}
                      </p>
                    </div>
                  )}
                  {report.fecha_fin_evento && (
                    <div>
                      <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
                        Fin del evento
                      </p>
                      <p className="mt-1 text-sm text-neutral-700">
                        {formatDateLong(report.fecha_fin_evento)}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </CardBody>
          </Card>

          {/* Map preview link */}
          <Card>
            <CardFooter>
              <Link href="/mapa" className="flex-1">
                <Button variant="outline" className="w-full">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4">
                    <path fillRule="evenodd" d="m9.504 1.087a.75.75 0 01.556.832 9.869 9.869 0 013.96 5.826 3.75 3.75 0 014.238 5.574c0 .75-.144 1.485-.41 2.197a.75.75 0 01-1.394-.43c.173-.46.274-.958.294-1.464a.75.75 0 011.196-.67 9.77 9.77 0 00.31 1.58c.26.665.638 1.287 1.12 1.814.496.55.984.86 1.444 1.025a.75.75 0 11-.42 1.444c-.308-.11-.624-.318-.95-.64a9.76 9.76 0 01-1.698-2.21 11.135 11.135 0 01-2.45-5.94 10.1 10.1 0 00-.31-1.58.75.75 0 01-.67-1.196 11.133 11.133 0 011.463-.294.75.75 0 01.43 1.394c-.463.18-.955.288-1.464.319a.75.75 0 01-.67-1.195A9.753 9.753 0 009.504 1.087zM12 7.5a4.5 4.5 0 100 9 4.5 4.5 0 000-9z" clipRule="evenodd" />
                  </svg>
                  Ver en mapa
                </Button>
              </Link>
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  );
}
