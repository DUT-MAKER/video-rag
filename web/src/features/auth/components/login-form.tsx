"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/auth-context";

export function LoginForm() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("demo@example.com");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    login("demo-token", {
      id: "demo-user",
      name: "Demo User",
      email,
    });
    router.push("/dashboard");
  }

  return (
    <Card className="w-full max-w-md p-6">
      <h1 className="text-2xl font-semibold text-slate-950">Sign in</h1>
      <p className="mt-2 text-sm text-slate-600">
        Use this placeholder form to wire real auth later.
      </p>
      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        <label className="block space-y-2">
          <span className="text-sm font-medium text-slate-700">Email</span>
          <Input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <label className="block space-y-2">
          <span className="text-sm font-medium text-slate-700">Password</span>
          <Input type="password" defaultValue="password" />
        </label>
        <Button className="w-full" type="submit">
          Continue
        </Button>
      </form>
    </Card>
  );
}
