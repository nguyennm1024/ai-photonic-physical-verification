# AI Photonic Physical Verification

A comprehensive GUI application for automated photonic integrated circuit (PIC) layout verification using AI-powered discontinuity detection.

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

### 1. Clone the Repository
```bash
git clone https://github.com/nguyennm1024/ai-photonic-physical-verification.git
cd ai-photonic-physical-verification
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
```bash
export GOOGLE_API_KEY=your_api_key_here
```

### 4. Optional: Install System Tools (Recommended)
For enhanced SVG-to-PNG conversion:

**macOS:**
```bash
brew install librsvg inkscape
```

**Ubuntu/Debian:**
```bash
sudo apt-get install librsvg2-bin inkscape
```

**Windows:**
- Download and install [Inkscape](https://inkscape.org/release/)
- Install [Google Chrome](https://www.google.com/chrome/) for browser-based conversion

## 🚀 Quick Start

### Basic Usage
```bash
python layout_verification_app.py
```

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

### Application Architecture
The application follows a monolithic design with several key components:
- **File Processing**: GDS loading and SVG conversion
- **Tile Management**: Virtual and physical tile generation
- **AI Analysis**: Gemini-powered discontinuity detection
- **User Interface**: Tkinter-based GUI with matplotlib integration
- **Data Export**: Comprehensive results formatting

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

#### "GOOGLE_API_KEY environment variable not set"
```bash
export GOOGLE_API_KEY=your_actual_api_key
```

#### "gdspy not available"
```bash
pip install gdspy>=1.6.13
```

#### SVG conversion fails
- Install system dependencies: `librsvg`, `inkscape`, or Chrome
- The app will show a placeholder if all conversion methods fail
- AI analysis will still work without perfect SVG conversion

#### Memory issues with large grids
- Reduce grid size (start with 5×5 or 10×10)
- Use lower tile resolution (512px instead of 2048px)
- Enable virtual tiles instead of pre-generated files

### Performance Optimization
- **Reduce CPU cores** for other system tasks
- **Use virtual tiles** for memory efficiency
- **Enable caching** for repeated analysis
- **Focus on ROI** for targeted analysis

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
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

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

**Current Version**: 1.0.0  
**Status**: Active Development  
**Last Updated**: August 2025

### Recent Updates
- Initial release with complete GUI application
- AI-powered discontinuity detection
- Virtual tile system implementation
- ROI analysis capabilities
- Comprehensive export functionality

---

*For detailed setup instructions, see the installation section above. For support, please open an issue on GitHub.*
