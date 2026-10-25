"""Command-line demo: chat with HerChoice AI in the terminal, no WhatsApp account needed.

Run:  python -m herchoice.cli            (Hausa by default)
      python -m herchoice.cli --lang en  (English)
"""

from __future__ import annotations

import argparse
import os


def main() -> None:
    parser = argparse.ArgumentParser(description="HerChoice AI terminal demo")
    parser.add_argument("--lang", choices=["ha", "en"], default=None, help="reply language")
    parser.add_argument("--approved-only", action="store_true",
                        help="answer only from clinically approved content (as in a pilot)")
    args = parser.parse_args()
    if args.lang:
        os.environ["HERCHOICE_DEFAULT_LANG"] = args.lang
    # The demo shows draft content, clearly labelled, unless --approved-only is given.
    os.environ.setdefault("HERCHOICE_ALLOW_DRAFT", "false" if args.approved_only else "true")

    from .config import get_settings
    from .engine import Engine

    engine = Engine(get_settings())
    print("HerChoice AI demo. Type a question (or MENU, DELETE). Ctrl+C to quit.\n")
    try:
        while True:
            text = input("You: ").strip()
            if not text:
                continue
            reply = engine.handle("demo-user", text)
            tag = f"  [safety: {reply.flag}]" if reply.flag != "none" else ""
            print(f"\nHerChoice:{tag}\n{reply.text}\n")
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye.")


if __name__ == "__main__":
    main()
