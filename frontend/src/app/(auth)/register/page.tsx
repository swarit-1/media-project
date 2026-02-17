"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff } from "lucide-react";
import { registerSchema, type RegisterFormData } from "@/lib/validations/auth";
import { register as registerUser } from "@/lib/api/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: { role: "freelancer" },
  });

  const selectedRole = watch("role");

  async function onSubmit(data: RegisterFormData) {
    setError(null);
    try {
      await registerUser({
        email: data.email,
        password: data.password,
        first_name: data.first_name,
        last_name: data.last_name,
        display_name: `${data.first_name} ${data.last_name}`,
        role: data.role,
      });
      router.push("/dashboard");
    } catch (err: any) {
      if (err.message === "Failed to fetch" || err.name === "TypeError") {
        setError("Cannot reach the server. Make sure the backend is running.");
      } else {
        setError(err.message || "Registration failed");
      }
    }
  }

  return (
    <div>
      <div className="mb-8 flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-[5px] bg-ink-950 text-white">
          <span className="text-xs font-bold">E</span>
        </div>
      </div>

      <h1 className="text-xl font-semibold text-ink-950">Create your account</h1>
      <p className="mt-1 text-sm text-ink-500">
        Join the Elastic platform
      </p>

      {error && (
        <div className="mt-4 rounded-[5px] border border-danger-600/20 bg-danger-100 px-4 py-3">
          <p className="text-sm text-danger-600">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
        {/* Role Selection */}
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink-700">
            I am a...
          </label>
          <div className="grid grid-cols-2 gap-3">
            {(["freelancer", "editor"] as const).map((role) => (
              <label
                key={role}
                className={`flex cursor-pointer items-center justify-center rounded-[3px] border px-4 py-2.5 text-sm font-medium transition-colors ${
                  selectedRole === role
                    ? "border-accent-500 bg-accent-50 text-accent-700"
                    : "border-ink-200 text-ink-600 hover:border-ink-300 hover:bg-ink-50"
                }`}
              >
                <input
                  type="radio"
                  value={role}
                  className="sr-only"
                  {...register("role")}
                />
                {role === "freelancer" ? "Freelance Journalist" : "Editor / Newsroom"}
              </label>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label htmlFor="first_name" className="mb-1.5 block text-sm font-medium text-ink-700">
              First name
            </label>
            <input
              id="first_name"
              type="text"
              className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
              {...register("first_name")}
            />
            {errors.first_name && (
              <p className="mt-1.5 text-xs text-danger-600">{errors.first_name.message}</p>
            )}
          </div>
          <div>
            <label htmlFor="last_name" className="mb-1.5 block text-sm font-medium text-ink-700">
              Last name
            </label>
            <input
              id="last_name"
              type="text"
              className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
              {...register("last_name")}
            />
            {errors.last_name && (
              <p className="mt-1.5 text-xs text-danger-600">{errors.last_name.message}</p>
            )}
          </div>
        </div>

        <div>
          <label htmlFor="reg-email" className="mb-1.5 block text-sm font-medium text-ink-700">
            Email
          </label>
          <input
            id="reg-email"
            type="email"
            autoComplete="email"
            placeholder="you@newsroom.com"
            className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
            {...register("email")}
          />
          {errors.email && (
            <p className="mt-1.5 text-xs text-danger-600">{errors.email.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="reg-password" className="mb-1.5 block text-sm font-medium text-ink-700">
            Password
          </label>
          <div className="relative">
            <input
              id="reg-password"
              type={showPassword ? "text" : "password"}
              placeholder="At least 8 characters"
              className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 pr-10 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
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

        <div>
          <label htmlFor="confirm-password" className="mb-1.5 block text-sm font-medium text-ink-700">
            Confirm password
          </label>
          <input
            id="confirm-password"
            type="password"
            placeholder="Confirm your password"
            className="flex h-9 w-full rounded-[3px] border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-500/20"
            {...register("confirm_password")}
          />
          {errors.confirm_password && (
            <p className="mt-1.5 text-xs text-danger-600">{errors.confirm_password.message}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="flex h-9 w-full items-center justify-center rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? "Creating account..." : "Create account"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-ink-500">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-accent-700 hover:text-accent-600">
          Sign in
        </Link>
      </p>
    </div>
  );
}
