#!/usr/bin/env python3
"""
Linting script for AI Photonic Physical Verification project.

Runs all linting tools and provides a comprehensive report.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def run_command(cmd: List[str], description: str) -> Tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        success = result.returncode == 0
        output = result.stdout + result.stderr
        return success, output
    except Exception as e:
        return False, f"Error running {description}: {e}"


def main():
    """Run all linting checks."""
    print("🔍 Running comprehensive linting checks...\n")

    # Get the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    checks = [
        ("Black (Code formatting)", ["black", "--check", "--diff", "."]),
        ("isort (Import sorting)", ["isort", "--check-only", "--diff", "."]),
        ("Flake8 (Style guide)", ["flake8", "."]),
        ("MyPy (Type checking)", ["mypy", "--ignore-missing-imports", "."]),
    ]

    all_passed = True
    results = []

    for description, cmd in checks:
        print(f"Running {description}...")
        success, output = run_command(cmd, description)
        results.append((description, success, output))

        if success:
            print(f"✅ {description} passed")
        else:
            print(f"❌ {description} failed")
            if output.strip():
                print(f"   Output: {output.strip()}")
        print()

    # Summary
    print("=" * 50)
    print("LINTING SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for description, success, output in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {description}")
        if not success and output.strip():
            print(f"   Details: {output.strip()}")

    print(f"\nOverall: {passed}/{total} checks passed")

    if all_passed:
        print("🎉 All linting checks passed!")
        return 0
    else:
        print("⚠️  Some linting checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
