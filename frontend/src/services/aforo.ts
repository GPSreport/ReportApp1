import { apiClient } from "@/services/api";

export interface AforoRegistro {
  id: number;
  foto_ruta: string;
  timestamp_captura: string | null;
  aforoo: number;
  latitud: number | null;
  longitud: number | null;
  lugar_id: string | null;
  created_at: string | null;
}

export interface AforoHistorialResponse {
  success: boolean;
  total: number;
  registros: AforoRegistro[];
}

export interface AforoEstadisticasResponse {
  success: boolean;
  lugar_id: string | null;
  estadisticas: {
    total_registros: number;
    aforoo_promedio: number;
    aforoo_maximo: number;
    aforoo_minimo: number;
    ultimo_registro: string | null;
    total_lugares: number;
  };
}

export const aforoService = {
  obtenerHistorial(params?: {
    lugar_id?: string;
    limite?: number;
    orden?: "asc" | "desc";
  }): Promise<AforoHistorialResponse> {
    const query = new URLSearchParams();
    if (params?.lugar_id) query.set("lugar_id", params.lugar_id);
    if (params?.limite) query.set("limite", String(params.limite));
    if (params?.orden) query.set("orden", params.orden);

    const qs = query.toString();
    const path = qs ? `/aforo/historial?${qs}` : "/aforo/historial";

    return apiClient.get<AforoHistorialResponse>(path).then((r) => r.data);
  },

  obtenerEstadisticas(lugar_id?: string): Promise<AforoEstadisticasResponse> {
    const path = lugar_id
      ? `/aforo/estadisticas?lugar_id=${encodeURIComponent(lugar_id)}`
      : "/aforo/estadisticas";

    return apiClient.get<AforoEstadisticasResponse>(path).then((r) => r.data);
  },
};
