"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  Clock,
  DollarSign,
  ExternalLink,
  FileText,
  RotateCcw,
  Send,
  User,
  XCircle,
} from "lucide-react";
import { Header } from "@/components/layouts/header";
import { PageWrapper } from "@/components/layouts/page-wrapper";
import { AssignmentStatusBadge } from "@/components/features/assignments/assignment-status-badge";
import type { Assignment, AssignmentStatus } from "@/types";

// ---------------------------------------------------------------------------
// Mock data – keyed by assignment id so the detail page shows the right one
// ---------------------------------------------------------------------------

type AssignmentDetail = Assignment & {
  pitch_title: string;
  pitch_summary: string;
  freelancer_name: string;
  freelancer_email: string;
};

const ASSIGNMENTS_MAP: Record<string, AssignmentDetail> = {
  "asgn-001": {
    id: "asgn-001",
    pitch_id: "pitch-101",
    freelancer_id: "fr-001",
    editor_id: "ed-001",
    newsroom_id: "nr-001",
    agreed_rate: 0.35,
    rate_type: "per_word",
    word_count_target: 1200,
    deadline: "2026-02-10T23:59:59Z",
    status: "in_progress",
    revision_count: 0,
    max_revisions: 2,
    kill_fee_percentage: 25,
    started_at: "2026-01-28T10:00:00Z",
    created_at: "2026-01-27T09:00:00Z",
    updated_at: "2026-01-28T10:00:00Z",
    pitch_title: "The Future of Remote Journalism in Africa",
    pitch_summary:
      "An exploration of how remote journalism is transforming media coverage across Africa, examining the tools, challenges, and opportunities for freelancers working from the continent. The piece will profile three journalists pioneering new approaches to remote reporting.",
    freelancer_name: "Amara Okafor",
    freelancer_email: "amara.okafor@example.com",
  },
  "asgn-002": {
    id: "asgn-002",
    pitch_id: "pitch-102",
    freelancer_id: "fr-002",
    editor_id: "ed-001",
    newsroom_id: "nr-001",
    agreed_rate: 500,
    rate_type: "flat",
    word_count_target: 2000,
    deadline: "2026-02-07T23:59:59Z",
    status: "submitted",
    revision_count: 0,
    max_revisions: 3,
    kill_fee_percentage: 25,
    draft_url: "https://docs.example.com/draft-102",
    started_at: "2026-01-20T08:00:00Z",
    submitted_at: "2026-02-01T14:30:00Z",
    created_at: "2026-01-18T11:00:00Z",
    updated_at: "2026-02-01T14:30:00Z",
    pitch_title: "Climate Policy Shifts in Southeast Asia",
    pitch_summary:
      "An in-depth analysis of how Southeast Asian nations are reshaping their climate policies in response to recent extreme weather events, with a focus on Indonesia, Vietnam, and the Philippines. The piece will examine new legislation, corporate accountability measures, and grassroots movements driving change.",
    freelancer_name: "Linh Nguyen",
    freelancer_email: "linh.nguyen@example.com",
  },
  "asgn-003": {
    id: "asgn-003",
    pitch_id: "pitch-103",
    freelancer_id: "fr-003",
    editor_id: "ed-001",
    newsroom_id: "nr-001",
    agreed_rate: 0.4,
    rate_type: "per_word",
    word_count_target: 800,
    deadline: "2026-02-15T23:59:59Z",
    status: "assigned",
    revision_count: 0,
    max_revisions: 2,
    kill_fee_percentage: 20,
    created_at: "2026-02-01T16:00:00Z",
    updated_at: "2026-02-01T16:00:00Z",
    pitch_title: "Tech Startups Reshaping Local News",
    pitch_summary:
      "A feature examining how technology startups are building new platforms and tools specifically designed to support local newsrooms. Covers three startups offering AI-assisted reporting tools, community engagement platforms, and sustainable revenue models for small publishers.",
    freelancer_name: "Marcus Webb",
    freelancer_email: "marcus.webb@example.com",
  },
  "asgn-004": {
    id: "asgn-004",
    pitch_id: "pitch-104",
    freelancer_id: "fr-004",
    editor_id: "ed-001",
    newsroom_id: "nr-001",
    agreed_rate: 750,
    rate_type: "flat",
    word_count_target: 3000,
    deadline: "2026-01-30T23:59:59Z",
    status: "revision_requested",
    revision_count: 1,
    max_revisions: 2,
    revision_notes:
      "Please strengthen the sourcing in section 3 and add a counter-perspective.",
    kill_fee_percentage: 25,
    draft_url: "https://docs.example.com/draft-104",
    started_at: "2026-01-15T09:00:00Z",
    submitted_at: "2026-01-28T11:00:00Z",
    created_at: "2026-01-12T10:00:00Z",
    updated_at: "2026-01-30T08:00:00Z",
    pitch_title: "Investigative: Water Rights in the Colorado Basin",
    pitch_summary:
      "A long-form investigative piece into the growing conflict over water rights in the Colorado River Basin. The article traces how corporate agriculture, urban expansion, and Indigenous water rights claims are colliding, and what it means for millions of people who depend on the river system.",
    freelancer_name: "Sofia Reyes",
    freelancer_email: "sofia.reyes@example.com",
  },
  "asgn-005": {
    id: "asgn-005",
    pitch_id: "pitch-105",
    freelancer_id: "fr-005",
    editor_id: "ed-001",
    newsroom_id: "nr-001",
    agreed_rate: 0.3,
    rate_type: "per_word",
    word_count_target: 1500,
    deadline: "2026-01-20T23:59:59Z",
    status: "published",
    revision_count: 1,
    max_revisions: 2,
    final_word_count: 1480,
    kill_fee_percentage: 25,
    final_url: "https://newsroom.example.com/articles/digital-divide",
    cms_post_id: "cms-9921",
    published_at: "2026-01-22T12:00:00Z",
    started_at: "2026-01-08T09:00:00Z",
    submitted_at: "2026-01-16T15:00:00Z",
    completed_at: "2026-01-22T12:00:00Z",
    created_at: "2026-01-05T14:00:00Z",
    updated_at: "2026-01-22T12:00:00Z",
    pitch_title: "Bridging the Digital Divide in Rural Schools",
    pitch_summary:
      "A reported feature on how rural school districts across the American South are tackling the digital divide, profiling innovative programs that provide internet access, devices, and digital literacy training to underserved students and their families.",
    freelancer_name: "James Thornton",
    freelancer_email: "james.thornton@example.com",
  },
  "asgn-006": {
    id: "asgn-006",
    pitch_id: "pitch-106",
    freelancer_id: "fr-006",
    editor_id: "ed-001",
    newsroom_id: "nr-001",
    agreed_rate: 350,
    rate_type: "flat",
    word_count_target: 1000,
    deadline: "2026-01-25T23:59:59Z",
    status: "killed",
    revision_count: 0,
    max_revisions: 2,
    kill_fee_percentage: 25,
    created_at: "2026-01-10T09:00:00Z",
    updated_at: "2026-01-23T10:00:00Z",
    pitch_title: "Election Polling Methodology Under Scrutiny",
    pitch_summary:
      "An analysis piece questioning the reliability of modern election polling methods, exploring why polls have consistently missed the mark in recent elections and what new methodologies pollsters are experimenting with to restore accuracy and public trust.",
    freelancer_name: "Dana Kim",
    freelancer_email: "dana.kim@example.com",
  },
};

// ---------------------------------------------------------------------------
// Build initial timeline from an assignment's dates
// ---------------------------------------------------------------------------

function buildTimeline(a: AssignmentDetail): TimelineEvent[] {
  const events: TimelineEvent[] = [];

  events.push({
    id: "evt-created",
    status: "assigned",
    label: "Assignment Created",
    timestamp: a.created_at,
    description: "Assignment created from accepted pitch.",
  });

  if (a.started_at) {
    events.push({
      id: "evt-started",
      status: "in_progress",
      label: "Work Started",
      timestamp: a.started_at,
      description: "Freelancer began working on the assignment.",
    });
  }

  if (a.submitted_at) {
    events.push({
      id: "evt-submitted",
      status: "submitted",
      label: "Draft Submitted",
      timestamp: a.submitted_at,
      description: "Draft submitted for editorial review.",
    });
  }

  if (a.status === "revision_requested" && a.revision_notes) {
    events.push({
      id: "evt-revision",
      status: "revision_requested",
      label: "Revision Requested",
      timestamp: a.updated_at,
      description: a.revision_notes,
    });
  }

  if (a.completed_at) {
    events.push({
      id: "evt-completed",
      status: "approved",
      label: "Approved",
      timestamp: a.completed_at,
      description: "Editor approved the final draft.",
    });
  }

  if (a.published_at) {
    events.push({
      id: "evt-published",
      status: "published",
      label: "Published",
      timestamp: a.published_at,
      description: "Article published and payment released.",
    });
  }

  if (a.status === "killed") {
    events.push({
      id: "evt-killed",
      status: "killed",
      label: "Assignment Killed",
      timestamp: a.updated_at,
      description: `Kill fee of ${a.kill_fee_percentage}% applied.`,
    });
  }

  return events;
}

// ---------------------------------------------------------------------------
// Types & helpers
// ---------------------------------------------------------------------------

interface TimelineEvent {
  id: string;
  status: AssignmentStatus;
  label: string;
  timestamp: string;
  description?: string;
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatRate(rate: number, rateType: string): string {
  if (rateType === "per_word") {
    return `$${rate.toFixed(2)}/word`;
  }
  return `$${rate.toLocaleString()}`;
}

function timelineIcon(status: AssignmentStatus) {
  switch (status) {
    case "assigned":
      return <FileText className="h-4 w-4" />;
    case "in_progress":
      return <Clock className="h-4 w-4" />;
    case "submitted":
      return <Send className="h-4 w-4" />;
    case "revision_requested":
      return <RotateCcw className="h-4 w-4" />;
    case "approved":
      return <CheckCircle2 className="h-4 w-4" />;
    case "published":
      return <CheckCircle2 className="h-4 w-4" />;
    case "killed":
      return <XCircle className="h-4 w-4" />;
  }
}

function timelineIconColor(status: AssignmentStatus): string {
  switch (status) {
    case "assigned":
      return "bg-blue-100 text-blue-600";
    case "in_progress":
      return "bg-yellow-100 text-yellow-600";
    case "submitted":
      return "bg-purple-100 text-purple-600";
    case "revision_requested":
      return "bg-orange-100 text-orange-600";
    case "approved":
      return "bg-green-100 text-green-600";
    case "published":
      return "bg-green-100 text-green-600";
    case "killed":
      return "bg-red-100 text-red-600";
  }
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function AssignmentDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const initialAssignment = ASSIGNMENTS_MAP[id];

  const [assignment, setAssignment] = useState(initialAssignment);
  const [timeline, setTimeline] = useState(() =>
    initialAssignment ? buildTimeline(initialAssignment) : []
  );
  const [showRevisionForm, setShowRevisionForm] = useState(false);
  const [revisionNotes, setRevisionNotes] = useState("");

  if (!assignment) {
    return (
      <>
        <Header title="Assignment Not Found" />
        <PageWrapper>
          <div className="rounded-[5px] border border-ink-200 bg-white p-10 text-center">
            <p className="text-sm text-ink-500">
              No assignment found with ID &quot;{id}&quot;.
            </p>
            <Link
              href="/assignments"
              className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-accent-600 hover:text-accent-700"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              Back to assignments
            </Link>
          </div>
        </PageWrapper>
      </>
    );
  }

  function handleApprove() {
    const now = new Date().toISOString();
    setAssignment((prev) => ({
      ...prev!,
      status: "approved" as AssignmentStatus,
      updated_at: now,
    }));
    setTimeline((prev) => [
      ...prev,
      {
        id: `evt-${Date.now()}`,
        status: "approved" as AssignmentStatus,
        label: "Draft Approved",
        timestamp: now,
        description: "Editor approved the submitted draft.",
      },
    ]);
  }

  function handleRequestRevision() {
    if (!revisionNotes.trim()) return;
    const now = new Date().toISOString();
    setAssignment((prev) => ({
      ...prev!,
      status: "revision_requested" as AssignmentStatus,
      revision_count: prev!.revision_count + 1,
      revision_notes: revisionNotes.trim(),
      updated_at: now,
    }));
    setTimeline((prev) => [
      ...prev,
      {
        id: `evt-${Date.now()}`,
        status: "revision_requested" as AssignmentStatus,
        label: "Revision Requested",
        timestamp: now,
        description: revisionNotes.trim(),
      },
    ]);
    setRevisionNotes("");
    setShowRevisionForm(false);
  }

  function handleReleasePayment() {
    const now = new Date().toISOString();
    setAssignment((prev) => ({
      ...prev!,
      status: "published" as AssignmentStatus,
      completed_at: now,
      published_at: now,
      updated_at: now,
    }));
    setTimeline((prev) => [
      ...prev,
      {
        id: `evt-${Date.now()}`,
        status: "published" as AssignmentStatus,
        label: "Payment Released & Published",
        timestamp: now,
        description: `Payment of ${formatRate(assignment.agreed_rate, assignment.rate_type)} released to ${assignment.freelancer_name}.`,
      },
    ]);
  }

  return (
    <>
      <Header
        title={assignment.pitch_title}
        subtitle={`Assignment ${id}`}
        actions={<AssignmentStatusBadge status={assignment.status} />}
      />
      <PageWrapper>
        {/* Back link */}
        <Link
          href="/assignments"
          className="mb-5 inline-flex items-center gap-1.5 text-sm text-ink-500 transition-colors hover:text-ink-700"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to assignments
        </Link>

        {/* Two-column layout */}
        <div className="grid grid-cols-3 gap-6">
          {/* Left column - 2/3 */}
          <div className="col-span-2 space-y-6">
            {/* Assignment details card */}
            <div className="rounded-[5px] border border-ink-200 bg-white p-5">
              <h2 className="text-sm font-semibold text-ink-950">
                Assignment Details
              </h2>
              <p className="mt-3 text-sm leading-relaxed text-ink-600">
                {assignment.pitch_summary}
              </p>

              {/* Content links */}
              {(assignment.draft_url || assignment.final_url) && (
                <div className="mt-5 border-t border-ink-100 pt-4">
                  <h3 className="text-xs font-medium uppercase tracking-wide text-ink-400">
                    Content Links
                  </h3>
                  <div className="mt-2 flex flex-col gap-2">
                    {assignment.draft_url && (
                      <a
                        href={assignment.draft_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-800"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                        View Draft
                      </a>
                    )}
                    {assignment.final_url && (
                      <a
                        href={assignment.final_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-800"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                        View Published Article
                      </a>
                    )}
                  </div>
                </div>
              )}

              {/* Revision notes */}
              {assignment.revision_notes && (
                <div className="mt-5 border-t border-ink-100 pt-4">
                  <h3 className="text-xs font-medium uppercase tracking-wide text-ink-400">
                    Revision Notes
                  </h3>
                  <div className="mt-2 rounded-[3px] border border-orange-200 bg-orange-50 p-3">
                    <p className="text-sm text-orange-800">
                      {assignment.revision_notes}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Action buttons */}
            {assignment.status === "submitted" && (
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <button
                    onClick={handleApprove}
                    className="inline-flex h-9 items-center gap-2 rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                    Approve
                  </button>
                  <button
                    onClick={() => setShowRevisionForm(!showRevisionForm)}
                    className="inline-flex h-9 items-center gap-2 rounded-[3px] border border-ink-200 px-4 text-sm font-medium text-ink-700 transition-colors hover:bg-ink-50"
                  >
                    <RotateCcw className="h-4 w-4" />
                    Request Revision
                  </button>
                </div>
                {showRevisionForm && (
                  <div className="rounded-[5px] border border-ink-200 bg-white p-4">
                    <label className="mb-1.5 block text-sm font-medium text-ink-700">
                      Revision notes
                    </label>
                    <textarea
                      value={revisionNotes}
                      onChange={(e) => setRevisionNotes(e.target.value)}
                      placeholder="Describe what changes are needed..."
                      className="mb-3 h-24 w-full rounded-[3px] border border-ink-200 px-3 py-2 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
                    />
                    <div className="flex items-center gap-2">
                      <button
                        onClick={handleRequestRevision}
                        disabled={!revisionNotes.trim()}
                        className="inline-flex h-8 items-center rounded-[3px] bg-orange-600 px-3 text-sm font-medium text-white transition-colors hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-40"
                      >
                        Send Revision Request
                      </button>
                      <button
                        onClick={() => {
                          setShowRevisionForm(false);
                          setRevisionNotes("");
                        }}
                        className="inline-flex h-8 items-center rounded-[3px] border border-ink-200 px-3 text-sm font-medium text-ink-600 transition-colors hover:bg-ink-50"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {assignment.status === "approved" && (
              <div className="flex items-center gap-3">
                <button
                  onClick={handleReleasePayment}
                  className="inline-flex h-9 items-center gap-2 rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800"
                >
                  <DollarSign className="h-4 w-4" />
                  Release Payment
                </button>
              </div>
            )}

            {assignment.status === "published" && (
              <div className="rounded-[5px] border border-green-200 bg-green-50 p-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <p className="text-sm font-medium text-green-900">
                    Assignment complete — payment released
                  </p>
                </div>
              </div>
            )}

            {assignment.status === "killed" && (
              <div className="rounded-[5px] border border-red-200 bg-red-50 p-4">
                <div className="flex items-center gap-2">
                  <XCircle className="h-5 w-5 text-red-600" />
                  <p className="text-sm font-medium text-red-900">
                    Assignment killed — {assignment.kill_fee_percentage}% kill fee applied
                  </p>
                </div>
              </div>
            )}

            {/* Timeline */}
            <div className="rounded-[5px] border border-ink-200 bg-white p-5">
              <h2 className="text-sm font-semibold text-ink-950">Activity</h2>
              <div className="mt-4">
                <ol className="relative border-l border-ink-200 ml-3">
                  {timeline.map((event, index) => (
                    <li
                      key={event.id}
                      className={`ml-6 ${
                        index < timeline.length - 1 ? "pb-6" : ""
                      }`}
                    >
                      <span
                        className={`absolute -left-[14px] flex h-7 w-7 items-center justify-center rounded-full ${timelineIconColor(
                          event.status
                        )}`}
                      >
                        {timelineIcon(event.status)}
                      </span>
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-medium text-ink-900">
                          {event.label}
                        </h3>
                        <AssignmentStatusBadge status={event.status} />
                      </div>
                      <time className="mt-0.5 text-xs text-ink-400">
                        {formatDateTime(event.timestamp)}
                      </time>
                      {event.description && (
                        <p className="mt-1 text-sm text-ink-500">
                          {event.description}
                        </p>
                      )}
                    </li>
                  ))}
                </ol>
              </div>
            </div>
          </div>

          {/* Right column - 1/3 sidebar */}
          <div className="col-span-1">
            <div className="rounded-[5px] border border-ink-200 bg-white p-5">
              <h2 className="text-sm font-semibold text-ink-950">Details</h2>
              <dl className="mt-4 space-y-4">
                {/* Freelancer */}
                <div>
                  <dt className="flex items-center gap-1.5 text-xs font-medium text-ink-400">
                    <User className="h-3.5 w-3.5" />
                    Freelancer
                  </dt>
                  <dd className="mt-1 text-sm text-ink-900">
                    {assignment.freelancer_name}
                  </dd>
                  <dd className="text-xs text-ink-500">
                    {assignment.freelancer_email}
                  </dd>
                </div>

                {/* Rate */}
                <div>
                  <dt className="flex items-center gap-1.5 text-xs font-medium text-ink-400">
                    <DollarSign className="h-3.5 w-3.5" />
                    Rate
                  </dt>
                  <dd className="mt-1 text-sm text-ink-900">
                    {formatRate(assignment.agreed_rate, assignment.rate_type)}
                    <span className="ml-1 text-xs text-ink-400">
                      ({assignment.rate_type === "per_word" ? "per word" : "flat rate"})
                    </span>
                  </dd>
                </div>

                {/* Deadline */}
                <div>
                  <dt className="flex items-center gap-1.5 text-xs font-medium text-ink-400">
                    <CalendarDays className="h-3.5 w-3.5" />
                    Deadline
                  </dt>
                  <dd className="mt-1 text-sm text-ink-900">
                    {formatDate(assignment.deadline)}
                  </dd>
                </div>

                {/* Word count target */}
                {assignment.word_count_target && (
                  <div>
                    <dt className="flex items-center gap-1.5 text-xs font-medium text-ink-400">
                      <FileText className="h-3.5 w-3.5" />
                      Word Count Target
                    </dt>
                    <dd className="mt-1 text-sm text-ink-900">
                      {assignment.word_count_target.toLocaleString()} words
                      {assignment.final_word_count && (
                        <span className="ml-1 text-xs text-ink-400">
                          (final: {assignment.final_word_count.toLocaleString()})
                        </span>
                      )}
                    </dd>
                  </div>
                )}

                {/* Revisions */}
                <div>
                  <dt className="flex items-center gap-1.5 text-xs font-medium text-ink-400">
                    <RotateCcw className="h-3.5 w-3.5" />
                    Revisions
                  </dt>
                  <dd className="mt-1 text-sm text-ink-900">
                    {assignment.revision_count} of {assignment.max_revisions} used
                  </dd>
                </div>

                {/* Kill fee */}
                <div>
                  <dt className="flex items-center gap-1.5 text-xs font-medium text-ink-400">
                    <XCircle className="h-3.5 w-3.5" />
                    Kill Fee
                  </dt>
                  <dd className="mt-1 text-sm text-ink-900">
                    {assignment.kill_fee_percentage}%
                  </dd>
                </div>
              </dl>

              {/* Key dates */}
              <div className="mt-6 border-t border-ink-100 pt-4">
                <h3 className="text-xs font-medium uppercase tracking-wide text-ink-400">
                  Key Dates
                </h3>
                <dl className="mt-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <dt className="text-xs text-ink-500">Created</dt>
                    <dd className="text-xs text-ink-700">
                      {formatDate(assignment.created_at)}
                    </dd>
                  </div>
                  {assignment.started_at && (
                    <div className="flex items-center justify-between">
                      <dt className="text-xs text-ink-500">Started</dt>
                      <dd className="text-xs text-ink-700">
                        {formatDate(assignment.started_at)}
                      </dd>
                    </div>
                  )}
                  {assignment.submitted_at && (
                    <div className="flex items-center justify-between">
                      <dt className="text-xs text-ink-500">Submitted</dt>
                      <dd className="text-xs text-ink-700">
                        {formatDate(assignment.submitted_at)}
                      </dd>
                    </div>
                  )}
                  {assignment.completed_at && (
                    <div className="flex items-center justify-between">
                      <dt className="text-xs text-ink-500">Completed</dt>
                      <dd className="text-xs text-ink-700">
                        {formatDate(assignment.completed_at)}
                      </dd>
                    </div>
                  )}
                  {assignment.published_at && (
                    <div className="flex items-center justify-between">
                      <dt className="text-xs text-ink-500">Published</dt>
                      <dd className="text-xs text-ink-700">
                        {formatDate(assignment.published_at)}
                      </dd>
                    </div>
                  )}
                </dl>
              </div>
            </div>
          </div>
        </div>
      </PageWrapper>
    </>
  );
}
