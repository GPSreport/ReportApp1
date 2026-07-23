"use client";

import { useAuth } from "@/store/auth";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

export function UserProfileSidebar() {
  const { isProfileOpen, closeProfile, user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <>
      {/* Overlay */}
      <div
        className={`fixed inset-0 z-40 bg-black/50 transition-opacity duration-300 ${
          isProfileOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        }`}
        onClick={closeProfile}
        aria-hidden="true"
      />

      {/* Sidebar */}
      <aside
        className={`fixed right-0 top-0 z-50 h-full w-80 bg-white shadow-xl transition-transform duration-300 ease-out ${
          isProfileOpen ? "translate-x-0" : "translate-x-full"
        }`}
        aria-label="Panel de perfil"
        role="dialog"
        aria-modal="true"
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-neutral-200 px-4 py-4">
            <h2 className="text-lg font-semibold text-neutral-900">
              Mi Perfil
            </h2>
            <button
              onClick={closeProfile}
              className="rounded-lg p-2 text-neutral-500 hover:bg-neutral-100 hover:text-neutral-700 transition-colors"
              aria-label="Cerrar"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-5 w-5"
              >
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Profile Content */}
          <div className="flex flex-1 flex-col gap-6 p-6">
            {/* Avatar */}
            <div className="flex flex-col items-center gap-3">
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-neutral-900 text-white text-2xl font-semibold">
                {user?.username?.charAt(0).toUpperCase() || "U"}
              </div>
              <div className="text-center">
                <p className="text-lg font-semibold text-neutral-900">
                  {user?.full_name || user?.username}
                </p>
                <p className="text-sm text-neutral-500">{user?.email}</p>
              </div>
            </div>

            {/* Info */}
            <div className="space-y-4">
              <div className="rounded-lg border border-neutral-200 p-4 space-y-3">
                <div>
                  <p className="text-xs font-medium text-neutral-500 uppercase tracking-wide">
                    Usuario
                  </p>
                  <p className="text-sm text-neutral-900">{user?.username}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-neutral-500 uppercase tracking-wide">
                    ID
                  </p>
                  <p className="text-sm text-neutral-900">#{user?.id}</p>
                </div>
              </div>

              {/* Verification Status */}
              <div className="rounded-lg border border-neutral-200 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-neutral-500 uppercase tracking-wide">
                      Estado de verificación
                    </p>
                    <div className="mt-1">
                      <Badge variant="secondary">
                        Verificado
                      </Badge>
                    </div>
                  </div>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    className="h-5 w-5 text-green-500"
                  >
                    <path
                      fillRule="evenodd"
                      d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
              </div>

              {/* Verify Button */}
              <Button variant="outline" className="w-full" disabled>
                Solicitar verificación
              </Button>
            </div>
          </div>

          {/* Footer */}
          <div className="border-t border-neutral-200 p-6">
            <Button
              variant="outline"
              className="w-full"
              onClick={handleLogout}
            >
              Cerrar sesión
            </Button>
          </div>
        </div>
      </aside>
    </>
  );
}
