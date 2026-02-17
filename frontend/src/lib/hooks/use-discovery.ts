import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { searchFreelancers, getFreelancerProfile, type SearchFilters } from "@/lib/api/discovery";

export function useSearchFreelancers(filters: SearchFilters, enabled = true) {
  return useQuery({
    queryKey: ["discovery", "search", filters],
    queryFn: () => searchFreelancers(filters),
    enabled,
  });
}

export function useFreelancerProfile(freelancerId: string | undefined) {
  return useQuery({
    queryKey: ["discovery", "freelancer", freelancerId],
    queryFn: () => getFreelancerProfile(freelancerId!),
    enabled: !!freelancerId,
  });
}
