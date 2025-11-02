"""
Script to run authentication tests with proper configuration.
"""
import sys
import subprocess


def run_tests():
    """Run pytest with recommended options."""
    print("=" * 70)
    print("Running Authentication Tests for Study Assistant API")
    print("=" * 70)
    print()
    
    # Run pytest with verbose output and coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-p", "no:warnings"
    ]
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install it:")
        print("  pip install pytest pytest-cov httpx")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
