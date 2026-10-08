# Umer's Auto-Reply Assistant (Slack bot)

A lightweight Slack bot that acts as **Umer's personal assistant for retail &
supply-chain**. Whenever an incoming message mentions the word **"Umer"**
(case-insensitive), the bot auto-replies on Umer's behalf, addressing the
sender and offering help.

## How it works

- Listens to Slack `message` events in **Socket Mode** (no public URL needed —
  it connects over a WebSocket, which keeps latency low and deployment simple).
- When a message contains the trigger word (default `umer`, configurable via
  the `TRIGGER_WORD` env var), it builds a reply with `build_reply()` and posts
  it in the same channel — **in-thread** if the original message was in a
  thread.
- Ignores the bot's own messages, other bots, and messages without text.

### Latency design (~1 second target)

The reply handler is **fast and synchronous**. It does **not** call any
external LLM or network service in the hot path. Replies are produced by fast
local logic (`reply_engine.py`): a predefined persona plus lightweight keyword
routing. This keeps the end-to-end response time within the ~1 second target.

### Persona & keyword routing

The assistant responds in a friendly, concise retail & supply-chain persona. It
acknowledges the sender, states that Umer's assistant is responding, and offers
help. Simple keyword routing tailors one line to the topic:

| Topic                         | Example triggers                                  |
| ----------------------------- | ------------------------------------------------- |
| Orders                        | order, orders, purchase order                     |
| Inventory / stock             | inventory, stock, sku, restock                    |
| Shipments / delivery          | shipment, shipping, delivery, tracking, freight   |
| Suppliers / vendors           | supplier, vendor, procurement                     |
| Returns                       | return, refund, rma, exchange                     |
| _Anything else_               | generic helpful acknowledgement                   |

## Setup

### 1. Create a Slack app

1. Go to <https://api.slack.com/apps> and click **Create New App** →
   **From scratch**. Name it and pick your workspace.

### 2. Add bot scopes

Under **OAuth & Permissions → Scopes → Bot Token Scopes**, add:

- `app_mentions:read`
- `channels:history`
- `groups:history`
- `im:history`
- `mpim:history`
- `chat:write`

### 3. Subscribe to message events

Under **Event Subscriptions**, enable events and subscribe the bot to:

- `message.channels`
- `message.groups`
- `message.im`
- `message.mpim`

### 4. Enable Socket Mode

1. Under **Socket Mode**, toggle it **on**.
2. Under **Basic Information → App-Level Tokens**, generate an app-level token
   with the `connections:write` scope. This is your `SLACK_APP_TOKEN`
   (starts with `xapp-`).

### 5. Install the app

Install the app to your workspace (**OAuth & Permissions → Install to
Workspace**). Copy the **Bot User OAuth Token** (starts with `xoxb-`) — this is
your `SLACK_BOT_TOKEN`. Invite the bot to any channels you want it active in.

### 6. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 7. Configure environment variables

Copy `.env.example` to `.env` and fill in your tokens:

```bash
cp .env.example .env
```

```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
TRIGGER_WORD=umer
```

Then export them into your shell (or use a tool like `direnv` / `python-dotenv`):

```bash
export $(grep -v '^#' .env | xargs)
```

### 8. Run

```bash
python app.py
```

The bot will connect over Socket Mode and start auto-replying to any message
containing the trigger word.

## Development & tests

The reply logic lives in `reply_engine.py`, which has **no Slack imports**, so
it is testable standalone without a Slack connection.

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -q
```

You can also run the tests without pytest installed:

```bash
python tests/test_reply_engine.py
```

## Files

- `app.py` — Slack Bolt app, Socket Mode handler, message routing.
- `reply_engine.py` — `build_reply()` persona + keyword routing (pure logic).
- `tests/test_reply_engine.py` — unit tests for the reply engine.
- `requirements.txt` / `requirements-dev.txt` — runtime and dev dependencies.
- `.env.example` — documents the required environment variables.
