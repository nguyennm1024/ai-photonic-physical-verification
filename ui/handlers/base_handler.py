"""
Base Handler Module
===================

Base class for all event handlers with shared functionality.
"""

from typing import Callable, Dict, Optional
from tkinter import messagebox

from core.file_manager import GDSLoader, SVGConverter, SVGParser
from core.tile_system import TileGenerator, TileCache
from core.ai_analyzer import GeminiClient, AnalysisEngine
from core.roi_manager import ROIStorage, ROICalculator
from core.app_state import StateManager


class BaseHandler:
    """
    Base class for all event handlers.

    Provides:
    - Access to all core modules
    - UI callback management
    - Shared state access
    """

    def __init__(
        self,
        state_manager: StateManager,
        gds_loader: GDSLoader,
        svg_converter: SVGConverter,
        svg_parser: SVGParser,
        tile_generator: TileGenerator,
        tile_cache: TileCache,
        gemini_client: Optional[GeminiClient],
        analysis_engine: Optional[AnalysisEngine],
        roi_storage: ROIStorage,
        roi_calculator: ROICalculator,
        ui_callbacks: Dict[str, Optional[Callable]]
    ):
        """
        Initialize base handler.

        Args:
            state_manager: Application state manager
            gds_loader: GDS file loader
            svg_converter: SVG converter
            svg_parser: SVG parser
            tile_generator: Tile generator
            tile_cache: Tile cache
            gemini_client: Gemini AI client (optional)
            analysis_engine: AI analysis engine (optional)
            roi_storage: ROI storage
            roi_calculator: ROI calculator
            ui_callbacks: Shared UI callback dictionary
        """
        # Core modules
        self.state = state_manager
        self.gds_loader = gds_loader
        self.svg_converter = svg_converter
        self.svg_parser = svg_parser
        self.tile_gen = tile_generator
        self.tile_cache = tile_cache
        self.gemini = gemini_client
        self.analyzer = analysis_engine
        self.roi_storage = roi_storage
        self.roi_calc = roi_calculator

        # Shared UI callbacks
        self.ui_callbacks = ui_callbacks

    def _call_ui(self, name: str, *args, **kwargs):
        """
        Call a UI callback if bound.

        Args:
            name: Callback name
            *args, **kwargs: Arguments to pass
        """
        if self.ui_callbacks.get(name):
            self.ui_callbacks[name](*args, **kwargs)

    def show_error(self, title: str, message: str):
        """Show error dialog"""
        messagebox.showerror(title, message)

    def show_warning(self, title: str, message: str):
        """Show warning dialog"""
        messagebox.showwarning(title, message)

    def show_info(self, title: str, message: str):
        """Show info dialog"""
        messagebox.showinfo(title, message)
