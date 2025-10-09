#!/bin/bash
# Google API Key Setup Script
# 
# USAGE:
#   Method 1 (Recommended - Automatic activation):
#     source ./setup_api_key.sh
#   
#   Method 2 (Manual activation):
#     ./setup_api_key.sh
#     Then copy and run the export command shown

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    SOURCED=false
else
    SOURCED=true
fi

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Google API Key Setup${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

if [[ "$SOURCED" == true ]]; then
    echo -e "${GREEN}✅ Running in source mode - API key will be active immediately${NC}"
    echo ""
fi

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


echo "1️⃣  Get your FREE Google API Key:"
echo "   👉 https://makersuite.google.com/app/apikey"
echo ""
echo "2️⃣  Enter your API key below:"
echo ""

# Unset any existing API key in current session
unset GOOGLE_API_KEY

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

# Source the shell config to ensure all changes are loaded
source "$SHELL_RC" 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ API Key Configured!${NC}"
echo ""

if [[ "$SOURCED" == true ]]; then
    # Script was sourced - key is active in current session
    echo -e "${GREEN}✅ API key is now active!${NC}"
    echo "   Verify: echo \$GOOGLE_API_KEY"
else
    # Script was executed - provide OS-specific activation command
    echo -e "${YELLOW}🚀 Copy and run this command:${NC}"
    echo ""
    
    # Provide OS-specific command
    if [[ "$OS" == "macos" ]]; then
        if [[ "$SHELL_NAME" == "zsh" ]]; then
            echo -e "${GREEN}source ~/.zshrc${NC}"
        else
            echo -e "${GREEN}source ~/.bash_profile${NC}"
        fi
    else
        # Linux (Ubuntu, Fedora, etc.)
        if [[ "$SHELL_NAME" == "zsh" ]]; then
            echo -e "${GREEN}source ~/.zshrc${NC}"
        else
            echo -e "${GREEN}source ~/.bashrc${NC}"
        fi
    fi
fi

if [[ "$SOURCED" == false ]]; then
    echo ""
    echo -e "${BLUE}💡 Tip: Next time use 'source ./setup_api_key.sh' for automatic activation${NC}"
fi
echo ""
