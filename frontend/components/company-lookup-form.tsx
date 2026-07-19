"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { parseCompanyQuery } from "@/lib/company-query";

export function CompanyLookupForm() {
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState<{
    type: "name" | "number";
    value: string;
  } | null>(null);

  function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const result = parseCompanyQuery(query);

    if (!result.ok) {
      setError(result.error);
      setSubmitted(null);
      return;
    }

    setError(null);
    setSubmitted({ type: result.type, value: result.value });
  }

  return (
    <form onSubmit={onSubmit} className="flex w-full max-w-md flex-col gap-4">
      <div className="flex flex-col gap-2">
        <Label htmlFor="company-query">Company</Label>
        <Input
          id="company-query"
          name="company-query"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (error) setError(null);
          }}
          placeholder="Company name or registration number"
          autoComplete="organization"
          aria-invalid={!!error}
          aria-describedby={error ? "company-query-error" : "company-query-hint"}
        />
        {error ? (
          <p id="company-query-error" className="text-destructive text-sm">
            {error}
          </p>
        ) : (
          <p id="company-query-hint" className="text-muted-foreground text-sm">
            e.g. Acme Ltd or 01234567
          </p>
        )}
      </div>

      <Button type="submit" className="w-full sm:w-auto">
        Look up
      </Button>

      {submitted && (
        <p className="text-muted-foreground text-sm">
          Looking up{" "}
          <span className="text-foreground font-medium">{submitted.value}</span>{" "}
          ({submitted.type === "number" ? "registration number" : "company name"})
        </p>
      )}
    </form>
  );
}
