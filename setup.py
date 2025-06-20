#!/usr/bin/env python3
"""
Setup script for AI Video Generator
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return True if successful."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up AI Video Generator")
    
    # Check if Python 3.8+ is installed
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    # Install requirements
    print("\n📦 Installing Python dependencies...")
    if not run_command("pip3 install -r requirements.txt"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Check Google Cloud authentication
    print("\n🔐 Checking Google Cloud authentication...")
    result = subprocess.run("gcloud auth list --filter=status:ACTIVE --format='value(account)'", 
                           shell=True, capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout.strip():
        print(f"✅ Authenticated as: {result.stdout.strip()}")
    else:
        print("⚠️  No active Google Cloud authentication found")
        print("   Please run: gcloud auth login")
        print("   Or set up a service account key")
    
    # Set environment variables
    print("\n🔧 Environment Setup:")
    print("   Set the following environment variables:")
    print("   export GOOGLE_CLOUD_PROJECT=veo-testing")
    print("   export GOOGLE_CLOUD_LOCATION=us-central1")
    print("   export GOOGLE_GENAI_USE_VERTEXAI=True")
    print("   export GCS_BUCKET=your-bucket-name  # Optional: for storing output videos")
    
    print("\n✅ Setup completed!")
    print("   Run the video generator with: python generate_video.py")

if __name__ == "__main__":
    main() 