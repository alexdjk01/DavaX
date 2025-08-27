# backend/safety.py
# Simple profanity gate with support for common inflections and light obfuscation.

from __future__ import annotations
import re
import unicodedata
from typing import Tuple

# 1) Base patterns (handle common suffixes/variants)
BASE_PATTERNS = [
    r"f(?:u|v)ck(?:ing|ed|er|ers|s)?",      # fuck, fucking, fvck, fucked, fucker(s), fucks
    r"mother\s*f(?:u|v)cker(?:s)?",         # motherfucker(s) with optional space
    r"shit(?:ty|ting|ted|s)?",              # shit, shitty, shitting, shitted, shits
    r"bitch(?:es|ing)?",                    # bitch, bitches, bitching
    r"asshole(?:s)?",                       # asshole(s)
    r"bastard(?:s)?",                       # bastard(s)
    r"dick(?:head|s)?",                     # dick, dicks, dickhead
    r"crap(?:py)?",                         # crap, crappy
    r"slut(?:s)?",                          # slut(s)
    r"whore(?:s)?"                          # whore(s)
]

# Token-wise detection (normal text)
TOKEN_RE = re.compile(r"\b(" + "|".join(BASE_PATTERNS) + r")\b", re.IGNORECASE)

# Spaced/obfuscated letters (e.g., "f u c k", "f*ck")
SPACED_RE = re.compile(
    r"\b("
    r"m\s*o\s*t\s*h\s*e\s*r\s*f\s*(?:u|v)\s*c\s*k(?:\s*s)?"  # mother f u c k (ers optional)
    r"|f\s*(?:u|v)\s*c\s*k(?:\s*(?:ing|ed|er|ers|s))?"       # f u c k, f-u-c-k-i-n-g, etc.
    r")\b",
    re.IGNORECASE
)

def _normalize(text: str) -> str:
    # Remove accents, keep spacing for spaced-letter detection
    t = unicodedata.normalize("NFKD", text)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return t

def is_input_allowed(user_text: str) -> Tuple[bool, str | None]:
    """
    Returns (True, None) if allowed, else (False, offending_fragment).
    """
    t = _normalize(user_text or "")

    # 1) Direct token match
    m = TOKEN_RE.search(t)
    if m:
        return False, m.group(0)

    # 2) Spaced/obfuscated letters
    m = SPACED_RE.search(t)
    if m:
        return False, m.group(0)

    # 3) Squeezed tokens (remove punctuation inside words like f*ck)
    squeezed_tokens = []
    for tok in t.split():
        squeezed_tokens.append(re.sub(r"[^A-Za-z0-9]+", "", tok))
    squeezed = " ".join(squeezed_tokens)
    m = TOKEN_RE.search(squeezed)
    if m:
        return False, m.group(0)

    return True, None
