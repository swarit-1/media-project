"use client";

import { useState } from "react";
import { Send } from "lucide-react";
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

interface SubmitPitchFormProps {
  trigger: React.ReactNode;
  windowTitle?: string;
  onSubmit?: (data: PitchFormData) => void;
}

export interface PitchFormData {
  headline: string;
  summary: string;
  approach: string;
  estimated_word_count: number | null;
  proposed_rate: number | null;
  estimated_delivery_days: number | null;
}

export function SubmitPitchForm({
  trigger,
  windowTitle,
  onSubmit,
}: SubmitPitchFormProps) {
  const [open, setOpen] = useState(false);
  const [headline, setHeadline] = useState("");
  const [summary, setSummary] = useState("");
  const [approach, setApproach] = useState("");
  const [wordCount, setWordCount] = useState("");
  const [proposedRate, setProposedRate] = useState("");
  const [deliveryDays, setDeliveryDays] = useState("");

  function resetForm() {
    setHeadline("");
    setSummary("");
    setApproach("");
    setWordCount("");
    setProposedRate("");
    setDeliveryDays("");
  }

  function handleSubmit() {
    if (!headline.trim() || !summary.trim()) return;

    const data: PitchFormData = {
      headline: headline.trim(),
      summary: summary.trim(),
      approach: approach.trim(),
      estimated_word_count: wordCount ? parseInt(wordCount, 10) : null,
      proposed_rate: proposedRate ? parseFloat(proposedRate) : null,
      estimated_delivery_days: deliveryDays ? parseInt(deliveryDays, 10) : null,
    };

    onSubmit?.(data);
    resetForm();
    setOpen(false);
  }

  function handleOpenChange(nextOpen: boolean) {
    setOpen(nextOpen);
    if (!nextOpen) {
      resetForm();
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-[560px]">
        <DialogHeader>
          <DialogTitle>Submit a Pitch</DialogTitle>
          <DialogDescription>
            {windowTitle
              ? `Pitching for: ${windowTitle}`
              : "Fill in the details for your pitch submission."}
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-2">
          {/* Headline */}
          <div className="grid gap-1.5">
            <Label htmlFor="pitch-headline" className="text-sm">
              Headline <span className="text-red-500">*</span>
            </Label>
            <Input
              id="pitch-headline"
              className="h-9 rounded-[3px] text-sm"
              placeholder="A compelling headline for your story"
              value={headline}
              onChange={(e) => setHeadline(e.target.value)}
            />
          </div>

          {/* Summary */}
          <div className="grid gap-1.5">
            <Label htmlFor="pitch-summary" className="text-sm">
              Summary <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="pitch-summary"
              className="min-h-[80px] rounded-[3px] text-sm"
              placeholder="Summarize the story you want to tell, the angle, and why it matters now..."
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
            />
          </div>

          {/* Approach (optional) */}
          <div className="grid gap-1.5">
            <Label htmlFor="pitch-approach" className="text-sm">
              Approach
              <span className="ml-1 text-xs font-normal text-ink-400">
                (optional)
              </span>
            </Label>
            <Textarea
              id="pitch-approach"
              className="min-h-[60px] rounded-[3px] text-sm"
              placeholder="How do you plan to report this story? Sources, methodology, access..."
              value={approach}
              onChange={(e) => setApproach(e.target.value)}
            />
          </div>

          {/* Estimated Word Count, Proposed Rate, Delivery Days */}
          <div className="grid grid-cols-3 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor="pitch-word-count" className="text-sm">
                Est. Word Count
              </Label>
              <Input
                id="pitch-word-count"
                type="number"
                className="h-9 rounded-[3px] text-sm"
                placeholder="1500"
                min={0}
                value={wordCount}
                onChange={(e) => setWordCount(e.target.value)}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="pitch-rate" className="text-sm">
                Proposed Rate ($)
              </Label>
              <Input
                id="pitch-rate"
                type="number"
                className="h-9 rounded-[3px] text-sm"
                placeholder="500"
                min={0}
                step="0.01"
                value={proposedRate}
                onChange={(e) => setProposedRate(e.target.value)}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="pitch-delivery" className="text-sm">
                Delivery (days)
              </Label>
              <Input
                id="pitch-delivery"
                type="number"
                className="h-9 rounded-[3px] text-sm"
                placeholder="14"
                min={1}
                value={deliveryDays}
                onChange={(e) => setDeliveryDays(e.target.value)}
              />
            </div>
          </div>
        </div>

        <DialogFooter>
          <button
            type="button"
            onClick={() => handleOpenChange(false)}
            className="inline-flex h-9 items-center justify-center rounded-[3px] border border-ink-200 bg-white px-4 text-sm font-medium text-ink-700 transition-colors hover:bg-ink-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!headline.trim() || !summary.trim()}
            className="inline-flex h-9 items-center justify-center gap-1.5 rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Send className="h-4 w-4" />
            Submit Pitch
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
