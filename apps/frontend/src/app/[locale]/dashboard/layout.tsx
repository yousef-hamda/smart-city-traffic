import type { Metadata } from "next";
import type { ReactNode } from "react";
import DashboardLayoutClient from "@/components/dashboard/layout-client";

export const metadata: Metadata = {
  title: "Smart City Traffic — Dashboard",
};

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return <DashboardLayoutClient>{children}</DashboardLayoutClient>;
}
