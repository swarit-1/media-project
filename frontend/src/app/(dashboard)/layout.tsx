"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/layouts/sidebar";
import { useAuth } from "@/lib/hooks/use-auth";
import { getMe, isAuthenticated } from "@/lib/api/auth";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, setUser, setLoading } = useAuth();

  useEffect(() => {
    async function loadUser() {
      if (!isAuthenticated()) {
        router.push("/login");
        return;
      }
      try {
        const userData = await getMe();
        setUser(userData);
      } catch {
        router.push("/login");
      }
    }
    if (!user) {
      loadUser();
    } else {
      setLoading(false);
    }
  }, [user, router, setUser, setLoading]);

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="ml-[280px] flex flex-1 flex-col">
        {children}
      </div>
    </div>
  );
}
