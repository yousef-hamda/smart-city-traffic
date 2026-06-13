"""Simple keyword-based guardrail to refuse off-topic questions."""

from __future__ import annotations

BLOCKED_KEYWORDS: list[str] = [
    # Sports
    "football",
    "soccer",
    "basketball",
    "tennis",
    "baseball",
    "cricket",
    "nba",
    "nfl",
    "fifa",
    "premier league",
    "champions league",
    "olympics",
    # Cooking / food
    "recipe",
    "cooking",
    "bake",
    "baking",
    "restaurant recommendation",
    "best food",
    "calories",
    "diet plan",
    # Movies / entertainment
    "movie",
    "film",
    "cinema",
    "netflix",
    "actor",
    "actress",
    "hollywood",
    "tv show",
    "series",
    "music",
    "song",
    "album",
    # Finance / stocks (non-transport)
    "stock market",
    "bitcoin",
    "crypto",
    "invest",
    "forex",
    # Other
    "horoscope",
    "astrology",
    "weather forecast for tomorrow",
    "lottery",
    "casino",
    "gambling",
]


def is_off_topic(text: str) -> bool:
    """Return True if the text is clearly unrelated to traffic/transport."""
    lower = text.lower()
    return any(kw in lower for kw in BLOCKED_KEYWORDS)


_REFUSALS: dict[str, str] = {
    "en": (
        "I'm the Jerusalem Smart City traffic assistant. "
        "I can only help with traffic conditions, road incidents, route recommendations, "
        "and congestion analysis. Please ask a traffic-related question."
    ),
    "he": (
        "אני עוזר התנועה של ירושלים העיר החכמה. "
        "אני יכול לעזור רק בנושאי תנועה, תקריות דרכים, המלצות מסלולים וניתוח פקקים. "
        "אנא שאל שאלה הקשורה לתנועה."
    ),
    "ar": (
        "أنا مساعد حركة المرور لمدينة القدس الذكية. "
        "يمكنني فقط المساعدة في أوضاع حركة المرور والحوادث وتوصيات المسارات وتحليل الازدحام. "
        "يرجى طرح سؤال متعلق بحركة المرور."
    ),
}


def get_refusal_message(lang: str = "en") -> str:
    """Return a polite refusal message in the requested language."""
    return _REFUSALS.get(lang, _REFUSALS["en"])
