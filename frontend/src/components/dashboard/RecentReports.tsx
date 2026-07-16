"use client";

import { memo } from "react";
import Link from "next/link";
import { ReporteResponse } from "@/services/reportes";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { formatDateShort, TipoBadge } from "@/lib/app-utils";

interface RecentReportsProps {
  reports: ReporteResponse[];
}

export const RecentReports = memo(function RecentReports({ reports }: RecentReportsProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <h2 className="text-base font-semibold text-neutral-900">
          Reportes recientes
        </h2>
        <Link href="/reportes">
          <Button variant="ghost" size="sm">
            Ver todos
          </Button>
        </Link>
      </CardHeader>
      <CardBody className="p-0">
        {reports.length === 0 ? (
          <div className="px-5 py-8 text-center text-sm text-neutral-500">
            No hay reportes aún
          </div>
        ) : (
          <div className="divide-y divide-neutral-100">
            {reports.map((r) => (
              <Link
                key={r.id}
                href={`/reportes/${r.id}`}
                className="flex items-center justify-between px-5 py-3 transition-colors hover:bg-neutral-50"
              >
                <div className="flex min-w-0 flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-neutral-900 text-sm">
                      #{r.id}
                    </span>
                    <TipoBadge tipo={r.tipo_reporte} />
                  </div>
                  <p className="truncate text-xs text-neutral-500">
                    {r.descripcion || "Sin descripción"}
                  </p>
                  <p className="text-xs text-neutral-400">{formatDateShort(r.timestamp)}</p>
                </div>
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-neutral-100 text-neutral-500">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    className="h-5 w-5"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
              </Link>
            ))}
          </div>
        )}
      </CardBody>
    </Card>
  );
});
