export type ArchitectureLayer = "presentacion" | "logica" | "datos" | "utilidades";

export interface LayerDefinition {
  layer: ArchitectureLayer;
  folder: string;
  description: string;
}

export interface BackendConnectionConfig {
  apiBaseUrl: string;
  proxyPrefix: string;
}

export interface ArchitectureSummary {
  backend: BackendConnectionConfig;
  layers: LayerDefinition[];
}
