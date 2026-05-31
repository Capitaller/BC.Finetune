#!/usr/bin/env python3
"""Count training text tokens with the same tokenizer used for training."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_TRAINING_TEXT = Path("data/bc_al_text/business_central_al_training_text.txt")
DEFAULT_MODEL = "unsloth/gemma-4-E2B"


def main() -> int:
    parser = argparse.ArgumentParser(description="Count tokens in a training text file with a Hugging Face tokenizer.")
    parser.add_argument(
        "--training-text",
        "--corpus",
        dest="training_text",
        type=Path,
        default=DEFAULT_TRAINING_TEXT,
        help=f"Training text file. Default: {DEFAULT_TRAINING_TEXT}",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Tokenizer model name. Default: {DEFAULT_MODEL}")
    parser.add_argument("--chunk-size", type=int, default=1_000_000, help="Characters per tokenizer batch.")
    args = parser.parse_args()

    try:
        from transformers import AutoTokenizer
    except ImportError as exc:
        raise SystemExit("Install transformers first: pip install transformers") from exc

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    total_tokens = 0
    total_chars = 0

    with args.training_text.open("r", encoding="utf-8") as training_text:
        while True:
            chunk = training_text.read(args.chunk_size)
            if not chunk:
                break
            total_chars += len(chunk)
            total_tokens += len(tokenizer.encode(chunk, add_special_tokens=False))

    print(f"Training text: {args.training_text}")
    print(f"Tokenizer: {args.model}")
    print(f"Characters: {total_chars:,}")
    print(f"Tokens: {total_tokens:,}")
    print(f"Characters per token: {total_chars / total_tokens:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
