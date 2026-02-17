"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Calendar,
  DollarSign,
  FileText,
  Check,
  X,
  Eye,
} from "lucide-react";
import { Header } from "@/components/layouts/header";
import { PageWrapper } from "@/components/layouts/page-wrapper";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import {
  PitchWindowStatusBadge,
  PitchStatusBadge,
} from "@/components/features/pitches/status-badge";
import type { PitchWindow, Pitch } from "@/types";

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

const mockWindow: PitchWindow = {
  id: "pw-1",
  newsroom_id: "nr-1",
  editor_id: "ed-1",
  title: "Climate & Environment Features - Spring 2026",
  description:
    "We are looking for in-depth feature pitches exploring climate policy, environmental justice, and sustainability innovations. Preference for original reporting with diverse sourcing.",
  beats: ["Climate", "Environment", "Policy"],
  requirements:
    "Pitches should include at least two confirmed sources and a reporting plan. 1,500-3,000 words.",
  budget_min: 400,
  budget_max: 1200,
  rate_type: "flat_rate",
  max_pitches: 25,
  current_pitch_count: 14,
  opens_at: "2026-02-01T00:00:00Z",
  closes_at: "2026-03-15T23:59:59Z",
  status: "open",
  created_at: "2026-01-20T10:00:00Z",
};

const initialPitches: Pitch[] = [
  {
    id: "p-1",
    pitch_window_id: "pw-1",
    freelancer_id: "fl-1",
    headline: "The Hidden Cost of Carbon Credits in the Global South",
    summary:
      "An investigation into how carbon offset markets are displacing indigenous communities in Southeast Asia while corporations claim net-zero status.",
    approach:
      "Field reporting in Indonesia and interviews with affected communities, academics, and industry reps.",
    estimated_word_count: 2500,
    proposed_rate: 900,
    proposed_rate_type: "flat_rate",
    estimated_delivery_days: 21,
    status: "submitted",
    submitted_at: "2026-02-05T14:23:00Z",
    created_at: "2026-02-04T09:00:00Z",
  },
  {
    id: "p-2",
    pitch_window_id: "pw-1",
    freelancer_id: "fl-2",
    headline: "Urban Heat Islands and Environmental Racism",
    summary:
      "Data-driven feature mapping how redlining shaped which neighborhoods are now most vulnerable to extreme heat, with profiles of community-led cooling initiatives.",
    estimated_word_count: 2000,
    proposed_rate: 700,
    proposed_rate_type: "flat_rate",
    estimated_delivery_days: 14,
    status: "under_review",
    submitted_at: "2026-02-03T11:45:00Z",
    reviewed_at: "2026-02-06T09:30:00Z",
    created_at: "2026-02-02T16:00:00Z",
  },
  {
    id: "p-3",
    pitch_window_id: "pw-1",
    freelancer_id: "fl-3",
    headline: "How Regenerative Agriculture Is Reshaping Rural Economies",
    summary:
      "A profile of three farming communities that transitioned to regenerative practices and their economic outcomes five years later.",
    estimated_word_count: 1800,
    proposed_rate: 600,
    proposed_rate_type: "flat_rate",
    estimated_delivery_days: 18,
    status: "accepted",
    editor_notes:
      "Strong angle. Let us discuss timing for a summer feature slot.",
    submitted_at: "2026-02-02T08:10:00Z",
    reviewed_at: "2026-02-07T15:00:00Z",
    created_at: "2026-02-01T20:00:00Z",
  },
  {
    id: "p-4",
    pitch_window_id: "pw-1",
    freelancer_id: "fl-4",
    headline: "Greenwashing in Fast Fashion Supply Chains",
    summary:
      "Examining sustainability claims from major fashion brands against actual environmental data from their supply chains.",
    estimated_word_count: 2200,
    proposed_rate: 500,
    proposed_rate_type: "flat_rate",
    estimated_delivery_days: 16,
    status: "rejected",
    rejection_reason:
      "Interesting topic but we covered a similar angle last quarter. Please consider a different framing.",
    submitted_at: "2026-02-04T19:00:00Z",
    reviewed_at: "2026-02-08T10:15:00Z",
    created_at: "2026-02-04T12:00:00Z",
  },
];

const freelancerNames: Record<string, string> = {
  "fl-1": "Maria Santos",
  "fl-2": "James Okafor",
  "fl-3": "Priya Sharma",
  "fl-4": "Alex Chen",
};

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

function formatRateType(type: string) {
  const labels: Record<string, string> = {
    per_word: "Per Word",
    flat_rate: "Flat Rate",
    hourly: "Hourly",
  };
  return labels[type] ?? type;
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function PitchWindowDetailPage() {
  const pw = mockWindow;
  const [pitches, setPitches] = useState<Pitch[]>(initialPitches);
  const [rejectingId, setRejectingId] = useState<string | null>(null);
  const [rejectionReason, setRejectionReason] = useState("");

  function handleAccept(pitchId: string) {
    setPitches((prev) =>
      prev.map((p) =>
        p.id === pitchId
          ? {
              ...p,
              status: "accepted" as const,
              reviewed_at: new Date().toISOString(),
            }
          : p
      )
    );
  }

  function handleReview(pitchId: string) {
    setPitches((prev) =>
      prev.map((p) =>
        p.id === pitchId
          ? {
              ...p,
              status: "under_review" as const,
              reviewed_at: new Date().toISOString(),
            }
          : p
      )
    );
  }

  function handleReject(pitchId: string) {
    setPitches((prev) =>
      prev.map((p) =>
        p.id === pitchId
          ? {
              ...p,
              status: "rejected" as const,
              rejection_reason: rejectionReason || undefined,
              reviewed_at: new Date().toISOString(),
            }
          : p
      )
    );
    setRejectingId(null);
    setRejectionReason("");
  }

  function canTakeAction(status: string) {
    return status === "submitted" || status === "under_review";
  }

  return (
    <>
      <Header
        title={pw.title}
        actions={<PitchWindowStatusBadge status={pw.status} />}
      />
      <PageWrapper>
        {/* Back link */}
        <Link
          href="/pitches"
          className="mb-4 inline-flex items-center gap-1 text-sm text-ink-500 transition-colors hover:text-ink-700"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to Pitch Inbox
        </Link>

        {/* Summary section */}
        <div className="rounded-[5px] border border-ink-200 bg-white p-5">
          <h2 className="text-lg font-semibold text-ink-950">Window Details</h2>
          <p className="mt-2 text-sm text-ink-600 leading-relaxed">
            {pw.description}
          </p>

          {pw.requirements && (
            <div className="mt-3">
              <p className="text-xs font-medium text-ink-500 uppercase tracking-wide">
                Requirements
              </p>
              <p className="mt-1 text-sm text-ink-600">{pw.requirements}</p>
            </div>
          )}

          <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-3">
            <div className="flex items-start gap-2">
              <FileText className="mt-0.5 h-4 w-4 shrink-0 text-ink-400" />
              <div>
                <p className="text-xs font-medium text-ink-500">Beats</p>
                <div className="mt-1 flex flex-wrap gap-1">
                  {pw.beats.map((beat) => (
                    <span
                      key={beat}
                      className="inline-flex items-center rounded-full border border-ink-200 bg-ink-50 px-2 py-0.5 text-xs text-ink-600"
                    >
                      {beat}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <DollarSign className="mt-0.5 h-4 w-4 shrink-0 text-ink-400" />
              <div>
                <p className="text-xs font-medium text-ink-500">Budget</p>
                <p className="mt-1 text-sm text-ink-700">
                  {formatBudget(pw.budget_min, pw.budget_max)}
                </p>
                <p className="text-xs text-ink-400">
                  {formatRateType(pw.rate_type)}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <Calendar className="mt-0.5 h-4 w-4 shrink-0 text-ink-400" />
              <div>
                <p className="text-xs font-medium text-ink-500">Deadline</p>
                <p className="mt-1 text-sm text-ink-700">
                  {formatDate(pw.closes_at)}
                </p>
                <p className="text-xs text-ink-400">
                  Opened {formatDate(pw.opens_at)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Received pitches table */}
        <div className="mt-6">
          <h2 className="mb-3 text-lg font-semibold text-ink-950">
            Received Pitches
          </h2>
          <div className="rounded-[5px] border border-ink-200 bg-white">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="pl-4">Headline</TableHead>
                  <TableHead>Freelancer</TableHead>
                  <TableHead>Rate</TableHead>
                  <TableHead>Word Count</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Submitted</TableHead>
                  <TableHead className="pr-4">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pitches.map((pitch) => (
                  <TableRow key={pitch.id}>
                    <TableCell className="pl-4 max-w-[300px]">
                      <p className="truncate text-sm font-medium text-ink-950">
                        {pitch.headline}
                      </p>
                      <p className="mt-0.5 truncate text-xs text-ink-400">
                        {pitch.summary}
                      </p>
                    </TableCell>
                    <TableCell className="text-sm text-ink-700">
                      {freelancerNames[pitch.freelancer_id] ??
                        pitch.freelancer_id}
                    </TableCell>
                    <TableCell className="text-sm text-ink-700">
                      {pitch.proposed_rate != null
                        ? `$${pitch.proposed_rate}`
                        : "-"}
                    </TableCell>
                    <TableCell className="text-sm text-ink-700">
                      {pitch.estimated_word_count != null
                        ? pitch.estimated_word_count.toLocaleString()
                        : "-"}
                    </TableCell>
                    <TableCell>
                      <PitchStatusBadge status={pitch.status} />
                    </TableCell>
                    <TableCell className="text-sm text-ink-500">
                      {pitch.submitted_at
                        ? formatDate(pitch.submitted_at)
                        : "-"}
                    </TableCell>
                    <TableCell className="pr-4">
                      {canTakeAction(pitch.status) ? (
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => handleAccept(pitch.id)}
                            className="inline-flex h-7 items-center gap-1 rounded-[3px] bg-green-600 px-2 text-xs font-medium text-white transition-colors hover:bg-green-700"
                            title="Accept pitch"
                          >
                            <Check className="h-3 w-3" />
                            Accept
                          </button>
                          {pitch.status === "submitted" && (
                            <button
                              onClick={() => handleReview(pitch.id)}
                              className="inline-flex h-7 items-center gap-1 rounded-[3px] border border-ink-200 bg-white px-2 text-xs font-medium text-ink-700 transition-colors hover:bg-ink-50"
                              title="Mark as under review"
                            >
                              <Eye className="h-3 w-3" />
                              Review
                            </button>
                          )}
                          <button
                            onClick={() => setRejectingId(pitch.id)}
                            className="inline-flex h-7 items-center gap-1 rounded-[3px] border border-red-200 bg-white px-2 text-xs font-medium text-red-600 transition-colors hover:bg-red-50"
                            title="Reject pitch"
                          >
                            <X className="h-3 w-3" />
                            Reject
                          </button>
                        </div>
                      ) : pitch.status === "accepted" ? (
                        <span className="text-xs text-green-600 font-medium">
                          Accepted
                        </span>
                      ) : pitch.status === "rejected" ? (
                        <span className="text-xs text-red-600 font-medium">
                          Rejected
                        </span>
                      ) : (
                        <span className="text-xs text-ink-400">-</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>

        {/* Rejection reason modal */}
        {rejectingId && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
            <div className="w-full max-w-md rounded-[5px] border border-ink-200 bg-white p-5 shadow-lg">
              <h3 className="text-sm font-semibold text-ink-950">
                Reject Pitch
              </h3>
              <p className="mt-1 text-xs text-ink-500">
                Optionally provide a reason for the rejection.
              </p>
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="Reason for rejection (optional)"
                className="mt-3 w-full rounded-[3px] border border-ink-200 bg-white px-3 py-2 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
                rows={3}
              />
              <div className="mt-4 flex justify-end gap-2">
                <button
                  onClick={() => {
                    setRejectingId(null);
                    setRejectionReason("");
                  }}
                  className="inline-flex h-9 items-center justify-center rounded-[3px] border border-ink-200 bg-white px-4 text-sm font-medium text-ink-700 transition-colors hover:bg-ink-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleReject(rejectingId)}
                  className="inline-flex h-9 items-center justify-center rounded-[3px] bg-red-600 px-4 text-sm font-medium text-white transition-colors hover:bg-red-700"
                >
                  Reject Pitch
                </button>
              </div>
            </div>
          </div>
        )}
      </PageWrapper>
    </>
  );
}
