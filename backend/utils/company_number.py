import re

COMPANY_NUMBER_RE = re.compile(r"^(?:\d{8}|[A-Za-z]{2}\d{6})$")


def normalize_company_number(value: str) -> str | None:
    compact = value.strip().replace(" ", "").upper()
    if not COMPANY_NUMBER_RE.match(compact):
        return None
    return compact
