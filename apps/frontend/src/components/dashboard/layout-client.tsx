"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname, useParams } from "next/navigation";
import { useTrafficStore } from "@/store/traffic";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface NavItem {
  href: string;
  label: string;
  icon: string;
  exact?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: "▣", exact: true },
  { href: "/dashboard/twin", label: "3D Twin", icon: "◈" },
  { href: "/dashboard/analytics", label: "Analytics", icon: "◐" },
  { href: "/dashboard/scenario", label: "Scenario", icon: "◑" },
  { href: "/dashboard/time-travel", label: "Time Travel", icon: "◷" },
];

export default function DashboardLayoutClient({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const params = useParams();
  const locale = (params.locale as string) ?? "en";
  const usingMockData = useTrafficStore((s) => s.usingMockData);
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside
        className={cn(
          "flex flex-col bg-slate-900 border-r border-slate-700/50 transition-all duration-300",
          sidebarOpen ? "w-56" : "w-14",
        )}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 p-4 border-b border-slate-700/50">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            SC
          </div>
          {sidebarOpen && <span className="font-semibold text-slate-100 truncate">Smart City</span>}
        </div>

        {/* Nav */}
        <nav className="flex-1 p-2 space-y-1" role="navigation" aria-label="Main navigation">
          {NAV_ITEMS.map((item) => {
            const href = `/${locale}${item.href}`;
            const isActive = item.exact ? pathname === href : pathname.startsWith(href);
            return (
              <Link
                key={item.href}
                href={href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                  isActive
                    ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30"
                    : "text-slate-400 hover:text-slate-100 hover:bg-slate-800",
                )}
                aria-current={isActive ? "page" : undefined}
              >
                <span className="text-base">{item.icon}</span>
                {sidebarOpen && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Bottom: demo badge + language switcher */}
        <div className="p-4 border-t border-slate-700/50 space-y-3">
          {usingMockData && (
            <div className={cn("flex items-center gap-2", !sidebarOpen && "justify-center")}>
              <Badge variant="warning" className="text-xs animate-pulse">
                {sidebarOpen ? "Demo Data" : "D"}
              </Badge>
            </div>
          )}
          {sidebarOpen && (
            <div className="flex gap-1">
              {(["en", "he", "ar"] as const).map((lang) => (
                <Link
                  key={lang}
                  href={pathname.replace(`/${locale}`, `/${lang}`)}
                  className={cn(
                    "px-2 py-1 rounded text-xs font-medium transition-colors",
                    locale === lang
                      ? "bg-indigo-600 text-white"
                      : "text-slate-400 hover:text-slate-100 hover:bg-slate-800",
                  )}
                >
                  {lang.toUpperCase()}
                </Link>
              ))}
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-slate-400 hover:text-slate-100 text-xs"
            aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          >
            {sidebarOpen ? "← Collapse" : "→"}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto" role="main">
        {children}
      </main>
    </div>
  );
}
