"use client";

import { Search } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const BEAT_OPTIONS = [
  "Politics",
  "Business",
  "Technology",
  "Science",
  "Health",
  "Environment",
  "Culture",
  "Sports",
  "Education",
  "International",
  "Investigative",
  "Opinion",
];

const AVAILABILITY_OPTIONS = [
  { value: "all", label: "All" },
  { value: "available", label: "Available" },
  { value: "busy", label: "Busy" },
  { value: "unavailable", label: "Unavailable" },
];

const SORT_OPTIONS = [
  { value: "relevance", label: "Relevance" },
  { value: "trust_score", label: "Trust Score" },
  { value: "quality_score", label: "Quality Score" },
  { value: "rate_low", label: "Rate: Low to High" },
  { value: "rate_high", label: "Rate: High to Low" },
];

interface SearchFiltersProps {
  query: string;
  onQueryChange: (query: string) => void;
  beat: string;
  onBeatChange: (beat: string) => void;
  availability: string;
  onAvailabilityChange: (availability: string) => void;
  sortBy: string;
  onSortChange: (sort: string) => void;
}

export function SearchFilters({
  query,
  onQueryChange,
  beat,
  onBeatChange,
  availability,
  onAvailabilityChange,
  sortBy,
  onSortChange,
}: SearchFiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="relative flex-1 min-w-[240px]">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-400" />
        <input
          type="text"
          placeholder="Search freelancers by name, beat, or location..."
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          className="h-9 w-full rounded-[3px] border border-ink-200 bg-white pl-9 pr-3 text-sm text-ink-950 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
        />
      </div>

      <Select value={beat} onValueChange={onBeatChange}>
        <SelectTrigger className="h-9 w-[160px] rounded-[3px] border-ink-200 text-sm">
          <SelectValue placeholder="All Beats" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Beats</SelectItem>
          {BEAT_OPTIONS.map((b) => (
            <SelectItem key={b} value={b.toLowerCase()}>
              {b}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={availability} onValueChange={onAvailabilityChange}>
        <SelectTrigger className="h-9 w-[150px] rounded-[3px] border-ink-200 text-sm">
          <SelectValue placeholder="Availability" />
        </SelectTrigger>
        <SelectContent>
          {AVAILABILITY_OPTIONS.map((opt) => (
            <SelectItem key={opt.value} value={opt.value}>
              {opt.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={sortBy} onValueChange={onSortChange}>
        <SelectTrigger className="h-9 w-[170px] rounded-[3px] border-ink-200 text-sm">
          <SelectValue placeholder="Sort by" />
        </SelectTrigger>
        <SelectContent>
          {SORT_OPTIONS.map((opt) => (
            <SelectItem key={opt.value} value={opt.value}>
              {opt.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
