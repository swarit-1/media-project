"use client";

import { useState } from "react";
import { CalendarDays } from "lucide-react";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface PitchWindowFormProps {
  trigger: React.ReactNode;
  defaultValues?: {
    title?: string;
    description?: string;
    beats?: string;
    budget_min?: number;
    budget_max?: number;
    rate_type?: string;
    max_pitches?: number;
    opens_at?: string;
    closes_at?: string;
  };
  mode?: "create" | "edit";
}

export function PitchWindowForm({
  trigger,
  defaultValues,
  mode = "create",
}: PitchWindowFormProps) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState(defaultValues?.title ?? "");
  const [description, setDescription] = useState(
    defaultValues?.description ?? ""
  );
  const [beats, setBeats] = useState(defaultValues?.beats ?? "");
  const [budgetMin, setBudgetMin] = useState<string>(
    defaultValues?.budget_min?.toString() ?? ""
  );
  const [budgetMax, setBudgetMax] = useState<string>(
    defaultValues?.budget_max?.toString() ?? ""
  );
  const [rateType, setRateType] = useState(
    defaultValues?.rate_type ?? "per_word"
  );
  const [maxPitches, setMaxPitches] = useState<string>(
    defaultValues?.max_pitches?.toString() ?? "20"
  );
  const [opensAt, setOpensAt] = useState(defaultValues?.opens_at ?? "");
  const [closesAt, setClosesAt] = useState(defaultValues?.closes_at ?? "");

  function handleSaveDraft() {
    // TODO: Save as draft via API
    setOpen(false);
  }

  function handlePublish() {
    // TODO: Publish via API
    setOpen(false);
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-[560px]">
        <DialogHeader>
          <DialogTitle>
            {mode === "create" ? "Create Pitch Window" : "Edit Pitch Window"}
          </DialogTitle>
          <DialogDescription>
            Define what you are looking for and set the submission window.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-2">
          {/* Title */}
          <div className="grid gap-1.5">
            <Label htmlFor="pw-title" className="text-sm">
              Title
            </Label>
            <Input
              id="pw-title"
              className="h-9 rounded-[3px] text-sm"
              placeholder="e.g. Climate & Environment Features - Spring 2026"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          {/* Description */}
          <div className="grid gap-1.5">
            <Label htmlFor="pw-description" className="text-sm">
              Description
            </Label>
            <Textarea
              id="pw-description"
              className="min-h-[80px] rounded-[3px] text-sm"
              placeholder="Describe the topics, angle, and tone you are looking for..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          {/* Beats */}
          <div className="grid gap-1.5">
            <Label htmlFor="pw-beats" className="text-sm">
              Beats
            </Label>
            <Input
              id="pw-beats"
              className="h-9 rounded-[3px] text-sm"
              placeholder="Comma-separated, e.g. Climate, Environment, Policy"
              value={beats}
              onChange={(e) => setBeats(e.target.value)}
            />
            <p className="text-xs text-ink-400">
              Separate multiple beats with commas.
            </p>
          </div>

          {/* Budget Range */}
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor="pw-budget-min" className="text-sm">
                Budget Min ($)
              </Label>
              <Input
                id="pw-budget-min"
                type="number"
                className="h-9 rounded-[3px] text-sm"
                placeholder="200"
                value={budgetMin}
                onChange={(e) => setBudgetMin(e.target.value)}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="pw-budget-max" className="text-sm">
                Budget Max ($)
              </Label>
              <Input
                id="pw-budget-max"
                type="number"
                className="h-9 rounded-[3px] text-sm"
                placeholder="800"
                value={budgetMax}
                onChange={(e) => setBudgetMax(e.target.value)}
              />
            </div>
          </div>

          {/* Rate Type & Max Pitches */}
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label className="text-sm">Rate Type</Label>
              <Select value={rateType} onValueChange={setRateType}>
                <SelectTrigger className="h-9 w-full rounded-[3px] text-sm">
                  <SelectValue placeholder="Select rate type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="per_word">Per Word</SelectItem>
                  <SelectItem value="flat_rate">Flat Rate</SelectItem>
                  <SelectItem value="hourly">Hourly</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="pw-max-pitches" className="text-sm">
                Max Pitches
              </Label>
              <Input
                id="pw-max-pitches"
                type="number"
                className="h-9 rounded-[3px] text-sm"
                placeholder="20"
                value={maxPitches}
                onChange={(e) => setMaxPitches(e.target.value)}
              />
            </div>
          </div>

          {/* Opens At / Closes At */}
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor="pw-opens-at" className="text-sm">
                Opens At
              </Label>
              <div className="relative">
                <Input
                  id="pw-opens-at"
                  type="date"
                  className="h-9 rounded-[3px] text-sm"
                  value={opensAt}
                  onChange={(e) => setOpensAt(e.target.value)}
                />
              </div>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="pw-closes-at" className="text-sm">
                Closes At
              </Label>
              <div className="relative">
                <Input
                  id="pw-closes-at"
                  type="date"
                  className="h-9 rounded-[3px] text-sm"
                  value={closesAt}
                  onChange={(e) => setClosesAt(e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <button
            type="button"
            onClick={handleSaveDraft}
            className="inline-flex h-9 items-center justify-center rounded-[3px] border border-ink-200 bg-white px-4 text-sm font-medium text-ink-700 transition-colors hover:bg-ink-50"
          >
            Save as Draft
          </button>
          <button
            type="button"
            onClick={handlePublish}
            className="inline-flex h-9 items-center justify-center rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800"
          >
            <CalendarDays className="mr-1.5 h-4 w-4" />
            Publish Window
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
