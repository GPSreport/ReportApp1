import type { ReactNode } from "react";

import { AuthProvider } from "@/store/auth";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { Footer } from "@/components/layout/Footer";
import { LoginSidebar } from "@/components/layout/LoginSidebar";
import { UserProfileSidebar } from "@/components/layout/UserProfileSidebar";

interface PrincipalLayoutProps {
  children: ReactNode;
}

export function PrincipalLayout({ children }: PrincipalLayoutProps) {
  return (
    <AuthProvider>
      <div className="flex h-screen w-full flex-col overflow-hidden bg-neutral-50">
        <Navbar />

        <div className="flex flex-1 overflow-hidden">
          <Sidebar />

          <main className="flex flex-1 flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto">{children}</div>
            <Footer />
          </main>
        </div>

        <LoginSidebar />
        <UserProfileSidebar />
      </div>
    </AuthProvider>
  );
}
