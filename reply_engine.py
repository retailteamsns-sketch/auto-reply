"""Reply engine for Umer's personal retail / supply-chain assistant bot.

This module is intentionally free of any Slack imports so it can be unit
tested standalone and called synchronously in the hot path. All reply
generation is fast local logic (no network / LLM calls) to stay within the
~1 second response-time target.
"""

import re

# Persona preamble lines. Kept short so replies are concise.
_PERSONA_INTRO = (
    "Hi <@{user_id}>, this is Umer's assistant handling retail & supply-chain "
    "on his behalf."
)

# Keyword routing table. Order matters: the first category whose keywords
# match the incoming text wins. Each entry maps a category to (keywords, line).
_ROUTES = [
    (
        "orders",
        ("order", "orders", "purchase order", "po "),
        "Happy to help with your order. Share the order number and I'll pull "
        "up its status and next steps.",
    ),
    (
        "inventory",
        ("inventory", "stock", "in stock", "out of stock", "sku", "restock"),
        "I can check inventory and stock levels for you. Let me know the SKU "
        "or product and I'll confirm availability.",
    ),
    (
        "shipments",
        ("shipment", "shipments", "shipping", "delivery", "deliver",
         "tracking", "track", "freight", "in transit"),
        "I can track that shipment for you. Send the tracking or shipment "
        "number and I'll share the latest delivery status.",
    ),
    (
        "suppliers",
        ("supplier", "suppliers", "vendor", "vendors", "procurement"),
        "I can help with supplier and vendor matters. Tell me which vendor or "
        "what you need and I'll coordinate it.",
    ),
    (
        "returns",
        ("return", "returns", "refund", "rma", "exchange"),
        "I can assist with returns and refunds. Share the order or RMA number "
        "and I'll get the return process moving.",
    ),
]

_GENERIC = (
    "How can I help today? I can assist with orders, inventory, shipments, "
    "suppliers, and returns, and I'll loop in Umer directly if needed."
)


def _matches(text_lower, keywords):
    """Return True if any keyword appears as a word-ish match in text."""
    for kw in keywords:
        # Build a boundary-aware pattern so short tokens like "po " and
        # "sku" don't fire on unrelated substrings.
        pattern = r"\b" + re.escape(kw.strip()) + r"\b"
        if re.search(pattern, text_lower):
            return True
    return False


def route_category(text):
    """Return the category name for the given text, or 'generic'."""
    text_lower = (text or "").lower()
    for category, keywords, _line in _ROUTES:
        if _matches(text_lower, keywords):
            return category
    return "generic"


def build_reply(text, user_id):
    """Build the auto-reply string addressing the sender.

    Args:
        text: the incoming Slack message text.
        user_id: the Slack user id of the sender (addressed in the reply).

    Returns:
        A concise, friendly reply in Umer's assistant persona.
    """
    intro = _PERSONA_INTRO.format(user_id=user_id)
    category = route_category(text)

    line = _GENERIC
    if category != "generic":
        for cat, _keywords, cat_line in _ROUTES:
            if cat == category:
                line = cat_line
                break

    return f"{intro} {line}"
