import { api } from "./client";
import type { Payment, PaginatedResponse } from "@/types";

export function listMyPayments() {
  return api.get<PaginatedResponse<Payment>>("/payments/my");
}

export function listNewsroomPayments() {
  return api.get<PaginatedResponse<Payment>>("/payments/newsroom");
}

export function getPayment(paymentId: string) {
  return api.get<Payment>(`/payments/${paymentId}`);
}

export function createPayment(data: Partial<Payment>) {
  return api.post<Payment>("/payments/", data);
}

export function holdEscrow(paymentId: string) {
  return api.post<Payment>(`/payments/${paymentId}/escrow`);
}

export function releaseEscrow(paymentId: string) {
  return api.post<Payment>(`/payments/${paymentId}/release`);
}

export function completePayment(paymentId: string) {
  return api.post<Payment>(`/payments/${paymentId}/complete`);
}

export function refundPayment(paymentId: string) {
  return api.post<Payment>(`/payments/${paymentId}/refund`);
}

export interface LedgerEntry {
  id: string;
  freelancer_id: string;
  payment_id: string;
  entry_type: string;
  amount: number;
  running_balance: number;
  description: string;
  created_at: string;
}

export function listMyLedger() {
  return api.get<PaginatedResponse<LedgerEntry>>("/ledger/my");
}

export function getMyBalance() {
  return api.get<{ balance: number }>("/ledger/balance");
}
