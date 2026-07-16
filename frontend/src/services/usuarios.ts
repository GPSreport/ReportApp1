import { apiClient } from "@/services/api";

export interface UsuarioInfo {
  usuario: string;
  correo: string;
  activo: number;
  created_at: string | null;
  last_login: string | null;
}

export const usuariosService = {
  obtenerInfo(): Promise<{ usuarios: UsuarioInfo[] }> {
    return apiClient.get<{ usuarios: UsuarioInfo[] }>("/usuarios/info").then((r) => r.data);
  },
};
