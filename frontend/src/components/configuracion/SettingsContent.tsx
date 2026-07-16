"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/services/api";
import { Card, CardHeader, CardBody } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { SpinnerOverlay, Alert } from "@/components/ui";

interface HealthStatus {
  database: boolean;
  status: string;
  error?: string;
}

export function SettingsContent() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [errorHealth, setErrorHealth] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<HealthStatus>("/debug/health")
      .then((r) => setHealth(r.data))
      .catch((e: unknown) =>
        setErrorHealth(e instanceof Error ? e.message : "Error consultando estado")
      )
      .finally(() => setLoadingHealth(false));
  }, []);

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Estado del sistema */}
      <Card>
        <CardHeader>
          <h2 className="text-base font-semibold">Estado del sistema</h2>
        </CardHeader>
        <CardBody>
          {loadingHealth ? (
            <SpinnerOverlay message="Consultando estado..." />
          ) : errorHealth ? (
            <Alert variant="destructive">{errorHealth}</Alert>
          ) : (
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-neutral-600">Base de datos</span>
                <Badge variant={health?.database ? "default" : "destructive"}>
                  {health?.database ? "Conectada" : "Desconectada"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-neutral-600">API</span>
                <Badge variant={health?.status === "UP" ? "default" : health?.status === "DEGRADED" ? "outline" : "destructive"}>
                  {health?.status ?? "Desconocido"}
                </Badge>
              </div>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Perfil de usuario */}
      <Card>
        <CardHeader>
          <h2 className="text-base font-semibold">Perfil de usuario</h2>
        </CardHeader>
        <CardBody>
          <p className="text-sm text-neutral-500">
            Inicia sesión para ver tu información de perfil y preferencias.
          </p>
          <div className="mt-3 flex gap-3">
            <a
              href="#"
              className="inline-flex items-center gap-1.5 rounded-lg bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-700 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
              Iniciar sesión
            </a>
          </div>
        </CardBody>
      </Card>

      {/* Acerca de */}
      <Card>
        <CardHeader>
          <h2 className="text-base font-semibold">Acerca de</h2>
        </CardHeader>
        <CardBody className="flex flex-col gap-2">
          <div className="flex justify-between text-sm">
            <span className="text-neutral-500">Aplicación</span>
            <span className="font-medium text-neutral-700">GPS Reporter</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-neutral-500">Versión frontend</span>
            <span className="font-medium text-neutral-700">1.0.0</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-neutral-500">API backend</span>
            <span className="font-medium text-neutral-700">localhost:5000</span>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
