#!/bin/bash
# AI Photonic Physical Verification - Automated Installation Script
# Supports: macOS (Homebrew), Ubuntu/Debian, Fedora
# Usage: ./install.sh [--skip-test]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_TEST=false
if [[ "$1" == "--skip-test" ]]; then
    SKIP_TEST=true
fi

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}AI Photonic Physical Verification${NC}"
echo -e "${BLUE}Automated Installation${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Detect OS
echo "🔍 Detecting operating system..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo -e "${GREEN}✅ Detected: macOS${NC}"
elif [[ -f /etc/debian_version ]]; then
    OS="debian"
    echo -e "${GREEN}✅ Detected: Ubuntu/Debian${NC}"
elif [[ -f /etc/fedora-release ]]; then
    OS="fedora"
    echo -e "${GREEN}✅ Detected: Fedora/RHEL${NC}"
else
    echo -e "${RED}❌ Unsupported OS${NC}"
    echo "This script supports: macOS (Homebrew), Ubuntu/Debian, Fedora"
    echo "For Windows, please use WSL2 or follow manual installation in INSTALLATION.md"
    exit 1
fi

echo ""

# Check for required commands
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# macOS Installation
install_macos() {
    echo -e "${BLUE}📦 Installing dependencies for macOS...${NC}"
    echo ""

    # Check for Homebrew
    if ! command_exists brew; then
        echo -e "${YELLOW}⚠️  Homebrew not found. Installing...${NC}"
        echo "This may take a few minutes..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        # Add Homebrew to PATH for Apple Silicon Macs
        if [[ $(uname -m) == 'arm64' ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        echo -e "${GREEN}✅ Homebrew already installed${NC}"
    fi

    # Install Python and dependencies
    echo ""
    echo "📥 Installing Python, Tcl/Tk, and SVG converter..."
    brew install python@3.11 tcl-tk librsvg || {
        echo -e "${YELLOW}⚠️  Some packages may already be installed, continuing...${NC}"
    }

    # Configure Tcl/Tk environment
    echo ""
    echo "Configuring Tcl/Tk environment..."

    SHELL_RC=""
    if [[ -f "$HOME/.zshrc" ]]; then
        SHELL_RC="$HOME/.zshrc"
    elif [[ -f "$HOME/.bash_profile" ]]; then
        SHELL_RC="$HOME/.bash_profile"
    else
        SHELL_RC="$HOME/.zshrc"
        touch "$SHELL_RC"
    fi

    # Add environment variables if not already present
    if ! grep -q "TCL_LIBRARY" "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# Tcl/Tk configuration (added by AI Photonic install script)" >> "$SHELL_RC"
        echo 'export TCL_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tcl9.0:/opt/homebrew/opt/tcl-tk/lib/tcl8.6' >> "$SHELL_RC"
        echo 'export TK_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tk9.0:/opt/homebrew/opt/tcl-tk/lib/tk8.6' >> "$SHELL_RC"
        echo 'export PATH=/opt/homebrew/opt/tcl-tk/bin:$PATH' >> "$SHELL_RC"
        echo -e "${GREEN}✅ Environment variables added to $SHELL_RC${NC}"
    else
        echo "Environment variables already configured"
    fi

    # Export for current session
    export TCL_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tcl9.0:/opt/homebrew/opt/tcl-tk/lib/tcl8.6
    export TK_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tk9.0:/opt/homebrew/opt/tcl-tk/lib/tk8.6
    export PATH=/opt/homebrew/opt/tcl-tk/bin:$PATH
}

# Ubuntu/Debian Installation
install_debian() {
    echo "📦 Installing dependencies for Ubuntu/Debian..."
    echo ""

    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-tk python3-dev librsvg2-bin

    echo -e "${GREEN}✅ System packages installed${NC}"
}

# Fedora Installation
install_fedora() {
    echo "📦 Installing dependencies for Fedora/RHEL..."
    echo ""

    sudo dnf install -y python3 python3-pip python3-tkinter python3-devel librsvg2-tools

    echo -e "${GREEN}✅ System packages installed${NC}"
}

# Install system dependencies based on OS
case $OS in
    macos)
        install_macos
        ;;
    debian)
        install_debian
        ;;
    fedora)
        install_fedora
        ;;
esac

echo ""
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
echo "This may take a few minutes..."

# Try pip3 first, fallback to pip
if command_exists pip3; then
    pip3 install -e . || pip3 install --user -e .
elif command_exists pip; then
    pip install -e . || pip install --user -e .
else
    echo -e "${RED}❌ pip not found. Please install Python pip.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python dependencies installed${NC}"

if [[ "$SKIP_TEST" == false ]]; then
    echo ""
    echo -e "${BLUE}🧪 Testing installation...${NC}"
    echo ""

    # Test Python modules
    echo -n "Testing Python dependencies... "
    if python3 -c "import gdspy, PIL, numpy, matplotlib, google.generativeai" 2>/dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo -e "${YELLOW}Some dependencies may be missing. Try running: pip3 install -e .${NC}"
    fi

    # Test Tcl/Tk (without opening window in headless mode)
    echo -n "Testing Tcl/Tk... "
    if python3 -c "import tkinter" 2>/dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ FAILED${NC}"
        if [[ "$OS" == "macos" ]]; then
            echo -e "${YELLOW}Try restarting your terminal and running: source ~/.zshrc${NC}"
        fi
    fi

    # Test SVG converter
    echo -n "Testing SVG converter... "
    if command_exists rsvg-convert; then
        echo -e "${GREEN}✅ rsvg-convert found${NC}"
    elif command_exists inkscape; then
        echo -e "${GREEN}✅ inkscape found${NC}"
    else
        echo -e "${YELLOW}⚠️  No SVG converter found (will use fallback)${NC}"
        echo -e "${YELLOW}For better performance, install librsvg: brew install librsvg${NC}"
    fi
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Installation Complete! 🎉${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${YELLOW}⚠️  NEXT STEP: Set your Google API Key${NC}"
echo ""
echo -e "${BLUE}1. Get your FREE API key:${NC}"
echo "   https://makersuite.google.com/app/apikey"
echo ""
echo -e "${BLUE}2. Run the setup script:${NC}"
echo "   ./setup_api_key.sh"
echo ""
echo -e "${BLUE}   OR manually set it:${NC}"

if [[ "$OS" == "macos" ]]; then
    echo "   echo 'export GOOGLE_API_KEY=\"your_api_key_here\"' >> $SHELL_RC"
    echo "   source $SHELL_RC"
else
    echo "   export GOOGLE_API_KEY=\"your_api_key_here\""
    echo "   # Add to ~/.bashrc to make it permanent"
fi

echo ""
echo -e "${BLUE}3. Start the application:${NC}"
echo "   python3 main.py"
echo ""

if [[ "$OS" == "macos" ]]; then
    echo -e "${YELLOW}📝 NOTE FOR macOS USERS:${NC}"
    echo "   Restart your terminal or run: source $SHELL_RC"
    echo "   This ensures Tcl/Tk environment is loaded."
    echo ""
fi

echo -e "${GREEN}Need help? Check INSTALLATION.md or README.md${NC}"
echo ""
