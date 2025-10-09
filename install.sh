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
    brew install python@3.11 python-tk@3.11 tcl-tk librsvg || {
        echo -e "${YELLOW}⚠️  Some packages may already be installed, continuing...${NC}"
    }
    
    # Ensure python-tk@3.11 is properly installed (fixes black window issue)
    if ! brew list python-tk@3.11 &>/dev/null; then
        echo "Installing python-tk@3.11 for proper GUI support..."
        brew install python-tk@3.11
    fi

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
        if [[ $(uname -m) == 'arm64' ]]; then
            # Apple Silicon Macs
            echo 'export TCL_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tcl9.0:/opt/homebrew/opt/tcl-tk/lib/tcl8.6' >> "$SHELL_RC"
            echo 'export TK_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tk9.0:/opt/homebrew/opt/tcl-tk/lib/tk8.6' >> "$SHELL_RC"
            echo 'export PATH=/opt/homebrew/opt/tcl-tk/bin:$PATH' >> "$SHELL_RC"
        else
            # Intel Macs
            echo 'export TCL_LIBRARY=/usr/local/opt/tcl-tk/lib/tcl9.0:/usr/local/opt/tcl-tk/lib/tcl8.6' >> "$SHELL_RC"
            echo 'export TK_LIBRARY=/usr/local/opt/tcl-tk/lib/tk9.0:/usr/local/opt/tcl-tk/lib/tk8.6' >> "$SHELL_RC"
            echo 'export PATH=/usr/local/opt/tcl-tk/bin:$PATH' >> "$SHELL_RC"
        fi
        echo -e "${GREEN}✅ Environment variables added to $SHELL_RC${NC}"
    else
        echo "Environment variables already configured"
    fi

    # Export for current session and detect architecture
    if [[ $(uname -m) == 'arm64' ]]; then
        # Apple Silicon Macs
        export TCL_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tcl9.0:/opt/homebrew/opt/tcl-tk/lib/tcl8.6
        export TK_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tk9.0:/opt/homebrew/opt/tcl-tk/lib/tk8.6
        export PATH=/opt/homebrew/opt/tcl-tk/bin:$PATH
    else
        # Intel Macs
        export TCL_LIBRARY=/usr/local/opt/tcl-tk/lib/tcl9.0:/usr/local/opt/tcl-tk/lib/tcl8.6
        export TK_LIBRARY=/usr/local/opt/tcl-tk/lib/tk9.0:/usr/local/opt/tcl-tk/lib/tk8.6
        export PATH=/usr/local/opt/tcl-tk/bin:$PATH
    fi
}

# Ubuntu/Debian Installation
install_debian() {
    echo -e "${BLUE}📦 Installing dependencies for Ubuntu/Debian...${NC}"
    echo ""

    echo "Updating package lists..."
    sudo apt-get update -qq
    
    echo "Installing system packages..."
    sudo apt-get install -y python3 python3-pip python3-tk python3-venv python3-dev build-essential librsvg2-bin

    echo -e "${GREEN}✅ System packages installed${NC}"
}

# Fedora Installation
install_fedora() {
    echo -e "${BLUE}📦 Installing dependencies for Fedora/RHEL...${NC}"
    echo ""

    echo "Installing system packages..."
    sudo dnf install -y python3 python3-pip python3-tkinter python3-devel gcc gcc-c++ librsvg2-tools

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

# Check if pyproject.toml exists
if [[ ! -f "pyproject.toml" ]]; then
    echo -e "${RED}❌ pyproject.toml not found. Please run this script from the project root directory.${NC}"
    exit 1
fi

# Try different installation methods to handle externally-managed environments
echo "Attempting to install Python dependencies..."

# Method 1: Try with --user flag first (safest for most systems)
if command_exists pip3; then
    if pip3 install --user -e . 2>/dev/null; then
        echo -e "${GREEN}✅ Python dependencies installed with --user flag${NC}"
    elif pip3 install -e . 2>/dev/null; then
        echo -e "${GREEN}✅ Python dependencies installed globally${NC}"
    else
        echo -e "${YELLOW}⚠️  Standard pip install failed, trying virtual environment...${NC}"
        # Method 2: Create virtual environment
        # Try to use system Python first (has tkinter support), then Homebrew Python
        PYTHON_CMD="python3"
        if [[ "$OS" == "macos" ]]; then
            # On macOS, prefer Homebrew Python 3.11 with python-tk (avoids black window issue)
            if command_exists /usr/local/bin/python3.11 && /usr/local/bin/python3.11 -c "import tkinter" 2>/dev/null; then
                PYTHON_CMD="/usr/local/bin/python3.11"
                echo -e "${YELLOW}Using Homebrew Python 3.11 with proper Tcl/Tk support${NC}"
            elif command_exists python3.11 && python3.11 -c "import tkinter" 2>/dev/null; then
                PYTHON_CMD="python3.11"
                echo -e "${YELLOW}Using Python 3.11 with tkinter support${NC}"
            elif command_exists /opt/homebrew/bin/python3.11 && /opt/homebrew/bin/python3.11 -c "import tkinter" 2>/dev/null; then
                PYTHON_CMD="/opt/homebrew/bin/python3.11"
                echo -e "${YELLOW}Using Homebrew Python 3.11 (Apple Silicon)${NC}"
            elif command_exists /usr/local/bin/python3 && /usr/local/bin/python3 -c "import tkinter" 2>/dev/null; then
                PYTHON_CMD="/usr/local/bin/python3"
                echo -e "${YELLOW}Using Homebrew Python (Intel)${NC}"
            elif /usr/bin/python3 -c "import tkinter" 2>/dev/null; then
                PYTHON_CMD="/usr/bin/python3"
                echo -e "${YELLOW}⚠️  Using system Python (may have GUI issues, consider reinstalling)${NC}"
            else
                PYTHON_CMD="python3"
                echo -e "${YELLOW}Using default Python 3${NC}"
            fi
        else
            # On Linux, prefer system Python (has tkinter support)
            if python3 -c "import tkinter" 2>/dev/null; then
                PYTHON_CMD="python3"
                echo -e "${YELLOW}Using system Python for tkinter support${NC}"
            elif command_exists python3.11 && python3.11 -c "import tkinter" 2>/dev/null; then
                PYTHON_CMD="python3.11"
                echo -e "${YELLOW}Using Python 3.11 for tkinter support${NC}"
            elif command_exists python3.10 && python3.10 -c "import tkinter" 2>/dev/null; then
                PYTHON_CMD="python3.10"
                echo -e "${YELLOW}Using Python 3.10 for tkinter support${NC}"
            else
                PYTHON_CMD="python3"
                echo -e "${YELLOW}Using default Python 3${NC}"
            fi
        fi
        
        if $PYTHON_CMD -m venv .venv 2>/dev/null; then
            source .venv/bin/activate
            
            # Set Tcl/Tk environment variables in virtual environment
            if [[ "$OS" == "macos" ]]; then
                if [[ $(uname -m) == 'arm64' ]]; then
                    export TCL_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tcl9.0:/opt/homebrew/opt/tcl-tk/lib/tcl8.6
                    export TK_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tk9.0:/opt/homebrew/opt/tcl-tk/lib/tk8.6
                    export PATH=/opt/homebrew/opt/tcl-tk/bin:$PATH
                else
                    export TCL_LIBRARY=/usr/local/opt/tcl-tk/lib/tcl9.0:/usr/local/opt/tcl-tk/lib/tcl8.6
                    export TK_LIBRARY=/usr/local/opt/tcl-tk/lib/tk9.0:/usr/local/opt/tcl-tk/lib/tk8.6
                    export PATH=/usr/local/opt/tcl-tk/bin:$PATH
                fi
            fi
            
            echo "Installing Python packages in virtual environment..."
            # Install build dependencies first
            pip install --upgrade setuptools wheel
            # Try different installation methods
            if pip install -e .; then
                echo -e "${GREEN}✅ Python dependencies installed in virtual environment${NC}"
            elif pip install .; then
                echo -e "${GREEN}✅ Python dependencies installed in virtual environment (non-editable)${NC}"
            elif pip install gdspy>=1.6.13 Pillow>=10.0.0 numpy>=1.20.0 matplotlib>=3.5.0 google-generativeai>=0.8.0 cairosvg>=2.7.0 lxml>=4.9.0; then
                echo -e "${GREEN}✅ Python dependencies installed in virtual environment (direct)${NC}"
            else
                echo -e "${RED}❌ Failed to install Python packages in virtual environment${NC}"
                echo -e "${YELLOW}Virtual environment was created but package installation failed.${NC}"
                exit 1
            fi
            
            if [[ -d ".venv" ]]; then
                echo -e "${YELLOW}📝 Note: Virtual environment created at ./.venv${NC}"
                echo -e "${YELLOW}   To activate: source .venv/bin/activate${NC}"
                echo -e "${YELLOW}   To run the app: source .venv/bin/activate && python main.py${NC}"
                
                # Create activation script with Tcl/Tk environment variables
                if [[ "$OS" == "macos" ]]; then
                    cat > .venv/bin/activate_tcl_tk << EOF
#!/bin/bash
# Activate virtual environment with Tcl/Tk support
source .venv/bin/activate

# Set Tcl/Tk environment variables
if [[ \$(uname -m) == 'arm64' ]]; then
    export TCL_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tcl9.0:/opt/homebrew/opt/tcl-tk/lib/tcl8.6
    export TK_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tk9.0:/opt/homebrew/opt/tcl-tk/lib/tk8.6
    export PATH=/opt/homebrew/opt/tcl-tk/bin:\$PATH
else
    export TCL_LIBRARY=/usr/local/opt/tcl-tk/lib/tcl9.0:/usr/local/opt/tcl-tk/lib/tcl8.6
    export TK_LIBRARY=/usr/local/opt/tcl-tk/lib/tk9.0:/usr/local/opt/tcl-tk/lib/tk8.6
    export PATH=/usr/local/opt/tcl-tk/bin:\$PATH
fi

echo "Virtual environment activated with Tcl/Tk support"
EOF
                    chmod +x .venv/bin/activate_tcl_tk
                    echo -e "${YELLOW}   For Tcl/Tk support: source .venv/bin/activate_tcl_tk${NC}"
                fi
            else
                echo -e "${RED}❌ Failed to install Python packages in virtual environment${NC}"
                echo -e "${YELLOW}Virtual environment was created but package installation failed.${NC}"
                exit 1
            fi
        else
            echo -e "${RED}❌ Failed to create virtual environment${NC}"
            echo -e "${YELLOW}Try installing python3-venv and build tools: ${NC}"
            if [[ "$OS" == "macos" ]]; then
                echo -e "${YELLOW}  brew install python@3.11${NC}"
            elif [[ "$OS" == "debian" ]]; then
                echo -e "${YELLOW}  sudo apt-get install python3-venv python3-dev build-essential${NC}"
            elif [[ "$OS" == "fedora" ]]; then
                echo -e "${YELLOW}  sudo dnf install python3-devel gcc gcc-c++${NC}"
            fi
            exit 1
        fi
    fi
elif command_exists pip; then
    if pip install --user -e . 2>/dev/null; then
        echo -e "${GREEN}✅ Python dependencies installed with --user flag${NC}"
    elif pip install -e . 2>/dev/null; then
        echo -e "${GREEN}✅ Python dependencies installed globally${NC}"
    else
        echo -e "${RED}❌ pip installation failed${NC}"
        exit 1
    fi
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
    
    # Check if we're in a virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        PYTHON_CMD="python"
    else
        PYTHON_CMD="python3"
    fi
    
    if $PYTHON_CMD -c "import gdspy, PIL, numpy, matplotlib, google.generativeai" 2>/dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo -e "${YELLOW}Some dependencies may be missing.${NC}"
        if [[ -n "$VIRTUAL_ENV" ]]; then
            echo -e "${YELLOW}Try running: pip install -e .${NC}"
        else
            echo -e "${YELLOW}Try running: pip3 install --user -e .${NC}"
        fi
    fi

    # Test Tcl/Tk (without opening window in headless mode)
    echo -n "Testing Tcl/Tk... "
    if $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ FAILED${NC}"
        if [[ "$OS" == "macos" ]]; then
            echo -e "${YELLOW}Try restarting your terminal and running: source ~/.zshrc${NC}"
            echo -e "${YELLOW}Or run: source $SHELL_RC${NC}"
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
elif [[ "$OS" == "debian" ]] || [[ "$OS" == "fedora" ]]; then
    LINUX_SHELL_RC="$HOME/.bashrc"
    if [[ -f "$HOME/.zshrc" ]]; then
        LINUX_SHELL_RC="$HOME/.zshrc"
    fi
    echo "   echo 'export GOOGLE_API_KEY=\"your_api_key_here\"' >> $LINUX_SHELL_RC"
    echo "   source $LINUX_SHELL_RC"
    echo "   # Or set it temporarily for current session:"
    echo "   export GOOGLE_API_KEY=\"your_api_key_here\""
else
    echo "   export GOOGLE_API_KEY=\"your_api_key_here\""
    echo "   # Add to ~/.bashrc to make it permanent"
fi

echo ""
echo -e "${BLUE}3. Start the application:${NC}"
if [[ -d ".venv" ]]; then
    if [[ "$OS" == "macos" ]] && [[ -f ".venv/bin/activate_tcl_tk" ]]; then
        echo "   source .venv/bin/activate_tcl_tk && python main.py"
        echo "   # Or activate the virtual environment first:"
        echo "   source .venv/bin/activate_tcl_tk"
        echo "   python main.py"
    else
        echo "   source .venv/bin/activate && python main.py"
        echo "   # Or activate the virtual environment first:"
        echo "   source .venv/bin/activate"
        echo "   python main.py"
    fi
else
    echo "   python3 main.py"
fi
echo ""

if [[ "$OS" == "macos" ]]; then
    echo -e "${YELLOW}📝 NOTE FOR macOS USERS:${NC}"
    echo "   Restart your terminal or run: source $SHELL_RC"
    echo "   This ensures Tcl/Tk environment is loaded."
    echo ""
    
    # Check if using old system Python which may cause black window issue
    if [[ -d ".venv" ]]; then
        VENV_PYTHON_VERSION=$(.venv/bin/python --version 2>&1)
        if [[ "$VENV_PYTHON_VERSION" == *"3.9.6"* ]]; then
            echo -e "${YELLOW}⚠️  WARNING: Black Window Issue Detected${NC}"
            echo "   Your virtual environment is using system Python 3.9.6 with old Tcl/Tk 8.5"
            echo "   This may cause black/blank windows in the GUI."
            echo ""
            echo "   To fix this, run:"
            echo -e "${BLUE}   rm -rf .venv && ./install.sh${NC}"
            echo ""
            echo "   This will recreate the virtual environment with Python 3.11"
            echo "   which has proper Tcl/Tk support."
            echo ""
        fi
    fi
elif [[ "$OS" == "debian" ]] || [[ "$OS" == "fedora" ]]; then
    echo -e "${YELLOW}📝 NOTE FOR LINUX USERS:${NC}"
    if [[ -d ".venv" ]]; then
        echo "   Virtual environment created. Always activate it before running the app."
        echo "   To activate: source .venv/bin/activate"
    fi
    echo "   Make sure to set your GOOGLE_API_KEY as shown above."
    echo ""
fi

echo -e "${GREEN}Need help? Check INSTALLATION.md or README.md${NC}"
echo ""
