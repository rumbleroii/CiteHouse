import { CompanyLookupForm } from "@/components/company-lookup-form";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 px-6 py-16">
      <div className="flex max-w-md flex-col gap-2 text-center">
        <h1 className="text-3xl font-semibold tracking-tight">Citehouse</h1>
        <p className="text-muted-foreground text-sm">
          Look up a UK company by Companies House number
        </p>
      </div>
      <CompanyLookupForm />
    </main>
  );
}
