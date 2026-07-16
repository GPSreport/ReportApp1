import { apiClient } from "@/services/api";

export interface LoginRequest {
  usuario: string;
  clave: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  usuario: string | null;
  numero_usuario: number | null;
  email: string | null;
  verificado: boolean | null;
}

export interface CrearUsuarioRequest {
  usuario: string;
  clave: string;
  nombres: string;
  telefono: string;
  correo: string;
}

export interface UsuarioResponse {
  success: boolean;
  message: string;
  usuario: string | null;
  numero_usuario: number | null;
}

export interface VerificationResponse {
  success: boolean;
  message: string;
}

export interface RecoverUserSendCodeRequest {
  email: string;
}

export interface RecoverUserVerifyRequest {
  email: string;
  codigo: string;
  nueva_clave: string;
}

export interface RecoverUserResponse {
  success: boolean;
  message: string;
  usuario: string | null;
  email: string | null;
}

export const authService = {
  login(data: LoginRequest): Promise<LoginResponse> {
    return apiClient.post<LoginResponse>("/login", data).then((r) => r.data);
  },

  crearUsuario(data: CrearUsuarioRequest): Promise<UsuarioResponse> {
    return apiClient.post<UsuarioResponse>("/usuarios/crear", data).then((r) => r.data);
  },

  verificarEmailToken(token: string): Promise<VerificationResponse> {
    return apiClient
      .post<VerificationResponse>("/verificar-email", { token })
      .then((r) => r.data);
  },

  reenviarVerificacion(data: LoginRequest): Promise<{ success: boolean; message: string }> {
    return apiClient
      .post<{ success: boolean; message: string }>("/reenviar-verificacion", data)
      .then((r) => r.data);
  },

  enviarCodigo(email: string): Promise<{
    success: boolean;
    message: string;
    expires_in_minutes: number;
    email: string;
    usuario: string;
  }> {
    return apiClient
      .post("/enviar-codigo", { email })
      .then((r) => r.data as Awaited<ReturnType<typeof authService.enviarCodigo>>);
  },

  verificarCodigo(codigo: string): Promise<{
    success: boolean;
    message: string;
    email: string;
    activo: number;
    verificado: boolean;
  }> {
    return apiClient
      .post("/verificar-codigo", { codigo })
      .then((r) => r.data as Awaited<ReturnType<typeof authService.verificarCodigo>>);
  },

  obtenerEstadoUsuario(
    email: string
  ): Promise<{
    nombre: string;
    email: string;
    verificado: boolean;
    estado_texto: string;
    activo: number | null;
    success: boolean;
  }> {
    return apiClient
      .get(`/usuario-estado/${encodeURIComponent(email)}`)
      .then((r) => r.data as Awaited<ReturnType<typeof authService.obtenerEstadoUsuario>>);
  },

  recuperarEnviarCodigo(data: RecoverUserSendCodeRequest): Promise<RecoverUserResponse> {
    return apiClient
      .post<RecoverUserResponse>("/recuperar-usuario/enviar-codigo", data)
      .then((r) => r.data);
  },

  recuperarVerificar(data: RecoverUserVerifyRequest): Promise<RecoverUserResponse> {
    return apiClient
      .post<RecoverUserResponse>("/recuperar-usuario/verificar", data)
      .then((r) => r.data);
  },
};
