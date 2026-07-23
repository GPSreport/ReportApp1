"use client";

import Link from "next/link";
import { useAuth } from "@/store/auth";
import { Button } from "@/components/ui/Button";

interface NavbarProps {
  appName?: string;
}

export function Navbar({ appName = "ReportMap" }: NavbarProps) {
  const { isAuthenticated, user, openLogin, openProfile } = useAuth();

  return (
    <header className="sticky top-0 z-50 flex h-14 w-full items-center justify-between border-b border-neutral-200 bg-white/90 px-6 backdrop-blur-sm">
      <Link href="/" className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-neutral-900 text-white">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="h-5 w-5"
          >
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" />
          </svg>
        </div>
        <span className="text-lg font-semibold tracking-tight text-neutral-900">
          {appName}
        </span>
      </Link>

      <div className="flex items-center gap-3">
        {isAuthenticated ? (
          <button
            onClick={openProfile}
            className="flex items-center gap-2 rounded-lg border border-neutral-200 px-3 py-1.5 text-sm font-medium text-neutral-700 transition-colors hover:bg-neutral-50"
          >
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-neutral-900 text-white text-xs font-semibold">
              {user?.username?.charAt(0).toUpperCase() || "U"}
            </div>
            <span>{user?.username}</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              className="h-4 w-4 text-neutral-500"
            >
              <path d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        ) : (
          <Button
            variant="outline"
            size="sm"
            onClick={openLogin}
          >
            Iniciar sesión
          </Button>
        )}
      </div>
    </header>
  );
}
