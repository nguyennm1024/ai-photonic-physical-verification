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

# Detect shell config file
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
    SHELL_RC="$HOME/.zshrc"
    SHELL_NAME="zsh"
    touch "$SHELL_RC"
fi

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
        # Remove old entry
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' '/export GOOGLE_API_KEY/d' "$SHELL_RC"
        else
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

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ API Key Configured!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "API key added to: $SHELL_RC"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "Run this command to activate for current session:"
echo ""
echo -e "${BLUE}  source $SHELL_RC${NC}"
echo ""
echo "Or restart your terminal."
echo ""
echo "To start the application:"
echo -e "${BLUE}  python3 main.py${NC}"
echo ""
