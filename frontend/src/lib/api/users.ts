import { api } from "./client";
import type { User, FreelancerProfile } from "@/types";

export function getMe() {
  return api.get<User>("/users/me");
}

export function updateMe(data: Partial<User>) {
  return api.patch<User>("/users/me", data);
}

export function getFreelancerProfile(freelancerId: string) {
  return api.get<FreelancerProfile>(`/freelancers/${freelancerId}`);
}

export function updateFreelancerProfile(data: Partial<FreelancerProfile>) {
  return api.patch<FreelancerProfile>("/freelancers/me", data);
}

export function updateAvailability(data: { availability_status: string }) {
  return api.post("/freelancers/me/availability", data);
}

export interface Newsroom {
  id: string;
  name: string;
  slug: string;
  domain?: string;
  logo_url?: string;
  created_at: string;
}

export function createNewsroom(data: Partial<Newsroom>) {
  return api.post<Newsroom>("/newsrooms/", data);
}

export function getNewsroom(newsroomId: string) {
  return api.get<Newsroom>(`/newsrooms/${newsroomId}`);
}

export function updateNewsroom(newsroomId: string, data: Partial<Newsroom>) {
  return api.patch<Newsroom>(`/newsrooms/${newsroomId}`, data);
}
