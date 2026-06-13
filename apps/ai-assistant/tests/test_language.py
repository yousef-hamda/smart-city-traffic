"""Tests for language detection."""

from __future__ import annotations

from ai_assistant.language import detect_language


def test_english_detected() -> None:
    assert detect_language("Hello traffic on route 1") == "en"


def test_hebrew_detected() -> None:
    assert detect_language("שלום") == "he"


def test_arabic_detected() -> None:
    assert detect_language("مرحبا") == "ar"


def test_mixed_hebrew_english() -> None:
    # Hebrew chars dominate — expect he
    result = detect_language("פקק תנועה on route 1")
    assert result == "he"


def test_empty_string_falls_back() -> None:
    result = detect_language("")
    assert result in {"en", "he", "ar"}
