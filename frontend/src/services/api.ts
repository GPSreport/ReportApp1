import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from "axios";

import { env } from "@/config/env";

export class ApiError extends Error {
  status: number | undefined;
  data: unknown;

  constructor(message: string, status: number | undefined, data: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

function buildAxiosInstance(baseURL: string): AxiosInstance {
  const instance = axios.create({
    baseURL,
    timeout: 15000,
    headers: {
      "Content-Type": "application/json",
    },
  });

  // Interceptor de peticion: inyectar token si existe
  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      if (typeof window !== "undefined") {
        const token = localStorage.getItem("auth_token");
        if (token && config.headers) {
          config.headers["Authorization"] = `Bearer ${token}`;
        }
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Interceptor de respuesta: normalizar errores
  instance.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      const message =
        (error.response?.data as { detail?: string })?.detail ??
        error.message ??
        "Error desconocido";

      return Promise.reject(new ApiError(message, error.response?.status, error.response?.data));
    }
  );

  return instance;
}

export const apiClient: AxiosInstance = buildAxiosInstance(env.nextPublicApiBaseUrl);
