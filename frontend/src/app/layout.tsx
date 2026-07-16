import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { PrincipalLayout } from "@/components/layout/PrincipalLayout";
import "@/styles/globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Reportes GPS Frontend",
  description: "Frontend independiente en Next.js para Reportes GPS",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <PrincipalLayout>{children}</PrincipalLayout>
      </body>
    </html>
  );
}
