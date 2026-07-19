const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Slim company shape returned by the search API (agent-friendly). */
export type CompanyLookupResponse = {
  company_number: string;
  company_name: string;
  company_status?: string;
  company_type?: string;
  date_of_creation?: string;
  date_of_cessation?: string;
  address_snippet?: string;
};

export async function lookupCompanyByNumber(
  companyNumber: string,
): Promise<CompanyLookupResponse> {
  const res = await fetch(
    `${API_BASE}/api/search/by-company-number/${encodeURIComponent(companyNumber)}`,
    { cache: "no-store" },
  );

  if (!res.ok) {
    let message = "Lookup failed";
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") message = body.detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(message);
  }

  return res.json();
}
