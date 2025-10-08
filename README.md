# AI Photonic Physical Verification

A comprehensive GUI application for automated photonic integrated circuit (PIC) layout verification using AI-powered discontinuity detection.

> **🎉 Recently Refactored**: The application has been refactored into a clean, modular architecture. See [REFACTORING_COMPLETE.md](REFACTORING_COMPLETE.md) for details.

## 🚀 Features

### Core Functionality
- **GDS File Processing**: Load and analyze GDS layout files
- **SVG Conversion**: Automatic conversion from GDS to SVG format
- **Tile-Based Analysis**: Split large layouts into manageable tiles for detailed inspection
- **AI-Powered Detection**: Uses Google's Gemini models for intelligent discontinuity detection
- **Interactive Classification**: Manual review and classification of detected issues

### Advanced Capabilities
- **Virtual Tile System**: On-demand tile generation with intelligent caching
- **Region of Interest (ROI)**: Focus analysis on specific layout areas
- **Multi-threaded Processing**: Configurable CPU usage for optimal performance
- **Real-time Preview**: Interactive navigation with coordinate transformation
- **Comprehensive Export**: JSON export with complete analysis metadata

### User Interface
- **Dual-Panel Layout**: Controls on left, original layout visualization on right
- **Interactive Canvas**: Click navigation, ROI drawing, and visual feedback
- **Progress Tracking**: Real-time analysis progress with pause/resume capability
- **Tooltip System**: Contextual help and guidance throughout the interface

## 📋 Requirements

### System Requirements
- **Python 3.8+** (Recommended: Python 3.9 or higher)
- **Operating System**: macOS, Linux, or Windows
- **Memory**: 4GB RAM minimum, 8GB+ recommended for large layouts
- **Storage**: 1GB free space for temporary files and caching

### API Requirements
- **Google API Key**: Required for AI analysis functionality
  - Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🛠 Installation

### Quick Installation

```bash
# 1. Clone repository
git clone https://github.com/nguyennm1024/ai-photonic-physical-verification.git
cd ai-photonic-physical-verification

# 2. Install dependencies
pip install -e .

# 3. Set API key
export GOOGLE_API_KEY='your_api_key_here'

# 4. Install SVG converter (REQUIRED)
brew install librsvg  # macOS
# OR
sudo apt-get install librsvg2-bin  # Ubuntu/Debian

# 5. Run tests
python test_modules.py
```

### ⚠️ Critical Requirements

Before installation, you **MUST** have:

1. ✅ **Python 3.9+** with tkinter
2. ✅ **Google Gemini API Key** ([Get it here](https://makersuite.google.com/app/apikey))
3. ✅ **SVG Converter** (rsvg-convert or inkscape) - **Required for AI analysis**

### 📖 Complete Installation Guide

**For detailed installation instructions, troubleshooting, and platform-specific notes:**

👉 **See [INSTALLATION.md](INSTALLATION.md)**

The installation guide includes:
- Detailed prerequisites checklist
- Step-by-step installation for macOS/Linux/Windows
- Verification commands
- Comprehensive troubleshooting
- Platform-specific notes

## 🚀 Quick Start

### Basic Usage
```bash
python main.py
```

> **Note**: The old `layout_verification_app.py` has been renamed to `layout_verification_app_OLD.py`. Use `main.py` for the refactored version.

### Workflow
1. **Load GDS File**: Click "Load GDS File" and select your layout file
2. **Configure Grid**: Set tile grid size, overlap, and resolution
3. **Split to Tiles**: Generate tiles for analysis
4. **Start AI Analysis**: Begin automated discontinuity detection
5. **Review Results**: Manually classify detected issues
6. **Export Results**: Save analysis results to JSON format

### Advanced Features
- **ROI Analysis**: Draw regions of interest for focused analysis
- **Virtual Tiles**: Use on-demand generation for memory efficiency
- **Pause/Resume**: Control analysis flow for large datasets
- **Interactive Navigation**: Click on original layout to jump to specific tiles

## 📖 Documentation

### Application Architecture (v2.0 - Refactored)

The application has been refactored into a **modular architecture** with clean separation of concerns:

**Core Business Logic** (`core/` directory):
- **`core/file_manager/`** - GDS loading and SVG conversion (3 modules)
- **`core/tile_system/`** - Tile generation, caching, splitting (3 modules)
- **`core/ai_analyzer/`** - Gemini integration with preserved prompts (4 modules)
- **`core/roi_manager/`** - Region of interest management (2 modules)
- **`core/app_state/`** - Centralized state management (2 modules)

**Utilities** (`utils/` directory):
- Coordinate transformations (SVG ↔ pixel)
- Image processing helpers
- Thread-safe communication

**User Interface** (`ui/` directory - work in progress):
- Reusable components
- Event handlers
- Styling and themes

**Key Improvements:**
- ✅ **Testable**: Core logic tested independently (13 unit tests, 6 integration tests)
- ✅ **Maintainable**: Files 50-200 lines each (vs. 2,826 line monolith)
- ✅ **Separated**: Business logic completely separate from UI
- ✅ **Documented**: Comprehensive API documentation
- ✅ **Validated**: Tested with real 4.5MB GDS files

### Configuration Options
- **Grid Size**: Configurable rows × columns (default: 10×10)
- **Tile Overlap**: Percentage overlap between adjacent tiles (default: 0%)
- **Resolution**: Tile resolution from 512px to 4096px (default: 512px)
- **CPU Cores**: Configurable parallel processing (default: 8 cores)
- **Cache Size**: Virtual tile cache limit (default: 50 tiles)

### File Formats
- **Input**: GDS files (.gds, .GDS)
- **Intermediate**: SVG format for visualization
- **Output**: JSON format with complete analysis metadata

## 🤖 AI Analysis

### Gemini Integration
- **Dual Model Architecture**:
  - **Gemini Pro**: Detailed analysis and reasoning
  - **Gemini Flash**: Fast binary classification
- **Sophisticated Prompting**: Specialized prompts for photonic layout analysis
- **Fallback Classification**: Keyword-based backup when AI models fail

### Analysis Pipeline
1. **Tile Generation**: Create analysis-ready image tiles
2. **AI Processing**: Send tiles to Gemini for analysis
3. **Classification**: Binary categorization (continuity/discontinuity)
4. **Result Storage**: Store detailed analysis and classification
5. **User Review**: Manual verification and correction

## 🔧 Troubleshooting

### Common Issues

**Installation Problems:**
- Missing dependencies → See [INSTALLATION.md](INSTALLATION.md#troubleshooting)
- API key not set → See [INSTALLATION.md](INSTALLATION.md#step-3-configure-google-api-key)
- SVG converter missing → See [INSTALLATION.md](INSTALLATION.md#step-4-install-svg-converter-critical)

**Runtime Problems:**
- Tile generation fails → Install rsvg-convert or inkscape
- Memory issues → Reduce grid size, use virtual tiles
- Analysis errors → Check API key and converters

### 📖 Full Troubleshooting Guide

For detailed troubleshooting instructions:

👉 **See [INSTALLATION.md - Troubleshooting Section](INSTALLATION.md#troubleshooting)**

Includes solutions for:
- All installation errors
- Runtime issues
- Platform-specific problems
- Performance optimization tips

## 📊 Example Usage

### Analyzing a Small Layout
```python
# Configuration for quick analysis
Grid Size: 5×5
Tile Resolution: 512px
CPU Cores: 4
Virtual Tiles: Enabled
```

### Analyzing a Large Layout
```python
# Configuration for comprehensive analysis
Grid Size: 20×20
Tile Resolution: 1024px
CPU Cores: 8
Virtual Tiles: Enabled
ROI Analysis: Use for focused areas
```

## 📚 Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Complete installation guide
- **[docs/REFACTORING_DESIGN.md](docs/REFACTORING_DESIGN.md)** - Architecture & design (for developers)

## 🤝 Contributing

We welcome contributions! Here are some areas where you can help:
- **Performance optimization** for large layouts
- **Additional AI models** integration
- **Export format** extensions
- **UI/UX improvements**
- **Documentation** enhancements

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Follow [INSTALLATION.md](INSTALLATION.md) for setup
4. Review [docs/REFACTORING_DESIGN.md](docs/REFACTORING_DESIGN.md) for architecture
5. Make your changes and add tests
6. Submit a pull request

## 📄 License

This project is open source. Please see the license file for details.

## 👤 Author

**William**  
*AI Photonic Physical Verification*

## 🔗 Links

- **Repository**: [GitHub](https://github.com/nguyennm1024/ai-photonic-physical-verification)
- **Google AI Studio**: [Get API Key](https://makersuite.google.com/app/apikey)
- **Issues**: [Report Bugs](https://github.com/nguyennm1024/ai-photonic-physical-verification/issues)

## 📈 Project Status

**Current Version**: 2.0.0 (Refactored)  
**Status**: Active Development  
**Last Updated**: October 2025

### Version 2.0 - Major Refactoring (October 2025)
- ✅ **Modular Architecture**: 24 new modules with clean separation
- ✅ **Core Logic Tested**: 13 unit tests + 6 integration tests (all passing)
- ✅ **Real GDS Validated**: Tested with 4.5MB Nexus_Sample2.GDS
- ✅ **AI Prompts Preserved**: Character-for-character accuracy maintained
- ✅ **Documentation**: Comprehensive architecture docs + troubleshooting
- 🚧 **UI Extraction**: In progress (Phase 3)

### Version 1.0 - Initial Release (August 2025)
- Initial release with complete GUI application
- AI-powered discontinuity detection
- Virtual tile system implementation
- ROI analysis capabilities
- Comprehensive export functionality

---

*For detailed setup instructions, see the installation section above. For support, please open an issue on GitHub.*
