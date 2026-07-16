"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { ReporteResponse } from "@/services/reportes";
import { Card, CardBody } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type L from "leaflet";

interface MapClientProps {
  reports: ReporteResponse[];
}

// Función de validación fuera del componente (mejora 8)
const isValidCoordinate = (lat: number, lng: number): boolean => {
  return (
    lat !== null &&
    lng !== null &&
    lat !== undefined &&
    lng !== undefined &&
    !Number.isNaN(lat) &&
    !Number.isNaN(lng) &&
    Number.isFinite(lat) &&
    Number.isFinite(lng) &&
    lat >= -90 &&
    lat <= 90 &&
    lng >= -180 &&
    lng <= 180
  );
};

export function MapClient({ reports }: MapClientProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Layer[]>([]);
  const resizeObserverRef = useRef<ResizeObserver | null>(null);
  const leafletRef = useRef<typeof import("leaflet") | null>(null);
  const invalidateSizeTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [selectedReport, setSelectedReport] = useState<ReporteResponse | null>(null);
  const [mapError, setMapError] = useState<string | null>(null);
  const [mapReady, setMapReady] = useState(false);
  const mapReadyRef = useRef(false);

  // Función para actualizar marcadores con try/catch (mejora 8)
  const updateMarkers = useCallback((reportsToShow: ReporteResponse[]) => {
    const map = mapInstanceRef.current;
    const leaflet = leafletRef.current;
    if (!map || !leaflet) return;

    try {
      // Limpiar marcadores con off() antes de remove()
      markersRef.current.forEach((marker) => {
        marker.off();
        marker.remove();
      });
      markersRef.current = [];

      // Si 0 reportes, no hacer nada más
      if (reportsToShow.length === 0) return;

      // Filtrar reportes con coordenadas válidas
      const validReports = reportsToShow.filter((r) =>
        isValidCoordinate(r.latitud, r.longitud)
      );

      if (validReports.length === 0) return;

      // Crear marcadores solo para reportes válidos
      validReports.forEach((report) => {
        const marker = leaflet.marker([report.latitud, report.longitud]).addTo(map);
        marker.bindPopup(`Reporte #${report.id}`);
        marker.on("click", () => setSelectedReport(report));
        markersRef.current.push(marker);
      });

      // Usar setView para 1 reporte, fitBounds para múltiples
      if (validReports.length === 1) {
        map.setView([validReports[0].latitud, validReports[0].longitud], 13);
      } else {
        const latlngs = validReports.map(
          (r) => [r.latitud, r.longitud] as [number, number]
        );
        map.fitBounds(latlngs, { padding: [50, 50] });
      }

      // invalidar tamaño después de ajustar la vista
      map.invalidateSize({ pan: false, animate: false });
    } catch (error) {
      console.error("Error updating markers:", error);
    }
  }, []);

  // Inicializar mapa UNA sola vez
  useEffect(() => {
    const container = mapContainerRef.current;
    if (!container || mapInstanceRef.current) return;

    let isMounted = true;
    let initAttempts = 0;
    const MAX_INIT_ATTEMPTS = 10;

    const tryInitMap = () => {
      // Verificar que el contenedor tenga dimensiones válidas
      if (container.offsetWidth === 0 || container.offsetHeight === 0) {
        initAttempts++;
        if (initAttempts < MAX_INIT_ATTEMPTS && isMounted) {
          // Reintentar después de un delay
          setTimeout(tryInitMap, 100);
        } else if (isMounted) {
          setMapError("No fue posible inicializar el mapa.");
        }
        return;
      }

      import("leaflet")
        .then((leaflet) => {
          if (!isMounted || !container || mapInstanceRef.current) return;

          // Guardar referencia al módulo para reutilizarla
          leafletRef.current = leaflet;

          // Configurar iconos
          delete (leaflet.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
          leaflet.Icon.Default.mergeOptions({
            iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
            iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
            shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
          });

          // Crear mapa
          const map = leaflet.map(container, {
            center: [4.6097, -74.0817],
            zoom: 6,
          });

          mapInstanceRef.current = map;

          // Tile layer
          const tileLayer = leaflet.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '&copy; OpenStreetMap',
            maxZoom: 19,
          }).addTo(map);

          tileLayer.on("error", () => {
            if (isMounted) {
              setMapError("Error al cargar las baldosas del mapa.");
            }
          });

          // Resize observer con debounce seguro
          const resizeObserver = new ResizeObserver(() => {
            if (invalidateSizeTimeoutRef.current) {
              clearTimeout(invalidateSizeTimeoutRef.current);
            }
            invalidateSizeTimeoutRef.current = setTimeout(() => {
              mapInstanceRef.current?.invalidateSize({ pan: false, animate: false });
            }, 100);
          });
          resizeObserver.observe(container);
          resizeObserverRef.current = resizeObserver;

          // Esperar la primera carga del TileLayer
          tileLayer.once("load", () => {
            if (!isMounted) return;
            finalizeMapInit(map);
          });

          // Fallback: si los tiles ya están en cache, whenReady se dispara inmediatamente
          map.whenReady(() => {
            if (!isMounted || mapReadyRef.current) return;
            finalizeMapInit(map);
          });
        })
        .catch((error) => {
          if (isMounted) {
            setMapError("Error al inicializar Leaflet.");
            console.error("Leaflet import error:", error);
          }
        });
    };

    const finalizeMapInit = (map: L.Map) => {
      // Secuencia correcta: esperar requestAnimationFrame, luego invalidateSize
      requestAnimationFrame(() => {
        if (!isMounted) return;
        map.invalidateSize({ pan: false, animate: false });
        mapReadyRef.current = true;
        setMapError(null);
        setMapReady(true);
      });
    };

    // Iniciar la secuencia
    tryInitMap();

    // Cleanup
    return () => {
      isMounted = false;

      if (invalidateSizeTimeoutRef.current) {
        clearTimeout(invalidateSizeTimeoutRef.current);
        invalidateSizeTimeoutRef.current = null;
      }

      if (resizeObserverRef.current) {
        resizeObserverRef.current.disconnect();
        resizeObserverRef.current = null;
      }

      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
      leafletRef.current = null;
      mapReadyRef.current = false;
    };
  }, []);

  // Actualizar marcadores cuando el mapa esté listo o cambien los reports (mejora 2)
  useEffect(() => {
    if (mapReady) {
      updateMarkers(reports);
    }
  }, [reports, mapReady, updateMarkers]);

  // Sincronizar selectedReport con reports disponibles y actualizar datos (mejora 7)
  useEffect(() => {
    if (!selectedReport) return;

    const freshReport = reports.find((r) => r.id === selectedReport.id);
    if (!freshReport) {
      setSelectedReport(null);
    } else if (freshReport !== selectedReport) {
      // Actualizar con la versión más reciente
      setSelectedReport(freshReport);
    }
  }, [reports, selectedReport]);

  return (
    <div className="flex flex-col lg:flex-row gap-4 h-full min-h-0">
      <div className="relative flex-1 min-h-96 lg:min-h-0 rounded-xl border border-neutral-200 overflow-hidden">
        <div
          ref={mapContainerRef}
          id="leaflet-map"
          className="w-full h-full"
          style={{ minHeight: "400px" }}
        />
        {!mapReady && !mapError && (
          <div className="absolute inset-0 flex items-center justify-center bg-neutral-50">
            <p className="text-sm text-neutral-500">Cargando mapa...</p>
          </div>
        )}
        {mapError && (
          <div className="absolute inset-0 flex items-center justify-center bg-neutral-50">
            <p className="text-sm text-red-500">{mapError}</p>
          </div>
        )}
      </div>
      <div className="w-full lg:w-80 shrink-0">
        {selectedReport ? (
          <Card>
            <CardBody className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-neutral-900">Reporte #{selectedReport.id}</h3>
                <button
                  onClick={() => setSelectedReport(null)}
                  className="text-neutral-400 hover:text-neutral-600"
                  aria-label="Cerrar detalles del reporte"
                >
                  X
                </button>
              </div>
              <Badge variant="default">{selectedReport.tipo_reporte}</Badge>
              <p className="text-sm text-neutral-600">
                {selectedReport.descripcion || "Sin descripcion"}
              </p>
            </CardBody>
          </Card>
        ) : (
          <Card>
            <CardBody className="flex flex-col items-center justify-center py-8 text-center">
              <p className="text-sm text-neutral-500">Haz clic en un marcador</p>
              <p className="text-xs text-neutral-400 mt-1">{reports.length} reportes</p>
            </CardBody>
          </Card>
        )}
      </div>
    </div>
  );
}