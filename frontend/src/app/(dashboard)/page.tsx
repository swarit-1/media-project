import { Header } from "@/components/layouts/header";
import { PageWrapper } from "@/components/layouts/page-wrapper";

export default function DashboardPage() {
  return (
    <>
      <Header title="Dashboard" subtitle="Welcome to Elastic Newsroom" />
      <PageWrapper>
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: "Open Pitches", value: "12", change: "+3", context: "this week" },
            { label: "Active Assignments", value: "8", change: "2 at risk", context: "in progress" },
            { label: "Pending Payments", value: "$4,200", change: "", context: "awaiting release" },
            { label: "Response Rate", value: "94%", change: "+2%", context: "last 30 days" },
          ].map((stat) => (
            <div
              key={stat.label}
              className="rounded-[5px] border border-ink-200 bg-white p-5"
            >
              <p className="text-xs font-medium text-ink-500">{stat.label}</p>
              <p className="mt-1 text-[28px] font-bold leading-tight text-ink-950">
                {stat.value}
              </p>
              <p className="mt-1 text-xs text-ink-400">
                {stat.change && (
                  <span className="mr-1 text-success-600">{stat.change}</span>
                )}
                {stat.context}
              </p>
            </div>
          ))}
        </div>

        <div className="mt-6 rounded-[5px] border border-ink-200 bg-white p-5">
          <h2 className="text-lg font-semibold text-ink-950">Recent Activity</h2>
          <p className="mt-2 text-sm text-ink-500">
            Your recent activity will appear here once you start using the platform.
          </p>
        </div>
      </PageWrapper>
    </>
  );
}
