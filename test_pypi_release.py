#!/usr/bin/env python3
"""
Test script for PyPI release process
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    print(f"Running: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} successful")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("Testing PyPI release process...")

    # Step 1: Build the package
    if not run_command("python -m build", "Building package"):
        return False

    # Step 2: Check the built files
    if not os.path.isdir("dist/"):
        print("✗ Build directory not found")
        return False

    files = os.listdir("dist/")
    print(f"✓ Built files: {files}")

    # Step 3: Check package with twine
    if not run_command("twine check dist/*", "Checking package with twine"):
        return False

    # Step 4: Test upload to TestPyPI (dry run)
    print("\nTesting upload to TestPyPI (dry run)...")
    print("Note: This requires TEST_PYPI_API_TOKEN to be set")

    test_pypi_token = os.getenv("TEST_PYPI_API_TOKEN")
    if not test_pypi_token:
        print("⚠ TEST_PYPI_API_TOKEN not set - skipping upload test")
        print("To test upload, set TEST_PYPI_API_TOKEN environment variable")
        return True

    # Test upload to TestPyPI
    upload_cmd = "twine upload --repository testpypi --verbose dist/*"
    if not run_command(upload_cmd, "Uploading to TestPyPI"):
        return False

    print("\n✓ PyPI release process test completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)