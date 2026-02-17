"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff } from "lucide-react";
import { loginSchema, type LoginFormData } from "@/lib/validations/auth";
import { login, devLogin } from "@/lib/api/auth";

export default function LoginPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDevLogin, setShowDevLogin] = useState(false);
  const [devPassword, setDevPassword] = useState("");
  const [devError, setDevError] = useState<string | null>(null);
  const [devRole, setDevRole] = useState<"editor" | "freelancer">("editor");

  function handleDevLogin(role?: "editor" | "freelancer") {
    setDevError(null);
    const selectedRole = role ?? devRole;
    if (devLogin(devPassword, selectedRole)) {
      router.push("/dashboard");
    } else {
      setDevError("Invalid dev password");
    }
  }

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  async function onSubmit(data: LoginFormData) {
    setError(null);
    try {
      await login(data);
      router.push("/dashboard");
    } catch (err: any) {
      if (err.message === "Failed to fetch" || err.name === "TypeError") {
        setError("Cannot reach the server. Make sure the backend is running, or use Dev Login below.");
      } else {
        setError(err.message || "Invalid email or password");
      }
    }
  }

  return (
    <div>
      {/* Logo */}
      <div className="mb-8 flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-[5px] bg-ink-950 text-white">
          <span className="text-xs font-bold">E</span>
        </div>
      </div>

      <h1 className="text-xl font-semibold text-ink-950">Welcome back</h1>
      <p className="mt-1 text-sm text-ink-500">
        Sign in to your Elastic account
      </p>

      {error && (
        <div className="mt-4 rounded-[5px] border border-danger-600/20 bg-danger-100 px-4 py-3">
          <p className="text-sm text-danger-600">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
        <div>
          <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-ink-700">
            Email
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="you@newsroom.com"
            className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20 disabled:cursor-not-allowed disabled:opacity-50"
            {...register("email")}
          />
          {errors.email && (
            <p className="mt-1.5 text-xs text-danger-600">{errors.email.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-ink-700">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              placeholder="Enter your password"
              className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 pr-10 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20 disabled:cursor-not-allowed disabled:opacity-50"
              {...register("password")}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-ink-400 hover:text-ink-600"
              tabIndex={-1}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {errors.password && (
            <p className="mt-1.5 text-xs text-danger-600">{errors.password.message}</p>
          )}
        </div>

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              className="h-4 w-4 rounded-[3px] border-ink-300 text-accent-600 focus:ring-accent-500/20"
            />
            <span className="text-sm text-ink-600">Remember me</span>
          </label>
          <Link
            href="/forgot-password"
            className="text-sm font-medium text-accent-700 hover:text-accent-600"
          >
            Forgot password?
          </Link>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="flex h-9 w-full items-center justify-center rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? "Signing in..." : "Sign in"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-ink-500">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="font-medium text-accent-700 hover:text-accent-600">
          Sign up
        </Link>
      </p>

      {/* Dev Skip Login */}
      <div className="mt-6 border-t border-ink-200 pt-6">
        {!showDevLogin ? (
          <button
            type="button"
            onClick={() => setShowDevLogin(true)}
            className="flex h-9 w-full items-center justify-center rounded-[3px] border border-dashed border-ink-300 px-4 text-sm text-ink-500 transition-colors hover:border-ink-400 hover:text-ink-600"
          >
            Skip Login (Dev)
          </button>
        ) : (
          <div className="space-y-3">
            <input
              type="password"
              value={devPassword}
              onChange={(e) => setDevPassword(e.target.value)}
              placeholder="Enter dev password"
              className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
              onKeyDown={(e) => e.key === "Enter" && handleDevLogin()}
            />
            {devError && (
              <p className="text-xs text-danger-600">{devError}</p>
            )}
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => {
                  setShowDevLogin(false);
                  setDevPassword("");
                  setDevError(null);
                }}
                className="flex h-9 flex-1 items-center justify-center rounded-[3px] border border-ink-200 px-4 text-sm text-ink-600 transition-colors hover:bg-ink-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => handleDevLogin("editor")}
                className="flex h-9 flex-1 items-center justify-center rounded-[3px] bg-ink-700 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-600"
              >
                Editor
              </button>
              <button
                type="button"
                onClick={() => handleDevLogin("freelancer")}
                className="flex h-9 flex-1 items-center justify-center rounded-[3px] bg-amber-600 px-4 text-sm font-medium text-white transition-colors hover:bg-amber-500"
              >
                Journalist
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
