import { api } from "./client";
import type { FreelancerProfile, PaginatedResponse } from "@/types";

export interface SearchFilters {
  beats?: string[];
  location?: string;
  availability_status?: string;
  min_trust_score?: number;
  rate_type?: string;
  min_rate?: number;
  max_rate?: number;
  page?: number;
  per_page?: number;
}

export function searchFreelancers(filters: SearchFilters) {
  return api.post<PaginatedResponse<FreelancerProfile>>("/discovery/search", filters);
}

export function getFreelancerProfile(freelancerId: string) {
  return api.get<FreelancerProfile>(`/discovery/freelancers/${freelancerId}`);
}
