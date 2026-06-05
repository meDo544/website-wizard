const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://34.27.91.3:8000";

export async function getCurrentUser(
  token: string
) {

  const response = await fetch(
    `${API_BASE}/auth/me`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {

    throw new Error(
      "Failed to fetch current user"
    );
  }

  return response.json();
}
