import { api } from "./client";
import type { AuthTokens, User, LoginRequest, RegisterRequest } from "@/types";

export async function login(data: LoginRequest): Promise<AuthTokens> {
  const tokens = await api.post<AuthTokens>("/auth/login", data);
  localStorage.setItem("access_token", tokens.access_token);
  localStorage.setItem("refresh_token", tokens.refresh_token);
  return tokens;
}

export async function register(data: RegisterRequest): Promise<AuthTokens> {
  const tokens = await api.post<AuthTokens>("/auth/register", {
    email: data.email,
    password: data.password,
    role: data.role,
    display_name: data.display_name,
  });
  localStorage.setItem("access_token", tokens.access_token);
  localStorage.setItem("refresh_token", tokens.refresh_token);
  return tokens;
}

export async function getMe(): Promise<User> {
  // Check for dev user first
  const devUser = localStorage.getItem("dev_user");
  if (devUser) {
    return JSON.parse(devUser) as User;
  }
  return api.get<User>("/users/me");
}

export function logout(): void {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("dev_user");
}

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("access_token");
}

export function devLogin(password: string, role: "editor" | "freelancer" = "editor"): boolean {
  if (password !== "1234") {
    return false;
  }
  localStorage.setItem("access_token", "dev_token");
  localStorage.setItem("refresh_token", "dev_refresh_token");
  const firstName = role === "editor" ? "Dev" : "Jane";
  const lastName = role === "editor" ? "Editor" : "Journalist";
  localStorage.setItem("dev_user", JSON.stringify({
    id: `dev-${role}-001`,
    email: `dev-${role}@example.com`,
    role,
    first_name: firstName,
    last_name: lastName,
    display_name: `${firstName} ${lastName}`,
    created_at: new Date().toISOString(),
  }));
  return true;
}

export function isDevUser(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("dev_user");
}

export function toggleDevRole(): User | null {
  const devUserStr = localStorage.getItem("dev_user");
  if (!devUserStr) return null;

  const devUser = JSON.parse(devUserStr) as User;
  const newRole = devUser.role === "editor" ? "freelancer" : "editor";
  const updatedUser = { ...devUser, role: newRole };
  localStorage.setItem("dev_user", JSON.stringify(updatedUser));
  return updatedUser as User;
}
