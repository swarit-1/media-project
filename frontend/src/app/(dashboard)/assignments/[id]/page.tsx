"use client";

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

const MOCK_ASSIGNMENT: Assignment & {
  pitch_title: string;
  pitch_summary: string;
  freelancer_name: string;
  freelancer_email: string;
} = {
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
};

interface TimelineEvent {
  id: string;
  status: AssignmentStatus;
  label: string;
  timestamp: string;
  description?: string;
}

const MOCK_TIMELINE: TimelineEvent[] = [
  {
    id: "evt-1",
    status: "assigned",
    label: "Assignment Created",
    timestamp: "2026-01-18T11:00:00Z",
    description: "Assignment created from accepted pitch.",
  },
  {
    id: "evt-2",
    status: "in_progress",
    label: "Work Started",
    timestamp: "2026-01-20T08:00:00Z",
    description: "Freelancer began working on the assignment.",
  },
  {
    id: "evt-3",
    status: "submitted",
    label: "Draft Submitted",
    timestamp: "2026-02-01T14:30:00Z",
    description: "First draft submitted for editorial review.",
  },
];

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

export default function AssignmentDetailPage() {
  const params = useParams();
  const assignment = MOCK_ASSIGNMENT;

  return (
    <>
      <Header
        title={assignment.pitch_title}
        subtitle={`Assignment ${params.id}`}
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
              <div className="flex items-center gap-3">
                <button className="inline-flex h-9 items-center gap-2 rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800">
                  <CheckCircle2 className="h-4 w-4" />
                  Approve
                </button>
                <button className="inline-flex h-9 items-center gap-2 rounded-[3px] border border-ink-200 px-4 text-sm font-medium text-ink-700 transition-colors hover:bg-ink-50">
                  <RotateCcw className="h-4 w-4" />
                  Request Revision
                </button>
              </div>
            )}

            {assignment.status === "approved" && (
              <div className="flex items-center gap-3">
                <button className="inline-flex h-9 items-center gap-2 rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800">
                  <DollarSign className="h-4 w-4" />
                  Release Payment
                </button>
              </div>
            )}

            {/* Timeline */}
            <div className="rounded-[5px] border border-ink-200 bg-white p-5">
              <h2 className="text-sm font-semibold text-ink-950">Activity</h2>
              <div className="mt-4">
                <ol className="relative border-l border-ink-200 ml-3">
                  {MOCK_TIMELINE.map((event, index) => (
                    <li
                      key={event.id}
                      className={`ml-6 ${
                        index < MOCK_TIMELINE.length - 1 ? "pb-6" : ""
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
