"use client";

import { useState, type FormEvent } from "react";
import { useAuth } from "@/store/auth";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { env } from "@/config/env";

export function LoginSidebar() {
  const { isLoginOpen, closeLogin, login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await fetch(`${env.nextPublicApiBaseUrl}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario: username, clave: password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Credenciales inválidas");
      }

      // TODO: re-habilitar verificación cuando esté lista
      // if (!data.verificado) {
      //   throw new Error(data.message || "Cuenta no verificada");
      // }

      login({
        id: data.numero_usuario,
        username: data.usuario,
        email: data.email,
        full_name: data.usuario,
      });
      setUsername("");
      setPassword("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al iniciar sesión");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Overlay */}
      <div
        className={`fixed inset-0 z-40 bg-black/50 transition-opacity duration-300 ${
          isLoginOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        }`}
        onClick={closeLogin}
        aria-hidden="true"
      />

      {/* Sidebar */}
      <aside
        className={`fixed right-0 top-0 z-50 h-full w-80 bg-white shadow-xl transition-transform duration-300 ease-out ${
          isLoginOpen ? "translate-x-0" : "translate-x-full"
        }`}
        aria-label="Panel de inicio de sesión"
        role="dialog"
        aria-modal="true"
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-neutral-200 px-4 py-4">
            <h2 className="text-lg font-semibold text-neutral-900">
              Iniciar Sesión
            </h2>
            <button
              onClick={closeLogin}
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

          {/* Form */}
          <form onSubmit={handleSubmit} className="flex flex-1 flex-col gap-4 p-6">
            {error && (
              <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-200">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <label
                htmlFor="username"
                className="text-sm font-medium text-neutral-700"
              >
                Usuario
              </label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Ingrese su usuario"
                required
                autoComplete="username"
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <label
                htmlFor="password"
                className="text-sm font-medium text-neutral-700"
              >
                Contraseña
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Ingrese su contraseña"
                required
                autoComplete="current-password"
                disabled={isLoading}
              />
            </div>

            <Button
              type="submit"
              className="mt-auto w-full"
              disabled={isLoading}
            >
              {isLoading ? "Iniciando sesión..." : "Iniciar Sesión"}
            </Button>
          </form>

          {/* Footer */}
          <div className="border-t border-neutral-200 px-6 py-4">
            <p className="text-center text-sm text-neutral-500">
              ¿No tienes cuenta?{" "}
              <a
                href="#"
                className="font-medium text-neutral-700 underline underline-offset-4 hover:text-neutral-900"
              >
                Contacta al administrador
              </a>
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
