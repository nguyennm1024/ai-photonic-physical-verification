#!/usr/bin/env python3
"""
Layout Verification Application - Main Entry Point
==================================================

Refactored modular architecture with clean separation between:
- Core business logic (core/)
- UI components (ui/)
- Utility functions (utils/)

Author: William (Refactored by AI Assistant)
Date: 2025-10-07
"""

try:
    import tkinter as tk
    from tkinter import ttk
except Exception as e:
    raise SystemExit(
        "Failed to import tkinter (Tcl/Tk).\n"
        "Install Tcl/Tk and ensure Python has Tk support.\n\n"
        "On macOS with Homebrew:\n"
        "  brew install tcl-tk\n\n"
        "If using uv-managed Python, upgrade it and recreate the venv:\n"
        "  uv python upgrade --reinstall\n"
        "  uv venv --clear .venv\n\n"
        "You can test Tk with: python3 -m tkinter\n\n"
        f"Original error: {e}"
    )
import os
import sys

# Import core modules
from core.file_manager import GDSLoader, SVGConverter, SVGParser
from core.tile_system import TileGenerator, TileCache
from core.ai_analyzer import GeminiClient, AnalysisEngine, ParallelAnalyzer
from core.roi_manager import ROIStorage, ROICalculator
from core.app_state import StateManager

# Import UI components
from ui.components import (
    FileControls,
    GridConfigPanel,
    ProcessingButtons,
    TileReviewPanel,
    AnalysisPanel,
    ImageCanvas,
    SummaryPanel
)
from ui.event_handlers import EventHandlers
from ui.modern_theme import ModernTheme


class LayoutVerificationApp:
    """
    Main application class - integrates all modules and UI components.
    
    This refactored version maintains clean separation of concerns:
    - Core logic is handled by core modules
    - UI is componentized in ui/components
    - Event handling bridges UI and core via ui/event_handlers
    """
    
    def __init__(self, root):
        """
        Initialize the application.
        
        Args:
            root: tkinter root window
        """
        self.root = root
        self.root.title("Layout Verification System (Refactored)")
        self.root.geometry("1400x900")
        
        # Initialize core modules
        self._init_core_modules()
        
        # Initialize event handlers
        self._init_event_handlers()
        
        # Setup UI
        self._setup_ui()
        
        # Bind UI callbacks to event handlers
        self._bind_callbacks()
        
        print("✅ Application initialized successfully")
    
    def _init_core_modules(self):
        """Initialize all core business logic modules"""
        # State management
        self.state_mgr = StateManager()
        
        # File operations
        self.gds_loader = GDSLoader()
        self.svg_converter = SVGConverter()
        self.svg_parser = SVGParser()
        
        # Tile system - share cache between generator and app
        self.tile_cache = TileCache(max_size=100)  # Increased cache size
        self.tile_generator = TileGenerator(self.svg_converter, self.tile_cache)
        
        # AI analyzer (optional - requires API key)
        self.gemini_client = None
        self.analysis_engine = None
        self.parallel_analyzer = None
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            try:
                self.gemini_client = GeminiClient(api_key)
                self.analysis_engine = AnalysisEngine(self.gemini_client, self.tile_generator)
                self.parallel_analyzer = ParallelAnalyzer(self.gemini_client, self.tile_generator)
                print("✅ AI analyzer initialized with Gemini Pro + Flash")
                print("   🤖 Gemini Pro: Detailed discontinuity analysis")
                print("   ⚡ Gemini Flash: Fast binary classification")
            except Exception as e:
                print(f"❌ AI analyzer initialization failed: {e}")
                print(f"   Check your GOOGLE_API_KEY and internet connection")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️  GOOGLE_API_KEY not set - AI features disabled")
            print("   To enable AI analysis:")
            print("   1. Get API key: https://makersuite.google.com/app/apikey")
            print("   2. Set environment: export GOOGLE_API_KEY='your_key_here'")
        
        # ROI management
        self.roi_storage = ROIStorage()
        self.roi_calculator = ROICalculator()
    
    def _init_event_handlers(self):
        """Initialize event handler layer"""
        self.handlers = EventHandlers(
            state_manager=self.state_mgr,
            gds_loader=self.gds_loader,
            svg_converter=self.svg_converter,
            svg_parser=self.svg_parser,
            tile_generator=self.tile_generator,
            tile_cache=self.tile_cache,
            gemini_client=self.gemini_client,
            analysis_engine=self.analysis_engine,
            roi_storage=self.roi_storage,
            roi_calculator=self.roi_calculator
        )
    
    def _setup_ui(self):
        """Setup UI components"""
        # Apply modern theme
        ModernTheme.apply(self.root)
        
        # Create main frames
        self._create_layout()
        
        # Create left panel components
        self.file_controls = FileControls(self.left_panel)
        self.file_controls.pack(fill=tk.X, padx=5, pady=5)
        
        self.grid_config = GridConfigPanel(self.left_panel)
        self.grid_config.pack(fill=tk.X, padx=5, pady=5)
        
        self.processing_btns = ProcessingButtons(self.left_panel)
        self.processing_btns.pack(fill=tk.X, padx=5, pady=5)
        
        # Tile review panel (replaces old ROI controls)
        self.tile_review = TileReviewPanel(self.left_panel)
        self.tile_review.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create right panel components
        self.image_canvas = ImageCanvas(self.right_top_panel)
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.analysis_panel = AnalysisPanel(self.right_bottom_panel)
        self.analysis_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.summary_panel = SummaryPanel(self.right_bottom_panel)
        self.summary_panel.pack(fill=tk.X, padx=5, pady=5)
        
        # Status bar
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            relief=tk.FLAT,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_layout(self):
        """Create main layout structure"""
        # Main horizontal split
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Left panel (controls and tile viewer)
        self.left_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_panel, weight=1)

        # Right panel (image and analysis)
        self.right_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_panel, weight=3)
        
        # Right panel vertical split
        self.right_paned = ttk.PanedWindow(self.right_panel, orient=tk.VERTICAL)
        self.right_paned.pack(fill=tk.BOTH, expand=True)
        
        self.right_top_panel = ttk.Frame(self.right_paned)
        self.right_paned.add(self.right_top_panel, weight=2)
        
        self.right_bottom_panel = ttk.Frame(self.right_paned)
        self.right_paned.add(self.right_bottom_panel, weight=1)
    
    def _bind_callbacks(self):
        """Bind UI callbacks to event handlers"""
        # File controls
        self.file_controls.bind_load_command(self.handlers.handle_load_gds)
        
        # Processing buttons (includes grid generation and ROI selection)
        self.processing_btns.bind_generate_command(self._handle_generate_with_config)
        self.processing_btns.bind_process_all_command(self.handlers.handle_process_all_tiles)
        self.processing_btns.bind_select_roi_command(self.handlers.handle_roi_select_toggle)
        self.processing_btns.bind_process_roi_command(self.handlers.handle_process_roi_tiles)
        self.processing_btns.bind_cancel_command(self.handlers.handle_cancel_processing)
        
        # Tile review panel
        self.tile_review.bind_prev_command(self.handlers.handle_prev_tile)
        self.tile_review.bind_next_command(self.handlers.handle_next_tile)
        self.tile_review.bind_classify_command(self.handlers.handle_classify_tile)
        
        # Image canvas - tile click
        self.image_canvas.bind_tile_click(self.handlers.handle_tile_click)
        
        # Bind event handler UI callbacks (do this once, not in generate function!)
        # This allows event handlers to update the UI
        self.handlers.bind_ui_callback('update_file_info', self._update_file_info)
        self.handlers.bind_ui_callback('update_status', self._update_status)
        self.handlers.bind_ui_callback('update_grid_info', self._update_grid_info)
        self.handlers.bind_ui_callback('set_progress', self._set_progress)
        self.handlers.bind_ui_callback('append_result', self._append_result)
        self.handlers.bind_ui_callback('display_image', self._display_image)
        self.handlers.bind_ui_callback('enable_roi_selection', self._enable_roi_selection)
        self.handlers.bind_ui_callback('disable_roi_selection', self._disable_roi_selection)
        self.handlers.bind_ui_callback('add_roi_to_list', self._add_roi_to_list)
        self.handlers.bind_ui_callback('update_summary', self._update_summary)
        self.handlers.bind_ui_callback('display_tile_review', self._display_tile_review)
        self.handlers.bind_ui_callback('update_tile_status', self._update_tile_status)
        self.handlers.bind_ui_callback('clear_tile_status', self._clear_tile_status)
    
    def _handle_generate_with_config(self):
        """Get config from grid panel and call handler"""
        config = self.grid_config.get_config()
        self.handlers.handle_generate_grid(config['rows'], config['cols'], config['overlap'])
    
    # UI callback implementations
    def _update_file_info(self, file_path: str):
        """Update file info display"""
        self.file_controls.set_file_info(file_path)
    
    def _update_status(self, message: str):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def _update_grid_info(self, message: str):
        """Update grid configuration info"""
        self.grid_config.set_info(message)
    
    def _set_progress(self, value: int, maximum: int = 100):
        """Update progress bar"""
        self.analysis_panel.set_progress(value, maximum)
        self.analysis_panel.set_progress_text(f"{value}/{maximum}")
        self.root.update_idletasks()
    
    def _append_result(self, text: str):
        """Append text to results panel"""
        self.analysis_panel.append_result(text)
    
    def _display_image(self, image, grid_config=None, svg_dimensions=None):
        """Display image on canvas with optional grid overlay and SVG dimensions"""
        self.image_canvas.display_image(image, grid_config, svg_dimensions)
    
    def _enable_roi_selection(self, callback):
        """Enable ROI selection on canvas"""
        self.image_canvas.enable_roi_selection(callback)
    
    def _disable_roi_selection(self):
        """Disable ROI selection"""
        self.image_canvas.disable_roi_selection()
        # ROI selection state is now managed by processing_btns
    
    def _add_roi_to_list(self, roi_text: str):
        """Add ROI to list"""
        # ROI list removed - just update status instead
        self._update_status(f"ROI added: {roi_text}")
    
    def _update_summary(self, total: int, issues: int, clean: int, time_elapsed: float):
        """Update summary panel"""
        self.summary_panel.update_summary(total, issues, clean, time_elapsed)
    
    def _display_tile_review(self, image, row: int, col: int, index: int, ai_result: str = ""):
        """Display tile in review panel"""
        self.tile_review.display_tile(image, row, col, index, ai_result)

    def _update_tile_status(self, row: int, col: int, classification: str):
        """Update visual status of tile on layout"""
        self.image_canvas.update_tile_status(row, col, classification, analyzed=True)

    def _clear_tile_status(self):
        """Clear all tile status overlays"""
        self.image_canvas.clear_tile_status()


def main():
    """Main application entry point"""
    # Create root window
    try:
        root = tk.Tk()
    except Exception as e:
        raise SystemExit(
            "Tcl/Tk runtime is not available.\n"
            "Ensure Tcl/Tk libraries are installed and discoverable.\n\n"
            "On macOS with Homebrew:\n"
            "  brew install tcl-tk\n\n"
            "If Python still cannot find Tcl/Tk, set environment variables before running:\n"
            "  export TCL_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tcl9.0:/opt/homebrew/opt/tcl-tk/lib/tcl8.6\n"
            "  export TK_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tk9.0:/opt/homebrew/opt/tcl-tk/lib/tk8.6\n"
            "  export PATH=/opt/homebrew/opt/tcl-tk/bin:$PATH\n\n"
            "If using uv-managed Python, upgrade and recreate the venv:\n"
            "  uv python upgrade --reinstall && uv venv --clear .venv\n\n"
            "Test Tk availability with: python3 -m tkinter\n\n"
            f"Original error: {e}"
        )
    
    # Set window icon if available
    try:
        # You can add an icon file later
        pass
    except:
        pass
    
    # Create application (theme is applied in _setup_ui)
    app = LayoutVerificationApp(root)
    
    # Center window on screen
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (1400 // 2)
    y = (screen_height // 2) - (900 // 2)
    root.geometry(f"1400x900+{x}+{y}")
    
    # Minimum window size - responsive but not too small
    root.minsize(800, 500)
    
    # Run
    print("🚀 Application started - Modern UI")
    print("📝 Overlap is now in percentage (0-50%)")
    root.mainloop()


if __name__ == "__main__":
    main()
