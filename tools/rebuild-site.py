#!/usr/bin/env python3
"""
rebuild-site.py — Clean rebuild of the Jekyll site.

What it does:
  1. Removes build artifacts (_site/, .jekyll-cache/)
  2. Removes gem lock file to ensure fresh dependencies
  3. Runs bundle install to install gems
  4. Performs a clean production build with Jekyll

Usage:
  ./tools/rebuild-site.py              # Standard clean rebuild
  ./tools/rebuild-site.py --verbose    # Show detailed output
  ./tools/rebuild-site.py --help       # Show this help information
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed output from each command"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleaned without actually doing it",
    )
    args = parser.parse_args()

    # Get repo root (parent of tools directory)
    repo_root = Path(__file__).resolve().parent.parent
    os.chdir(repo_root)

    # Directories and files to clean
    clean_targets = [
        repo_root / "_site",
        repo_root / ".jekyll-cache",
    ]

    print("=" * 60)
    print("  Jekyll Site Clean Rebuild")
    print("=" * 60)
    print()

    # Clean phase
    print("→ Cleaning build artifacts...")
    for target in clean_targets:
        if target.exists():
            if args.dry_run:
                print(f"  [dry-run] remove {target.relative_to(repo_root)}/")
            else:
                shutil.rmtree(target)
                print(f"  ✓ removed {target.relative_to(repo_root)}/")
        else:
            if args.verbose:
                print(f"  - {target.relative_to(repo_root)}/ not found (skipped)")

    if args.dry_run:
        print("\n[dry-run] Skipping bundle and build steps\n")
        return

    # Bundle phase
    print("\n→ Installing gems...")
    bundle_cmd = ["bundle", "install"]
    try:
        result = subprocess.run(
            bundle_cmd,
            cwd=repo_root,
            check=True,
            capture_output=not args.verbose,
        )
        print("  ✓ gems installed")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ bundle install failed with exit code {e.returncode}")
        sys.exit(1)

    # Build phase
    print("\n→ Building site...")
    build_cmd = ["bundle", "exec", "jekyll", "build", "--trace" if args.verbose else ""]
    build_cmd = [cmd for cmd in build_cmd if cmd]  # Remove empty strings

    try:
        result = subprocess.run(
            build_cmd,
            cwd=repo_root,
            env={**os.environ, "JEKYLL_ENV": "production"},
            check=True,
            capture_output=not args.verbose,
        )
        print("  ✓ build complete")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ jekyll build failed with exit code {e.returncode}")
        if not args.verbose:
            print("\nRe-run with --verbose to see detailed output")
        sys.exit(1)

    print()
    print("=" * 60)
    print("  ✓ Site rebuilt successfully")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
