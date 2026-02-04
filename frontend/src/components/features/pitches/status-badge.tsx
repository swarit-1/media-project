"use client";

import { Badge } from "@/components/ui/badge";
import type { PitchWindowStatus, PitchStatus } from "@/types";

const pitchWindowStatusConfig: Record<
  PitchWindowStatus,
  { label: string; className: string }
> = {
  open: {
    label: "Open",
    className: "bg-emerald-50 text-emerald-700 border-emerald-200",
  },
  draft: {
    label: "Draft",
    className: "bg-ink-50 text-ink-600 border-ink-200",
  },
  closed: {
    label: "Closed",
    className: "bg-amber-50 text-amber-700 border-amber-200",
  },
  cancelled: {
    label: "Cancelled",
    className: "bg-red-50 text-red-700 border-red-200",
  },
};

const pitchStatusConfig: Record<
  PitchStatus,
  { label: string; className: string }
> = {
  draft: {
    label: "Draft",
    className: "bg-ink-50 text-ink-600 border-ink-200",
  },
  submitted: {
    label: "Submitted",
    className: "bg-blue-50 text-blue-700 border-blue-200",
  },
  under_review: {
    label: "Under Review",
    className: "bg-amber-50 text-amber-700 border-amber-200",
  },
  accepted: {
    label: "Accepted",
    className: "bg-emerald-50 text-emerald-700 border-emerald-200",
  },
  rejected: {
    label: "Rejected",
    className: "bg-red-50 text-red-700 border-red-200",
  },
  withdrawn: {
    label: "Withdrawn",
    className: "bg-ink-50 text-ink-500 border-ink-200",
  },
};

interface PitchWindowStatusBadgeProps {
  status: PitchWindowStatus;
}

export function PitchWindowStatusBadge({ status }: PitchWindowStatusBadgeProps) {
  const config = pitchWindowStatusConfig[status];
  return (
    <Badge variant="outline" className={config.className}>
      {config.label}
    </Badge>
  );
}

interface PitchStatusBadgeProps {
  status: PitchStatus;
}

export function PitchStatusBadge({ status }: PitchStatusBadgeProps) {
  const config = pitchStatusConfig[status];
  return (
    <Badge variant="outline" className={config.className}>
      {config.label}
    </Badge>
  );
}
