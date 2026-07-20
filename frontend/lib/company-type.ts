/** Companies House company_type codes → human-readable labels. */
const COMPANY_TYPE_LABELS: Record<string, string> = {
  "private-unlimited": "Private unlimited company",
  ltd: "Private limited company",
  plc: "Public limited company",
  "old-public-company": "Old public company",
  "private-limited-guarant-nsc-limited-exemption":
    "Private limited company by guarantee without share capital, use of 'Limited' exemption",
  "limited-partnership": "Limited partnership",
  "private-limited-guarant-nsc":
    "Private limited by guarantee without share capital",
  "converted-or-closed": "Converted / closed",
  "private-unlimited-nsc": "Private unlimited company without share capital",
  "private-limited-shares-section-30-exemption":
    "Private limited company, use of 'Limited' exemption",
  "protected-cell-company": "Protected cell company",
  "assurance-company": "Assurance company",
  "oversea-company": "Overseas company",
  "eeig-establishment":
    "European Economic Interest Grouping Establishment (EEIG)",
  "icvc-securities": "Investment company with variable capital",
  "icvc-warrant": "Investment company with variable capital",
  "icvc-umbrella": "Investment company with variable capital",
  "registered-society-non-jurisdictional": "Registered society",
  "industrial-and-provident-society": "Industrial and Provident society",
  "northern-ireland": "Northern Ireland company",
  "northern-ireland-other": "Credit union (Northern Ireland)",
  llp: "Limited liability partnership",
  "royal-charter": "Royal charter company",
  "investment-company-with-variable-capital":
    "Investment company with variable capital",
  "unregistered-company": "Unregistered company",
  other: "Other company type",
  "european-public-limited-liability-company-se":
    "European public limited liability company (SE)",
  "united-kingdom-societas": "United Kingdom Societas",
  "uk-establishment": "UK establishment company",
  "scottish-partnership": "Scottish qualifying partnership",
  "charitable-incorporated-organisation":
    "Charitable incorporated organisation",
  "scottish-charitable-incorporated-organisation":
    "Scottish charitable incorporated organisation",
  "further-education-or-sixth-form-college-corporation":
    "Further education or sixth form college corporation",
  eeig: "European Economic Interest Grouping (EEIG)",
  ukeig: "United Kingdom Economic Interest Grouping",
  "registered-overseas-entity": "Overseas entity",
};

/** Format a CH company_type code for display, e.g. "Public limited company". */
export function formatCompanyType(type: string | null | undefined): string {
  if (!type) return "";
  return COMPANY_TYPE_LABELS[type] ?? type;
}
