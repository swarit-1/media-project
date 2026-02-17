import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as mlApi from "@/lib/api/ml";

export function useMyPortfolio() {
  return useQuery({
    queryKey: ["portfolio", "my"],
    queryFn: mlApi.listMyPortfolio,
  });
}

export function useFreelancerPortfolio(freelancerId: string | undefined) {
  return useQuery({
    queryKey: ["portfolio", freelancerId],
    queryFn: () => mlApi.listFreelancerPortfolio(freelancerId!),
    enabled: !!freelancerId,
  });
}

export function useIngestPortfolio() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: mlApi.ingestPortfolio,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["portfolio"] }),
  });
}

export function useMyTrustScore() {
  return useQuery({
    queryKey: ["trust-score", "my"],
    queryFn: mlApi.getMyTrustScore,
  });
}
