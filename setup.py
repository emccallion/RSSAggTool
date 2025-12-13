#!/usr/bin/env python3
"""
Setup script for the news aggregation system.
"""

import subprocess
import sys
from pathlib import Path

def install_dependencies():
    """Install required Python packages."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def setup_nltk():
    """Download required NLTK data."""
    print("Setting up NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        print("NLTK data downloaded successfully!")
        return True
    except Exception as e:
        print(f"Error setting up NLTK: {e}")
        return False

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        import feedparser
        import requests
        import yaml
        import sqlite3
        from bs4 import BeautifulSoup
        import nltk
        from textblob import TextBlob
        print("All imports successful!")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False

def main():
    """Main setup function."""
    print("=== News Aggregation System Setup ===")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    import os
    os.chdir(project_dir)
    
    success = True
    
    # Install dependencies
    if not install_dependencies():
        success = False
    
    # Setup NLTK
    if success and not setup_nltk():
        success = False
    
    # Test imports
    if success and not test_imports():
        success = False
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: python src/main.py --dry-run  (to test feed parsing)")
        print("2. Run: python src/main.py  (to start collecting data)")
        print("3. Run: python src/query.py --stats  (to view statistics)")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)