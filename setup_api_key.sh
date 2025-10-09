#!/bin/bash
# Google API Key Setup Script

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Google API Key Setup${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Detect OS and shell
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ -f /etc/debian_version ]]; then
        OS="ubuntu"
    elif [[ -f /etc/fedora-release ]]; then
        OS="fedora"
    elif [[ -f /etc/redhat-release ]]; then
        OS="rhel"
    else
        OS="linux"
    fi
}

# Detect shell config file based on OS and available shells
detect_shell_config() {
    # Check current shell first
    CURRENT_SHELL=$(basename "$SHELL")
    
    if [[ "$CURRENT_SHELL" == "zsh" ]] && [[ -f "$HOME/.zshrc" ]]; then
        SHELL_RC="$HOME/.zshrc"
        SHELL_NAME="zsh"
    elif [[ "$CURRENT_SHELL" == "bash" ]]; then
        # For bash, prefer .bashrc on Linux, .bash_profile on macOS
        if [[ "$OS" == "macos" ]] && [[ -f "$HOME/.bash_profile" ]]; then
            SHELL_RC="$HOME/.bash_profile"
            SHELL_NAME="bash"
        elif [[ -f "$HOME/.bashrc" ]]; then
            SHELL_RC="$HOME/.bashrc"
            SHELL_NAME="bash"
        elif [[ -f "$HOME/.bash_profile" ]]; then
            SHELL_RC="$HOME/.bash_profile"
            SHELL_NAME="bash"
        else
            # Create appropriate file based on OS
            if [[ "$OS" == "macos" ]]; then
                SHELL_RC="$HOME/.bash_profile"
            else
                SHELL_RC="$HOME/.bashrc"
            fi
            SHELL_NAME="bash"
            touch "$SHELL_RC"
        fi
    else
        # Fallback: try common config files
        if [[ -f "$HOME/.zshrc" ]]; then
            SHELL_RC="$HOME/.zshrc"
            SHELL_NAME="zsh"
        elif [[ -f "$HOME/.bashrc" ]]; then
            SHELL_RC="$HOME/.bashrc"
            SHELL_NAME="bash"
        elif [[ -f "$HOME/.bash_profile" ]]; then
            SHELL_RC="$HOME/.bash_profile"
            SHELL_NAME="bash"
        else
            # Default based on OS
            if [[ "$OS" == "macos" ]]; then
                SHELL_RC="$HOME/.zshrc"
                SHELL_NAME="zsh"
            else
                SHELL_RC="$HOME/.bashrc"
                SHELL_NAME="bash"
            fi
            touch "$SHELL_RC"
        fi
    fi
}

# Run detection
detect_os
detect_shell_config

echo "🔍 Detected: $OS with $SHELL_NAME shell"
echo "📁 Using config file: $SHELL_RC"
echo ""

echo "1️⃣  Get your FREE Google API Key:"
echo "   👉 https://makersuite.google.com/app/apikey"
echo ""
echo "2️⃣  Enter your API key below:"
echo ""

# Read API key
read -p "Enter your Google API Key: " api_key

if [[ -z "$api_key" ]]; then
    echo -e "${YELLOW}⚠️  No API key entered. Exiting.${NC}"
    exit 1
fi

# Check if API key already exists in shell config
if grep -q "GOOGLE_API_KEY" "$SHELL_RC" 2>/dev/null; then
    echo ""
    echo -e "${YELLOW}⚠️  GOOGLE_API_KEY already exists in $SHELL_RC${NC}"
    read -p "Do you want to update it? (y/n): " update_choice

    if [[ "$update_choice" == "y" || "$update_choice" == "Y" ]]; then
        # Remove old entry (handle different sed implementations)
        if [[ "$OS" == "macos" ]]; then
            sed -i '' '/export GOOGLE_API_KEY/d' "$SHELL_RC"
        else
            # Linux (Ubuntu, Fedora, etc.)
            sed -i '/export GOOGLE_API_KEY/d' "$SHELL_RC"
        fi
        echo -e "${GREEN}✅ Removed old API key${NC}"
    else
        echo "Keeping existing configuration."
        exit 0
    fi
fi

# Add API key to shell config
echo "" >> "$SHELL_RC"
echo "# Google API Key for AI Photonic Verification (added by setup script)" >> "$SHELL_RC"
echo "export GOOGLE_API_KEY=\"$api_key\"" >> "$SHELL_RC"

# Automatically activate the API key in current session
export GOOGLE_API_KEY="$api_key"

# Note: The source command below only affects the script's subshell
# The parent shell needs to be updated separately
echo "🔄 Loading updated shell configuration..."
source "$SHELL_RC" 2>/dev/null || true

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ API Key Configured!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "API key added to: $SHELL_RC"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT - To activate in your current shell, run:${NC}"
echo ""
echo -e "${GREEN}  source $SHELL_RC${NC}"
echo ""
echo -e "${BLUE}💡 Or use this one-liner to activate and verify:${NC}"
echo -e "${GREEN}  source $SHELL_RC && echo \"API Key: \$GOOGLE_API_KEY\"${NC}"
echo ""
echo -e "${YELLOW}📝 NOTE:${NC}"
echo "  • API key is saved to $SHELL_RC"
echo "  • Run 'source $SHELL_RC' to activate in current session"
echo "  • New terminal sessions will automatically load it"
echo "  • Verify with: echo \$GOOGLE_API_KEY"
echo ""
if [[ "$OS" == "macos" ]]; then
    echo -e "${BLUE}🍎 macOS:${NC} API key will be available in new Terminal windows"
elif [[ "$OS" == "ubuntu" ]]; then
    echo -e "${BLUE}🐧 Ubuntu:${NC} API key will be available in new terminal sessions"
elif [[ "$OS" == "fedora" ]]; then
    echo -e "${BLUE}🎩 Fedora:${NC} API key will be available in new terminal sessions"
else
    echo -e "${BLUE}🐧 Linux:${NC} API key will be available in new terminal sessions"
fi
echo ""
echo "Ready to start the application:"
if [[ -d ".venv" ]]; then
    echo -e "${BLUE}  source .venv/bin/activate${NC}"
    echo -e "${BLUE}  python main.py${NC}"
else
    echo -e "${BLUE}  python3 main.py${NC}"
fi
echo ""

# Provide a convenient one-liner
echo -e "${YELLOW}💡 Quick start (copy & paste):${NC}"
if [[ -d ".venv" ]]; then
    echo -e "${BLUE}  source .venv/bin/activate && python main.py${NC}"
else
    echo -e "${BLUE}  python3 main.py${NC}"
fi
echo ""
