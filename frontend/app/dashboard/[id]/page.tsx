"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"

interface Website {
  id: string
  business_name: string
  prompt: string
  status: string
  generated_url?: string
  created_at: string
}

export default function WebsiteDetailPage() {
  const params = useParams()
  const id = params.id as string

  const [website, setWebsite] =
    useState<Website | null>(null)

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState("")

  const fetchWebsite = async () => {
    try {
      const token =
        localStorage.getItem(
          "access_token"
        )

      if (!token) {
        throw new Error(
          "Authentication required"
        )
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/websites/${id}`,
        {
          headers: {
            Authorization:
              `Bearer ${token}`,
            "Content-Type":
              "application/json",
          },
        }
      )

      if (!response.ok) {
        const text =
          await response.text()

        throw new Error(
          `API Error ${response.status}: ${text}`
        )
      }

      const data =
        await response.json()

      setWebsite(data)

    } catch (err: any) {
      console.error(err)

      setError(
        err.message ||
          "Something went wrong"
      )

    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (id) {
      fetchWebsite()
    }
  }, [id])

  useEffect(() => {
    if (
      website?.status !== "queued"
    ) {
      return
    }

    const interval =
      setInterval(() => {
        fetchWebsite()
      }, 5000)

    return () =>
      clearInterval(interval)

  }, [website])

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto p-8">
        <div className="animate-pulse text-gray-500">
          Loading website...
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto p-8">
        <div className="border border-red-300 bg-red-50 text-red-700 rounded-2xl p-4">
          {error}
        </div>
      </div>
    )
  }

  if (!website) {
    return (
      <div className="max-w-5xl mx-auto p-8">
        Website not found
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto p-8 space-y-6">

      <div>
        <h1 className="text-4xl font-bold">
          {website.business_name}
        </h1>

        <p className="text-gray-500 mt-2">
          AI Generated Website Details
        </p>
      </div>

      <div className="border rounded-2xl p-6">
        <h2 className="text-lg font-semibold mb-3">
          Status
        </h2>

        <div
          className={`inline-flex px-4 py-2 rounded-full text-sm font-medium ${
            website.status ===
            "completed"
              ? "bg-green-100 text-green-700"
              : website.status ===
                "queued"
              ? "bg-yellow-100 text-yellow-700"
              : website.status ===
                "failed"
              ? "bg-red-100 text-red-700"
              : "bg-gray-100 text-gray-700"
          }`}
        >
          {website.status}
        </div>
      </div>

      <div className="border rounded-2xl p-6">
        <h2 className="text-lg font-semibold mb-3">
          Original Prompt
        </h2>

        <p className="text-gray-700 leading-relaxed">
          {website.prompt}
        </p>
      </div>

      <div className="border rounded-2xl p-6">
        <h2 className="text-lg font-semibold mb-4">
          Website Preview
        </h2>

        {website.generated_url ? (
          <div className="space-y-4">

            <a
              href={
                website.generated_url
              }
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center bg-black text-white px-5 py-3 rounded-xl hover:opacity-90 transition"
            >
              Open Full Website
            </a>

            <div className="border rounded-2xl overflow-hidden bg-white">
              <iframe
                src={
                  website.generated_url
                }
                className="w-full h-[800px]"
              />
            </div>

          </div>
        ) : (
          <div className="text-yellow-700 bg-yellow-50 border border-yellow-200 rounded-xl p-4">
            Website generation is still in progress.
          </div>
        )}
      </div>

      <div className="border rounded-2xl p-6">
        <h2 className="text-lg font-semibold mb-3">
          Created At
        </h2>

        <p className="text-gray-700">
          {new Date(
            website.created_at
          ).toLocaleString()}
        </p>
      </div>

    </div>
  )
}
