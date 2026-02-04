"use client";

import { useRouter } from "next/navigation";
import { CalendarDays, DollarSign, FileText, Users } from "lucide-react";
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
import { AssignmentStatusBadge } from "@/components/features/assignments/assignment-status-badge";
import type { Assignment } from "@/types";

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
    revision_notes: "Please strengthen the sourcing in section 3 and add a counter-perspective.",
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

const ACTIVE_STATUSES = ["assigned", "in_progress", "submitted", "revision_requested"];
const COMPLETED_STATUSES = ["approved", "published", "killed"];

function formatRate(rate: number, rateType: string): string {
  if (rateType === "per_word") {
    return `$${rate.toFixed(2)}/word`;
  }
  return `$${rate.toLocaleString()} flat`;
}

function formatDeadline(deadline: string): string {
  const date = new Date(deadline);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function isOverdue(deadline: string, status: string): boolean {
  if (COMPLETED_STATUSES.includes(status)) return false;
  return new Date(deadline) < new Date();
}

function AssignmentsTable({
  assignments,
}: {
  assignments: typeof MOCK_ASSIGNMENTS;
}) {
  const router = useRouter();

  if (assignments.length === 0) {
    return (
      <div className="rounded-[5px] border border-ink-200 bg-white p-10 text-center">
        <FileText className="mx-auto h-10 w-10 text-ink-300" />
        <p className="mt-3 text-sm font-medium text-ink-700">
          No assignments found
        </p>
        <p className="mt-1 text-xs text-ink-400">
          Assignments will appear here once pitches are accepted and assigned.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-[5px] border border-ink-200 bg-white">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="pl-4">Title</TableHead>
            <TableHead>Freelancer</TableHead>
            <TableHead>Rate</TableHead>
            <TableHead>Deadline</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="pr-4">Revisions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {assignments.map((assignment) => (
            <TableRow
              key={assignment.id}
              className="cursor-pointer"
              onClick={() => router.push(`/assignments/${assignment.id}`)}
            >
              <TableCell className="pl-4">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 shrink-0 text-ink-400" />
                  <span className="text-sm font-medium text-ink-900">
                    {assignment.pitch_title}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <Users className="h-3.5 w-3.5 text-ink-400" />
                  <span className="text-sm text-ink-700">
                    {assignment.freelancer_name}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5">
                  <DollarSign className="h-3.5 w-3.5 text-ink-400" />
                  <span className="text-sm text-ink-700">
                    {formatRate(assignment.agreed_rate, assignment.rate_type)}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-1.5">
                  <CalendarDays className="h-3.5 w-3.5 text-ink-400" />
                  <span
                    className={`text-sm ${
                      isOverdue(assignment.deadline, assignment.status)
                        ? "font-medium text-red-600"
                        : "text-ink-700"
                    }`}
                  >
                    {formatDeadline(assignment.deadline)}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <AssignmentStatusBadge status={assignment.status} />
              </TableCell>
              <TableCell className="pr-4">
                <span className="text-sm text-ink-700">
                  {assignment.revision_count}/{assignment.max_revisions}
                </span>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

export default function AssignmentsPage() {
  const activeAssignments = MOCK_ASSIGNMENTS.filter((a) =>
    ACTIVE_STATUSES.includes(a.status)
  );
  const completedAssignments = MOCK_ASSIGNMENTS.filter((a) =>
    COMPLETED_STATUSES.includes(a.status)
  );

  return (
    <>
      <Header title="Assignments" subtitle="Manage editorial assignments" />
      <PageWrapper>
        <Tabs defaultValue="active">
          <TabsList>
            <TabsTrigger value="active">
              Active
              <span className="ml-1.5 rounded-full bg-ink-100 px-1.5 py-0.5 text-xs text-ink-600">
                {activeAssignments.length}
              </span>
            </TabsTrigger>
            <TabsTrigger value="completed">
              Completed
              <span className="ml-1.5 rounded-full bg-ink-100 px-1.5 py-0.5 text-xs text-ink-600">
                {completedAssignments.length}
              </span>
            </TabsTrigger>
            <TabsTrigger value="all">
              All
              <span className="ml-1.5 rounded-full bg-ink-100 px-1.5 py-0.5 text-xs text-ink-600">
                {MOCK_ASSIGNMENTS.length}
              </span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="active" className="mt-4">
            <AssignmentsTable assignments={activeAssignments} />
          </TabsContent>

          <TabsContent value="completed" className="mt-4">
            <AssignmentsTable assignments={completedAssignments} />
          </TabsContent>

          <TabsContent value="all" className="mt-4">
            <AssignmentsTable assignments={MOCK_ASSIGNMENTS} />
          </TabsContent>
        </Tabs>
      </PageWrapper>
    </>
  );
}
