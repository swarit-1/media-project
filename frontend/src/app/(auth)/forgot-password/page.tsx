"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, Mail } from "lucide-react";
import { forgotPasswordSchema, type ForgotPasswordFormData } from "@/lib/validations/auth";

export default function ForgotPasswordPage() {
  const [submitted, setSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    getValues,
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  async function onSubmit() {
    // API call would go here
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <div>
        <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-full bg-success-100">
          <Mail className="h-5 w-5 text-success-600" />
        </div>
        <h1 className="text-xl font-semibold text-ink-950">Check your email</h1>
        <p className="mt-2 text-sm text-ink-500">
          We sent a password reset link to{" "}
          <span className="font-medium text-ink-700">{getValues("email")}</span>
        </p>
        <p className="mt-4 text-sm text-ink-500">
          Didn&apos;t receive the email? Check your spam folder or{" "}
          <button
            onClick={() => setSubmitted(false)}
            className="font-medium text-accent-700 hover:text-accent-600"
          >
            try again
          </button>
        </p>
        <Link
          href="/login"
          className="mt-6 flex h-9 w-full items-center justify-center rounded-[3px] border border-ink-200 px-4 text-sm font-medium text-ink-900 transition-colors hover:bg-ink-50"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to sign in
        </Link>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8 flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-[5px] bg-ink-950 text-white">
          <span className="text-xs font-bold">EN</span>
        </div>
      </div>

      <h1 className="text-xl font-semibold text-ink-950">Reset your password</h1>
      <p className="mt-1 text-sm text-ink-500">
        Enter your email and we&apos;ll send you a reset link
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
        <div>
          <label htmlFor="reset-email" className="mb-1.5 block text-sm font-medium text-ink-700">
            Email
          </label>
          <input
            id="reset-email"
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

        <button
          type="submit"
          disabled={isSubmitting}
          className="flex h-9 w-full items-center justify-center rounded-[3px] bg-ink-950 px-4 text-sm font-medium text-white transition-colors hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? "Sending..." : "Send reset link"}
        </button>
      </form>

      <Link
        href="/login"
        className="mt-4 flex items-center justify-center gap-2 text-sm text-ink-500 hover:text-ink-700"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to sign in
      </Link>
    </div>
  );
}
