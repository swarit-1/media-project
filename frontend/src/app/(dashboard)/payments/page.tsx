"use client";

import { useMemo, useState } from "react";
import { DollarSign, Landmark, Clock, ExternalLink, CreditCard, CheckCircle2 } from "lucide-react";
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
import { PaymentStatusBadge } from "@/components/features/payments/payment-status-badge";
import { useAuth } from "@/lib/hooks/use-auth";
import type { Payment } from "@/types";

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

const FREELANCER_NAMES: Record<string, string> = {
  "fr-001": "Amara Osei",
  "fr-002": "Jake Whitfield",
  "fr-003": "Priya Nair",
  "fr-004": "Carlos Medina",
  "fr-005": "Lin Zhang",
};

const MOCK_PAYMENTS: Payment[] = [
  {
    id: "pay-001",
    assignment_id: "asg-101",
    newsroom_id: "nr-01",
    freelancer_id: "fr-001",
    payment_type: "assignment",
    gross_amount: 1200,
    platform_fee: 60,
    net_amount: 1140,
    status: "completed",
    description: "Feature: City housing crisis deep-dive",
    created_at: "2025-12-02T10:00:00Z",
    completed_at: "2025-12-05T14:30:00Z",
  },
  {
    id: "pay-002",
    assignment_id: "asg-102",
    newsroom_id: "nr-01",
    freelancer_id: "fr-002",
    payment_type: "assignment",
    gross_amount: 800,
    platform_fee: 40,
    net_amount: 760,
    status: "escrow_held",
    description: "Investigation: School board spending",
    created_at: "2025-12-10T09:00:00Z",
  },
  {
    id: "pay-003",
    assignment_id: "asg-103",
    newsroom_id: "nr-01",
    freelancer_id: "fr-003",
    payment_type: "assignment",
    gross_amount: 500,
    platform_fee: 25,
    net_amount: 475,
    status: "pending",
    description: "Op-ed: Climate policy analysis",
    created_at: "2025-12-15T11:30:00Z",
  },
  {
    id: "pay-004",
    assignment_id: "asg-104",
    newsroom_id: "nr-01",
    freelancer_id: "fr-004",
    payment_type: "assignment",
    gross_amount: 2000,
    platform_fee: 100,
    net_amount: 1900,
    status: "completed",
    description: "Longform: Immigration court backlog",
    created_at: "2025-11-20T08:00:00Z",
    completed_at: "2025-11-28T16:00:00Z",
  },
  {
    id: "pay-005",
    assignment_id: "asg-105",
    newsroom_id: "nr-01",
    freelancer_id: "fr-005",
    payment_type: "assignment",
    gross_amount: 650,
    platform_fee: 32.5,
    net_amount: 617.5,
    status: "processing",
    description: "News brief: Tech layoffs roundup",
    created_at: "2025-12-18T14:00:00Z",
  },
  {
    id: "pay-006",
    assignment_id: "asg-106",
    newsroom_id: "nr-01",
    freelancer_id: "fr-001",
    payment_type: "assignment",
    gross_amount: 1500,
    platform_fee: 75,
    net_amount: 1425,
    status: "escrow_held",
    description: "Feature: Public transit overhaul series",
    created_at: "2025-12-20T09:15:00Z",
  },
  {
    id: "pay-007",
    assignment_id: "asg-107",
    newsroom_id: "nr-01",
    freelancer_id: "fr-003",
    payment_type: "assignment",
    gross_amount: 350,
    platform_fee: 17.5,
    net_amount: 332.5,
    status: "failed",
    description: "Explainer: New tax regulations",
    created_at: "2025-12-12T13:45:00Z",
  },
  {
    id: "pay-008",
    assignment_id: "asg-108",
    newsroom_id: "nr-01",
    freelancer_id: "fr-002",
    payment_type: "assignment",
    gross_amount: 900,
    platform_fee: 45,
    net_amount: 855,
    status: "pending",
    description: "Profile: Incoming police commissioner",
    created_at: "2025-12-22T10:00:00Z",
  },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatUSD(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

type TabValue = "all" | "pending" | "escrow" | "completed";

// ---------------------------------------------------------------------------
// Stripe Connect Banner
// ---------------------------------------------------------------------------

function StripeConnectBanner({ isEditor }: { isEditor: boolean }) {
  const [connected, setConnected] = useState(false);

  if (connected) {
    return (
      <div className="mb-6 flex items-center justify-between rounded-[5px] border border-green-200 bg-green-50 p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-[5px] bg-green-100">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-green-900">
              Stripe Connected
            </p>
            <p className="text-xs text-green-700">
              {isEditor
                ? "Your newsroom is connected to Stripe. Payments will be processed automatically."
                : "Your Stripe account is connected. You'll receive payouts directly to your bank."}
            </p>
          </div>
        </div>
        <a
          href="https://dashboard.stripe.com"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex h-8 items-center gap-1.5 rounded-[3px] border border-green-300 bg-white px-3 text-xs font-medium text-green-700 transition-colors hover:bg-green-50"
        >
          <ExternalLink className="h-3 w-3" />
          Stripe Dashboard
        </a>
      </div>
    );
  }

  return (
    <div className="mb-6 rounded-[5px] border border-ink-200 bg-white p-5">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[5px] bg-[#635BFF]/10">
            <CreditCard className="h-5 w-5 text-[#635BFF]" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-ink-950">
              {isEditor ? "Connect Stripe to Pay Freelancers" : "Connect Stripe to Get Paid"}
            </h3>
            <p className="mt-1 text-xs text-ink-500 max-w-md">
              {isEditor
                ? "Connect your Stripe account to securely manage escrow payments, release funds to freelancers, and track all transactions in one place."
                : "Set up Stripe Connect to receive payments directly to your bank account when editors release funds for completed assignments."}
            </p>
            <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-400">
              <span>Secure payments via Stripe</span>
              <span>Automatic escrow management</span>
              <span>Direct bank payouts</span>
            </div>
          </div>
        </div>
        <button
          onClick={() => setConnected(true)}
          className="shrink-0 inline-flex h-9 items-center gap-1.5 rounded-[3px] bg-[#635BFF] px-4 text-sm font-medium text-white transition-colors hover:bg-[#4B45C6]"
        >
          <CreditCard className="h-4 w-4" />
          Connect Stripe
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function PaymentsPage() {
  const { user } = useAuth();
  const isEditor = user?.role === "editor";
  const [tab, setTab] = useState<TabValue>("all");

  const totals = useMemo(() => {
    const completed = MOCK_PAYMENTS.filter((p) => p.status === "completed").reduce(
      (s, p) => s + p.gross_amount,
      0
    );
    const escrow = MOCK_PAYMENTS.filter((p) => p.status === "escrow_held").reduce(
      (s, p) => s + p.gross_amount,
      0
    );
    const pending = MOCK_PAYMENTS.filter((p) => p.status === "pending").reduce(
      (s, p) => s + p.gross_amount,
      0
    );
    return { completed, escrow, pending };
  }, []);

  const filtered = useMemo(() => {
    switch (tab) {
      case "pending":
        return MOCK_PAYMENTS.filter((p) => p.status === "pending");
      case "escrow":
        return MOCK_PAYMENTS.filter((p) => p.status === "escrow_held");
      case "completed":
        return MOCK_PAYMENTS.filter((p) => p.status === "completed");
      default:
        return MOCK_PAYMENTS;
    }
  }, [tab]);

  return (
    <>
      <Header title="Payments" subtitle="Track assignment payments" />
      <PageWrapper>
        {/* Stripe Connect */}
        <StripeConnectBanner isEditor={isEditor ?? true} />

        {/* Summary cards */}
        <div className="grid grid-cols-3 gap-4">
          <SummaryCard
            icon={<DollarSign className="h-4 w-4 text-green-600" />}
            label="Total Paid"
            value={formatUSD(totals.completed)}
            context={`${MOCK_PAYMENTS.filter((p) => p.status === "completed").length} completed`}
          />
          <SummaryCard
            icon={<Landmark className="h-4 w-4 text-blue-600" />}
            label="In Escrow"
            value={formatUSD(totals.escrow)}
            context={`${MOCK_PAYMENTS.filter((p) => p.status === "escrow_held").length} held`}
          />
          <SummaryCard
            icon={<Clock className="h-4 w-4 text-ink-500" />}
            label="Pending"
            value={formatUSD(totals.pending)}
            context={`${MOCK_PAYMENTS.filter((p) => p.status === "pending").length} awaiting action`}
          />
        </div>

        {/* Tabs + Table */}
        <div className="mt-6 rounded-[5px] border border-ink-200 bg-white">
          <Tabs
            value={tab}
            onValueChange={(v) => setTab(v as TabValue)}
            className="w-full"
          >
            <div className="border-b border-ink-200 px-5 pt-3">
              <TabsList variant="line">
                <TabsTrigger value="all" className="text-sm">
                  All
                </TabsTrigger>
                <TabsTrigger value="pending" className="text-sm">
                  Pending
                </TabsTrigger>
                <TabsTrigger value="escrow" className="text-sm">
                  In Escrow
                </TabsTrigger>
                <TabsTrigger value="completed" className="text-sm">
                  Completed
                </TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value={tab}>
              <Table>
                <TableHeader>
                  <TableRow className="border-ink-200">
                    <TableHead className="pl-5 text-xs font-medium text-ink-500">
                      Description
                    </TableHead>
                    <TableHead className="text-xs font-medium text-ink-500">
                      Freelancer
                    </TableHead>
                    <TableHead className="text-right text-xs font-medium text-ink-500">
                      Gross Amount
                    </TableHead>
                    <TableHead className="text-right text-xs font-medium text-ink-500">
                      Platform Fee
                    </TableHead>
                    <TableHead className="text-right text-xs font-medium text-ink-500">
                      Net Amount
                    </TableHead>
                    <TableHead className="text-xs font-medium text-ink-500">
                      Status
                    </TableHead>
                    <TableHead className="pr-5 text-xs font-medium text-ink-500">
                      Date
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filtered.length === 0 ? (
                    <TableRow>
                      <TableCell
                        colSpan={7}
                        className="py-10 text-center text-sm text-ink-400"
                      >
                        No payments found in this category.
                      </TableCell>
                    </TableRow>
                  ) : (
                    filtered.map((payment) => (
                      <TableRow
                        key={payment.id}
                        className="border-ink-200 hover:bg-ink-50"
                      >
                        <TableCell className="pl-5 text-sm font-medium text-ink-950">
                          {payment.description ?? "--"}
                        </TableCell>
                        <TableCell className="text-sm text-ink-600">
                          {FREELANCER_NAMES[payment.freelancer_id] ?? "Unknown"}
                        </TableCell>
                        <TableCell className="text-right text-sm tabular-nums text-ink-950">
                          {formatUSD(payment.gross_amount)}
                        </TableCell>
                        <TableCell className="text-right text-sm tabular-nums text-ink-400">
                          {formatUSD(payment.platform_fee)}
                        </TableCell>
                        <TableCell className="text-right text-sm tabular-nums text-ink-950">
                          {formatUSD(payment.net_amount)}
                        </TableCell>
                        <TableCell>
                          <PaymentStatusBadge status={payment.status} />
                        </TableCell>
                        <TableCell className="pr-5 text-sm text-ink-500">
                          {formatDate(payment.created_at)}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TabsContent>
          </Tabs>
        </div>
      </PageWrapper>
    </>
  );
}

// ---------------------------------------------------------------------------
// Summary card sub-component
// ---------------------------------------------------------------------------

function SummaryCard({
  icon,
  label,
  value,
  context,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  context: string;
}) {
  return (
    <div className="rounded-[5px] border border-ink-200 bg-white p-5">
      <div className="flex items-center gap-2">
        {icon}
        <p className="text-xs font-medium text-ink-500">{label}</p>
      </div>
      <p className="mt-1 text-[28px] font-bold leading-tight text-ink-950">
        {value}
      </p>
      <p className="mt-1 text-xs text-ink-400">{context}</p>
    </div>
  );
}
