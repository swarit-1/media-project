"use client";

import { Badge } from "@/components/ui/badge";
import type { AssignmentStatus } from "@/types";

const statusConfig: Record<
  AssignmentStatus,
  { label: string; className: string }
> = {
  assigned: {
    label: "Assigned",
    className: "bg-blue-50 text-blue-700 border-blue-200",
  },
  in_progress: {
    label: "In Progress",
    className: "bg-yellow-50 text-yellow-700 border-yellow-200",
  },
  submitted: {
    label: "Submitted",
    className: "bg-purple-50 text-purple-700 border-purple-200",
  },
  revision_requested: {
    label: "Revision Requested",
    className: "bg-orange-50 text-orange-700 border-orange-200",
  },
  approved: {
    label: "Approved",
    className: "bg-green-50 text-green-700 border-green-200",
  },
  published: {
    label: "Published",
    className: "bg-green-50 text-green-700 border-green-200",
  },
  killed: {
    label: "Killed",
    className: "bg-red-50 text-red-700 border-red-200",
  },
};

interface AssignmentStatusBadgeProps {
  status: AssignmentStatus;
  className?: string;
}

export function AssignmentStatusBadge({
  status,
  className,
}: AssignmentStatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <Badge
      variant="outline"
      className={`${config.className} ${className ?? ""}`}
    >
      {config.label}
    </Badge>
  );
}
