import { api } from "./client";

export interface SquadTemplate {
  id: string;
  name: string;
  required_beats: string[];
  required_roles: string[];
  min_members: number;
  max_members: number;
  min_trust_score: number;
  created_at: string;
}

export interface SquadMember {
  id: string;
  freelancer_id: string;
  display_name?: string;
  status: "invited" | "accepted" | "declined" | "removed";
  role?: string;
  beats: string[];
}

export interface SquadInstance {
  id: string;
  template_id: string;
  name: string;
  status: "forming" | "active" | "completed" | "disbanded";
  project_brief?: string;
  members: SquadMember[];
  created_at: string;
}

// ---- Templates ----

export function createSquadTemplate(data: Partial<SquadTemplate>) {
  return api.post<SquadTemplate>("/squads/templates", data);
}

export function listSquadTemplates() {
  return api.get<SquadTemplate[]>("/squads/templates");
}

export function getSquadTemplate(id: string) {
  return api.get<SquadTemplate>(`/squads/templates/${id}`);
}

export function updateSquadTemplate(id: string, data: Partial<SquadTemplate>) {
  return api.patch<SquadTemplate>(`/squads/templates/${id}`, data);
}

export function deleteSquadTemplate(id: string) {
  return api.delete(`/squads/templates/${id}`);
}

// ---- Instances ----

export function createSquadInstance(data: { template_id: string; name: string; project_brief?: string }) {
  return api.post<SquadInstance>("/squads/instances", data);
}

export function listSquadInstances() {
  return api.get<SquadInstance[]>("/squads/instances");
}

export function getSquadInstance(id: string) {
  return api.get<SquadInstance>(`/squads/instances/${id}`);
}

export function activateSquad(id: string) {
  return api.post<SquadInstance>(`/squads/instances/${id}/activate`);
}

export function completeSquad(id: string) {
  return api.post<SquadInstance>(`/squads/instances/${id}/complete`);
}

export function disbandSquad(id: string) {
  return api.post<SquadInstance>(`/squads/instances/${id}/disband`);
}

export function inviteSquadMember(instanceId: string, data: { freelancer_id: string; role?: string; beats?: string[] }) {
  return api.post<SquadMember>(`/squads/instances/${instanceId}/members`, data);
}

export function respondToInvitation(memberId: string, data: { response: "accepted" | "declined" }) {
  return api.post(`/squads/members/${memberId}/respond`, data);
}

export function removeSquadMember(instanceId: string, memberId: string) {
  return api.delete(`/squads/instances/${instanceId}/members/${memberId}`);
}

export function listMyInvitations() {
  return api.get<SquadMember[]>("/squads/invitations/my");
}
