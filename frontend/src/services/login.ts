const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://34.27.91.3:8000";

export async function login(
  email: string,
  password: string
) {

  const formData =
    new URLSearchParams();

  formData.append(
    "username",
    email
  );

  formData.append(
    "password",
    password
  );

  const response = await fetch(
    `${API_BASE}/auth/login`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },

      body: formData,
    }
  );

  if (!response.ok) {

    throw new Error(
      "Login failed"
    );
  }

  return response.json();
}
