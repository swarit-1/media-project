"use client";

import { CalendarClock, DollarSign, Send, Users } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { PitchWindow } from "@/types";

interface OpportunityCardProps {
  window: PitchWindow;
  onSubmitPitch?: (windowId: string) => void;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatBudget(min?: number, max?: number): string {
  if (min != null && max != null) return `$${min} - $${max}`;
  if (min != null) return `From $${min}`;
  if (max != null) return `Up to $${max}`;
  return "Rate negotiable";
}

function formatRateType(type: string): string {
  const map: Record<string, string> = {
    per_word: "Per Word",
    flat_rate: "Flat Rate",
    hourly: "Hourly",
  };
  return map[type] || type;
}

function formatClosesAt(iso: string): string {
  const closes = new Date(iso);
  const now = new Date();
  const diffMs = closes.getTime() - now.getTime();

  // Already closed
  if (diffMs <= 0) {
    return "Closed";
  }

  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    if (diffHours === 0) {
      return "Closes in < 1 hour";
    }
    return `Closes in ${diffHours}h`;
  }

  if (diffDays <= 7) {
    return `Closes in ${diffDays}d`;
  }

  return closes.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trimEnd() + "...";
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function OpportunityCard({ window: pw, onSubmitPitch }: OpportunityCardProps) {
  const pitchesRemaining = pw.max_pitches - pw.current_pitch_count;
  const isFull = pitchesRemaining <= 0;
  const closesLabel = formatClosesAt(pw.closes_at);
  const isClosed = closesLabel === "Closed";

  return (
    <div className="rounded-[5px] border border-ink-200 bg-white p-5">
      {/* Title */}
      <h3 className="text-sm font-semibold text-ink-950">{pw.title}</h3>

      {/* Description */}
      <p className="mt-2 text-xs leading-relaxed text-ink-600">
        {truncateText(pw.description, 150)}
      </p>

      {/* Beats */}
      {pw.beats.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {pw.beats.map((beat) => (
            <Badge
              key={beat}
              variant="secondary"
              className="rounded-[3px] px-2 py-0.5 text-xs font-normal"
            >
              {beat}
            </Badge>
          ))}
        </div>
      )}

      {/* Meta row */}
      <div className="mt-4 grid grid-cols-2 gap-3">
        {/* Budget */}
        <div className="flex items-center gap-1.5">
          <DollarSign className="h-3.5 w-3.5 text-ink-400" />
          <div>
            <p className="text-xs text-ink-500">Budget</p>
            <p className="text-sm font-medium text-ink-900">
              {formatBudget(pw.budget_min, pw.budget_max)}
            </p>
          </div>
        </div>

        {/* Rate type */}
        <div className="flex items-center gap-1.5">
          <DollarSign className="h-3.5 w-3.5 text-ink-400" />
          <div>
            <p className="text-xs text-ink-500">Rate Type</p>
            <p className="text-sm font-medium text-ink-900">
              {formatRateType(pw.rate_type)}
            </p>
          </div>
        </div>

        {/* Pitches remaining */}
        <div className="flex items-center gap-1.5">
          <Users className="h-3.5 w-3.5 text-ink-400" />
          <div>
            <p className="text-xs text-ink-500">Pitches Remaining</p>
            <p
              className={`text-sm font-medium ${
                isFull ? "text-red-600" : "text-ink-900"
              }`}
            >
              {isFull
                ? "Full"
                : `${pitchesRemaining} of ${pw.max_pitches}`}
            </p>
          </div>
        </div>

        {/* Deadline */}
        <div className="flex items-center gap-1.5">
          <CalendarClock className="h-3.5 w-3.5 text-ink-400" />
          <div>
            <p className="text-xs text-ink-500">Deadline</p>
            <p
              className={`text-sm font-medium ${
                isClosed ? "text-red-600" : "text-ink-900"
              }`}
            >
              {closesLabel}
            </p>
          </div>
        </div>
      </div>

      {/* Submit Pitch button */}
      <div className="mt-5">
        <button
          onClick={() => onSubmitPitch?.(pw.id)}
          disabled={isFull || isClosed}
          className="inline-flex h-9 w-full items-center justify-center gap-1.5 rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Send className="h-4 w-4" />
          Submit Pitch
        </button>
      </div>
    </div>
  );
}
