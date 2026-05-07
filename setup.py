#!/usr/bin/env python
"""
Quick setup script for AI Reception System API
Run this to initialize your development environment
"""

import os
import subprocess
import sys
import platform
from pathlib import Path

def print_header(message: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")

def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status"""
    print(f"▶ {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during {description}:")
        print(e.stderr)
        return False

def main():
    """Main setup function"""
    print_header("AI Reception System API - Setup")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version.split()[0]} detected\n")
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Run this script from the project root directory")
        sys.exit(1)
    
    # Determine OS and create venv
    is_windows = platform.system() == "Windows"
    venv_path = "venv"
    
    if not os.path.exists(venv_path):
        print_header("Step 1: Creating Virtual Environment")
        if not run_command([sys.executable, "-m", "venv", venv_path], "Creating virtual environment"):
            sys.exit(1)
    else:
        print("✓ Virtual environment already exists\n")
    
    # Determine pip command
    if is_windows:
        pip_cmd = [os.path.join(venv_path, "Scripts", "pip")]
        python_cmd = [os.path.join(venv_path, "Scripts", "python")]
    else:
        pip_cmd = [os.path.join(venv_path, "bin", "pip")]
        python_cmd = [os.path.join(venv_path, "bin", "python")]
    
    # Upgrade pip
    print_header("Step 2: Upgrading pip")
    run_command(pip_cmd + ["install", "--upgrade", "pip"], "Upgrading pip")
    
    # Install requirements
    print_header("Step 3: Installing Dependencies")
    if not run_command(pip_cmd + ["install", "-r", "requirements.txt"], "Installing requirements"):
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    print_header("Step 4: Setting up Configuration")
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("▶ Creating .env file from template...")
            with open(".env.example", "r") as f:
                content = f.read()
            with open(".env", "w") as f:
                f.write(content)
            print("✓ .env file created (update with your credentials)\n")
    else:
        print("✓ .env file already exists\n")
    
    # Display next steps
    print_header("Setup Complete!")
    print("""
✓ Virtual environment created
✓ Dependencies installed
✓ Configuration file ready

Next steps:

1. Update your .env file with Supabase credentials:
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_new_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_new_service_role_key

2. Activate the virtual environment:
   """)
    
    if is_windows:
        print("   .\\venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("""
3. Start the API server:
   python main.py

4. Open Swagger documentation:
   http://localhost:8000/docs

5. Deploy to production (optional):
   docker-compose up -d

For more information, see README.md
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
