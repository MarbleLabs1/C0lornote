#!/bin/bash

# C0lorNote Quick Installer
# This script provides a one-click installation method directly from GitHub

set -e

echo "C0lorNote Quick Installer"
echo "========================="
echo ""

# Define repository URL
REPO_URL="https://github.com/MarbleCeo/C0lornote.git"
INSTALL_DIR="$HOME/.local/share/c0lornote"

echo "Checking dependencies..."

# Check for git
if ! command -v git &> /dev/null; then
    echo "Git not found. Please install git first."
    echo "Example: sudo apt install git"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please install Python 3 first."
    echo "Example: sudo apt install python3"
    exit 1
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "Pip not found. Please install pip3 first."
    echo "Example: sudo apt install python3-pip"
    exit 1
fi

# Detect OS
echo "Detecting operating system..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OS="Windows"
else
    OS="Unknown"
fi
echo "Detected OS: $OS"

echo "Installing dependencies..."
# Install PyQt6 and matplotlib
pip3 install PyQt6 matplotlib

echo "Cloning repository..."
mkdir -p "$INSTALL_DIR"
if [ -d "$INSTALL_DIR/.git" ]; then
    # Repository already exists, just pull latest changes
    cd "$INSTALL_DIR"
    git pull
else
    # Clone new repository
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Generate icon
echo "Generating application icon..."
python3 create_icon.py

# Create desktop entry (Linux only)
if [ "$OS" == "Linux" ]; then
    echo "Creating desktop entry..."
    mkdir -p "$HOME/.local/share/applications"
    cat > "$HOME/.local/share/applications/c0lornote.desktop" << DESKTOP
[Desktop Entry]
Name=C0lorNote
Comment=A modern note-taking application with rich text and code editing
Exec=python3 $INSTALL_DIR/modern_colornote.py
Icon=$INSTALL_DIR/assets/c0lornote_icon.png
Terminal=false
Type=Application
Categories=Utility;TextEditor;Development;
StartupNotify=true
Keywords=Notes;Text;Code;Editor;
DESKTOP
    
    # Create launcher script
    mkdir -p "$HOME/.local/bin"
    cat > "$HOME/.local/bin/c0lornote" << LAUNCHER
#!/bin/bash
python3 $INSTALL_DIR/modern_colornote.py
LAUNCHER
    chmod +x "$HOME/.local/bin/c0lornote"
    
    # Update desktop database
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    
    echo ""
    echo "C0lorNote has been installed successfully!"
    echo "You can run it from your application menu or by typing 'c0lornote' in the terminal."
    echo "(Make sure $HOME/.local/bin is in your PATH)"
elif [ "$OS" == "Windows" ]; then
    # Create batch file for Windows
    echo "Creating launcher for Windows..."
    cat > "$INSTALL_DIR/C0lorNote.bat" << BATCH
@echo off
python "$INSTALL_DIR\modern_colornote.py"
BATCH
    
    echo ""
    echo "C0lorNote has been installed successfully!"
    echo "You can run it by executing $INSTALL_DIR/C0lorNote.bat"
elif [ "$OS" == "macOS" ]; then
    # Create launcher script for macOS
    echo "Creating launcher for macOS..."
    mkdir -p "$HOME/.local/bin"
    cat > "$HOME/.local/bin/c0lornote" << LAUNCHER
#!/bin/bash
python3 $INSTALL_DIR/modern_colornote.py
LAUNCHER
    chmod +x "$HOME/.local/bin/c0lornote"
    
    echo ""
    echo "C0lorNote has been installed successfully!"
    echo "You can run it by typing 'c0lornote' in the terminal."
    echo "(Make sure $HOME/.local/bin is in your PATH)"
fi

# Setup auto-update functionality
echo "Setting up auto-update mechanism..."
cat > "$INSTALL_DIR/update.sh" << UPDATE
#!/bin/bash
cd "$INSTALL_DIR"
git pull
UPDATE
chmod +x "$INSTALL_DIR/update.sh"

echo ""
echo "To update C0lorNote to the latest version, run:"
echo "$INSTALL_DIR/update.sh"
echo ""
echo "Enjoy C0lorNote!"
