"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Search,
  Inbox,
  FileText,
  Users,
  CreditCard,
  Settings,
  FolderOpen,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/hooks/use-auth";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  roles?: string[];
  badge?: number;
}

const editorNav: NavItem[] = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Discovery", href: "/discovery", icon: Search },
  { label: "Pitch Inbox", href: "/pitches", icon: Inbox },
  { label: "Assignments", href: "/assignments", icon: FileText },
  { label: "Squads", href: "/squads", icon: Users },
  { label: "Payments", href: "/payments", icon: CreditCard },
];

const freelancerNav: NavItem[] = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Opportunities", href: "/discovery", icon: Search },
  { label: "My Pitches", href: "/pitches", icon: Inbox },
  { label: "Assignments", href: "/assignments", icon: FileText },
  { label: "Portfolio", href: "/portfolio", icon: FolderOpen },
  { label: "Payments", href: "/payments", icon: CreditCard },
];

const settingsNav: NavItem[] = [
  { label: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();

  const navItems = user?.role === "editor" ? editorNav : freelancerNav;

  const initials = user
    ? `${user.first_name?.[0] || ""}${user.last_name?.[0] || ""}`.toUpperCase()
    : "??";

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-[280px] flex-col bg-ink-900">
      {/* Logo */}
      <div className="flex h-14 items-center border-b border-ink-800 px-5">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-[5px] bg-white text-ink-900">
            <span className="text-xs font-bold">EN</span>
          </div>
          <span className="text-sm font-semibold text-white">
            Elastic Newsroom
          </span>
        </Link>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 overflow-y-auto px-2 py-3">
        <div className="space-y-0.5">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex h-9 items-center gap-3 rounded-[5px] px-3 text-sm transition-colors",
                  isActive
                    ? "bg-ink-800 text-white"
                    : "text-ink-400 hover:bg-ink-800 hover:text-ink-100"
                )}
              >
                <item.icon className="h-4 w-4 shrink-0" />
                <span>{item.label}</span>
                {item.badge ? (
                  <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-accent-600 px-1.5 text-[11px] font-medium text-white">
                    {item.badge}
                  </span>
                ) : null}
              </Link>
            );
          })}
        </div>

        {/* Settings Section */}
        <div className="mt-6">
          <p className="px-3 py-2 text-[11px] font-medium uppercase tracking-wider text-ink-500">
            Settings
          </p>
          <div className="space-y-0.5">
            {settingsNav.map((item) => {
              const isActive = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex h-9 items-center gap-3 rounded-[5px] px-3 text-sm transition-colors",
                    isActive
                      ? "bg-ink-800 text-white"
                      : "text-ink-400 hover:bg-ink-800 hover:text-ink-100"
                  )}
                >
                  <item.icon className="h-4 w-4 shrink-0" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </nav>

      {/* User Section */}
      <div className="border-t border-ink-800 p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-ink-700 text-xs font-medium text-ink-200">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-ink-100">
              {user?.display_name || "Loading..."}
            </p>
            <p className="truncate text-xs text-ink-500">
              {user?.role || ""}
            </p>
          </div>
          <button
            className="shrink-0 rounded-[3px] p-1.5 text-ink-500 transition-colors hover:bg-ink-800 hover:text-ink-300"
            title="Sign out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
