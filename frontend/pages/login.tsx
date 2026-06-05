import { useState }
from "react";

import { useRouter }
from "next/router";

import { login }
from "../src/services/login";

export default function LoginPage() {

  const router = useRouter();

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [error, setError] =
    useState("");

  async function handleLogin(
    e: any
  ) {

    e.preventDefault();

    try {

      const data =
        await login(
          email,
          password
        );

      localStorage.setItem(
        "token",
        data.access_token
      );

      router.push(
        "/settings/billing"
      );

    } catch (err) {

      setError(
        "Invalid credentials"
      );
    }
  }

  return (
    <div
      style={{
        padding: "40px",
        maxWidth: "400px",
      }}
    >

      <h1>
        Login
      </h1>

      <form onSubmit={handleLogin}>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) =>
            setEmail(
              e.target.value
            )
          }
          style={{
            width: "100%",
            marginBottom: "12px",
            padding: "10px",
          }}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(
              e.target.value
            )
          }
          style={{
            width: "100%",
            marginBottom: "12px",
            padding: "10px",
          }}
        />

        <button
          type="submit"
          style={{
            padding: "10px 20px",
          }}
        >
          Login
        </button>

      </form>

      {error && (
        <p style={{ color: "red" }}>
          {error}
        </p>
      )}

    </div>
  );
}
