"""Woosdom Task Bridge v3.1 — file watcher → Redis Stream + Telegram notification.

Watches to_hands.md for changes, records tasks in Redis, and sends
Telegram notifications. Execution is manual — user forwards to the
appropriate engine (AG/Codex/CC).
"""
import os
import re
import time
import urllib.request
import json
import hashlib
from datetime import datetime

# Configure via environment variables
VAULT_ROOT = os.getenv("WOOSDOM_VAULT", "/path/to/your/Woosdom_Brain")
TO_HANDS   = os.path.join(VAULT_ROOT, "00_System", "Templates", "to_hands.md")
FROM_HANDS = os.path.join(VAULT_ROOT, "00_System", "Templates", "from_hands.md")

POLL_INTERVAL = 2  # seconds
DEBOUNCE_WINDOW = 5  # seconds

# Telegram config (set via environment variables)
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID   = os.getenv("TG_CHAT_ID", "")

# Note: Full implementation omitted for brevity.
# See the actual task_bridge project for complete code.
# This file demonstrates the configuration pattern.

def send_telegram(message: str):
    """Send notification via Telegram bot."""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("[skip] Telegram not configured")
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    data = json.dumps({"chat_id": TG_CHAT_ID, "text": message}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req)

def main():
    """Poll to_hands.md for changes and notify."""
    print(f"Task Bridge watching: {TO_HANDS}")
    last_hash = ""
    while True:
        try:
            if os.path.exists(TO_HANDS):
                with open(TO_HANDS) as f:
                    content = f.read()
                h = hashlib.md5(content.encode()).hexdigest()
                if h != last_hash and content.strip():
                    last_hash = h
                    send_telegram(f"📋 New task in to_hands.md")
                    print(f"[{datetime.now()}] Task detected")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
