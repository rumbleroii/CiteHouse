import { Button } from "@/components/ui/button";

async function getHealth() {
  try {
    const res = await fetch("http://localhost:8000/api/health", {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function Home() {
  const health = await getHealth();

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-2xl font-semibold tracking-tight">Citehouse</h1>
      <p className="text-muted-foreground text-sm">
        API: {health?.status ?? "offline"}
      </p>
      <Button>Get started</Button>
    </main>
  );
}
