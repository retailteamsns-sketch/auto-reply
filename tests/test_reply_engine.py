"""Unit tests for reply_engine.build_reply.

These tests exercise pure local logic only -- no Slack connection is needed.
reply_engine.py has no Slack imports, so this file can run even when the
Slack libraries are not installed.
"""

import os
import sys

# Make the project root importable when run directly or via pytest.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reply_engine import build_reply, route_category  # noqa: E402

SENDER = "U12345"


def _reply(text):
    return build_reply(text, SENDER)


def test_addresses_sender():
    reply = _reply("Hey Umer, quick question")
    assert "<@U12345>" in reply
    assert "Umer's assistant" in reply


def test_orders_routing():
    assert route_category("Where is my order?") == "orders"
    reply = _reply("Can you check on my order status?")
    assert "order" in reply.lower()


def test_inventory_routing():
    assert route_category("Do we have this in stock?") == "inventory"
    assert route_category("What is the inventory level?") == "inventory"
    reply = _reply("Checking inventory for SKU 42")
    assert "inventory" in reply.lower() or "stock" in reply.lower()


def test_shipments_routing():
    assert route_category("Need the tracking number for my delivery") == "shipments"
    assert route_category("When will the shipment arrive?") == "shipments"
    reply = _reply("Any update on the shipment?")
    assert "shipment" in reply.lower() or "delivery" in reply.lower()


def test_suppliers_routing():
    assert route_category("Issue with a supplier") == "suppliers"
    assert route_category("Need to contact the vendor") == "suppliers"
    reply = _reply("Question about our vendor contract")
    assert "supplier" in reply.lower() or "vendor" in reply.lower()


def test_returns_routing():
    assert route_category("I want to return this item") == "returns"
    assert route_category("How do I get a refund?") == "returns"
    reply = _reply("Starting an RMA for a damaged product")
    assert "return" in reply.lower() or "refund" in reply.lower()


def test_generic_fallback():
    assert route_category("Hello there, how are you?") == "generic"
    reply = _reply("Just saying hi to Umer")
    # Generic reply still addresses the sender and offers help.
    assert "<@U12345>" in reply
    assert "help" in reply.lower()


def test_no_false_positive_substring():
    # "reorder" contains "order" but should still route to orders via \b? No:
    # \border\b will not match inside "reorder", so this is generic.
    assert route_category("Let's reinvent the process") == "generic"


def test_empty_text_is_generic_and_safe():
    assert route_category("") == "generic"
    reply = build_reply("", SENDER)
    assert "<@U12345>" in reply


def _run_all():
    """Allow running this file directly without pytest installed."""
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    if failures:
        print(f"\n{failures} test(s) failed")
        sys.exit(1)
    print("\nAll tests passed")


if __name__ == "__main__":
    _run_all()
