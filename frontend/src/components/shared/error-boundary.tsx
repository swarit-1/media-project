"use client";

import { Component, type ReactNode } from "react";
import { AlertTriangle } from "lucide-react";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div className="flex flex-col items-center justify-center rounded-[5px] border border-danger-100 bg-white py-16 px-8">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-danger-100">
            <AlertTriangle className="h-5 w-5 text-danger-600" />
          </div>
          <h3 className="mt-4 text-sm font-semibold text-ink-900">
            Something went wrong
          </h3>
          <p className="mt-1 max-w-sm text-center text-xs text-ink-500">
            {this.state.error?.message || "An unexpected error occurred"}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-4 flex h-9 items-center justify-center rounded-[3px] border border-ink-200 px-4 text-sm font-medium text-ink-700 transition-colors hover:bg-ink-50"
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
