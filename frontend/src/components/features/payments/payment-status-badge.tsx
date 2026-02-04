"use client";

import { Badge } from "@/components/ui/badge";
import type { PaymentStatus } from "@/types";

const statusConfig: Record<
  PaymentStatus,
  { label: string; className: string }
> = {
  pending: {
    label: "Pending",
    className: "bg-ink-100 text-ink-600 border-ink-200",
  },
  escrow_held: {
    label: "In Escrow",
    className: "bg-blue-50 text-blue-700 border-blue-200",
  },
  release_triggered: {
    label: "Release Triggered",
    className: "bg-yellow-50 text-yellow-700 border-yellow-200",
  },
  processing: {
    label: "Processing",
    className: "bg-yellow-50 text-yellow-700 border-yellow-200",
  },
  completed: {
    label: "Completed",
    className: "bg-green-50 text-green-700 border-green-200",
  },
  failed: {
    label: "Failed",
    className: "bg-red-50 text-red-700 border-red-200",
  },
  refunded: {
    label: "Refunded",
    className: "bg-orange-50 text-orange-700 border-orange-200",
  },
};

interface PaymentStatusBadgeProps {
  status: PaymentStatus;
}

export function PaymentStatusBadge({ status }: PaymentStatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <Badge
      variant="outline"
      className={`text-xs font-medium ${config.className}`}
    >
      {config.label}
    </Badge>
  );
}
