import { Header } from "@/components/layout/Header";

export default function ReportesGuardadosPage() {
  return (
    <>
      <Header
        title="Reportes Guardados"
        description="Reportes guardados como favoritos"
      />
      <div className="flex flex-col gap-6 p-6">
        <p className="text-neutral-600">Aquí aparecerán tus reportes guardados.</p>
      </div>
    </>
  );
}
