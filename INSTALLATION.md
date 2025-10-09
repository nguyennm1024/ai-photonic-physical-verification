# Installation Guide

Complete installation guide for AI Photonic Physical Verification.

**Version**: 2.0.0  
**Last Updated**: October 7, 2025

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Verification](#verification)
4. [Troubleshooting](#troubleshooting)
5. [Platform-Specific Notes](#platform-specific-notes)

---

## Prerequisites

### ⚠️ Critical Requirements

Before installing, ensure you have ALL of the following:

#### 1. Python 3.9 or Higher

```bash
# Check your Python version
python --version  # Should show 3.9.0 or higher
```

**If Python is too old or not installed:**
- **macOS**: `brew install python@3.11`
- **Ubuntu/Debian**: `sudo apt-get install python3.11`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

#### 2. tkinter & Tcl/Tk (GUI Library)

**Tkinter is Python's standard GUI library, requires Tcl/Tk runtime.**

**Test if Tcl/Tk is available:**

```bash
# Test tkinter/Tcl/Tk availability
python3 -m tkinter
# Should open a small Tk window if working correctly
```

**If the test fails, install Tcl/Tk for your platform:**

##### macOS with Homebrew

```bash
# 1. Install Tcl/Tk
brew install tcl-tk

# 2. Set environment variables (add to ~/.zshrc or ~/.bash_profile)
echo 'export TCL_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tcl9.0:/opt/homebrew/opt/tcl-tk/lib/tcl8.6' >> ~/.zshrc
echo 'export TK_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tk9.0:/opt/homebrew/opt/tcl-tk/lib/tk8.6' >> ~/.zshrc
echo 'export PATH=/opt/homebrew/opt/tcl-tk/bin:$PATH' >> ~/.zshrc

# 3. Reload shell configuration
source ~/.zshrc

# 4. If using uv-managed Python, reinstall Python
uv python uninstall
uv python install

# 5. Verify
python3 -m tkinter
```

##### Ubuntu/Debian Linux

```bash
sudo apt-get update
sudo apt-get install python3-tk
```

##### Fedora/RHEL Linux

```bash
sudo dnf install python3-tkinter
```

##### Windows

Usually pre-installed with Python from python.org. If missing:
1. Reinstall Python from [python.org](https://www.python.org/downloads/)
2. During installation, ensure "tcl/tk and IDLE" is checked

#### 3. Google Gemini API Key (REQUIRED)

**Get your FREE API key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Create a new API key
4. Save it securely - you'll need it in Step 3

**⚠️ Without this key, AI analysis will not work!**

#### 4. SVG to PNG Converter (CRITICAL)

**At least ONE of the following is REQUIRED for tile image generation:**

##### Option A: rsvg-convert (✅ Recommended - Fastest)

```bash
# macOS
brew install librsvg

# Ubuntu/Debian
sudo apt-get install librsvg2-bin

# Fedora
sudo dnf install librsvg2-tools

# Verify installation
rsvg-convert --version
```

##### Option B: Inkscape (Alternative)

```bash
# macOS
brew install inkscape

# Ubuntu/Debian
sudo apt-get install inkscape

# Fedora
sudo dnf install inkscape

# Verify installation
inkscape --version
```

##### Option C: Google Chrome/Chromium (Fallback)

If Chrome or Chromium browser is installed, it will be used as a fallback converter.

```bash
# Check if available
which google-chrome chromium
```

**⚠️ WITHOUT ANY CONVERTER:**
- Virtual tiles will work (metadata only)
- Tile PNG images will NOT be generated
- **AI analysis will FAIL** (requires actual images)

---

## Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/nguyennm1024/ai-photonic-physical-verification.git
cd ai-photonic-physical-verification
```

**Verify:**
```bash
pwd  # Should show: .../ai-photonic-physical-verification
ls   # Should show: core/, ui/, utils/, README.md, etc.
```

---

### Step 2: Install Python Dependencies

**Option A: Using pip with pyproject.toml (Recommended)**

```bash
pip install -e .
```

**Option B: Using requirements.txt (if available)**

```bash
pip install -r requirements.txt
```

**What gets installed:**
- `gdspy>=1.6.13` - GDS file processing
- `Pillow>=10.0.0` - Image processing
- `numpy>=1.20.0` - Numerical operations
- `matplotlib>=3.5.0` - Visualization and plotting
- `google-generativeai>=0.8.0` - Gemini AI models

**Verify installation:**
```bash
python -c "import gdspy, PIL, numpy, matplotlib, google.generativeai; print('✅ All dependencies OK')"
```

---

### Step 3: Configure Google API Key

#### macOS / Linux

**For current session only:**
```bash
export GOOGLE_API_KEY='your_api_key_here'
```

**Make it permanent (Recommended):**
```bash
# For bash (add to ~/.bashrc)
echo 'export GOOGLE_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc

# For zsh (add to ~/.zshrc) - macOS default
echo 'export GOOGLE_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

**Verify:**
```bash
echo $GOOGLE_API_KEY  # Should show your API key
```

#### Windows (PowerShell)

**For current session only:**
```powershell
$env:GOOGLE_API_KEY='your_api_key_here'
```

**Make it permanent:**
```powershell
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'your_api_key_here', 'User')
```

**Verify:**
```powershell
echo $env:GOOGLE_API_KEY  # Should show your API key
```

---

### Step 4: Install SVG Converter (CRITICAL)

Choose and install at least ONE converter:

#### Recommended: rsvg-convert

```bash
# macOS
brew install librsvg

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install librsvg2-bin

# Fedora
sudo dnf install librsvg2-tools

# Verify
which rsvg-convert
rsvg-convert --version
```

#### Alternative: Inkscape

```bash
# macOS
brew install inkscape

# Ubuntu/Debian
sudo apt-get install inkscape

# Fedora
sudo dnf install inkscape

# Verify
which inkscape
inkscape --version
```

---

## Verification

### Quick Verification Script

Run this to check all requirements at once:

```bash
#!/bin/bash

echo "=== Installation Verification ==="
echo ""

# Python version
echo -n "Python version: "
python --version

# tkinter/Tcl/Tk
python -c "import tkinter; tkinter.Tk().destroy(); print('✅ tkinter/Tcl/Tk OK')" 2>/dev/null || echo "❌ tkinter/Tcl/Tk MISSING"

# Core dependencies
python -c "import gdspy; print('✅ gdspy OK')" 2>/dev/null || echo "❌ gdspy MISSING"
python -c "import PIL; print('✅ Pillow OK')" 2>/dev/null || echo "❌ Pillow MISSING"
python -c "import numpy; print('✅ numpy OK')" 2>/dev/null || echo "❌ numpy MISSING"
python -c "import matplotlib; print('✅ matplotlib OK')" 2>/dev/null || echo "❌ matplotlib MISSING"
python -c "import google.generativeai; print('✅ Gemini OK')" 2>/dev/null || echo "❌ Gemini MISSING"

# API key
if [ -n "$GOOGLE_API_KEY" ]; then
    echo "✅ GOOGLE_API_KEY set"
else
    echo "❌ GOOGLE_API_KEY NOT SET"
fi

# SVG converters (need at least one)
echo ""
echo "SVG Converters (need at least one):"
which rsvg-convert >/dev/null 2>&1 && echo "  ✅ rsvg-convert found" || echo "  ❌ rsvg-convert not found"
which inkscape >/dev/null 2>&1 && echo "  ✅ inkscape found" || echo "  ❌ inkscape not found"
which google-chrome chromium >/dev/null 2>&1 && echo "  ✅ Chrome/Chromium found" || echo "  ❌ Chrome not found"

echo ""
echo "=== End Verification ==="
```

**Save as `check_install.sh` and run:**
```bash
chmod +x check_install.sh
./check_install.sh
```

### Run Test Suite

**Test core modules (13 tests):**
```bash
python test_modules.py
```

**Expected output:**
```
============================================================
Testing Refactored Modules
============================================================
✅ Utility modules imported successfully
✅ App state modules imported successfully
✅ File manager modules imported successfully
✅ Tile system modules imported successfully
✅ ROI manager modules imported successfully
✅ AI analyzer modules imported successfully
...
============================================================
✅ ALL TESTS PASSED!
============================================================
```

**Test with real GDS file (6 integration tests):**
```bash
python test_real_gds.py
```

**Expected output:**
```
✅ GDS Loading: PASSED
✅ SVG Conversion: PASSED
✅ SVG Parsing: PASSED
✅ Virtual Tiles: PASSED
✅ Tile Generation: PASSED
✅ State Management: PASSED
```

---

## Troubleshooting

### Installation Issues

#### ❌ "ModuleNotFoundError: No module named '_tkinter'" or "Tcl/Tk runtime not available"

**Problem**: Tcl/Tk libraries not installed or not configured
**Solution**:

**macOS with Homebrew:**
```bash
# 1. Install Tcl/Tk
brew install tcl-tk

# 2. Set environment variables (add to ~/.zshrc or ~/.bash_profile)
export TCL_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tcl9.0:/opt/homebrew/opt/tcl-tk/lib/tcl8.6
export TK_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tk9.0:/opt/homebrew/opt/tcl-tk/lib/tk8.6
export PATH=/opt/homebrew/opt/tcl-tk/bin:$PATH

# 3. Reload shell
source ~/.zshrc

# 4. If using uv-managed Python, reinstall
uv python uninstall && uv python install

# 5. Test
python3 -m tkinter
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

**Fedora/RHEL:**
```bash
sudo dnf install python3-tkinter
```

**Windows:**
- Reinstall Python from python.org
- During installation, check "tcl/tk and IDLE"

---

#### ❌ "GOOGLE_API_KEY environment variable not set"

**Problem**: API key not configured  
**Solution**:
```bash
# Get API key from: https://makersuite.google.com/app/apikey

# Set for current session
export GOOGLE_API_KEY='your_actual_api_key'

# Make permanent (add to ~/.zshrc or ~/.bashrc)
echo 'export GOOGLE_API_KEY="your_key"' >> ~/.zshrc
source ~/.zshrc

# Verify
echo $GOOGLE_API_KEY
```

---

#### ❌ "gdspy not available" or ImportError

**Problem**: Missing GDS processing library  
**Solution**:
```bash
pip install gdspy>=1.6.13

# Verify installation
python -c "import gdspy; print('gdspy version:', gdspy.__version__)"
```

---

#### ⚠️ "Tile generation failed (may need rsvg-convert/inkscape)"

**Problem**: No SVG to PNG converter installed  
**Impact**: **AI analysis will not work** (needs tile images)  
**Solution**:

```bash
# Install rsvg-convert (RECOMMENDED - fastest)
brew install librsvg  # macOS
sudo apt-get install librsvg2-bin  # Ubuntu

# OR install inkscape
brew install inkscape  # macOS
sudo apt-get install inkscape  # Ubuntu

# Verify installation
which rsvg-convert  # Should show path
rsvg-convert --version
```

**Fallback Order:**
1. `rsvg-convert` (fastest)
2. `inkscape` (good quality)
3. Chrome/Chromium (slower but works)
4. Enhanced placeholder (fallback - **AI won't work**)

---

#### ❌ "google.generativeai not available"

**Problem**: Gemini library not installed  
**Solution**:
```bash
pip install google-generativeai>=0.8.0

# Verify installation
python -c "import google.generativeai as genai; print('Gemini version:', genai.__version__)"
```

---

#### ❌ "pip: command not found"

**Problem**: pip not in PATH  
**Solution**:
```bash
# Use python -m pip instead
python -m pip install -e .

# Or install pip
python -m ensurepip --upgrade
```

---

#### ❌ Permission denied errors

**Problem**: Need admin privileges  
**Solution**:
```bash
# Option 1: Use --user flag
pip install --user -e .

# Option 2: Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
pip install -e .
```

---

### Runtime Issues

#### ⚠️ SVG conversion fails or shows placeholder

**Symptoms**: Tiles show placeholder text instead of layout  
**Cause**: Missing SVG converter (rsvg-convert/inkscape/Chrome)  
**Solution**:
1. Install at least one converter (see Step 4 above)
2. Restart the application
3. The app will automatically detect available converters

---

#### ⚠️ Memory issues with large grids

**Symptoms**: Application becomes slow or crashes  
**Solutions**:
- Reduce grid size (start with 5×5 or 10×10 instead of 20×20)
- Use lower tile resolution (512px instead of 2048px)
- Enable virtual tiles (on-demand generation)
- Reduce CPU cores to leave memory for system
- Close other memory-intensive applications

---

#### ⚠️ "Gemini API quota exceeded"

**Symptoms**: Analysis stops with quota error  
**Solutions**:
- Wait for quota reset (usually 1 minute)
- Use a different API key
- Check your quota at [Google AI Studio](https://makersuite.google.com/)

---

## Platform-Specific Notes

### macOS

**Homebrew Required:**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Recommended Installation:**
```bash
# Install Python and required system packages
brew install python@3.11 tcl-tk librsvg

# Configure Tcl/Tk environment variables (add to ~/.zshrc)
echo 'export TCL_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tcl9.0:/opt/homebrew/opt/tcl-tk/lib/tcl8.6' >> ~/.zshrc
echo 'export TK_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tk9.0:/opt/homebrew/opt/tcl-tk/lib/tk8.6' >> ~/.zshrc
echo 'export PATH=/opt/homebrew/opt/tcl-tk/bin:$PATH' >> ~/.zshrc
source ~/.zshrc

# Install Python dependencies
pip install -e .

# Set API key
export GOOGLE_API_KEY='your_key'

# Test Tcl/Tk
python3 -m tkinter
```

**Common Issues:**
- Python from Xcode might be outdated → Use Homebrew Python
- Multiple Python versions → Use `python3` explicitly
- Tcl/Tk not found → Set environment variables as shown above
- Using uv-managed Python → Run `uv python uninstall && uv python install` after installing tcl-tk

---

### Ubuntu/Debian Linux

**System Packages First:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-tk python3-dev librsvg2-bin

# Test Tcl/Tk installation
python3 -m tkinter
```

**Then Python Packages:**
```bash
pip3 install -e .
```

**Common Issues:**
- Need `sudo` for system packages but NOT for pip
- Use `python3` and `pip3` explicitly
- May need `python3-venv` for virtual environments

---

### Fedora Linux

**System Packages:**
```bash
sudo dnf install python3 python3-pip python3-tkinter python3-devel librsvg2-tools

# Test Tcl/Tk installation
python3 -m tkinter

# Install Python dependencies
pip3 install -e .
```

---

### Windows

**Install Python from python.org (includes pip and tkinter)**

**Recommended: Use PowerShell as Administrator**

```powershell
# Install dependencies
pip install -e .

# Set API key permanently
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'your_key', 'User')
```

**SVG Converter Options:**
1. Install Inkscape from [inkscape.org](https://inkscape.org/)
2. Use Chrome (usually already installed)

**Common Issues:**
- Need to restart PowerShell after setting environment variables
- Path issues → Use `python` not `py`
- Microsoft Store Python → Use python.org version instead

---

## Quick Start After Installation

Once everything is installed and verified:

```bash
# Run the application
python layout_verification_app.py
```

**First-Time Workflow:**
1. Click "Load GDS File" and select your layout
2. Configure grid: 5×5 for testing, 10×10 for normal use
3. Click "Split to Tiles" to generate virtual tiles
4. Click "Start AI Analysis" to begin automated detection
5. Review and classify results

---

## Additional Resources

- **Project Overview**: [README.md](README.md)
- **Architecture & Design**: [docs/REFACTORING_DESIGN.md](docs/REFACTORING_DESIGN.md) (for developers)

---

## Getting Help

If you encounter issues not covered here:

1. **Check test results**: `python test_modules.py`
2. **Review error messages**: Often indicate missing dependency
3. **Verify all prerequisites**: Run verification script above
4. **Check GitHub Issues**: [Report bugs](https://github.com/nguyennm1024/ai-photonic-physical-verification/issues)

---

## Summary Checklist

Before running the application, verify:

- [ ] Python 3.9+ installed (`python --version`)
- [ ] Tcl/Tk working (`python3 -m tkinter` - should open window)
- [ ] All pip dependencies installed (`pip install -e .`)
- [ ] GOOGLE_API_KEY set (`echo $GOOGLE_API_KEY`)
- [ ] At least one SVG converter installed (`which rsvg-convert`)
- [ ] Test suite passes (`python test_modules.py`)

**If all checked, you're ready to run the application!**

---

**Installation Complete! 🎉**

Proceed to [README.md](README.md) for usage instructions.

