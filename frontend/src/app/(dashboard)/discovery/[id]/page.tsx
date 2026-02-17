"use client";

import Link from "next/link";
import {
  ArrowLeft,
  MapPin,
  ShieldCheck,
  FolderCheck,
  Globe,
  DollarSign,
  Clock,
  CircleDot,
} from "lucide-react";
import { Header } from "@/components/layouts/header";
import { PageWrapper } from "@/components/layouts/page-wrapper";
import { Badge } from "@/components/ui/badge";
import type { FreelancerProfile } from "@/types";

// Mock data — in a real app this would be fetched by ID
const MOCK_FREELANCERS: Record<string, FreelancerProfile> = {
  f1: {
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
  },
  f2: {
    id: "f2",
    user_id: "u2",
    display_name: "Marcus Williams",
    bio: "Political correspondent covering local and state government, elections, and public policy. Deep sourcing across the political spectrum with years of experience in legislative reporting.",
    home_city: "Washington",
    home_state: "DC",
    home_country: "USA",
    primary_beats: ["Politics", "International"],
    secondary_beats: ["Opinion"],
    languages: ["English", "Spanish"],
    availability_status: "available",
    per_word_rate: 0.6,
    hourly_rate_min: undefined,
    hourly_rate_max: undefined,
    identity_verified: true,
    portfolio_verified: false,
    trust_score: 88,
    quality_score: 90,
    reliability_score: 94,
  },
  f3: {
    id: "f3",
    user_id: "u3",
    display_name: "Priya Patel",
    bio: "Health and science reporter with expertise in epidemiology, clinical research, and public health policy. Published in leading medical and general-interest outlets.",
    home_city: "London",
    home_state: "",
    home_country: "UK",
    primary_beats: ["Health", "Science"],
    secondary_beats: ["Environment"],
    languages: ["English", "Hindi", "Gujarati"],
    availability_status: "busy",
    per_word_rate: undefined,
    hourly_rate_min: 80,
    hourly_rate_max: 120,
    identity_verified: true,
    portfolio_verified: true,
    trust_score: 91,
    quality_score: 94,
    reliability_score: 85,
  },
  f4: {
    id: "f4",
    user_id: "u4",
    display_name: "James O'Sullivan",
    bio: "Sports journalist covering professional football and basketball with a data-driven approach. Experienced in longform features and deadline game coverage.",
    home_city: "Chicago",
    home_state: "IL",
    home_country: "USA",
    primary_beats: ["Sports"],
    secondary_beats: ["Culture"],
    languages: ["English"],
    availability_status: "available",
    per_word_rate: 0.5,
    hourly_rate_min: undefined,
    hourly_rate_max: undefined,
    identity_verified: false,
    portfolio_verified: true,
    trust_score: 82,
    quality_score: 86,
    reliability_score: 90,
  },
  f5: {
    id: "f5",
    user_id: "u5",
    display_name: "Amira Hassan",
    bio: "International affairs correspondent with extensive on-the-ground reporting from the Middle East and North Africa. Fluent in Arabic and French with a focus on conflict reporting and humanitarian stories.",
    home_city: "Beirut",
    home_state: "",
    home_country: "Lebanon",
    primary_beats: ["International", "Politics"],
    secondary_beats: ["Investigative"],
    languages: ["English", "Arabic", "French"],
    availability_status: "available",
    per_word_rate: 0.85,
    hourly_rate_min: undefined,
    hourly_rate_max: undefined,
    identity_verified: true,
    portfolio_verified: true,
    trust_score: 97,
    quality_score: 96,
    reliability_score: 93,
  },
  f6: {
    id: "f6",
    user_id: "u6",
    display_name: "David Kim",
    bio: "Business and finance reporter tracking markets, startups, and venture capital. Previously covered Wall Street for a top financial publication.",
    home_city: "New York",
    home_state: "NY",
    home_country: "USA",
    primary_beats: ["Business", "Technology"],
    secondary_beats: ["Politics"],
    languages: ["English", "Korean"],
    availability_status: "unavailable",
    per_word_rate: 0.7,
    hourly_rate_min: undefined,
    hourly_rate_max: undefined,
    identity_verified: true,
    portfolio_verified: false,
    trust_score: 85,
    quality_score: 88,
    reliability_score: 79,
  },
};

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

  return (
    <span
      className={`inline-flex items-center gap-1.5 text-sm font-medium ${colorMap[status] || "text-ink-400"}`}
    >
      <span className={`h-2 w-2 rounded-full ${dotColorMap[status] || "bg-ink-400"}`} />
      {labelMap[status] || status}
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

export default function FreelancerProfilePage({
  params,
}: {
  params: { id: string };
}) {
  const profile = MOCK_FREELANCERS[params.id];

  if (!profile) {
    return (
      <>
        <Header title="Freelancer Profile" />
        <PageWrapper>
          <Link
            href="/discovery"
            className="mb-4 inline-flex items-center gap-1 text-sm text-ink-500 transition-colors hover:text-ink-700"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to Discovery
          </Link>
          <div className="rounded-[5px] border border-ink-200 bg-white p-10 text-center">
            <p className="text-sm font-medium text-ink-700">
              Freelancer not found
            </p>
            <p className="mt-1 text-xs text-ink-400">
              This profile may no longer be available.
            </p>
          </div>
        </PageWrapper>
      </>
    );
  }

  const location = formatLocation(profile);

  return (
    <>
      <Header title={profile.display_name} />
      <PageWrapper>
        <Link
          href="/discovery"
          className="mb-4 inline-flex items-center gap-1 text-sm text-ink-500 transition-colors hover:text-ink-700"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to Discovery
        </Link>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          {/* Left Column: Profile & Rates */}
          <div className="space-y-6 xl:col-span-2">
            {/* Profile Card */}
            <div className="rounded-[5px] border border-ink-200 bg-white p-5">
              <div className="flex items-start justify-between">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <h2 className="text-lg font-semibold text-ink-950">
                      {profile.display_name}
                    </h2>
                    {profile.identity_verified && (
                      <ShieldCheck className="h-4 w-4 text-accent-600" />
                    )}
                    {profile.portfolio_verified && (
                      <FolderCheck className="h-4 w-4 text-accent-600" />
                    )}
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

              <p className="mt-4 text-sm leading-relaxed text-ink-600">
                {profile.bio}
              </p>

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
          </div>

          {/* Right Column: Scores & Verification */}
          <div className="space-y-6">
            <div className="rounded-[5px] border border-ink-200 bg-white p-5">
              <h3 className="text-sm font-semibold text-ink-950">Scores</h3>
              <div className="mt-4 space-y-3">
                <ScoreBar label="Trust" value={profile.trust_score} />
                <ScoreBar label="Quality" value={profile.quality_score} />
                <ScoreBar label="Reliability" value={profile.reliability_score} />
              </div>
            </div>

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
                        ? "Identity has been confirmed"
                        : "Identity not yet verified"}
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
                        ? "Portfolio has been reviewed and verified"
                        : "Portfolio not yet verified"}
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
