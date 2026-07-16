import { Header } from "@/components/layout/Header";
import { DashboardContent } from "@/components/dashboard/DashboardContent";

export default function DashboardPage() {
  return (
    <>
      <Header
        title="Dashboard"
        description="Resumen y estadísticas del sistema"
      />
      <DashboardContent />
    </>
  );
}
