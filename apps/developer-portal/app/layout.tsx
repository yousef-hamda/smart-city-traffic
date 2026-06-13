import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import TopNav from "@/src/components/TopNav";

export const metadata: Metadata = {
  title: "Smart City Traffic — Developer Portal",
  description:
    "API catalog, key management, and interactive explorer for the Smart City Traffic platform",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-slate-950 text-slate-100">
        <TopNav />
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</main>
      </body>
    </html>
  );
}
