"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { reportesService, ReporteResponse } from "@/services/reportes";
import { Card, CardBody } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Pagination } from "@/components/ui/Pagination";
import { SpinnerOverlay, Alert } from "@/components/ui";
import { formatDateShort, TipoBadge, TIPO_REPORTE_OPTIONS } from "@/lib/app-utils";

const PAGE_SIZE = 10;

export function ReportList() {
  const [allReports, setAllReports] = useState<ReporteResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState("");
  const [tipoFilter, setTipoFilter] = useState("");

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    reportesService
      .obtenerReportes()
      .then(setAllReports)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Error cargando reportes")
      )
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    let list = allReports;
    if (tipoFilter) {
      list = list.filter((r) => r.tipo_reporte === tipoFilter);
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (r) =>
          r.descripcion?.toLowerCase().includes(q) ||
          String(r.id).includes(q) ||
          r.tipo_reporte.toLowerCase().includes(q)
      );
    }
    return list;
  }, [allReports, tipoFilter, search]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const paginated = filtered.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE
  );

  const handlePageChange = (page: number) => {
    setCurrentPage(Math.min(Math.max(1, page), totalPages));
  };

  if (loading) return <SpinnerOverlay message="Cargando reportes..." />;

  if (error)
    return (
      <Alert variant="destructive" title="Error">
        {error}
      </Alert>
    );

  return (
    <div className="flex flex-col gap-4">
      {/* Filters */}
      <Card>
        <CardBody>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
            <div className="flex-1">
              <Input
                placeholder="Buscar por ID, descripción o tipo..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setCurrentPage(1);
                }}
              />
            </div>
            <div className="w-full sm:w-48">
              <Select
                options={[...TIPO_REPORTE_OPTIONS]}
                value={tipoFilter}
                onChange={(e) => {
                  setTipoFilter(e.target.value);
                  setCurrentPage(1);
                }}
              />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Table */}
      <Card>
        <CardBody className="p-0">
          {paginated.length === 0 ? (
            <div className="py-12 text-center text-sm text-neutral-500">
              {allReports.length === 0
                ? "No hay reportes en el sistema"
                : "Ningún reporte coincide con los filtros"}
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-neutral-50">
                    <tr>
                      <th className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                        ID
                      </th>
                      <th className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                        Tipo
                      </th>
                      <th className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                        Descripción
                      </th>
                      <th className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                        Coordenadas
                      </th>
                      <th className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                        Fecha
                      </th>
                      <th className="whitespace-nowrap px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-neutral-500">
                        Acción
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-100 bg-white">
                    {paginated.map((r) => (
                      <tr key={r.id} className="hover:bg-neutral-50">
                        <td className="px-4 py-3 font-medium text-neutral-900">
                          #{r.id}
                        </td>
                        <td className="px-4 py-3">
                          <TipoBadge tipo={r.tipo_reporte} />
                        </td>
                        <td className="px-4 py-3 text-neutral-600 max-w-xs truncate">
                          {r.descripcion || "—"}
                        </td>
                        <td className="px-4 py-3 text-neutral-500 font-mono text-xs">
                          {r.latitud.toFixed(5)}, {r.longitud.toFixed(5)}
                        </td>
                        <td className="px-4 py-3 text-neutral-500 whitespace-nowrap">
                          {formatDateShort(r.timestamp)}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <Link href={`/reportes/${r.id}`}>
                            <Button variant="ghost" size="sm">
                              Ver
                            </Button>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="border-t border-neutral-100 px-4 py-3">
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={handlePageChange}
                  />
                </div>
              )}
            </>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
