"use client";

import {
  MapPin,
  ShieldCheck,
  FolderCheck,
  CircleDot,
  Pencil,
  Globe,
  DollarSign,
  Clock,
  Plus,
  FileText,
} from "lucide-react";
import { Header } from "@/components/layouts/header";
import { PageWrapper } from "@/components/layouts/page-wrapper";
import { Badge } from "@/components/ui/badge";
import type { FreelancerProfile } from "@/types";

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

const MOCK_PROFILE: FreelancerProfile = {
  id: "f1",
  user_id: "u1",
  display_name: "Sarah Chen",
  bio: "Award-winning investigative journalist specializing in technology policy and corporate accountability. Former staff writer at a major national daily with over a decade of experience covering Silicon Valley, data privacy, and the intersection of technology and civil liberties.",
  home_city: "San Francisco",
  home_state: "CA",
  home_country: "USA",
  primary_beats: ["Technology", "Investigative"],
  secondary_beats: ["Business", "Policy"],
  languages: ["English", "Mandarin"],
  availability_status: "available",
  per_word_rate: 0.75,
  hourly_rate_min: 90,
  hourly_rate_max: 150,
  identity_verified: true,
  portfolio_verified: true,
  trust_score: 95,
  quality_score: 92,
  reliability_score: 88,
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

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
  const dotColorMap: Record<string, string> = {
    available: "bg-success-600",
    busy: "bg-warning-500",
    unavailable: "bg-ink-400",
  };
  const color = colorMap[status] || "text-ink-400";
  const label = labelMap[status] || status;
  const dotColor = dotColorMap[status] || "bg-ink-400";

  return (
    <span
      className={`inline-flex items-center gap-1.5 text-sm font-medium ${color}`}
    >
      <span className={`h-2 w-2 rounded-full ${dotColor}`} />
      {label}
    </span>
  );
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-3">
      <span className="w-20 text-sm text-ink-600">{label}</span>
      <div className="h-2 flex-1 rounded-full bg-ink-100">
        <div
          className="h-2 rounded-full bg-accent-600 transition-all"
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
      <span className="w-8 text-right text-sm font-semibold text-ink-900">
        {value}
      </span>
    </div>
  );
}

function formatLocation(profile: FreelancerProfile): string {
  const parts = [profile.home_city, profile.home_state, profile.home_country].filter(
    Boolean
  );
  return parts.join(", ");
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function PortfolioPage() {
  const profile = MOCK_PROFILE;
  const location = formatLocation(profile);

  return (
    <>
      <Header
        title="Portfolio"
        actions={
          <button className="inline-flex h-9 items-center gap-1.5 rounded-[3px] border border-ink-200 bg-white px-4 text-sm font-medium text-ink-700 transition-colors hover:bg-ink-50">
            <Pencil className="h-4 w-4" />
            Edit Profile
          </button>
        }
      />
      <PageWrapper>
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          {/* ---- Left Column: Profile & Rates ---- */}
          <div className="space-y-6 xl:col-span-2">
            {/* Profile Card */}
            <div className="rounded-[5px] border border-ink-200 bg-white p-5">
              <div className="flex items-start justify-between">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <h2 className="text-lg font-semibold text-ink-950">
                      {profile.display_name}
                    </h2>
                    <AvailabilityIndicator status={profile.availability_status} />
                  </div>

                  {location && (
                    <p className="mt-1 flex items-center gap-1.5 text-sm text-ink-500">
                      <MapPin className="h-3.5 w-3.5" />
                      {location}
                    </p>
                  )}
                </div>
              </div>

              {/* Bio */}
              <p className="mt-4 text-sm leading-relaxed text-ink-600">
                {profile.bio}
              </p>

              {/* Primary Beats */}
              <div className="mt-5">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-ink-400">
                  Primary Beats
                </h3>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {profile.primary_beats.map((beat) => (
                    <Badge
                      key={beat}
                      variant="secondary"
                      className="rounded-[3px] px-2 py-0.5 text-xs font-normal"
                    >
                      {beat}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Secondary Beats */}
              {profile.secondary_beats.length > 0 && (
                <div className="mt-4">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-ink-400">
                    Secondary Beats
                  </h3>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {profile.secondary_beats.map((beat) => (
                      <Badge
                        key={beat}
                        variant="outline"
                        className="rounded-[3px] px-2 py-0.5 text-xs font-normal"
                      >
                        {beat}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Languages */}
              {profile.languages.length > 0 && (
                <div className="mt-4">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-ink-400">
                    Languages
                  </h3>
                  <div className="mt-2 flex items-center gap-1.5">
                    <Globe className="h-3.5 w-3.5 text-ink-400" />
                    <span className="text-sm text-ink-700">
                      {profile.languages.join(", ")}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Rates Card */}
            <div className="rounded-[5px] border border-ink-200 bg-white p-5">
              <h3 className="text-sm font-semibold text-ink-950">Rates</h3>
              <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                {profile.per_word_rate != null && (
                  <div className="flex items-center gap-3 rounded-[5px] border border-ink-100 bg-ink-50 p-4">
                    <DollarSign className="h-5 w-5 text-ink-400" />
                    <div>
                      <p className="text-xs text-ink-500">Per-Word Rate</p>
                      <p className="text-lg font-semibold text-ink-950">
                        ${profile.per_word_rate.toFixed(2)}
                      </p>
                    </div>
                  </div>
                )}
                {profile.hourly_rate_min != null &&
                  profile.hourly_rate_max != null && (
                    <div className="flex items-center gap-3 rounded-[5px] border border-ink-100 bg-ink-50 p-4">
                      <Clock className="h-5 w-5 text-ink-400" />
                      <div>
                        <p className="text-xs text-ink-500">Hourly Range</p>
                        <p className="text-lg font-semibold text-ink-950">
                          ${profile.hourly_rate_min} - ${profile.hourly_rate_max}
                        </p>
                      </div>
                    </div>
                  )}
              </div>
            </div>

            {/* Portfolio Items */}
            <div className="rounded-[5px] border border-ink-200 bg-white p-5">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-ink-950">
                  Work Samples
                </h3>
                <button className="inline-flex h-9 items-center gap-1.5 rounded-[3px] border border-ink-200 bg-white px-3 text-sm font-medium text-ink-700 transition-colors hover:bg-ink-50">
                  <Plus className="h-4 w-4" />
                  Add Sample
                </button>
              </div>
              {/* Empty state */}
              <div className="mt-6 flex flex-col items-center justify-center rounded-[5px] border border-dashed border-ink-200 py-12">
                <FileText className="h-8 w-8 text-ink-300" />
                <p className="mt-3 text-sm font-medium text-ink-700">
                  No work samples yet
                </p>
                <p className="mt-1 text-xs text-ink-400">
                  Add published articles, clips, or other writing samples to
                  showcase your work.
                </p>
                <button className="mt-4 inline-flex h-9 items-center gap-1.5 rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800">
                  <Plus className="h-4 w-4" />
                  Add Work Samples
                </button>
              </div>
            </div>
          </div>

          {/* ---- Right Column: Scores & Verification ---- */}
          <div className="space-y-6">
            {/* Scores Card */}
            <div className="rounded-[5px] border border-ink-200 bg-white p-5">
              <h3 className="text-sm font-semibold text-ink-950">Scores</h3>
              <div className="mt-4 space-y-3">
                <ScoreBar label="Trust" value={profile.trust_score} />
                <ScoreBar label="Quality" value={profile.quality_score} />
                <ScoreBar label="Reliability" value={profile.reliability_score} />
              </div>
            </div>

            {/* Verification Card */}
            <div className="rounded-[5px] border border-ink-200 bg-white p-5">
              <h3 className="text-sm font-semibold text-ink-950">Verification</h3>
              <div className="mt-4 space-y-3">
                <div className="flex items-center gap-3">
                  <ShieldCheck
                    className={`h-5 w-5 ${
                      profile.identity_verified
                        ? "text-accent-600"
                        : "text-ink-300"
                    }`}
                  />
                  <div>
                    <p className="text-sm font-medium text-ink-900">
                      Identity Verified
                    </p>
                    <p className="text-xs text-ink-500">
                      {profile.identity_verified
                        ? "Your identity has been confirmed"
                        : "Complete identity verification to build trust"}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <FolderCheck
                    className={`h-5 w-5 ${
                      profile.portfolio_verified
                        ? "text-accent-600"
                        : "text-ink-300"
                    }`}
                  />
                  <div>
                    <p className="text-sm font-medium text-ink-900">
                      Portfolio Verified
                    </p>
                    <p className="text-xs text-ink-500">
                      {profile.portfolio_verified
                        ? "Your portfolio has been reviewed and verified"
                        : "Submit work samples for portfolio verification"}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </PageWrapper>
    </>
  );
}
