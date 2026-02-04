def normalize_course(s: str) -> str:
    s = (s or "").strip().upper()
    s = " ".join(s.split())

    if s.endswith(" F"):
        s = s[:-2].strip()
    return s
