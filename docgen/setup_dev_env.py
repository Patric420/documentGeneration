#!/usr/bin/env python3
"""
Setup script for initializing development environment.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and report results."""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError as e:
        print(f"✗ Command not found: {e}")
        return False


def main():
    """Run setup operations."""
    print("\n" + "="*60)
    print("🚀 DOCUMENT GENERATION SYSTEM - DEVELOPMENT SETUP")
    print("="*60)
    
    # Check Python version
    print("\n📋 Checking Python version...")
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Install dependencies
    steps = [
        (["pip", "install", "--upgrade", "pip"], "Upgrading pip"),
        (["pip", "install", "-r", "requirements.txt"], "Installing production dependencies"),
        (["pip", "install", "-r", "requirements-dev.txt"], "Installing development dependencies"),
    ]
    
    success = True
    for cmd, description in steps:
        if not run_command(cmd, description):
            success = False
            break
    
    if not success:
        print("\n✗ Setup failed. Please fix errors and try again.")
        return False
    
    # Create necessary directories
    print("\n📁 Creating directories...")
    directories = [
        "generated_documents",
        ".pytest_cache",
        "htmlcov"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created/verified: {directory}/")
    
    # Run tests
    print("\n🧪 Running tests...")
    has_tests = Path("test_suite.py").exists()
    if has_tests:
        test_cmd = ["python", "-m", "pytest", "test_suite.py", "-v", "--tb=short"]
        run_command(test_cmd, "Running unit tests")
    else:
        print("⚠ No test file found at test_suite.py")
    
    # Print next steps
    print("\n" + "="*60)
    print("✓ SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Configure environment variables:")
    print("     cp .env.example .env")
    print("     # Edit .env with your API keys")
    print()
    print("  2. Run the application:")
    print("     python main.py --help")
    print()
    print("  3. Example usage:")
    print("     python main.py --input document.pdf --fields '{\"Name\": \"John Doe\"}'")
    print()
    print("  4. List supported document types:")
    print("     python main.py --list-types")
    print()
    print("  5. Run tests:")
    print("     pytest test_suite.py -v")
    print()
    print("  6. Run with verbose logging:")
    print("     python main.py --input document.pdf --fields fields.json --verbose")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
