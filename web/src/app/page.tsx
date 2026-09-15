import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col justify-center px-6 py-16">
      <p className="text-sm font-semibold uppercase tracking-wide text-blue-600">
        Next.js Boilerplate
      </p>
      <h1 className="mt-4 max-w-3xl text-5xl font-bold leading-tight text-slate-950">
        Build feature-first frontend apps with a clean App Router foundation.
      </h1>
      <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600">
        This starter includes providers, auth context, API utilities, shared UI
        primitives, and a protected dashboard route.
      </p>
      <div className="mt-8 flex flex-wrap gap-3">
        <Button asChild>
          <Link href="/dashboard">Open Dashboard</Link>
        </Button>
        <Button variant="secondary" asChild>
          <Link href="/login">Login</Link>
        </Button>
      </div>
    </main>
  );
}
