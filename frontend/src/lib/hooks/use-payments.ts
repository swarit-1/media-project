import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as paymentApi from "@/lib/api/payments";

export function useMyPayments() {
  return useQuery({
    queryKey: ["payments", "my"],
    queryFn: paymentApi.listMyPayments,
  });
}

export function useNewsroomPayments() {
  return useQuery({
    queryKey: ["payments", "newsroom"],
    queryFn: paymentApi.listNewsroomPayments,
  });
}

export function useReleaseEscrow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: paymentApi.releaseEscrow,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["payments"] }),
  });
}

export function useMyBalance() {
  return useQuery({
    queryKey: ["ledger", "balance"],
    queryFn: paymentApi.getMyBalance,
  });
}

export function useMyLedger() {
  return useQuery({
    queryKey: ["ledger", "my"],
    queryFn: paymentApi.listMyLedger,
  });
}
