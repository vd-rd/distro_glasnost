#!/usr/bin/env python3
"""
Determine which boards to build based on changed files in a PR.

Rules:
- If any versions/*.version file changed, build every board.
- Otherwise, build only boards whose directories contain changes.

Outputs for GitHub Actions (when --github-output is passed):
- include: JSON list of objects with board/arch
- boards: JSON list of board identifiers
- total: number of boards to build
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml


def read_board_spec(spec_path: Path) -> Optional[Dict]:
    """Load a board spec.yaml file."""
    try:
        with open(spec_path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Warning: failed to read {spec_path}: {exc}", file=sys.stderr)
        return None


def find_all_boards(base_path: Path) -> List[Dict[str, str]]:
    """Return every board with its architecture."""
    boards: List[Dict[str, str]] = []
    boards_dir = base_path / "boards"

    if not boards_dir.exists():
        return boards

    for spec_file in boards_dir.rglob("spec.yaml"):
        relative = spec_file.parent.relative_to(boards_dir)
        board_path = str(relative)

        spec = read_board_spec(spec_file) or {}
        arch = "unknown"
        if isinstance(spec, dict):
            arch = spec.get("board", {}).get("cpu", {}).get("arch", "unknown")

        boards.append({"board": board_path, "arch": arch})

    return boards


def extract_affected_boards(changed_files: List[str]) -> Set[str]:
    """Collect board identifiers that have file changes."""
    boards: Set[str] = set()
    for changed in changed_files:
        path = Path(changed)
        if len(path.parts) >= 3 and path.parts[0] == "boards":
            boards.add(str(Path(path.parts[1]) / path.parts[2]))
    return boards


def determine_build_matrix(changed_files: List[str], base_path: Path) -> Dict:
    """Compute the build matrix data structure."""
    all_boards = find_all_boards(base_path)
    board_lookup = {b["board"]: b["arch"] for b in all_boards}

    version_changed = any(
        Path(name).parts[0] == "versions" and name.endswith(".version")
        for name in changed_files
    )

    if version_changed:
        include = all_boards
        reason = "version update (testing all boards)"
    else:
        affected = extract_affected_boards(changed_files)
        include = [
            {"board": board, "arch": board_lookup.get(board, "unknown")}
            for board in sorted(affected)
            if board in board_lookup
        ]
        reason = "board-specific changes" if include else "no boards affected"

    boards = [entry["board"] for entry in include]

    return {
        "include": include,
        "boards": boards,
        "total": len(include),
        "reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Determine build matrix based on changed files",
    )
    parser.add_argument(
        "changed_files",
        nargs="*",
        help="List of changed files (reads from stdin if not provided)",
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path.cwd(),
        help="Base path of the repository (default: current directory)",
    )
    parser.add_argument(
        "--github-output",
        action="store_true",
        help="Emit key/value pairs for GitHub Actions",
    )

    args = parser.parse_args()

    if args.changed_files:
        changed_files = args.changed_files
    else:
        changed_files = [line.strip() for line in sys.stdin if line.strip()]

    if not changed_files:
        print("Error: no changed files provided", file=sys.stderr)
        return 1

    result = determine_build_matrix(changed_files, args.base_path)

    if args.github_output:
        include_json = json.dumps(result["include"], separators=(",", ":"))
        boards_json = json.dumps(result["boards"], separators=(",", ":"))
        print(f"include={include_json}")
        print(f"boards={boards_json}")
        print(f"total={result['total']}")
        print(f"reason={result['reason']}")
    else:
        print(json.dumps(result, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
