# Quick Start Guide

Get up and running in **3 simple steps** (5-10 minutes).

---

## Step 1: Install Everything Automatically

```bash
# Clone the repository
git clone https://github.com/nguyennm1024/ai-photonic-physical-verification.git
cd ai-photonic-physical-verification

# Run the installer (automatically detects your OS)
./install.sh
```

**What this does:**
- ✅ Installs Python 3.11
- ✅ Installs Tcl/Tk (GUI libraries)
- ✅ Installs SVG converter (librsvg)
- ✅ Installs all Python packages
- ✅ Configures your system

**Time**: 5-10 minutes (mostly downloading)

---

## Step 2: Get Your FREE Google API Key

1. Go to: **https://makersuite.google.com/app/apikey**
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

Then run:

```bash
./setup_api_key.sh
```

Paste your API key when prompted. Done!

---

## Step 3: Run the Application

```bash
python3 main.py
```

**That's it!** 🎉

---

## First-Time Usage

When the app opens:

1. **Click "Load GDS File"** → Select your GDS layout file
2. **Click "Generate Grid"** → Uses default 50×50 tiles
3. **Click "Process All Tiles"** → AI analyzes the layout
4. **Review results** → Click any tile to see details
5. **Classify manually** → Use the 3 buttons if needed

---

## Troubleshooting

### "Command not found: ./install.sh"

Make it executable:
```bash
chmod +x install.sh setup_api_key.sh
./install.sh
```

### "Tcl/Tk not found" (macOS only)

Restart your terminal:
```bash
# Close terminal, open new one
cd ai-photonic-physical-verification
python3 main.py
```

### "API key not set"

Run the setup script again:
```bash
./setup_api_key.sh
```

Or manually:
```bash
export GOOGLE_API_KEY="your_key_here"
python3 main.py
```

### Still having issues?

Check the detailed guide: [INSTALLATION.md](INSTALLATION.md)

---

## What's Next?

- **Tutorial**: See [README.md](README.md#workflow) for detailed workflow
- **Architecture**: Check [docs/REFACTORING_DESIGN.md](docs/REFACTORING_DESIGN.md)
- **Report issues**: [GitHub Issues](https://github.com/nguyennm1024/ai-photonic-physical-verification/issues)

---

## Summary

```bash
# 1. Install
git clone https://github.com/nguyennm1024/ai-photonic-physical-verification.git
cd ai-photonic-physical-verification
./install.sh

# 2. Setup API key
./setup_api_key.sh

# 3. Run
python3 main.py
```

**Total time: 5-10 minutes** ⚡

---

**Need more help?** Read the full [Installation Guide](INSTALLATION.md)
