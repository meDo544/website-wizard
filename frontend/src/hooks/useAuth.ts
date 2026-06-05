import { useEffect, useState } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://34.27.91.3:8000";

export interface CurrentUser {
  id: string;
  email: string;
  subscription_tier: string;
  monthly_token_quota: number;
  monthly_spend_quota_usd: number;
}

export function useAuth() {
  const [user, setUser] =
    useState<CurrentUser | null>(null);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    async function loadUser() {

      const token =
        localStorage.getItem("token");

      if (!token) {
        setLoading(false);
        return;
      }

      try {

        const response = await fetch(
          `${API_BASE}/auth/me`,
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {

          localStorage.removeItem(
            "token"
          );

          setLoading(false);

          return;
        }

        const data =
          await response.json();

        setUser(data);

      } catch (err) {

        console.error(err);

      } finally {

        setLoading(false);
      }
    }

    loadUser();

  }, []);

  return {
    user,
    loading,
    authenticated: !!user,
  };
}
