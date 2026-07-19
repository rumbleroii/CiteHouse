const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type CompanyLookupResponse = {
  company_number: string;
  company_name: string;
  registered_office_address: Record<string, unknown>;
};

export async function lookupCompanyByNumber(
  companyNumber: string,
): Promise<CompanyLookupResponse> {
  const res = await fetch(
    `${API_BASE}/api/company/${encodeURIComponent(companyNumber)}`,
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
