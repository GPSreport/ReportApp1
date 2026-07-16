import Link from "next/link";
import { Button } from "@/components/ui/Button";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-6 px-4 text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-neutral-100">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          className="h-10 w-10 text-neutral-400"
        >
          <path
            fillRule="evenodd"
            d="M18.685 19.097A9.724 9.724 0 0021.75 12c0-5.385-4.365-9.75-9.75-9.75S2.25 6.615 2.25 12a9.723 9.723 0 003.065 7.097A9.724 9.724 0 0012 21.75a9.724 9.724 0 007.935-4.565A9.725 9.725 0 0021.75 12c0 5.385-4.365 9.75-9.75 9.75s-9.75-4.365-9.75-9.75c0-1.33.266-2.597.75-3.753a9.725 9.725 0 013.665-2.498zM12 9.25a.75.75 0 100-1.5.75.75 0 000 1.5zm-7.25 5.5a.75.75 0 100 1.5.75.75 0 000-1.5zm14.25.75a.75.75 0 11-1.5 0 .75.75 0 011.5 0z"
            clipRule="evenodd"
          />
        </svg>
      </div>
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-bold text-neutral-900">404</h1>
        <h2 className="text-lg font-semibold text-neutral-700">
          Página no encontrada
        </h2>
        <p className="text-sm text-neutral-500">
          La página que buscas no existe o fue movida.
        </p>
      </div>
      <Link href="/">
        <Button variant="default">Volver al inicio</Button>
      </Link>
    </div>
  );
}
