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
    <Card className="w-full max-w-md rounded-[28px] border-[#ffe6dc] bg-white p-8 shadow-xl">
      <div className="flex flex-col items-center text-center">
        {/* Markee Circular Logo */}
        <div className="relative flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-tr from-[#ff7442] to-[#ff8c64] text-white shadow-md">
          <span className="font-heading text-lg font-black tracking-wider">VC</span>
          <span className="absolute right-1 top-1 h-3 w-3 rounded-full border-2 border-white bg-white" />
        </div>

        <h1 className="mt-5 font-heading text-2xl font-extrabold text-[#0f172a]">
          Chào mừng trở lại
        </h1>
        <p className="mt-1.5 text-xs text-[#667085]">
          Đăng nhập vào Không gian Sáng tạo Viral Video AI
        </p>
      </div>

      <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
        <label className="block space-y-1.5">
          <span className="text-xs font-bold text-[#0f172a]">Email</span>
          <Input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="h-10 text-xs rounded-xl"
            placeholder="name@company.com"
          />
        </label>
        <label className="block space-y-1.5">
          <span className="text-xs font-bold text-[#0f172a]">Mật khẩu</span>
          <Input
            type="password"
            defaultValue="password"
            className="h-10 text-xs rounded-xl"
          />
        </label>
        <div className="pt-2">
          <Button className="w-full h-10 text-sm font-semibold" type="submit">
            Đăng nhập vào Studio
          </Button>
        </div>
      </form>
    </Card>
  );
}
