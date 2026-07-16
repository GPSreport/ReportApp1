import type { ArchitectureSummary } from "@/types/architecture";

interface ArchitectureSummaryCardProps {
  summary: ArchitectureSummary;
}

export function ArchitectureSummaryCard({ summary }: ArchitectureSummaryCardProps) {
  return (
    <section className="rounded-xl border border-neutral-200 bg-neutral-50 p-5">
      <h2 className="mb-2 text-lg font-medium">Arquitectura base</h2>
      <p className="mb-3 text-sm text-neutral-700">
        Separacion por capas aplicada para evitar logica de negocio en componentes visuales.
      </p>

      <ul className="mb-3 space-y-2 text-sm text-neutral-700">
        {summary.layers.map((item) => (
          <li key={item.layer} className="rounded-md border border-neutral-200 bg-white p-3">
            <p className="font-semibold capitalize">{item.layer}</p>
            <p className="text-neutral-600">{item.folder}</p>
            <p className="text-neutral-600">{item.description}</p>
          </li>
        ))}
      </ul>

      <div className="text-sm text-neutral-700">
        <p>API base publica: {summary.backend.apiBaseUrl}</p>
        <p>Proxy desarrollo: {summary.backend.proxyPrefix}\/\*</p>
      </div>
    </section>
  );
}
