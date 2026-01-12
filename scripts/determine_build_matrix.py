#!/usr/bin/env python3
"""
Determine which boards to build based on changed files in a PR.

Logic:
- If any versions/*.version file changed → build ALL boards
- Else → build only boards whose directories have changes
"""

import argparse
import json
import sys
import yaml
from pathlib import Path
from typing import List, Set, Dict, Optional


def read_board_spec(spec_path: Path) -> Optional[Dict]:
    """Read and parse a board's spec.yaml file."""
    try:
        with open(spec_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Failed to read {spec_path}: {e}", file=sys.stderr)
        return None


def find_all_boards(base_path: Path) -> List[Dict[str, str]]:
    """
    Find all boards by locating spec.yaml files.
    
    Returns list of dicts with 'board' and 'arch' keys.
    """
    boards = []
    boards_dir = base_path / "boards"
    
    if not boards_dir.exists():
        return boards
    
    for spec_file in boards_dir.rglob("spec.yaml"):
        # Get relative path from boards/ directory
        # e.g., boards/vd-rd/glasnost-aa13/spec.yaml -> vd-rd/glasnost-aa13
        relative = spec_file.parent.relative_to(boards_dir)
        board_path = str(relative)
        
        # Parse spec to get architecture
        spec = read_board_spec(spec_file)
        arch = "unknown"
        if spec and "board" in spec and "cpu" in spec["board"]:
            arch = spec["board"]["cpu"].get("arch", "unknown")
        
        boards.append({
            "board": board_path,
            "arch": arch
        })
    include' key containing list of board objects with 'board' and 'arch'
    """
    # Check if any version file changed
    version_changed = any(
        Path(f).parts[0] == "versions" and f.endswith(".version")
        for f in changed_files
    )
    
    if version_changed:
        # Build ALL boards
        boards = find_all_boards(base_path)
        reason = "version update (testing all boards)"
    else:
        # Build only affected boards
        affected = extract_affected_boards(changed_files)
        
        # Get full board info including arch
        all_boards = find_all_boards(base_path)
        boards = [b for b in all_boards if b["board"] in affected]
        reason = "board-specific changes" if boards else "no boards affected"
    
    return {
        "include
def determine_build_matrix(changed_files: List[str], base_path: Path) -> dict:
    """
    Determine which boards should be built.
    
    Returns:
        dict with 'boards' key containing list of board paths
    """
    # Check if any version file changed
    version_changed = any(
        Path(f).parts[0] == "versions" and f.endswith(".version")
        for f in changed_files
    )
    
    if version_changed:
        # Build ALL boards
        boards = find_all_boards(base_path)
        reason = "version update (testing all boards)"
    else:
        # Build only affected boards
        affected = extract_affected_boards(changed_files)
        boards = sorted(affected)
        reason = "board-specific changes" if boards else "no boards affected"
    
    return {
        "boards": boards,
        "reason": reason,
        "total": len(boards)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Determine build matrix based on changed files"
    )
    parser.add_argument(
        "changed_files",
        nargs="*",
        help="List of changed files (reads from stdin if not provided)"
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path.cwd(),
        help="Base path of the repository (default: current directory)"
    )
    parser.add_argument(
        "--github-output",
        action="store_true",
        help="Format output for GitHub Actions"
    )
    
    args = parser.parse_args()
    
    # Get changed files from args or stdin
    if args.changed_files:
        changed_files = args.changed_files
    else:
        changed_files = [line.strip() for line in sys.stdin if line.strip()]
    
    if not changed_files:
        print("Error: No changed files provided", file=sys.stderr)
        sys.exit(1)
    
    # Determine matrix
    result = determine_build_matrix(changed_files, args.base_path)
    
    # Output resulinclude=[{"board":"vd-rd/glasnost-aa13","arch":"arm"}]
        include_json = json.dumps(result["include"])
        print(f"include={includex format
        # Output: boards=["vd-rd/glasnost-aa13","vd-rd/glasnost-av3s"]
        boards_json = json.dumps(result["boards"])
        print(f"boards={boards_json}")
        print(f"total={result['total']}")
    else:
        # Human-readable format
        print(json.dumps(result, indent=2))
    
    # Exit with status 0 even if no boards (let workflow decide)
    return 0


if __name__ == "__main__":
    sys.exit(main())
