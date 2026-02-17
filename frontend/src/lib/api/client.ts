// ---------------------------------------------------------------------------
// Centralised HTTP client — all requests go through the API gateway
// ---------------------------------------------------------------------------

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, message: string, code: string) {
    super(message);
    this.status = status;
    this.code = code;
    this.name = "ApiError";
  }
}

class ApiClient {
  // ---- Token management ----

  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("refresh_token");
  }

  private setTokens(access: string, refresh: string) {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
  }

  private clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("dev_user");
  }

  // ---- Headers ----

  private getHeaders(newsroomId?: string): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    const token = this.getToken();
    if (token && token !== "dev_token") {
      headers["Authorization"] = `Bearer ${token}`;
    }
    if (newsroomId) {
      headers["X-Newsroom-ID"] = newsroomId;
    }
    return headers;
  }

  // ---- Core request ----

  async request<T>(
    path: string,
    options: RequestInit & { newsroomId?: string } = {}
  ): Promise<T> {
    const { newsroomId, ...fetchOptions } = options;
    const url = `${API_BASE}/api/v1${path}`;

    let response = await fetch(url, {
      ...fetchOptions,
      headers: {
        ...this.getHeaders(newsroomId),
        ...(fetchOptions.headers as Record<string, string> || {}),
      },
    });

    // Attempt silent token refresh on 401
    if (response.status === 401 && this.getRefreshToken()) {
      const refreshed = await this.tryRefresh();
      if (refreshed) {
        response = await fetch(url, {
          ...fetchOptions,
          headers: {
            ...this.getHeaders(newsroomId),
            ...(fetchOptions.headers as Record<string, string> || {}),
          },
        });
      }
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        error?.error?.message || error?.detail?.message || error?.detail || "Request failed",
        error?.error?.code || error?.detail?.code || "UNKNOWN_ERROR"
      );
    }

    if (response.status === 204) return undefined as T;
    return response.json();
  }

  // ---- Token refresh ----

  private async tryRefresh(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) return false;

    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!res.ok) {
        this.clearTokens();
        return false;
      }

      const data = await res.json();
      this.setTokens(data.access_token, data.refresh_token);
      return true;
    } catch {
      this.clearTokens();
      return false;
    }
  }

  // ---- Convenience methods ----

  get<T>(path: string, newsroomId?: string) {
    return this.request<T>(path, { method: "GET", newsroomId });
  }

  post<T>(path: string, body?: unknown, newsroomId?: string) {
    return this.request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
      newsroomId,
    });
  }

  patch<T>(path: string, body?: unknown, newsroomId?: string) {
    return this.request<T>(path, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
      newsroomId,
    });
  }

  delete<T>(path: string, newsroomId?: string) {
    return this.request<T>(path, { method: "DELETE", newsroomId });
  }
}

export const api = new ApiClient();
