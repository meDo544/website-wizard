"use client";

import Link from "next/link";

import {
  useEffect,
  useState,
} from "react";

interface Website {

  id: string;

  business_name: string;

  industry: string;

  prompt: string;

  generation_status: string;

  html: string;

  css: string;

  js: string;

  created_at: string;
}

export default function DashboardPage() {

  const [websites, setWebsites] =
    useState<Website[]>([]);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {

    const fetchWebsites = async () => {

      try {

        const token =
          localStorage.getItem(
            "access_token"
          );

        if (!token) {

          console.error(
            "No access token found"
          );

          setLoading(false);

          return;
        }

        const response = await fetch(
          "http://34.27.91.3:8000/websites",
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

        const data =
          await response.json();

        console.log(
          "API Response:",
          data
        );

        if (Array.isArray(data)) {

          setWebsites(data);

        } else {

          console.error(
            "Unexpected API response:",
            data
          );

          setWebsites([]);
        }

      } catch (error) {

        console.error(
          "Dashboard fetch error:",
          error
        );

      } finally {

        setLoading(false);
      }
    };

    fetchWebsites();

  }, []);

  if (loading) {

    return (
      <div style={{ padding: "40px" }}>
        Loading dashboard...
      </div>
    );
  }

  return (

    <div
      style={{
        padding: "40px",
      }}
    >

      <h1>
        Dashboard
      </h1>

      {websites.length === 0 ? (

        <p>
          No websites generated yet.
        </p>

      ) : (

        <div>

          {websites.map((website) => (

            <div
              key={website.id}
              style={{
                border:
                  "1px solid #ddd",

                padding: "20px",

                marginBottom: "20px",

                borderRadius: "10px",
              }}
            >

              <h2>
                {website.business_name}
              </h2>

              <p>
                {website.industry}
              </p>

              <p>
                Status:
                {" "}
                {website.generation_status}
              </p>

              <p>
                Created:
                {" "}
                {new Date(
                  website.created_at
                ).toLocaleString()}
              </p>

              <Link
                href={`/dashboard/${website.id}`}
              >

                <button
                  style={{
                    marginTop: "10px",
                    cursor: "pointer",
                  }}
                >
                  View Website
                </button>

              </Link>

            </div>
          ))}

        </div>
      )}

    </div>
  );
}
