import { z } from "zod";

/** Companies House numbers: 8 digits, or 2-letter prefix + 6 digits (e.g. SC123456). */
const COMPANY_NUMBER =
  /^(?:\d{8}|[A-Za-z]{2}\d{6})$/;

export const companyQuerySchema = z
  .string()
  .trim()
  .min(1, "Enter a company name or registration number")
  .refine(
    (value) => {
      const compact = value.replace(/\s+/g, "");
      if (COMPANY_NUMBER.test(compact)) return true;
      return value.trim().length >= 2;
    },
    {
      message:
        "Enter a company name, or an 8-character Companies House number",
    },
  );

export type CompanyQuery = z.infer<typeof companyQuerySchema>;

export function parseCompanyQuery(value: string) {
  const result = companyQuerySchema.safeParse(value);
  if (!result.success) {
    return {
      ok: false as const,
      error: result.error.issues[0]?.message ?? "Invalid input",
    };
  }

  const trimmed = result.data.trim();
  const compact = trimmed.replace(/\s+/g, "");
  const isNumber = COMPANY_NUMBER.test(compact);

  return {
    ok: true as const,
    query: trimmed,
    type: isNumber ? ("number" as const) : ("name" as const),
    value: isNumber ? compact.toUpperCase() : trimmed,
  };
}
