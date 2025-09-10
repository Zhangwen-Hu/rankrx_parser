import re, json, sys, pathlib

def _extract_text_from_pdf(pdf_path: str) -> str:
    p = pathlib.Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text = ""
    # Attempt PyPDF2
    try:
        import PyPDF2
        with open(p, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            parts = []
            for page in reader.pages:
                try:
                    parts.append(page.extract_text() or "")
                except Exception:
                    parts.append("")
            text = "\n".join(parts)
    except Exception:
        text = ""

    if text and text.strip():
        return text

    # Fallback to pdfminer.six
    try:
        from pdfminer.high_level import extract_text
        return extract_text(str(p)) or ""
    except Exception as e:
        raise RuntimeError("Could not extract text from PDF using PyPDF2 or pdfminer.six") from e

def parse_eras_visa(text: str):
    header_ok = re.search(r'\bMy\s*ERAS\s*Application\b', text, re.I) is not None

    def grab(field):
        m = re.search(rf'{field}\s*:\s*([^\n\r]+)', text, re.I)
        return m.group(1).strip() if m else None

    authorized = grab(r'Authorized to Work in the U\.S\.')
    current_work_authorization = grab(r'Current Work Authorization')
    visa_needed = grab(r'Visa Sponsorship Needed')
    visa_sought = grab(r'Visa Sponsorship Sought')

    block = re.search(r'(Authorized to Work in the U\.S\.:.*?)(?:\n{2,}|Self Identification:|Present Mailing Address:)', text, re.I|re.S)
    raw_extract = block.group(1).strip() if block else None

    return {
        "section": "ERAS Application",
        "header_found": bool(header_ok),
        "authorized_to_work_us": authorized,
        "current_work_authorization": current_work_authorization,
        "visa_sponsorship_needed": visa_needed,
        "visa_sponsorship_sought": visa_sought,
        "raw_extract": raw_extract,
    }

def parse_usmle_transcript(text: str):
    header_ok = bool(re.search(r'\bUSMLE\s*Transcript\b', text, re.I)) and bool(re.search(r'United States Medical Licensing Examination', text, re.I))

    step1_attempts = []
    for m in re.finditer(r'(?:^|\s)(\d{1,2}/\d{1,2}/\d{2,4})\s+(Pass|Fail)\b(?:\s*\(?(\d{2,3})\)?)?', text, re.I):
        date, outcome, score = m.groups()
        step1_attempts.append({"date": date.strip(), "outcome": outcome.title(), "score": score})

    step2_attempts = []
    for m in re.finditer(r'(?:USMLE\s*Step\s*2\s*CK.*?\n)?\s*(\d{1,2}/\d{1,2}/\d{2,4})\s+Pass\b(?:\s*\(?(\d{2,3})\)?)?', text, re.I):
        date, score = m.groups()
        step2_attempts.append({"date": date.strip(), "outcome": "Pass", "score": score})

    for m in re.finditer(r'Clinical Knowledge\s*\(CK\).*?(\d{1,2}/\d{1,2}/\d{2,4})\s+(Pass|Fail)\b(?:\s*\(?(\d{2,3})\)?)?', text, re.I|re.S):
        date, outcome, score = m.groups()
        step2_attempts.append({"date": date.strip(), "outcome": outcome.title(), "score": score})

    def dedupe(attempts):
        uniq, seen = [], set()
        for a in attempts:
            key = (a.get("date"), a.get("outcome"), a.get("score"))
            if key not in seen:
                seen.add(key)
                uniq.append(a)
        return uniq

    step1_attempts = dedupe(step1_attempts)
    step2_attempts = dedupe(step2_attempts)

    step1_failures = sum(1 for a in step1_attempts if (a.get("outcome","").lower()=="fail"))
    step2_failures = sum(1 for a in step2_attempts if (a.get("outcome","").lower()=="fail"))

    def latest_pass(attempts):
        for a in reversed(attempts):
            if a.get("outcome","").lower()=="pass":
                return a
        return None

    step1_latest_pass = latest_pass(step1_attempts)
    step2_latest_pass = latest_pass(step2_attempts)

    return {
        "section": "USMLE Transcript",
        "header_found": bool(header_ok),
        "step_1": {
            "passed": bool(step1_latest_pass),
            "score": step1_latest_pass.get("score") if step1_latest_pass else None,
            "failures": step1_failures,
            "attempts": step1_attempts,
        },
        "step_2_ck": {
            "passed": bool(step2_latest_pass),
            "pass_date": step2_latest_pass.get("date") if step2_latest_pass else None,
            "score": step2_latest_pass.get("score") if step2_latest_pass else None,
            "failures": step2_failures,
            "attempts": step2_attempts,
        },
    }

def parse_ecfmg_status(text: str):
    header_in_header = bool(re.search(r'\bECFMG\s*Status\s*Report\b', text, re.I))
    midline_ok = bool(re.search(r'\bECFMG\s*STATUS\s*REPORT\b', text, re.I))

    m = re.search(r'ECFMG Certified\s*:\s*(Yes|No)\b', text, re.I)
    certified = m.group(1).title() if m else None

    return {
        "section": "ECFMG Status Report",
        "header_found": bool(header_in_header and midline_ok),
        "ecfmg_certified": certified if certified else "Not Available",
    }

def parse_all_text(text: str):
    return {
        "eras_visa": parse_eras_visa(text),
        "usmle_transcript": parse_usmle_transcript(text),
        "ecfmg_status": parse_ecfmg_status(text),
    }

def parse_pdf(pdf_path: str):
    text = _extract_text_from_pdf(pdf_path)
    return parse_all_text(text)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rankrx_pdf_parser.py /path/to/file.pdf", file=sys.stderr)
        sys.exit(2)
    pdf_path = sys.argv[1]
    data = parse_pdf(pdf_path)
    print(json.dumps(data, indent=2))
