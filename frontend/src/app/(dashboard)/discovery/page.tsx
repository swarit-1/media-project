"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Header } from "@/components/layouts/header";
import { PageWrapper } from "@/components/layouts/page-wrapper";
import { SearchFilters } from "@/components/features/discovery/search-filters";
import { FreelancerCard } from "@/components/features/discovery/freelancer-card";
import type { FreelancerProfile } from "@/types";

// Mock data for initial development
const MOCK_FREELANCERS: FreelancerProfile[] = [
  {
    id: "f1",
    user_id: "u1",
    display_name: "Sarah Chen",
    bio: "Award-winning investigative journalist specializing in technology policy and corporate accountability. Former staff writer at a major national daily.",
    home_city: "San Francisco",
    home_state: "CA",
    home_country: "USA",
    primary_beats: ["Technology", "Investigative"],
    secondary_beats: ["Business"],
    languages: ["English", "Mandarin"],
    availability_status: "available",
    per_word_rate: 0.75,
    hourly_rate_min: undefined,
    hourly_rate_max: undefined,
    identity_verified: true,
    portfolio_verified: true,
    trust_score: 95,
    quality_score: 92,
    reliability_score: 88,
  },
  {
    id: "f2",
    user_id: "u2",
    display_name: "Marcus Williams",
    bio: "Political correspondent covering local and state government, elections, and public policy. Deep sourcing across the political spectrum.",
    home_city: "Washington",
    home_state: "DC",
    home_country: "USA",
    primary_beats: ["Politics", "International"],
    secondary_beats: ["Opinion"],
    languages: ["English", "Spanish"],
    availability_status: "available",
    per_word_rate: 0.60,
    hourly_rate_min: undefined,
    hourly_rate_max: undefined,
    identity_verified: true,
    portfolio_verified: false,
    trust_score: 88,
    quality_score: 90,
    reliability_score: 94,
  },
  {
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
  {
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
    per_word_rate: 0.50,
    hourly_rate_min: undefined,
    hourly_rate_max: undefined,
    identity_verified: false,
    portfolio_verified: true,
    trust_score: 82,
    quality_score: 86,
    reliability_score: 90,
  },
  {
    id: "f5",
    user_id: "u5",
    display_name: "Amira Hassan",
    bio: "International affairs correspondent with extensive on-the-ground reporting from the Middle East and North Africa. Fluent in Arabic and French.",
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
  {
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
    per_word_rate: 0.70,
    hourly_rate_min: undefined,
    hourly_rate_max: undefined,
    identity_verified: true,
    portfolio_verified: false,
    trust_score: 85,
    quality_score: 88,
    reliability_score: 79,
  },
];

const PER_PAGE = 6;

export default function DiscoveryPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [beat, setBeat] = useState("all");
  const [availability, setAvailability] = useState("all");
  const [sortBy, setSortBy] = useState("relevance");
  const [page, setPage] = useState(1);

  // Filter and sort the mock data
  const filtered = useMemo(() => {
    let results = [...MOCK_FREELANCERS];

    // Text search
    if (query.trim()) {
      const q = query.toLowerCase();
      results = results.filter(
        (f) =>
          f.display_name.toLowerCase().includes(q) ||
          f.bio.toLowerCase().includes(q) ||
          f.primary_beats.some((b) => b.toLowerCase().includes(q)) ||
          f.home_city.toLowerCase().includes(q) ||
          f.home_country.toLowerCase().includes(q)
      );
    }

    // Beat filter
    if (beat !== "all") {
      results = results.filter((f) =>
        f.primary_beats.some((b) => b.toLowerCase() === beat)
      );
    }

    // Availability filter
    if (availability !== "all") {
      results = results.filter((f) => f.availability_status === availability);
    }

    // Sort
    switch (sortBy) {
      case "trust_score":
        results.sort((a, b) => b.trust_score - a.trust_score);
        break;
      case "quality_score":
        results.sort((a, b) => b.quality_score - a.quality_score);
        break;
      case "rate_low":
        results.sort(
          (a, b) => (a.per_word_rate ?? Infinity) - (b.per_word_rate ?? Infinity)
        );
        break;
      case "rate_high":
        results.sort(
          (a, b) => (b.per_word_rate ?? 0) - (a.per_word_rate ?? 0)
        );
        break;
      default:
        // relevance — keep original order
        break;
    }

    return results;
  }, [query, beat, availability, sortBy]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PER_PAGE));
  const currentPage = Math.min(page, totalPages);
  const paginated = filtered.slice(
    (currentPage - 1) * PER_PAGE,
    currentPage * PER_PAGE
  );

  function handleViewProfile(id: string) {
    router.push(`/discovery/${id}`);
  }

  return (
    <>
      <Header title="Discovery" subtitle="Find freelance journalists" />
      <PageWrapper>
        {/* Search & Filters */}
        <div className="rounded-[5px] border border-ink-200 bg-white p-4">
          <SearchFilters
            query={query}
            onQueryChange={(q) => {
              setQuery(q);
              setPage(1);
            }}
            beat={beat}
            onBeatChange={(b) => {
              setBeat(b);
              setPage(1);
            }}
            availability={availability}
            onAvailabilityChange={(a) => {
              setAvailability(a);
              setPage(1);
            }}
            sortBy={sortBy}
            onSortChange={setSortBy}
          />
        </div>

        {/* Results summary */}
        <div className="mt-4 flex items-center justify-between">
          <p className="text-sm text-ink-500">
            {filtered.length} freelancer{filtered.length !== 1 ? "s" : ""} found
          </p>
        </div>

        {/* Results grid */}
        {paginated.length > 0 ? (
          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {paginated.map((freelancer) => (
              <FreelancerCard
                key={freelancer.id}
                freelancer={freelancer}
                onViewProfile={handleViewProfile}
              />
            ))}
          </div>
        ) : (
          <div className="mt-8 flex flex-col items-center justify-center rounded-[5px] border border-ink-200 bg-white py-16">
            <p className="text-sm font-medium text-ink-700">No freelancers found</p>
            <p className="mt-1 text-xs text-ink-400">
              Try adjusting your search or filters
            </p>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-6 flex items-center justify-center gap-1">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="flex h-8 w-8 items-center justify-center rounded-[3px] border border-ink-200 text-ink-600 transition-colors hover:bg-ink-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
              <button
                key={p}
                onClick={() => setPage(p)}
                className={`flex h-8 w-8 items-center justify-center rounded-[3px] text-sm font-medium transition-colors ${
                  p === currentPage
                    ? "bg-ink-950 text-white"
                    : "border border-ink-200 text-ink-600 hover:bg-ink-50"
                }`}
              >
                {p}
              </button>
            ))}
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="flex h-8 w-8 items-center justify-center rounded-[3px] border border-ink-200 text-ink-600 transition-colors hover:bg-ink-50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        )}
      </PageWrapper>
    </>
  );
}
