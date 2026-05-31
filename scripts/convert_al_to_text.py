#!/usr/bin/env python3
"""Convert Business Central AL source files into training text for CPT."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_INPUT = Path("Base Application.Source")
DEFAULT_OUTPUT = Path("data/bc_al_text")
TRAINING_TEXT_FILENAME = "business_central_al_training_text.txt"
MICROSOFT_LICENSE_HEADER = """// ------------------------------------------------------------------------------------------------
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.
// ------------------------------------------------------------------------------------------------
"""
HEADER_SEPARATOR = "// ------------------------------------------------------------------------------------------------"
HEADER_COPYRIGHT = "// Copyright (c) Microsoft Corporation. All rights reserved."
HEADER_LICENSE_PREFIXES = (
    "// Licensed under the MIT License. See License.txt in the project root for license information.",
    "// Licensed under the MIT License. See License.txt in the project oder for license information.",
)


def iter_al_files(source_dir: Path) -> list[Path]:
    return sorted(path for path in source_dir.rglob("*.al") if path.is_file())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n")


def strip_repeated_header(text: str) -> tuple[str, int]:
    occurrences = text.count(MICROSOFT_LICENSE_HEADER)
    if occurrences:
        text = text.replace(MICROSOFT_LICENSE_HEADER, "")

    lines = text.splitlines(keepends=True)
    cleaned_lines = []
    index = 0
    while index < len(lines):
        line = lines[index]
        line_text = line.rstrip("\r\n")
        has_separator = line_text == HEADER_SEPARATOR
        copyright_index = index + 1 if has_separator else index
        license_index = copyright_index + 1

        if (
            copyright_index < len(lines)
            and license_index < len(lines)
            and lines[copyright_index].rstrip("\r\n") == HEADER_COPYRIGHT
        ):
            license_line = lines[license_index].rstrip("\r\n")
            matching_prefix = next(
                (prefix for prefix in HEADER_LICENSE_PREFIXES if license_line.startswith(prefix)),
                None,
            )
            if matching_prefix:
                occurrences += 1
                suffix = license_line[len(matching_prefix) :]
                if suffix:
                    cleaned_lines.append(suffix + "\n")

                index = license_index + 1
                if index < len(lines) and lines[index].rstrip("\r\n") == HEADER_SEPARATOR:
                    index += 1
                continue

        cleaned_lines.append(line)
        index += 1

    return "".join(cleaned_lines).lstrip("\n"), occurrences


def convert(source_dir: Path, output_dir: Path, dry_run: bool = False) -> dict[str, object]:
    source_dir = source_dir.resolve()
    output_dir = output_dir.resolve()
    files_dir = output_dir / "files"
    training_text_path = output_dir / TRAINING_TEXT_FILENAME
    manifest_path = output_dir / "manifest.json"

    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {source_dir}")

    al_files = iter_al_files(source_dir)
    summary = {
        "source_dir": str(source_dir),
        "output_dir": str(output_dir),
        "files_dir": str(files_dir),
        "training_text_path": str(training_text_path),
        "manifest_path": str(manifest_path),
        "al_file_count": len(al_files),
        "dry_run": dry_run,
    }

    if dry_run:
        return summary

    files_dir.mkdir(parents=True, exist_ok=True)
    manifest_files = []
    stripped_header_count = 0

    with training_text_path.open("w", encoding="utf-8", newline="\n") as training_text:
        for source_path in al_files:
            relative_path = source_path.relative_to(source_dir)
            output_path = files_dir / relative_path.with_suffix(".txt")
            output_path.parent.mkdir(parents=True, exist_ok=True)

            raw_content = read_text(source_path)
            content, stripped_header_occurrences = strip_repeated_header(raw_content)
            stripped_header_count += stripped_header_occurrences
            content = content.strip()
            output_path.write_text(content + "\n", encoding="utf-8", newline="\n")

            training_text.write(f"\n\n<|bc_al_file|>{relative_path.as_posix()}\n")
            training_text.write(content)
            training_text.write("\n<|end_bc_al_file|>\n")

            manifest_files.append(
                {
                    "source": relative_path.as_posix(),
                    "text": output_path.relative_to(output_dir).as_posix(),
                    "characters": len(content),
                    "stripped_microsoft_license_header_count": stripped_header_occurrences,
                }
            )

    summary["stripped_microsoft_license_header_count"] = stripped_header_count
    manifest = {**summary, "files": manifest_files}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"Convert Business Central .al files into mirrored .txt files and {TRAINING_TEXT_FILENAME}."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_INPUT, help=f"Input AL source directory. Default: {DEFAULT_INPUT}")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help=f"Output training text directory. Default: {DEFAULT_OUTPUT}")
    parser.add_argument("--dry-run", action="store_true", help="Report what would be converted without writing files.")
    args = parser.parse_args()

    summary = convert(args.source, args.output, args.dry_run)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
