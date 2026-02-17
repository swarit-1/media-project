"use client";

import { useRouter } from "next/navigation";
import { CalendarDays, DollarSign, Users } from "lucide-react";
import { Header } from "@/components/layouts/header";
import { PageWrapper } from "@/components/layouts/page-wrapper";
import { AssignmentStatusBadge } from "@/components/features/assignments/assignment-status-badge";
import type { Assignment } from "@/types";

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

const MOCK_ASSIGNMENTS: (Assignment & {
  pitch_title: string;
  freelancer_name: string;
})[] = [
  {
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
    freelancer_name: "Amara Okafor",
  },
  {
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
    freelancer_name: "Linh Nguyen",
  },
  {
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
    freelancer_name: "Marcus Webb",
  },
  {
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
    freelancer_name: "Sofia Reyes",
  },
  {
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
    freelancer_name: "James Thornton",
  },
  {
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
    freelancer_name: "Dana Kim",
  },
];

// ---------------------------------------------------------------------------
// Kanban configuration
// ---------------------------------------------------------------------------

interface KanbanColumn {
  key: string;
  label: string;
  statuses: string[];
  headerColor: string;
}

const KANBAN_COLUMNS: KanbanColumn[] = [
  {
    key: "assigned",
    label: "Assigned",
    statuses: ["assigned"],
    headerColor: "bg-ink-200 text-ink-700",
  },
  {
    key: "in_progress",
    label: "In Progress",
    statuses: ["in_progress"],
    headerColor: "bg-blue-100 text-blue-700",
  },
  {
    key: "submitted",
    label: "Submitted",
    statuses: ["submitted"],
    headerColor: "bg-amber-100 text-amber-700",
  },
  {
    key: "revision",
    label: "Revision Requested",
    statuses: ["revision_requested"],
    headerColor: "bg-orange-100 text-orange-700",
  },
  {
    key: "approved",
    label: "Approved",
    statuses: ["approved", "published"],
    headerColor: "bg-green-100 text-green-700",
  },
  {
    key: "killed",
    label: "Killed",
    statuses: ["killed"],
    headerColor: "bg-red-100 text-red-700",
  },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatRate(rate: number, rateType: string): string {
  if (rateType === "per_word") {
    return `$${rate.toFixed(2)}/word`;
  }
  return `$${rate.toLocaleString()} flat`;
}

function formatDeadline(deadline: string): string {
  return new Date(deadline).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

function isOverdue(deadline: string, status: string): boolean {
  const completedStatuses = ["approved", "published", "killed"];
  if (completedStatuses.includes(status)) return false;
  return new Date(deadline) < new Date();
}

// ---------------------------------------------------------------------------
// Kanban Card
// ---------------------------------------------------------------------------

function KanbanCard({
  assignment,
  onClick,
}: {
  assignment: (typeof MOCK_ASSIGNMENTS)[0];
  onClick: () => void;
}) {
  const overdue = isOverdue(assignment.deadline, assignment.status);

  return (
    <button
      onClick={onClick}
      className="w-full rounded-[5px] border border-ink-200 bg-white p-3 text-left transition-shadow hover:shadow-sm"
    >
      <p className="text-sm font-medium text-ink-950 leading-snug">
        {assignment.pitch_title}
      </p>

      <div className="mt-2 flex items-center gap-1.5">
        <Users className="h-3 w-3 text-ink-400" />
        <span className="text-xs text-ink-600">{assignment.freelancer_name}</span>
      </div>

      <div className="mt-2 flex items-center justify-between">
        <div className="flex items-center gap-1">
          <DollarSign className="h-3 w-3 text-ink-400" />
          <span className="text-xs text-ink-600">
            {formatRate(assignment.agreed_rate, assignment.rate_type)}
          </span>
        </div>

        <div className="flex items-center gap-1">
          <CalendarDays className="h-3 w-3 text-ink-400" />
          <span
            className={`text-xs ${
              overdue ? "font-medium text-red-600" : "text-ink-600"
            }`}
          >
            {formatDeadline(assignment.deadline)}
          </span>
        </div>
      </div>

      {assignment.revision_count > 0 && (
        <p className="mt-2 text-xs text-ink-400">
          Revisions: {assignment.revision_count}/{assignment.max_revisions}
        </p>
      )}
    </button>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function AssignmentsPage() {
  const router = useRouter();

  return (
    <>
      <Header title="Assignments" subtitle="Manage editorial assignments" />
      <PageWrapper>
        <div className="grid grid-cols-2 gap-4 xl:grid-cols-3">
          {KANBAN_COLUMNS.map((column) => {
            const columnAssignments = MOCK_ASSIGNMENTS.filter((a) =>
              column.statuses.includes(a.status)
            );

            return (
              <div
                key={column.key}
                className="flex flex-col"
              >
                {/* Column header */}
                <div
                  className={`flex items-center justify-between rounded-t-[5px] px-3 py-2 ${column.headerColor}`}
                >
                  <span className="text-xs font-semibold">{column.label}</span>
                  <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-white/60 px-1.5 text-[11px] font-medium">
                    {columnAssignments.length}
                  </span>
                </div>

                {/* Column body */}
                <div className="flex flex-1 flex-col gap-2 rounded-b-[5px] border border-t-0 border-ink-200 bg-ink-50 p-2 min-h-[200px]">
                  {columnAssignments.length > 0 ? (
                    columnAssignments.map((assignment) => (
                      <KanbanCard
                        key={assignment.id}
                        assignment={assignment}
                        onClick={() =>
                          router.push(`/assignments/${assignment.id}`)
                        }
                      />
                    ))
                  ) : (
                    <div className="flex flex-1 items-center justify-center">
                      <p className="text-xs text-ink-400">No assignments</p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </PageWrapper>
    </>
  );
}
