"use client";

import { useEffect, useState } from "react";
import { usuariosService, UsuarioInfo } from "@/services/usuarios";
import { Card, CardBody } from "@/components/ui/Card";
import { SpinnerOverlay, Alert } from "@/components/ui";
import { formatDateNullable, ActivoBadge } from "@/lib/app-utils";

export function UsersList() {
  const [usuarios, setUsuarios] = useState<UsuarioInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    usuariosService
      .obtenerInfo()
      .then((data) => setUsuarios(data.usuarios))
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Error cargando usuarios")
      )
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <SpinnerOverlay message="Cargando usuarios..." />;

  if (error)
    return (
      <Alert variant="destructive" title="Error">
        {error}
      </Alert>
    );

  return (
    <div className="flex flex-col gap-4">
      <Card>
        <CardBody className="p-0">
          {usuarios.length === 0 ? (
            <div className="py-12 text-center text-sm text-neutral-500">
              No hay usuarios registrados
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-neutral-50">
                  <tr>
                    <th className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                      Usuario
                    </th>
                    <th className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                      Correo
                    </th>
                    <th className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                      Estado
                    </th>
                    <th className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                      Registro
                    </th>
                    <th className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                      Último login
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-100 bg-white">
                  {usuarios.map((u) => (
                    <tr key={u.usuario} className="hover:bg-neutral-50">
                      <td className="px-4 py-3 font-medium text-neutral-900">
                        @{u.usuario}
                      </td>
                      <td className="px-4 py-3 text-neutral-600">{u.correo}</td>
                      <td className="px-4 py-3">
                        <ActivoBadge activo={Boolean(u.activo)} />
                      </td>
                      <td className="px-4 py-3 text-neutral-500 whitespace-nowrap">
                        {formatDateNullable(u.created_at)}
                      </td>
                      <td className="px-4 py-3 text-neutral-500 whitespace-nowrap">
                        {formatDateNullable(u.last_login)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
