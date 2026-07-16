import { Header } from "@/components/layout/Header";
import { ReportDetail } from "@/components/reportes/ReportDetail";

interface Props {
  params: Promise<{ id: string }>;
}

export default async function ReporteDetallePage({ params }: Props) {
  const { id } = await params;
  return (
    <>
      <Header
        title={`Reporte #${id}`}
        description="Detalle del reporte"
      />
      <ReportDetail reportId={Number(id)} />
    </>
  );
}
