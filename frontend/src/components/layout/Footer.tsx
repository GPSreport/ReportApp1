interface FooterProps {
  appName?: string;
  year?: number;
}

export function Footer({ appName = "ReportMap", year = 2025 }: FooterProps) {
  return (
    <footer className="flex h-12 w-full items-center justify-between border-t border-neutral-200 bg-white px-6">
      <p className="text-xs text-neutral-500">
        &copy; {year} {appName}. Todos los derechos reservados.
      </p>
      <p className="text-xs text-neutral-400">
        Sistema de monitoreo y reporte en tiempo real
      </p>
    </footer>
  );
}
