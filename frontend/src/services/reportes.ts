import { apiClient } from "@/services/api";

export interface ReporteCreate {
  latitud: number;
  longitud: number;
  timestamp?: string;
  foto_base64?: string;
  descripcion?: string;
  tipo_reporte?: string;
  fecha_inicio_evento?: string;
  fecha_fin_evento?: string;
}

export interface ReporteResponse {
  id: number;
  latitud: number;
  longitud: number;
  timestamp: string;
  foto_base64: string;
  descripcion: string | null;
  tipo_reporte: string;
  fecha_inicio_evento: string | null;
  fecha_fin_evento: string | null;
}

export interface StatsResponse {
  total_reportes: number;
  ultimo_reporte: string | null;
}

export const reportesService = {
  obtenerReportes(): Promise<ReporteResponse[]> {
    return apiClient.get<ReporteResponse[]>("/reportes/").then((r) => r.data);
  },

  crearReporte(data: ReporteCreate): Promise<ReporteResponse> {
    return apiClient.post<ReporteResponse>("/reportes/", data).then((r) => r.data);
  },

  obtenerStats(): Promise<StatsResponse> {
    return apiClient.get<StatsResponse>("/stats").then((r) => r.data);
  },
};
