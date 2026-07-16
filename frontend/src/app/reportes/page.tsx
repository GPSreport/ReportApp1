import { Header } from "@/components/layout/Header";
import { ReportList } from "@/components/reportes/ReportList";

export default function ReportesPage() {
  return (
    <>
      <Header
        title="Reportes"
        description="Lista y gestión de reportes geolocalizados"
      />
      <div className="flex flex-col gap-6 p-6">
        <ReportList />
      </div>
    </>
  );
}
