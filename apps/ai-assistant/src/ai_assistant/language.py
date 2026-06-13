"""Language detection for multilingual support (EN / HE / AR)."""

from __future__ import annotations

import re  # noqa: I001

# Unicode ranges
_HE_RANGE = re.compile(r"[א-תיִ-פֿ]")
_AR_RANGE = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")


def detect_language(text: str) -> str:
    """Detect language of *text*, returning 'en', 'he', or 'ar'.

    Heuristics run first (character set); langdetect is the fallback.
    """
    if _HE_RANGE.search(text):
        return "he"
    if _AR_RANGE.search(text):
        return "ar"
    try:
        from langdetect import detect

        lang = detect(text)
        if lang == "he":
            return "he"
        if lang == "ar":
            return "ar"
        return "en"
    except Exception:
        return "en"
