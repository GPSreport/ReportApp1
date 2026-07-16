const DEFAULT_API_BASE_URL = "http://localhost:5000";

function readEnv(name: string, fallback: string): string {
  const value = process.env[name];
  if (!value || value.trim().length === 0) {
    return fallback;
  }
  return value;
}

export const env = {
  nextPublicApiBaseUrl: readEnv("NEXT_PUBLIC_API_BASE_URL", DEFAULT_API_BASE_URL),
  backendApiOrigin: readEnv("BACKEND_API_ORIGIN", DEFAULT_API_BASE_URL),
} as const;
