"""Tests for guardrail off-topic detection."""

from __future__ import annotations

from ai_assistant.guardrails import get_refusal_message, is_off_topic


def test_football_is_off_topic() -> None:
    assert is_off_topic("what is the best football team?") is True


def test_traffic_is_not_off_topic() -> None:
    assert is_off_topic("traffic on route 1") is False


def test_congestion_is_not_off_topic() -> None:
    assert is_off_topic("what is the congestion level near Malha?") is False


def test_movie_is_off_topic() -> None:
    assert is_off_topic("recommend a good movie to watch") is True


def test_recipe_is_off_topic() -> None:
    assert is_off_topic("give me a recipe for chocolate cake") is True


def test_refusal_message_en() -> None:
    msg = get_refusal_message("en")
    assert isinstance(msg, str)
    assert len(msg) > 10


def test_refusal_message_he() -> None:
    msg = get_refusal_message("he")
    assert isinstance(msg, str)
    assert len(msg) > 10


def test_refusal_message_ar() -> None:
    msg = get_refusal_message("ar")
    assert isinstance(msg, str)
    assert len(msg) > 10


def test_refusal_message_unknown_lang_falls_back_to_en() -> None:
    en_msg = get_refusal_message("en")
    unknown_msg = get_refusal_message("xx")
    assert en_msg == unknown_msg
