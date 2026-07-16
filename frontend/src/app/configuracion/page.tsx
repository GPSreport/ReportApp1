import { Header } from "@/components/layout/Header";
import { SettingsContent } from "@/components/configuracion/SettingsContent";

export default function ConfiguracionPage() {
  return (
    <>
      <Header
        title="Configuración"
        description="Preferencias y estado del sistema"
      />
      <SettingsContent />
    </>
  );
}
