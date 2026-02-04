"use client";

import Link from "next/link";
import { Plus } from "lucide-react";
import { Header } from "@/components/layouts/header";
import { PageWrapper } from "@/components/layouts/page-wrapper";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import { PitchWindowStatusBadge } from "@/components/features/pitches/status-badge";
import { PitchWindowForm } from "@/components/features/pitches/pitch-window-form";
import type { PitchWindow } from "@/types";

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

const mockPitchWindows: PitchWindow[] = [
  {
    id: "pw-1",
    newsroom_id: "nr-1",
    editor_id: "ed-1",
    title: "Climate & Environment Features - Spring 2026",
    description:
      "We are looking for in-depth feature pitches exploring climate policy, environmental justice, and sustainability innovations.",
    beats: ["Climate", "Environment", "Policy"],
    budget_min: 400,
    budget_max: 1200,
    rate_type: "flat_rate",
    max_pitches: 25,
    current_pitch_count: 14,
    opens_at: "2026-02-01T00:00:00Z",
    closes_at: "2026-03-15T23:59:59Z",
    status: "open",
    created_at: "2026-01-20T10:00:00Z",
  },
  {
    id: "pw-2",
    newsroom_id: "nr-1",
    editor_id: "ed-1",
    title: "Tech & AI Investigations",
    description:
      "Investigative pieces on AI governance, algorithmic bias, and Big Tech accountability.",
    beats: ["Technology", "AI", "Investigations"],
    budget_min: 600,
    budget_max: 2000,
    rate_type: "flat_rate",
    max_pitches: 15,
    current_pitch_count: 9,
    opens_at: "2026-01-15T00:00:00Z",
    closes_at: "2026-02-28T23:59:59Z",
    status: "open",
    created_at: "2026-01-10T08:30:00Z",
  },
  {
    id: "pw-3",
    newsroom_id: "nr-1",
    editor_id: "ed-2",
    title: "Health & Wellness Personal Essays",
    description:
      "First-person narratives on mental health, chronic illness, and healthcare access.",
    beats: ["Health", "Personal Essay"],
    budget_min: 200,
    budget_max: 500,
    rate_type: "flat_rate",
    max_pitches: 30,
    current_pitch_count: 30,
    opens_at: "2025-11-01T00:00:00Z",
    closes_at: "2025-12-31T23:59:59Z",
    status: "closed",
    created_at: "2025-10-20T09:00:00Z",
  },
  {
    id: "pw-4",
    newsroom_id: "nr-1",
    editor_id: "ed-1",
    title: "Summer Long-Reads: Culture & Society",
    description:
      "Seeking ambitious long-form pieces on cultural shifts, identity, and community stories.",
    beats: ["Culture", "Society", "Long-form"],
    budget_min: 800,
    budget_max: 2500,
    rate_type: "flat_rate",
    max_pitches: 10,
    current_pitch_count: 0,
    opens_at: "2026-04-01T00:00:00Z",
    closes_at: "2026-05-15T23:59:59Z",
    status: "draft",
    created_at: "2026-01-28T14:00:00Z",
  },
  {
    id: "pw-5",
    newsroom_id: "nr-1",
    editor_id: "ed-2",
    title: "Election 2025 Coverage",
    description: "Rapid-turnaround opinion and analysis pieces for election season.",
    beats: ["Politics", "Elections"],
    budget_min: 150,
    budget_max: 400,
    rate_type: "flat_rate",
    max_pitches: 40,
    current_pitch_count: 38,
    opens_at: "2025-08-01T00:00:00Z",
    closes_at: "2025-11-10T23:59:59Z",
    status: "closed",
    created_at: "2025-07-15T12:00:00Z",
  },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatBudget(min?: number, max?: number) {
  if (min != null && max != null) return `$${min} - $${max}`;
  if (min != null) return `From $${min}`;
  if (max != null) return `Up to $${max}`;
  return "-";
}

// ---------------------------------------------------------------------------
// Sub-component: window table
// ---------------------------------------------------------------------------

function PitchWindowTable({ windows }: { windows: PitchWindow[] }) {
  if (windows.length === 0) {
    return (
      <div className="rounded-[5px] border border-ink-200 bg-white p-8 text-center">
        <p className="text-sm text-ink-500">No pitch windows found.</p>
      </div>
    );
  }

  return (
    <div className="rounded-[5px] border border-ink-200 bg-white">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="pl-4">Title</TableHead>
            <TableHead>Beats</TableHead>
            <TableHead>Pitches</TableHead>
            <TableHead>Budget</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="pr-4">Closes At</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {windows.map((pw) => (
            <TableRow key={pw.id} className="group">
              <TableCell className="pl-4 font-medium">
                <Link
                  href={`/pitches/${pw.id}`}
                  className="text-sm text-ink-950 hover:underline"
                >
                  {pw.title}
                </Link>
              </TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-1">
                  {pw.beats.map((beat) => (
                    <span
                      key={beat}
                      className="inline-flex items-center rounded-full border border-ink-200 bg-ink-50 px-2 py-0.5 text-xs text-ink-600"
                    >
                      {beat}
                    </span>
                  ))}
                </div>
              </TableCell>
              <TableCell className="text-sm text-ink-700">
                {pw.current_pitch_count}/{pw.max_pitches}
              </TableCell>
              <TableCell className="text-sm text-ink-700">
                {formatBudget(pw.budget_min, pw.budget_max)}
              </TableCell>
              <TableCell>
                <PitchWindowStatusBadge status={pw.status} />
              </TableCell>
              <TableCell className="pr-4 text-sm text-ink-500">
                {formatDate(pw.closes_at)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function PitchesPage() {
  const activeWindows = mockPitchWindows.filter((w) => w.status === "open");
  const closedWindows = mockPitchWindows.filter(
    (w) => w.status === "closed" || w.status === "cancelled"
  );
  const draftWindows = mockPitchWindows.filter((w) => w.status === "draft");

  return (
    <>
      <Header
        title="Pitch Inbox"
        actions={
          <PitchWindowForm
            trigger={
              <button className="inline-flex h-9 items-center gap-1.5 rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800">
                <Plus className="h-4 w-4" />
                Create Window
              </button>
            }
          />
        }
      />
      <PageWrapper>
        <Tabs defaultValue="active">
          <TabsList>
            <TabsTrigger value="active">Active Windows</TabsTrigger>
            <TabsTrigger value="closed">Closed</TabsTrigger>
            <TabsTrigger value="drafts">Drafts</TabsTrigger>
          </TabsList>

          <TabsContent value="active" className="mt-4">
            <PitchWindowTable windows={activeWindows} />
          </TabsContent>

          <TabsContent value="closed" className="mt-4">
            <PitchWindowTable windows={closedWindows} />
          </TabsContent>

          <TabsContent value="drafts" className="mt-4">
            <PitchWindowTable windows={draftWindows} />
          </TabsContent>
        </Tabs>
      </PageWrapper>
    </>
  );
}
