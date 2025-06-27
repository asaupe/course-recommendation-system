#!/usr/bin/env python3
"""
GitHub Repository Creation Script for Course Recommendation System
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=check
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error output: {e.stderr}")
        return None


def check_git_installed():
    """Check if git is installed."""
    return run_command("git --version", check=False) is not None


def initialize_git_repo():
    """Initialize git repository if not already initialized."""
    if not Path(".git").exists():
        print("📦 Initializing Git repository...")
        run_command("git init")
        print("✅ Git repository initialized")
    else:
        print("📦 Git repository already exists")


def create_initial_commit():
    """Create initial commit with all files."""
    print("📝 Adding files to git...")
    run_command("git add .")
    
    print("💾 Creating initial commit...")
    run_command('git commit -m "Initial commit: Course Recommendation System"')
    print("✅ Initial commit created")


def setup_github_repo():
    """Instructions for setting up GitHub repository."""
    print("\n🚀 GitHub Repository Setup Instructions:")
    print("=" * 50)
    print("\n1. Create a new repository on GitHub:")
    print("   - Go to https://github.com/new")
    print("   - Repository name: course-recommendation-system")
    print("   - Description: A GenAI-powered course recommendation system using prompt engineering and RAG")
    print("   - Make it public or private as preferred")
    print("   - Don't initialize with README, .gitignore, or license (we already have these)")
    
    print("\n2. Connect your local repository to GitHub:")
    print("   Replace 'yourusername' with your actual GitHub username:")
    print("   git remote add origin https://github.com/yourusername/course-recommendation-system.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    
    print("\n3. Set up environment secrets (for CI/CD):")
    print("   - Go to your repository settings > Secrets and variables > Actions")
    print("   - Add these secrets:")
    print("     * OPENAI_API_KEY: Your OpenAI API key")
    print("     * DOCKER_USERNAME: Your Docker Hub username (optional)")
    print("     * DOCKER_PASSWORD: Your Docker Hub password (optional)")
    
    print("\n4. Enable GitHub Pages (optional):")
    print("   - Go to repository settings > Pages")
    print("   - Set source to 'Deploy from a branch'")
    print("   - Choose 'main' branch and '/ (root)' folder")
    
    print("\n📚 Repository Features:")
    print("- ✅ Complete Python project structure")
    print("- ✅ Streamlit web application")
    print("- ✅ RAG implementation with ChromaDB")
    print("- ✅ OpenAI GPT integration")
    print("- ✅ Docker containerization")
    print("- ✅ GitHub Actions CI/CD")
    print("- ✅ Comprehensive documentation")
    print("- ✅ Unit tests and code quality tools")


def main():
    """Main function to set up the repository."""
    print("🎓 Course Recommendation System - GitHub Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: Run this script from the project root directory")
        sys.exit(1)
    
    # Check if git is installed
    if not check_git_installed():
        print("❌ Error: Git is not installed. Please install Git first.")
        sys.exit(1)
    
    # Initialize git repository
    initialize_git_repo()
    
    # Create initial commit
    create_initial_commit()
    
    # Provide GitHub setup instructions
    setup_github_repo()
    
    print("\n🎉 Local repository setup complete!")
    print("Follow the instructions above to push to GitHub.")


if __name__ == "__main__":
    main()
