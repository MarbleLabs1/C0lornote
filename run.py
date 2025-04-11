#!/usr/bin/env python3
"""
C0lorNote Runner Script

This script simplifies running C0lorNote directly from the source directory.
It handles Python path setup, virtual environment activation, dependency checks,
and launching the application.
"""

import os
import sys
import subprocess
import importlib.util
import venv
import site
from pathlib import Path


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(text):
    """Print a formatted header text"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}=== {text} ==={Colors.END}\n")


def print_success(text):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Print an error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text):
    """Print an info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def print_warning(text):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def is_venv_activated():
    """Check if a virtual environment is currently activated"""
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )


def check_and_activate_venv():
    """Check for a virtual environment and activate it if found"""
    print_header("Checking for virtual environment")
    
    # If already in a virtual environment, just use it
    if is_venv_activated():
        print_success("Already using virtual environment")
        return True
    
    venv_dir = Path("venv")
    if not venv_dir.exists():
        print_warning("No virtual environment found")
        create_response = input("Would you like to create one? (y/n): ").lower()
        if create_response.startswith('y'):
            print_info("Creating virtual environment...")
            try:
                venv.create("venv", with_pip=True)
                print_success("Virtual environment created successfully")
            except Exception as e:
                print_error(f"Failed to create virtual environment: {e}")
                return False
        else:
            print_info("Continuing without virtual environment")
            return True
    
    # Try to activate the virtual environment
    print_info("Activating virtual environment")
    
    # Different activation script based on OS
    if sys.platform == "win32":
        activate_script = venv_dir / "Scripts" / "activate_this.py"
    else:
        activate_script = venv_dir / "bin" / "activate_this.py"
    
    if not activate_script.exists():
        print_error(f"Activation script not found: {activate_script}")
        return False
    
    try:
        with open(activate_script) as f:
            exec(f.read(), {'__file__': str(activate_script)})
        print_success("Virtual environment activated")
        return True
    except Exception as e:
        print_error(f"Failed to activate virtual environment: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    print_header("Checking dependencies")
    
    # Required packages
    required_packages = [
        "ttkthemes",
        "pillow",
        "reportlab",
        "sqlalchemy",
        "pyyaml"
    ]
    
    missing_packages = []
    
    # Check each package
    for package in required_packages:
        if importlib.util.find_spec(package.lower()) is None:
            missing_packages.append(package)
            print_warning(f"Missing package: {package}")
        else:
            print_success(f"Found package: {package}")
    
    # If missing packages, ask to install them
    if missing_packages:
        install_response = input("Install missing packages? (y/n): ").lower()
        if install_response.startswith('y'):
            print_info("Installing missing packages...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
                print_success("Packages installed successfully")
            except subprocess.CalledProcessError as e:
                print_error(f"Failed to install packages: {e}")
                return False
    
    return True


def setup_python_path():
    """Set up the Python path to include our src directory"""
    print_header("Setting up Python path")
    
    # Add the src directory to the Python path
    base_dir = Path(__file__).parent.resolve()
    src_dir = base_dir / "src"
    
    if not src_dir.exists():
        print_error(f"Source directory not found: {src_dir}")
        return False
    
    # Add src directory to path
    sys.path.insert(0, str(base_dir))
    sys.path.insert(0, str(src_dir))
    print_success(f"Added to Python path: {src_dir}")
    
    return True


def launch_application():
    """Launch the C0lorNote application"""
    print_header("Launching C0lorNote")
    
    try:
        from src.main import main
        print_info("Starting application...")
        main()
        return True
    except ImportError as e:
        print_error(f"Failed to import application modules: {e}")
        print_info("Make sure the application code is correctly structured in the src directory.")
        return False
    except Exception as e:
        print_error(f"Error during application startup: {e}")
        return False


def main():
    """Main function to run the application"""
    print(f"\n{Colors.BOLD}C0lorNote Runner{Colors.END}")
    print("This script helps run C0lorNote directly from the source directory.\n")
    
    # Check steps in sequence
    if not setup_python_path():
        sys.exit(1)
    
    if not check_and_activate_venv():
        print_warning("Continuing without virtual environment")
    
    if not check_dependencies():
        print_warning("Some dependencies may be missing")
        continue_response = input("Continue anyway? (y/n): ").lower()
        if not continue_response.startswith('y'):
            sys.exit(1)
    
    if not launch_application():
        print_error("Failed to launch application")
        sys.exit(1)


if __name__ == "__main__":
    main()

