"use client";

import { useState } from "react";
import { Header } from "@/components/layouts/header";
import { PageWrapper } from "@/components/layouts/page-wrapper";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Users, Plus, MoreHorizontal, MapPin, Star, Trash2 } from "lucide-react";

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

const INITIAL_SQUADS: Squad[] = [
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

function CreateSquadDialog({
  trigger,
  onSave,
}: {
  trigger: React.ReactNode;
  onSave: (name: string, description: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  function handleSave() {
    if (!name.trim()) return;
    onSave(name.trim(), description.trim());
    setName("");
    setDescription("");
    setOpen(false);
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <DialogTitle>Create Squad</DialogTitle>
          <DialogDescription>
            Organize freelancers into a team for specific beats or projects.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-2">
          <div className="grid gap-1.5">
            <Label htmlFor="squad-name" className="text-sm">
              Squad Name
            </Label>
            <Input
              id="squad-name"
              className="h-9 rounded-[3px] text-sm"
              placeholder="e.g. City Hall Bureau"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor="squad-desc" className="text-sm">
              Description
            </Label>
            <Textarea
              id="squad-desc"
              className="min-h-[60px] rounded-[3px] text-sm"
              placeholder="What does this squad cover?"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
        </div>
        <DialogFooter>
          <button
            type="button"
            onClick={() => setOpen(false)}
            className="inline-flex h-9 items-center justify-center rounded-[3px] border border-ink-200 bg-white px-4 text-sm font-medium text-ink-700 transition-colors hover:bg-ink-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={!name.trim()}
            className="inline-flex h-9 items-center justify-center rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Create Squad
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function AddMemberDialog({
  trigger,
  squadName,
  onAdd,
}: {
  trigger: React.ReactNode;
  squadName: string;
  onAdd: (name: string, beats: string, location: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [beats, setBeats] = useState("");
  const [location, setLocation] = useState("");

  function handleAdd() {
    if (!name.trim()) return;
    onAdd(name.trim(), beats.trim(), location.trim());
    setName("");
    setBeats("");
    setLocation("");
    setOpen(false);
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <DialogTitle>Add Member to {squadName}</DialogTitle>
          <DialogDescription>
            Add a freelancer to this squad.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-2">
          <div className="grid gap-1.5">
            <Label htmlFor="member-name" className="text-sm">Name</Label>
            <Input id="member-name" className="h-9 rounded-[3px] text-sm" placeholder="Freelancer name" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor="member-beats" className="text-sm">Beats</Label>
            <Input id="member-beats" className="h-9 rounded-[3px] text-sm" placeholder="e.g. Politics, Government" value={beats} onChange={(e) => setBeats(e.target.value)} />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor="member-location" className="text-sm">Location</Label>
            <Input id="member-location" className="h-9 rounded-[3px] text-sm" placeholder="e.g. New York, NY" value={location} onChange={(e) => setLocation(e.target.value)} />
          </div>
        </div>
        <DialogFooter>
          <button type="button" onClick={() => setOpen(false)} className="inline-flex h-9 items-center justify-center rounded-[3px] border border-ink-200 bg-white px-4 text-sm font-medium text-ink-700 transition-colors hover:bg-ink-50">Cancel</button>
          <button type="button" onClick={handleAdd} disabled={!name.trim()} className="inline-flex h-9 items-center justify-center rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-40">Add Member</button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function SquadOptionsMenu({ onDelete }: { onDelete: () => void }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex h-8 w-8 items-center justify-center rounded-[3px] text-ink-400 transition-colors hover:bg-ink-100 hover:text-ink-600"
      >
        <MoreHorizontal className="h-4 w-4" />
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-full z-50 mt-1 w-40 rounded-[5px] border border-ink-200 bg-white py-1 shadow-lg">
            <button
              onClick={() => { setOpen(false); onDelete(); }}
              className="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-red-600 transition-colors hover:bg-red-50"
            >
              <Trash2 className="h-3.5 w-3.5" />
              Delete Squad
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default function SquadsPage() {
  const [squads, setSquads] = useState(INITIAL_SQUADS);

  function handleCreateSquad(name: string, description: string) {
    const newSquad: Squad = {
      id: `sq-${Date.now()}`,
      name,
      description,
      members: [],
      created_at: new Date().toISOString().split("T")[0],
    };
    setSquads((prev) => [...prev, newSquad]);
  }

  function handleDeleteSquad(squadId: string) {
    setSquads((prev) => prev.filter((s) => s.id !== squadId));
  }

  function handleAddMember(squadId: string, name: string, beats: string, location: string) {
    const newMember: SquadMember = {
      id: `mem-${Date.now()}`,
      display_name: name,
      primary_beats: beats.split(",").map((b) => b.trim()).filter(Boolean),
      location: location || "Unknown",
      trust_score: 80,
      availability: "available",
    };
    setSquads((prev) =>
      prev.map((s) => s.id === squadId ? { ...s, members: [...s.members, newMember] } : s)
    );
  }

  function handleRemoveMember(squadId: string, memberId: string) {
    setSquads((prev) =>
      prev.map((s) => s.id === squadId ? { ...s, members: s.members.filter((m) => m.id !== memberId) } : s)
    );
  }

  return (
    <>
      <Header
        title="Squads"
        subtitle="Organize your trusted freelancers into teams"
        actions={
          <CreateSquadDialog
            trigger={
              <button className="flex h-9 items-center gap-2 rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800">
                <Plus className="h-4 w-4" />
                Create Squad
              </button>
            }
            onSave={handleCreateSquad}
          />
        }
      />
      <PageWrapper>
        {squads.length === 0 ? (
          <div className="rounded-[5px] border border-ink-200 bg-white p-10 text-center">
            <Users className="mx-auto h-10 w-10 text-ink-300" />
            <p className="mt-3 text-sm font-medium text-ink-700">No squads yet</p>
            <p className="mt-1 text-xs text-ink-400">Create a squad to organize your freelancers into teams.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {squads.map((squad) => (
              <div key={squad.id} className="rounded-[5px] border border-ink-200 bg-white">
                <div className="flex items-center justify-between border-b border-ink-100 px-5 py-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-[5px] bg-ink-100">
                      <Users className="h-4 w-4 text-ink-600" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-ink-950">{squad.name}</h3>
                      <p className="text-xs text-ink-500">{squad.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-ink-400">
                      {squad.members.length} member{squad.members.length !== 1 ? "s" : ""}
                    </span>
                    <SquadOptionsMenu onDelete={() => handleDeleteSquad(squad.id)} />
                  </div>
                </div>

                {squad.members.length > 0 ? (
                  <div className="divide-y divide-ink-100">
                    {squad.members.map((member) => (
                      <div key={member.id} className="flex items-center justify-between px-5 py-3">
                        <div className="flex items-center gap-3">
                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-ink-100 text-xs font-medium text-ink-600">
                            {member.display_name.split(" ").map((n) => n[0]).join("")}
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-ink-900">{member.display_name}</span>
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
                              <Badge key={beat} variant="secondary" className="text-[11px]">{beat}</Badge>
                            ))}
                          </div>
                          <div className="flex items-center gap-1 text-xs text-ink-500">
                            <Star className="h-3 w-3 text-warning-600" />
                            {member.trust_score}
                          </div>
                          <button
                            onClick={() => handleRemoveMember(squad.id, member.id)}
                            className="flex h-7 w-7 items-center justify-center rounded-[3px] text-ink-400 transition-colors hover:bg-red-50 hover:text-red-500"
                            title="Remove member"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="px-5 py-6 text-center">
                    <p className="text-xs text-ink-400">No members yet</p>
                  </div>
                )}

                <div className="border-t border-ink-100 px-5 py-3">
                  <AddMemberDialog
                    trigger={
                      <button className="flex items-center gap-1.5 text-xs font-medium text-accent-600 transition-colors hover:text-accent-700">
                        <Plus className="h-3.5 w-3.5" />
                        Add member
                      </button>
                    }
                    squadName={squad.name}
                    onAdd={(name, beats, location) => handleAddMember(squad.id, name, beats, location)}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </PageWrapper>
    </>
  );
}
