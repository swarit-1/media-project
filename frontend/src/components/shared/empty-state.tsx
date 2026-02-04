"use client";

import { FileX, Search, Inbox, CreditCard, Users, FolderOpen } from "lucide-react";

const icons = {
  default: FileX,
  search: Search,
  inbox: Inbox,
  payments: CreditCard,
  squads: Users,
  portfolio: FolderOpen,
};

interface EmptyStateProps {
  icon?: keyof typeof icons;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon = "default", title, description, action }: EmptyStateProps) {
  const Icon = icons[icon];

  return (
    <div className="flex flex-col items-center justify-center rounded-[5px] border border-ink-200 bg-white py-16 px-8">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-ink-100">
        <Icon className="h-5 w-5 text-ink-400" />
      </div>
      <h3 className="mt-4 text-sm font-semibold text-ink-900">{title}</h3>
      {description && (
        <p className="mt-1 max-w-sm text-center text-xs text-ink-500">
          {description}
        </p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
