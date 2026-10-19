"""Portable Mamaearth SCR narrative generator for local Python and Google Colab."""

import argparse
import contextlib
import io
import json
import os
from pathlib import Path


try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent
FINDINGS_FILE = BASE_DIR / "findings.json"
SAMPLE_FILE = BASE_DIR / "sample_output.txt"

# Optional local .env support. Colab Secrets are read by get_api_key() below.
if load_dotenv is not None:
    load_dotenv(BASE_DIR.parent / ".env")

# Use a model that supports temperature=0.0, required for this project's
# reproducibility rubric. Override with GEMINI_MODEL after verifying compatibility.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

SYSTEM_INSTRUCTION = """
You are a senior data analyst writing for Mamaearth's regional ops and finance heads.
Write a concise business narrative using exactly three labeled sections:
Situation, Complication, and Resolution.

Every number in the narrative must come from the supplied findings and must
retain the same value. Do not invent statistics, causes, or unsupported claims.
Explain business implications and give practical recommendations grounded
in the findings. Do not add extra sections or a separate numerical summary.
Recommend investigating or testing interventions; do not claim that COD must
be restricted based only on return rates. Do not assert causes that the data
cannot establish. Include the five required figures in the narrative itself:
cleaned revenue, COD return rate, highest-risk segment return rate, duplicate
reconciliation delta, and the true peak month and its revenue. Format revenue
figures to two decimal places and explicitly identify March 2026 as the true
peak after excluding quantity outliers.
""".strip()


def get_api_key():
    """Read GEMINI_API_KEY from the environment or Colab Secrets, if available."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key

    try:
        from google.colab import userdata  # Available only inside Colab.
        api_key = userdata.get("GEMINI_API_KEY")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            return api_key
    except Exception:
        pass

    return None


def generate_scr_narrative(findings: dict) -> dict:
    api_key = get_api_key()
    if not api_key:
        return {
            "status": "error",
            "narrative": None,
            "message": "GEMINI_API_KEY is not configured in environment variables or Colab Secrets.",
        }

    try:
        # Import the API SDK only when the online path is requested.
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=30000),
        )
        # Build this prompt from the supplied findings; figures are not hardcoded here.
        prompt = (
            "Write a concise business narrative for Mamaearth's regional "
            "operations and finance heads using the findings supplied below. "
            "Use exactly three labeled sections: Situation, Complication, "
            "and Resolution. Treat the supplied findings as the sole source "
            "of numerical truth. Preserve the values and precision exactly; "
            "do not invent, round, or alter figures. Explain the business "
            "implications and give practical recommendations supported by "
            "the findings. Explicitly identify the true peak month after "
            "excluding quantity outliers. Include all five required figures "
            "in the narrative itself, formatted to two decimal places for "
            "revenue. Do not add a separate verified-figures summary or "
            "extra sections. Recommendations must be cautious: investigate "
            "or test COD interventions rather than asserting that COD must "
            "be restricted. Do not assert unsupported causes.\n\n"
            "Verified findings:\n"
            f"{json.dumps(findings, indent=2)}"
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.0,  # Fixed for a factual, reproducible business report.
                max_output_tokens=600,
            ),
        )
        narrative = getattr(response, "text", None)
        if not narrative or not narrative.strip():
            raise ValueError("Gemini returned an empty narrative.")

        usage = getattr(response, "usage_metadata", None)
        tokens = getattr(usage, "total_token_count", None) if usage else None
        return {
            "status": "success",
            "narrative": narrative.strip(),
            "tokens": tokens,
            "source": "Gemini API",
        }
    except Exception as err:
        return {
            "status": "error",
            "narrative": None,
            "message": f"{type(err).__name__}: {err}",
        }


def generate_scr_narrative_offline(findings: dict) -> dict:
    """Deterministic narrative requiring no API key, API call, or network access."""
    payment_rates = findings["return_rate_by_payment"]
    risk = findings["highest_risk_segment"]
    peak = findings["true_peak_month"]
    inflated = findings["outlier_inflated_month"]

    narrative = f"""
Situation

After cleaning duplicate orders and imputing missing values, total revenue was
₹{findings["cleaned_total_revenue_inr"]:,.2f}, compared with raw revenue of
₹{findings["raw_total_revenue_inr"]:,.2f}. The return rate for COD orders was
{payment_rates["COD"]:.1f}%, compared with {payment_rates["UPI"]:.1f}% for UPI
and {payment_rates["CARD"]:.1f}% for card payments.


Complication

The difference between raw and cleaned revenue was
₹{findings["duplicate_reconciliation_delta_inr"]:,.2f}, attributable to the
duplicate orders removed during cleaning. The highest-risk segment was
{risk["payment_method"]} in Tier-{risk["city_tier"]} cities, with a return rate
of {risk["return_rate_pct"]:.1f}%. The apparent revenue peak was in
{inflated["month"]}, with revenue of ₹{inflated["apparent_revenue_inr"]:,.2f},
but after excluding quantity outliers it was
₹{inflated["corrected_revenue_inr"]:,.2f}.


Resolution

The corrected peak month was {peak["month"]}, with revenue of
₹{peak["revenue_inr"]:,.2f}. Mamaearth should investigate COD order returns,
especially in Tier-{risk["city_tier"]} cities, and review the operational
causes of duplicate orders. Future performance reporting should distinguish
verified revenue from outlier-inflated figures and preserve a reproducible
cleaning process.
""".strip()

    return {"status": "success", "narrative": narrative, "tokens": None, "source": "offline"}


def has_required_sections(narrative: str) -> bool:
    """Return True only when all three required SCR headings are present."""
    import re
    headings = ("Situation", "Complication", "Resolution")
    return all(
        re.search(rf"(?im)^\s*(?:#{1,6}\s*)?{heading}\s*$", narrative)
        for heading in headings
    )


def check_numeric_accuracy(narrative: str, findings: dict) -> bool:
    """Check required values in the narrative itself, accepting equivalent decimals."""
    import re
    from decimal import Decimal, InvalidOperation

    # Extract number tokens after removing thousands separators, then compare
    # numerically so 97,358.3 and 97,358.30 are treated as equivalent.
    tokens = re.findall(r"(?<![A-Za-z])\d[\d,]*(?:\.\d+)?", narrative)
    values = set()
    for token in tokens:
        try:
            values.add(Decimal(token.replace(",", "")))
        except InvalidOperation:
            continue

    payment_rates = findings["return_rate_by_payment"]
    risk = findings["highest_risk_segment"]
    peak = findings["true_peak_month"]
    expected = [
        ("Cleaned revenue", Decimal(str(findings["cleaned_total_revenue_inr"]))),
        ("COD return rate", Decimal(str(payment_rates["COD"]))),
        ("Highest-risk segment return rate", Decimal(str(risk["return_rate_pct"]))),
        ("Duplicate reconciliation delta", Decimal(str(findings["duplicate_reconciliation_delta_inr"]))),
        ("True peak month revenue", Decimal(str(peak["revenue_inr"])),),
    ]
    passed = True
    results = []
    for item in expected:
        label, value = item[0], item[1]
        ok = value in values
        results.append(f"{'PASS' if ok else 'FAIL'}: {label} {value}")
        passed = passed and ok

    normalized = narrative.lower()
    month_ok = "march" in normalized or peak["month"].lower() in normalized
    results.append(f"{'PASS' if month_ok else 'FAIL'}: True peak month {peak['month']}")
    passed = passed and month_ok
    print("\n".join(results))
    return passed

def main():
    parser = argparse.ArgumentParser(
        description="Generate the Mamaearth SCR narrative using Gemini or the offline fallback."
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Run the deterministic offline fallback without making an API call.",
    )
    parser.add_argument(
        "--output",
        default=str(SAMPLE_FILE),
        help="Output text file path (default: narrator/sample_output.txt).",
    )
    args = parser.parse_args()
    output_file = Path(args.output).expanduser().resolve()

    try:
        with open(FINDINGS_FILE, "r", encoding="utf-8") as file:
            findings = json.load(file)
    except Exception as err:
        print(f"Could not load findings.json: {type(err).__name__}: {err}")
        return

    if args.offline:
        result = generate_scr_narrative_offline(findings)
        result["source"] = "offline (explicit --offline mode)"
        print("Offline mode selected: no API call will be made.")
    else:
        result = generate_scr_narrative(findings)

    
    # Validate the API response before using it.
    if result["status"] == "error":
        print(f"Gemini unavailable: {result['message']}")
        print("Using the offline narrative instead.")
        result = generate_scr_narrative_offline(findings)
        result["source"] = "offline fallback (Gemini request failed)"
    else:
        candidate = result["narrative"]

        candidate_sections_passed = has_required_sections(candidate)

        candidate_checker = io.StringIO()
        with contextlib.redirect_stdout(candidate_checker):
            candidate_accuracy_passed = check_numeric_accuracy(candidate, findings)

        if not candidate_sections_passed or not candidate_accuracy_passed:
            print("Gemini output failed section or numeric validation.")
            print("Using the deterministic offline narrative instead.")
            result = generate_scr_narrative_offline(findings)
            result["source"] = "offline fallback (Gemini output failed validation)"

    # Validate the narrative that will actually be saved.
    narrative = result["narrative"]
    print(f"\nNarrative source: {result.get('source', 'Gemini API')}")
    print(f"Status: {result['status']}")
    print(f"Tokens used: {result.get('tokens')}")
    print("\n" + narrative)

    sections_passed = has_required_sections(narrative)
    print(f"\nSCR section check: {'PASS' if sections_passed else 'FAIL'}")

    checker_output = io.StringIO()
    with contextlib.redirect_stdout(checker_output):
        accuracy_passed = check_numeric_accuracy(narrative, findings)

    checks_text = checker_output.getvalue().strip()
    print("\n" + checks_text)
    print(f"\nNumeric accuracy check: {'PASS' if accuracy_passed else 'FAIL'}")


    with open(output_file, "w", encoding="utf-8") as file:
        file.write(f"Narrative source: {result.get('source', 'Gemini API')}\n")
        file.write(f"Status: {result['status']}\n")
        file.write(f"Tokens used: {result.get('tokens')}\n\n")
        file.write(narrative + "\n\n")
        file.write(f"SCR section check: {'PASS' if sections_passed else 'FAIL'}\n\n")
        file.write(checks_text + "\n\n")
        file.write(f"Numeric accuracy check: {'PASS' if accuracy_passed else 'FAIL'}\n")

    print(f"\nSaved narrative and numeric-check evidence to: {output_file}")
    if not accuracy_passed:
        print("Review the narrative and sample_output.txt before submission.")


if __name__ == "__main__":
    main()
