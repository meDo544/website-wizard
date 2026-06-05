import { useEffect, useState } from "react";

import ProtectedRoute from "../../src/components/auth/ProtectedRoute";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://34.27.91.3:8000";

interface UserData {
  id: string;
  email: string;

  subscription_tier: string;
  subscription_status: string;

  monthly_token_quota: number;
  monthly_tokens_used: number;

  monthly_spend_quota_usd: number;
  monthly_spend_used_usd: number;

  monthly_request_count: number;
}

export default function BillingPage() {

  const [user, setUser] =
    useState<UserData | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [checkoutLoading, setCheckoutLoading] =
    useState(false);

  const tokenUsagePercent =
    user && user.monthly_token_quota > 0
      ? (
          user.monthly_tokens_used /
          user.monthly_token_quota
        ) * 100
      : 0;

  const spendUsagePercent =
    user && user.monthly_spend_quota_usd > 0
      ? (
          user.monthly_spend_used_usd /
          user.monthly_spend_quota_usd
        ) * 100
      : 0;

  const nearingLimits =
    tokenUsagePercent >= 80 ||
    spendUsagePercent >= 80;

async function startCheckout(
  plan: string
) {

  try {

    setCheckoutLoading(true);

    const token =
      localStorage.getItem("token");

    if (!token) {
      return;
    }

    const response = await fetch(
      `${API_BASE}/billing/create-checkout-session`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",

          Authorization:
            `Bearer ${token}`,
        },

        body: JSON.stringify({
          plan,
        }),
      }
    );

    if (!response.ok) {

      throw new Error(
        "Failed to create checkout session"
      );
    }

    const data =
      await response.json();

    window.location.href =
      data.checkout_url;

  } catch (err) {

    console.error(err);

    alert(
      "Unable to start checkout."
    );

  } finally {

    setCheckoutLoading(false);
  }
}  

  useEffect(() => {

    async function loadUser() {

      try {

        const token =
          localStorage.getItem("token");

        if (!token) {
          return;
        }

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

          throw new Error(
            "Failed to fetch current user"
          );
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

  return (
    <ProtectedRoute>

      <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-200 p-4 md:p-10">

        <div className="max-w-5xl mx-auto">

          <h1 className="text-5xl font-bold text-slate-800 mb-10">
            Billing Dashboard
          </h1>

          {loading && (
            <p className="text-slate-600">
              Loading...
            </p>
          )}

          {user && (
            <>

              {/* CURRENT PLAN CARD */}

              <div className="bg-white rounded-3xl shadow-xl p-8 mb-8">

                <h2 className="text-3xl font-semibold mb-6 text-slate-800">
                  Current Plan
                </h2>

                <div className="space-y-4 text-lg text-slate-700">

                  <p>
                    <span className="font-semibold">
                      Email:
                    </span>
                    {" "}
                    {user.email}
                  </p>

                  <p>
                    <span className="font-semibold">
                      Subscription:
                    </span>
                    {" "}
                    {user.subscription_tier}
                  </p>

                  <p>
                    <span className="font-semibold">
                      Monthly Token Quota:
                    </span>
                    {" "}
                    {user.monthly_token_quota.toLocaleString()}
                  </p>

                  <p>
                    <span className="font-semibold">
                      Monthly Spend Limit:
                    </span>
                    {" "}
                    $
                    {user.monthly_spend_quota_usd}
                  </p>

                </div>

              </div>

              {/* AI USAGE CARD */}

              <div className="bg-white rounded-3xl shadow-xl p-8">

                <h2 className="text-3xl font-semibold mb-6 text-slate-800">
                  AI Usage
                </h2>

                <div className="space-y-6">

                  <div>

                    <p className="mb-2 text-slate-700 font-medium">
                      Tokens Used:
                      {" "}
                      {user.monthly_tokens_used.toLocaleString()}
                    </p>

                    <div className="w-full bg-slate-200 rounded-full h-5">

                      <div
                        className="bg-indigo-600 h-5 rounded-full transition-all duration-500"
                        style={{
                          width:
                            `${Math.min(tokenUsagePercent, 100)}%`,
                        }}
                      />

                    </div>

                  </div>

                  <div>

                    <p className="mb-2 text-slate-700 font-medium">
                      Spend Used:
                      {" "}
                      $
                      {user.monthly_spend_used_usd.toFixed(4)}
                    </p>

                    <div className="w-full bg-slate-200 rounded-full h-5">

                      <div
                        className="bg-emerald-600 h-5 rounded-full transition-all duration-500"
                        style={{
                          width:
                            `${Math.min(spendUsagePercent, 100)}%`,
                        }}
                      />

                    </div>

                  </div>

                  <div className="space-y-2 text-slate-700">

                    <p>
                      <span className="font-semibold">
                        Monthly Requests:
                      </span>
                      {" "}
                      {user.monthly_request_count}
                    </p>

                    <p>
                      <span className="font-semibold">
                        Subscription Status:
                      </span>
                      {" "}
                      {user.subscription_status}
                    </p>

                  </div>

                </div>

              </div>

              {/* MONETIZATION CTA CARD */}

              <div className="mt-8 bg-gradient-to-r from-indigo-600 to-violet-600 rounded-3xl shadow-2xl p-10 text-white">

                <h2 className="text-3xl font-bold mb-4">
                  Scale Your AI Power
                </h2>

                <p className="text-lg text-indigo-100 mb-6 max-w-2xl">
                  Upgrade your subscription to unlock higher GPT quotas,
                  faster generations, premium AI models, and enterprise-scale website creation.
                </p>

                {nearingLimits && (
                  <div className="bg-white/20 border border-white/30 rounded-2xl p-4 mb-6">

                    <p className="font-semibold text-lg">
                      ⚠️ You are nearing your monthly usage limits.
                    </p>

                    <p className="text-indigo-100">
                      Upgrade now to avoid interrupted AI generation access.
                    </p>

                  </div>
                )}

                <div className="flex flex-wrap gap-4">

                  <button
                    onClick={() =>
                      startCheckout("enterprise")
                    }

                    disabled={checkoutLoading}

                    className="
                      bg-white
                      text-indigo-700
                      font-semibold
                      px-6
                      py-3
                      rounded-2xl
                      shadow-lg
                      hover:bg-slate-100
                      transition
                      disabled:opacity-50
                    "
                  >
                    {checkoutLoading
                      ? "Redirecting..."
                      : "Upgrade to Enterprise"}
                  </button>

                  <button
                    className="bg-indigo-900 text-white font-semibold px-6 py-3 rounded-2xl shadow-lg hover:bg-indigo-950 transition"
                  >
                    Buy More Tokens
                  </button>

                </div>

              </div>

            </>
          )}

        </div>

      </div>

    </ProtectedRoute>
  );
}
