#!/bin/bash
#
# build_deb.sh - Build script for C0lorNote Debian package
#
# This script automates the process of building a Debian package (.deb)
# for the C0lorNote application. It checks for dependencies, verifies
# packaging files, and runs the build process.
#

# Text formatting for output
BOLD="\033[1m"
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
RESET="\033[0m"

# Project information
PROJECT_NAME="C0lorNote"
PACKAGE_NAME="c0lornote"
VERSION="1.0.0"

echo -e "${BOLD}Building ${PROJECT_NAME} ${VERSION} Debian Package${RESET}\n"

# Function to check if a command exists
check_command() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required dependencies
echo -e "${BOLD}Checking dependencies...${RESET}"
MISSING_DEPS=0

# List of required tools
REQUIRED_TOOLS=(
    "dpkg-buildpackage"
    "debhelper"
    "dh_python3"
    "python3"
    "fakeroot"
)

for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! check_command "$tool"; then
        echo -e "  ${RED}✗ $tool not found${RESET}"
        MISSING_DEPS=1
    else
        echo -e "  ${GREEN}✓ $tool found${RESET}"
    fi
done

# If any dependencies are missing, suggest how to install them
if [ $MISSING_DEPS -ne 0 ]; then
    echo -e "\n${RED}Missing dependencies found.${RESET}"
    echo -e "Please install them with:\n"
    echo -e "  sudo apt install dpkg-dev debhelper dh-python python3-all fakeroot\n"
    exit 1
fi

echo -e "${GREEN}All dependencies found.${RESET}\n"

# Check if necessary Debian packaging files exist
echo -e "${BOLD}Checking packaging files...${RESET}"
MISSING_FILES=0

# List of required debian files
REQUIRED_FILES=(
    "debian/control"
    "debian/rules"
    "debian/compat"
    "debian/changelog"
    "debian/c0lornote.desktop"
    "debian/postinst"
    "debian/postrm"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "  ${RED}✗ $file not found${RESET}"
        MISSING_FILES=1
    else
        echo -e "  ${GREEN}✓ $file found${RESET}"
    fi
done

# If any files are missing, exit with error
if [ $MISSING_FILES -ne 0 ]; then
    echo -e "\n${RED}Missing packaging files.${RESET}"
    echo -e "Please create the missing files before building the package.\n"
    exit 1
fi

echo -e "${GREEN}All required files found.${RESET}\n"

# Check for application icon
if [ ! -f "assets/c0lornote.png" ]; then
    echo -e "${YELLOW}Application icon not found.${RESET}"
    echo -e "Generating icon..."
    
    # Run the icon generation script if available
    if [ -f "create_icon.py" ]; then
        python3 create_icon.py
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Icon generated successfully.${RESET}"
        else
            echo -e "${RED}Failed to generate icon.${RESET}"
            exit 1
        fi
    else
        echo -e "${RED}Icon generation script not found.${RESET}"
        exit 1
    fi
fi

# Make scripts executable
chmod +x debian/postinst debian/postrm debian/rules

# Make sure the required directories exist
mkdir -p assets

# Build the package
echo -e "\n${BOLD}Building Debian package...${RESET}"
BUILDDIR=$(pwd)

# Clean any previous build artifacts
echo "Cleaning previous build artifacts..."
rm -rf "${BUILDDIR}/../${PACKAGE_NAME}_${VERSION}"*

# Execute the build command
echo "Running dpkg-buildpackage..."
dpkg-buildpackage -us -uc -b

# Check if the build was successful
if [ $? -eq 0 ]; then
    # Get the parent directory
    PARENT_DIR=$(dirname "$BUILDDIR")
    
    # Check if the .deb file was created
    DEB_FILE="${PARENT_DIR}/${PACKAGE_NAME}_${VERSION}_all.deb"
    
    if [ -f "$DEB_FILE" ]; then
        echo -e "\n${GREEN}${BOLD}Package built successfully!${RESET}"
        echo -e "Package file: ${BOLD}$DEB_FILE${RESET}"
        echo -e "\nYou can install it with:"
        echo -e "  sudo apt install $DEB_FILE\n"
    else
        echo -e "\n${RED}${BOLD}Package file not found.${RESET}"
        echo -e "The build might have failed. Check the logs for errors.\n"
        exit 1
    fi
else
    echo -e "\n${RED}${BOLD}Build failed.${RESET}"
    echo -e "Please check the output above for errors.\n"
    exit 1
fi

exit 0

