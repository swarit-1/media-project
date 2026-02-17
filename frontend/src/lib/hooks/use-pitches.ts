import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as pitchApi from "@/lib/api/pitches";
import type { PitchWindow } from "@/types";

// ---- Pitch Windows ----

export function usePitchWindows(params?: { status?: string; beats?: string }) {
  return useQuery({
    queryKey: ["pitch-windows", params],
    queryFn: () => pitchApi.listPitchWindows(params),
  });
}

export function usePitchWindow(windowId: string | undefined) {
  return useQuery({
    queryKey: ["pitch-windows", windowId],
    queryFn: () => pitchApi.getPitchWindow(windowId!),
    enabled: !!windowId,
  });
}

export function useCreatePitchWindow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: pitchApi.createPitchWindow,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["pitch-windows"] }),
  });
}

export function useUpdatePitchWindow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<PitchWindow> }) =>
      pitchApi.updatePitchWindow(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["pitch-windows"] }),
  });
}

// ---- Pitches ----

export function useMyPitches() {
  return useQuery({
    queryKey: ["pitches", "my"],
    queryFn: pitchApi.listMyPitches,
  });
}

export function useWindowPitches(windowId: string | undefined) {
  return useQuery({
    queryKey: ["pitches", "window", windowId],
    queryFn: () => pitchApi.listWindowPitches(windowId!),
    enabled: !!windowId,
  });
}

export function useCreatePitch() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: pitchApi.createPitch,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["pitches"] }),
  });
}

export function useSubmitPitch() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: pitchApi.submitPitch,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["pitches"] }),
  });
}

export function useReviewPitch() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ pitchId, data }: { pitchId: string; data: Parameters<typeof pitchApi.reviewPitch>[1] }) =>
      pitchApi.reviewPitch(pitchId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["pitches"] }),
  });
}

// ---- Assignments ----

export function useMyAssignments() {
  return useQuery({
    queryKey: ["assignments", "my"],
    queryFn: pitchApi.listMyAssignments,
  });
}

export function useNewsroomAssignments() {
  return useQuery({
    queryKey: ["assignments", "newsroom"],
    queryFn: pitchApi.listNewsroomAssignments,
  });
}

export function useAssignment(assignmentId: string | undefined) {
  return useQuery({
    queryKey: ["assignments", assignmentId],
    queryFn: () => pitchApi.getAssignment(assignmentId!),
    enabled: !!assignmentId,
  });
}

export function useUpdateAssignmentStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { status: string; revision_notes?: string } }) =>
      pitchApi.updateAssignmentStatus(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["assignments"] }),
  });
}
