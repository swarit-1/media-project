"use client";

import { useState } from "react";
import { Header } from "@/components/layouts/header";
import { PageWrapper } from "@/components/layouts/page-wrapper";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useAuth } from "@/lib/hooks/use-auth";

export default function SettingsPage() {
  const { user } = useAuth();
  const [saving, setSaving] = useState(false);

  return (
    <>
      <Header title="Settings" subtitle="Manage your account and preferences" />
      <PageWrapper>
        <Tabs defaultValue="profile" className="w-full">
          <TabsList className="mb-6">
            <TabsTrigger value="profile">Profile</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="integrations">Integrations</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
          </TabsList>

          <TabsContent value="profile">
            <div className="max-w-2xl space-y-6">
              <div className="rounded-[5px] border border-ink-200 bg-white p-6">
                <h3 className="text-sm font-semibold text-ink-950">
                  Personal Information
                </h3>
                <p className="mt-1 text-xs text-ink-500">
                  Update your name and contact details
                </p>
                <div className="mt-5 grid grid-cols-2 gap-4">
                  <div>
                    <label className="mb-1.5 block text-sm font-medium text-ink-700">
                      First name
                    </label>
                    <input
                      type="text"
                      defaultValue={user?.first_name || ""}
                      className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
                    />
                  </div>
                  <div>
                    <label className="mb-1.5 block text-sm font-medium text-ink-700">
                      Last name
                    </label>
                    <input
                      type="text"
                      defaultValue={user?.last_name || ""}
                      className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="mb-1.5 block text-sm font-medium text-ink-700">
                      Email
                    </label>
                    <input
                      type="email"
                      defaultValue={user?.email || ""}
                      className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
                    />
                  </div>
                </div>
                <div className="mt-5 flex justify-end">
                  <button
                    disabled={saving}
                    className="flex h-9 items-center justify-center rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {saving ? "Saving..." : "Save changes"}
                  </button>
                </div>
              </div>

              <div className="rounded-[5px] border border-ink-200 bg-white p-6">
                <h3 className="text-sm font-semibold text-ink-950">Role</h3>
                <p className="mt-1 text-xs text-ink-500">
                  Your account role determines what features you can access
                </p>
                <div className="mt-4 flex items-center gap-3">
                  <span className="inline-flex h-7 items-center rounded-[3px] bg-ink-100 px-2.5 text-xs font-medium capitalize text-ink-700">
                    {user?.role || "—"}
                  </span>
                  <span className="text-xs text-ink-400">
                    Contact support to change your role
                  </span>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="notifications">
            <div className="max-w-2xl">
              <div className="rounded-[5px] border border-ink-200 bg-white p-6">
                <h3 className="text-sm font-semibold text-ink-950">
                  Email Notifications
                </h3>
                <p className="mt-1 text-xs text-ink-500">
                  Choose which emails you want to receive
                </p>
                <div className="mt-5 space-y-4">
                  {[
                    {
                      label: "New pitch submissions",
                      desc: "Get notified when a freelancer submits a pitch",
                    },
                    {
                      label: "Assignment updates",
                      desc: "Receive updates when assignment status changes",
                    },
                    {
                      label: "Payment confirmations",
                      desc: "Get notified when payments are processed",
                    },
                    {
                      label: "Weekly digest",
                      desc: "A summary of your newsroom activity each week",
                    },
                  ].map((item) => (
                    <label
                      key={item.label}
                      className="flex items-start gap-3 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        defaultChecked
                        className="mt-0.5 h-4 w-4 rounded-[2px] border-ink-300 text-accent-600 focus:ring-accent-500/20"
                      />
                      <div>
                        <p className="text-sm font-medium text-ink-900">
                          {item.label}
                        </p>
                        <p className="text-xs text-ink-500">{item.desc}</p>
                      </div>
                    </label>
                  ))}
                </div>
                <div className="mt-5 flex justify-end">
                  <button className="flex h-9 items-center justify-center rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800">
                    Save preferences
                  </button>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="integrations">
            <div className="max-w-2xl space-y-6">
              <div className="rounded-[5px] border border-ink-200 bg-white p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[5px] bg-blue-50">
                      <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none">
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" fill="#4285F4"/>
                        <path d="M14 2v6h6" fill="#A1C2FA"/>
                        <path d="M8 13h8M8 17h5" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-ink-950">
                        Google Docs
                      </h3>
                      <p className="mt-1 text-xs text-ink-500">
                        Connect Google Docs to collaborate on drafts, review
                        submissions, and share documents with freelancers
                        directly from the platform.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => alert("Google Docs integration coming soon!")}
                    className="shrink-0 inline-flex h-9 items-center justify-center rounded-[3px] border border-ink-200 bg-white px-4 text-sm font-medium text-ink-700 transition-colors hover:bg-ink-50"
                  >
                    Connect
                  </button>
                </div>
              </div>

              <div className="rounded-[5px] border border-ink-200 bg-white p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[5px] bg-purple-50">
                      <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none">
                        <path d="M14.5 2L6 10.5v5L9.5 19l8.5-8.5v-5L14.5 2z" fill="#611F69"/>
                        <circle cx="12" cy="10.5" r="1.5" fill="white"/>
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-ink-950">
                        Slack
                      </h3>
                      <p className="mt-1 text-xs text-ink-500">
                        Integrate with Slack to receive notifications about
                        pitch submissions, assignment updates, and payment
                        status changes in your preferred channels.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => alert("Slack integration coming soon!")}
                    className="shrink-0 inline-flex h-9 items-center justify-center rounded-[3px] border border-ink-200 bg-white px-4 text-sm font-medium text-ink-700 transition-colors hover:bg-ink-50"
                  >
                    Connect
                  </button>
                </div>
              </div>

              <div className="rounded-[5px] border border-dashed border-ink-200 bg-ink-50 p-6 text-center">
                <p className="text-sm text-ink-500">
                  More integrations coming soon
                </p>
                <p className="mt-1 text-xs text-ink-400">
                  CMS, analytics, and payment provider integrations are on the
                  roadmap.
                </p>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="security">
            <div className="max-w-2xl space-y-6">
              <div className="rounded-[5px] border border-ink-200 bg-white p-6">
                <h3 className="text-sm font-semibold text-ink-950">
                  Change Password
                </h3>
                <p className="mt-1 text-xs text-ink-500">
                  Update your password to keep your account secure
                </p>
                <div className="mt-5 space-y-4">
                  <div>
                    <label className="mb-1.5 block text-sm font-medium text-ink-700">
                      Current password
                    </label>
                    <input
                      type="password"
                      className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
                    />
                  </div>
                  <div>
                    <label className="mb-1.5 block text-sm font-medium text-ink-700">
                      New password
                    </label>
                    <input
                      type="password"
                      className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
                    />
                  </div>
                  <div>
                    <label className="mb-1.5 block text-sm font-medium text-ink-700">
                      Confirm new password
                    </label>
                    <input
                      type="password"
                      className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
                    />
                  </div>
                </div>
                <div className="mt-5 flex justify-end">
                  <button className="flex h-9 items-center justify-center rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800">
                    Update password
                  </button>
                </div>
              </div>

              <div className="rounded-[5px] border border-danger-100 bg-white p-6">
                <h3 className="text-sm font-semibold text-danger-600">
                  Danger Zone
                </h3>
                <p className="mt-1 text-xs text-ink-500">
                  Permanently delete your account and all associated data
                </p>
                <div className="mt-4">
                  <button className="flex h-9 items-center justify-center rounded-[3px] border border-danger-600 px-4 text-sm font-medium text-danger-600 transition-colors hover:bg-danger-100">
                    Delete account
                  </button>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </PageWrapper>
    </>
  );
}
