import { useMemo } from "react";

import { env } from "@/config/env";
import { buildArchitectureSummary } from "@/lib/architecture/build-architecture-summary";
import { getBackendConnectionConfig } from "@/services/system/backend-config.service";

export function useArchitectureSummary() {
  return useMemo(() => {
    const backend = getBackendConnectionConfig(env.nextPublicApiBaseUrl);
    return buildArchitectureSummary(backend);
  }, []);
}
