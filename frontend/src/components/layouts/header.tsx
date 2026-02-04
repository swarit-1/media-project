"use client";

import { Bell, Search } from "lucide-react";

interface HeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export function Header({ title, subtitle, actions }: HeaderProps) {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-ink-200 bg-white px-8">
      <div>
        <h1 className="text-[22px] font-semibold text-ink-950 leading-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="mt-0.5 text-sm text-ink-500">{subtitle}</p>
        )}
      </div>
      <div className="flex items-center gap-2">
        {actions}
        <button className="flex h-9 w-9 items-center justify-center rounded-[3px] text-ink-500 transition-colors hover:bg-ink-100 hover:text-ink-700">
          <Search className="h-4 w-4" />
        </button>
        <button className="relative flex h-9 w-9 items-center justify-center rounded-[3px] text-ink-500 transition-colors hover:bg-ink-100 hover:text-ink-700">
          <Bell className="h-4 w-4" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-accent-600" />
        </button>
      </div>
    </header>
  );
}
