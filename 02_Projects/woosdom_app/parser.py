#!/usr/bin/env python3
from __future__ import annotations
"""
parser.py v0.2 — active_context.md → dashboard_data.json

Parses the Brain's active_context and generates structured data
for the Woosdom dashboard (PyWebView).
"""

import json
import re
import os
from datetime import datetime

# ─── Paths (configure via environment variable or edit directly) ──────────
VAULT_ROOT     = os.getenv("WOOSDOM_VAULT", "/path/to/your/Woosdom_Brain")
INPUT_FILE     = os.path.join(VAULT_ROOT, "00_System", "Prompts", "Ontology", "active_context.md")
DIRECTIVE      = os.path.join(VAULT_ROOT, "00_System", "Prompts", "Ontology", "brain_directive.md")
TRAINING_FILE  = os.path.join(VAULT_ROOT, "01_Domains", "Health", "training_protocol.md")
ROADMAP_FILE   = os.path.join(VAULT_ROOT, "01_Domains", "life_roadmap.md")
ACTIVITY_FILE  = os.path.join(VAULT_ROOT, "00_System", "Logs", "agent_activity.md")
TO_HANDS_FILE  = os.path.join(VAULT_ROOT, "00_System", "Templates", "to_hands.md")
FROM_HANDS_FILE= os.path.join(VAULT_ROOT, "00_System", "Templates", "from_hands.md")
SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE    = os.path.join(SCRIPT_DIR, "dashboard_data.json")

# Note: Full parser implementation omitted for brevity.
# See the actual woosdom_app project for complete code.
# This file demonstrates the vault path configuration pattern.

def main():
    """Parse active_context.md and generate dashboard_data.json"""
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Check WOOSDOM_VAULT env var.")
        return
    
    # ... parsing logic ...
    print(f"Dashboard data written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
