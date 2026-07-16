import type { BackendConnectionConfig } from "@/types/architecture";

export function getBackendConnectionConfig(apiBaseUrl: string): BackendConnectionConfig {
  return {
    apiBaseUrl,
    proxyPrefix: "/backend",
  };
}
