"use client";

import { MapPin, ShieldCheck, FolderCheck, CircleDot } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { FreelancerProfile } from "@/types";

interface FreelancerCardProps {
  freelancer: FreelancerProfile;
  onViewProfile?: (id: string) => void;
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-2">
      <span className="w-[72px] text-xs text-ink-500">{label}</span>
      <div className="h-1.5 flex-1 rounded-full bg-ink-100">
        <div
          className="h-1.5 rounded-full bg-accent-600"
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
      <span className="w-7 text-right text-xs font-medium text-ink-700">
        {value}
      </span>
    </div>
  );
}

function AvailabilityIndicator({ status }: { status: string }) {
  const colorMap: Record<string, string> = {
    available: "text-success-600",
    busy: "text-warning-500",
    unavailable: "text-ink-400",
  };
  const labelMap: Record<string, string> = {
    available: "Available",
    busy: "Busy",
    unavailable: "Unavailable",
  };
  const color = colorMap[status] || "text-ink-400";
  const label = labelMap[status] || status;

  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium ${color}`}>
      <CircleDot className="h-3 w-3" />
      {label}
    </span>
  );
}

function formatRate(freelancer: FreelancerProfile): string | null {
  if (freelancer.per_word_rate) {
    return `$${freelancer.per_word_rate.toFixed(2)}/word`;
  }
  if (freelancer.hourly_rate_min && freelancer.hourly_rate_max) {
    return `$${freelancer.hourly_rate_min}–$${freelancer.hourly_rate_max}/hr`;
  }
  if (freelancer.hourly_rate_min) {
    return `From $${freelancer.hourly_rate_min}/hr`;
  }
  return null;
}

function formatLocation(freelancer: FreelancerProfile): string {
  const parts = [freelancer.home_city, freelancer.home_country].filter(Boolean);
  return parts.join(", ");
}

export function FreelancerCard({ freelancer, onViewProfile }: FreelancerCardProps) {
  const location = formatLocation(freelancer);
  const rate = formatRate(freelancer);
  const truncatedBio =
    freelancer.bio && freelancer.bio.length > 120
      ? freelancer.bio.slice(0, 120) + "..."
      : freelancer.bio;

  return (
    <div className="rounded-[5px] border border-ink-200 bg-white p-5">
      <div className="flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h3 className="truncate text-sm font-semibold text-ink-950">
              {freelancer.display_name}
            </h3>
            {freelancer.identity_verified && (
              <ShieldCheck className="h-3.5 w-3.5 shrink-0 text-accent-600" />
            )}
            {freelancer.portfolio_verified && (
              <FolderCheck className="h-3.5 w-3.5 shrink-0 text-accent-600" />
            )}
          </div>
          {location && (
            <p className="mt-0.5 flex items-center gap-1 text-xs text-ink-500">
              <MapPin className="h-3 w-3" />
              {location}
            </p>
          )}
        </div>
        <AvailabilityIndicator status={freelancer.availability_status} />
      </div>

      {truncatedBio && (
        <p className="mt-3 text-xs leading-relaxed text-ink-600">{truncatedBio}</p>
      )}

      {freelancer.primary_beats.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {freelancer.primary_beats.map((beat) => (
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

      <div className="mt-4 space-y-1.5">
        <ScoreBar label="Trust" value={freelancer.trust_score} />
        <ScoreBar label="Quality" value={freelancer.quality_score} />
        <ScoreBar label="Reliability" value={freelancer.reliability_score} />
      </div>

      <div className="mt-4 flex items-center justify-between">
        {rate ? (
          <span className="text-xs font-medium text-ink-700">{rate}</span>
        ) : (
          <span className="text-xs text-ink-400">Rate not set</span>
        )}
        <button
          onClick={() => onViewProfile?.(freelancer.id)}
          className="rounded-[3px] bg-ink-950 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-ink-800"
        >
          View Profile
        </button>
      </div>
    </div>
  );
}
