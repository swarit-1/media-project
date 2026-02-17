import { api } from "./client";
import type {
  PitchWindow,
  Pitch,
  Assignment,
  PaginatedResponse,
} from "@/types";

// ---- Pitch Windows ----

export function listPitchWindows(params?: { status?: string; beats?: string }) {
  const query = new URLSearchParams();
  if (params?.status) query.set("status", params.status);
  if (params?.beats) query.set("beats", params.beats);
  const qs = query.toString();
  return api.get<PaginatedResponse<PitchWindow>>(`/pitch-windows/${qs ? `?${qs}` : ""}`);
}

export function getPitchWindow(windowId: string) {
  return api.get<PitchWindow>(`/pitch-windows/${windowId}`);
}

export function createPitchWindow(data: Partial<PitchWindow>) {
  return api.post<PitchWindow>("/pitch-windows/", data);
}

export function updatePitchWindow(windowId: string, data: Partial<PitchWindow>) {
  return api.patch<PitchWindow>(`/pitch-windows/${windowId}`, data);
}

export function openPitchWindow(windowId: string) {
  return api.post<PitchWindow>(`/pitch-windows/${windowId}/open`);
}

export function closePitchWindow(windowId: string) {
  return api.post<PitchWindow>(`/pitch-windows/${windowId}/close`);
}

// ---- Pitches ----

export function listMyPitches() {
  return api.get<PaginatedResponse<Pitch>>("/pitches/my");
}

export function listWindowPitches(windowId: string) {
  return api.get<PaginatedResponse<Pitch>>(`/pitches/window/${windowId}`);
}

export function getPitch(pitchId: string) {
  return api.get<Pitch>(`/pitches/${pitchId}`);
}

export function createPitch(data: Partial<Pitch>) {
  return api.post<Pitch>("/pitches/", data);
}

export function updatePitch(pitchId: string, data: Partial<Pitch>) {
  return api.patch<Pitch>(`/pitches/${pitchId}`, data);
}

export function submitPitch(pitchId: string) {
  return api.post<Pitch>(`/pitches/${pitchId}/submit`);
}

export function reviewPitch(pitchId: string, data: { decision: "accepted" | "rejected"; editor_notes?: string; rejection_reason?: string }) {
  return api.post<Pitch>(`/pitches/${pitchId}/review`, data);
}

export function withdrawPitch(pitchId: string) {
  return api.post<Pitch>(`/pitches/${pitchId}/withdraw`);
}

// ---- Assignments ----

export function listMyAssignments() {
  return api.get<PaginatedResponse<Assignment>>("/assignments/my");
}

export function listNewsroomAssignments() {
  return api.get<PaginatedResponse<Assignment>>("/assignments/newsroom");
}

export function getAssignment(assignmentId: string) {
  return api.get<Assignment>(`/assignments/${assignmentId}`);
}

export function updateAssignment(assignmentId: string, data: Partial<Assignment>) {
  return api.patch<Assignment>(`/assignments/${assignmentId}`, data);
}

export function updateAssignmentStatus(assignmentId: string, data: { status: string; revision_notes?: string }) {
  return api.post<Assignment>(`/assignments/${assignmentId}/status`, data);
}
