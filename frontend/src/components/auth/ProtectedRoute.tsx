import { useRouter } from "next/router";
import { useEffect } from "react";

interface Props {
  children: React.ReactNode;
}

export default function ProtectedRoute({
  children,
}: Props) {

  const router = useRouter();

  useEffect(() => {

    const token =
      localStorage.getItem("token");

    if (!token) {

      router.push("/login");
    }

  }, [router]);

  return <>{children}</>;
}
