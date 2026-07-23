import { Header } from "@/components/layout/Header";

export default function MisReportesPage() {
  return (
    <>
      <Header
        title="Mis Reportes"
        description="Reportes creados por ti"
      />
      <div className="flex flex-col gap-6 p-6">
        <p className="text-neutral-600">Aquí aparecerán tus reportes creados.</p>
      </div>
    </>
  );
}
