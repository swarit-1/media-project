"use client";

import { useState } from "react";
import { Header } from "@/components/layouts/header";
import { PageWrapper } from "@/components/layouts/page-wrapper";
import { Badge } from "@/components/ui/badge";
import { Users, Plus, MoreHorizontal, MapPin, Star } from "lucide-react";

interface SquadMember {
  id: string;
  display_name: string;
  primary_beats: string[];
  location: string;
  trust_score: number;
  availability: string;
}

interface Squad {
  id: string;
  name: string;
  description: string;
  members: SquadMember[];
  created_at: string;
}

const mockSquads: Squad[] = [
  {
    id: "1",
    name: "City Hall Bureau",
    description: "Reporters covering local government and politics",
    members: [
      { id: "1", display_name: "Marcus Johnson", primary_beats: ["Politics", "Government"], location: "Washington, DC", trust_score: 95, availability: "available" },
      { id: "2", display_name: "Elena Rodriguez", primary_beats: ["Politics", "Immigration"], location: "Austin, TX", trust_score: 91, availability: "available" },
      { id: "3", display_name: "David Kim", primary_beats: ["Government", "Policy"], location: "Sacramento, CA", trust_score: 88, availability: "busy" },
    ],
    created_at: "2025-11-15",
  },
  {
    id: "2",
    name: "Tech & Innovation",
    description: "Freelancers covering technology, AI, and startups",
    members: [
      { id: "4", display_name: "Sarah Chen", primary_beats: ["Technology", "AI"], location: "San Francisco, CA", trust_score: 97, availability: "available" },
      { id: "5", display_name: "James Wright", primary_beats: ["Startups", "Venture Capital"], location: "New York, NY", trust_score: 89, availability: "available" },
    ],
    created_at: "2025-12-01",
  },
  {
    id: "3",
    name: "Climate & Environment",
    description: "Environmental reporting specialists",
    members: [
      { id: "6", display_name: "Aisha Patel", primary_beats: ["Climate", "Energy"], location: "Denver, CO", trust_score: 93, availability: "available" },
      { id: "7", display_name: "Tom Nguyen", primary_beats: ["Environment", "Science"], location: "Portland, OR", trust_score: 90, availability: "unavailable" },
      { id: "8", display_name: "Rachel Green", primary_beats: ["Climate", "Policy"], location: "Boston, MA", trust_score: 86, availability: "available" },
      { id: "9", display_name: "Carlos Silva", primary_beats: ["Agriculture", "Environment"], location: "Miami, FL", trust_score: 84, availability: "busy" },
    ],
    created_at: "2026-01-10",
  },
];

function AvailabilityDot({ status }: { status: string }) {
  const colors: Record<string, string> = {
    available: "bg-success-600",
    busy: "bg-warning-600",
    unavailable: "bg-ink-400",
  };
  return <span className={`inline-block h-2 w-2 rounded-full ${colors[status] || "bg-ink-400"}`} />;
}

export default function SquadsPage() {
  const [squads] = useState(mockSquads);

  return (
    <>
      <Header
        title="Squads"
        subtitle="Organize your trusted freelancers into teams"
        actions={
          <button className="flex h-9 items-center gap-2 rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800">
            <Plus className="h-4 w-4" />
            Create Squad
          </button>
        }
      />
      <PageWrapper>
        <div className="space-y-4">
          {squads.map((squad) => (
            <div
              key={squad.id}
              className="rounded-[5px] border border-ink-200 bg-white"
            >
              <div className="flex items-center justify-between border-b border-ink-100 px-5 py-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-[5px] bg-ink-100">
                    <Users className="h-4 w-4 text-ink-600" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-ink-950">
                      {squad.name}
                    </h3>
                    <p className="text-xs text-ink-500">{squad.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-ink-400">
                    {squad.members.length} members
                  </span>
                  <button className="flex h-8 w-8 items-center justify-center rounded-[3px] text-ink-400 transition-colors hover:bg-ink-100 hover:text-ink-600">
                    <MoreHorizontal className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="divide-y divide-ink-100">
                {squad.members.map((member) => (
                  <div
                    key={member.id}
                    className="flex items-center justify-between px-5 py-3"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-ink-100 text-xs font-medium text-ink-600">
                        {member.display_name
                          .split(" ")
                          .map((n) => n[0])
                          .join("")}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-ink-900">
                            {member.display_name}
                          </span>
                          <AvailabilityDot status={member.availability} />
                        </div>
                        <div className="flex items-center gap-2 text-xs text-ink-500">
                          <MapPin className="h-3 w-3" />
                          {member.location}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="flex gap-1.5">
                        {member.primary_beats.map((beat) => (
                          <Badge
                            key={beat}
                            variant="secondary"
                            className="text-[11px]"
                          >
                            {beat}
                          </Badge>
                        ))}
                      </div>
                      <div className="flex items-center gap-1 text-xs text-ink-500">
                        <Star className="h-3 w-3 text-warning-600" />
                        {member.trust_score}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="border-t border-ink-100 px-5 py-3">
                <button className="flex items-center gap-1.5 text-xs font-medium text-accent-600 transition-colors hover:text-accent-700">
                  <Plus className="h-3.5 w-3.5" />
                  Add member
                </button>
              </div>
            </div>
          ))}
        </div>
      </PageWrapper>
    </>
  );
}
