"""
Event Handlers Module
=====================

Modular event handlers for the layout verification application.

This module uses a facade pattern to provide a unified interface
while organizing handlers into specialized modules.
"""

from typing import Optional, Callable, Dict

from core.file_manager import GDSLoader, SVGConverter, SVGParser
from core.tile_system import TileGenerator, TileCache
from core.ai_analyzer import GeminiClient, AnalysisEngine
from core.roi_manager import ROIStorage, ROICalculator
from core.app_state import StateManager

from .file_handler import FileHandler
from .grid_handler import GridHandler
from .processing_handler import ProcessingHandler
from .tile_handler import TileHandler
from .roi_handler import ROIHandler


class EventHandlers:
    """
    Unified event handler facade.

    This class provides a single interface to all event handlers,
    delegating to specialized handler modules internally.

    Architecture:
    - FileHandler: GDS/SVG operations
    - GridHandler: Grid generation
    - ProcessingHandler: AI processing
    - TileHandler: Tile display & navigation
    - ROIHandler: ROI operations
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
        roi_calculator: ROICalculator
    ):
        """
        Initialize event handlers.

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
        """
        # Shared UI callbacks dictionary
        self.ui_callbacks: Dict[str, Optional[Callable]] = {
            'update_file_info': None,
            'update_status': None,
            'update_grid_info': None,
            'set_progress': None,
            'display_image': None,
            'enable_roi_selection': None,
            'disable_roi_selection': None,
            'add_roi_to_list': None,
            'update_summary': None,
            'display_tile_review': None,
            'update_tile_status': None,
            'clear_tile_status': None,
            'update_tile_review_status': None,
            'update_focused_tile': None,
        }

        # Initialize specialized handlers
        handler_args = (
            state_manager,
            gds_loader,
            svg_converter,
            svg_parser,
            tile_generator,
            tile_cache,
            gemini_client,
            analysis_engine,
            roi_storage,
            roi_calculator,
            self.ui_callbacks
        )

        self.file = FileHandler(*handler_args)
        self.grid = GridHandler(*handler_args)
        self.processing = ProcessingHandler(*handler_args)
        self.tile = TileHandler(*handler_args)
        self.roi = ROIHandler(*handler_args)

    def bind_ui_callback(self, name: str, callback: Callable):
        """
        Bind a UI update callback.

        Args:
            name: Callback name
            callback: Callback function
        """
        if name in self.ui_callbacks:
            self.ui_callbacks[name] = callback

    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================

    def handle_load_gds(self, file_path: str):
        """Delegate to file handler"""
        return self.file.handle_load_gds(file_path)

    def handle_generate_svg(self, gds_lib, gds_path: str):
        """Delegate to file handler"""
        return self.file.handle_generate_svg(gds_lib, gds_path)

    # ========================================================================
    # GRID OPERATIONS
    # ========================================================================

    def handle_generate_grid(self, rows: int, cols: int, overlap: int):
        """Delegate to grid handler"""
        return self.grid.handle_generate_grid(rows, cols, overlap)

    # ========================================================================
    # PROCESSING OPERATIONS
    # ========================================================================

    def handle_process_all_tiles(self):
        """Delegate to processing handler"""
        return self.processing.handle_process_all_tiles()

    def handle_process_roi_tiles(self):
        """Delegate to processing handler"""
        return self.processing.handle_process_roi_tiles()

    def handle_cancel_processing(self):
        """Delegate to processing handler"""
        return self.processing.handle_cancel_processing()

    # ========================================================================
    # TILE OPERATIONS
    # ========================================================================

    def handle_tile_click(self, row: int, col: int):
        """Delegate to tile handler"""
        return self.tile.handle_tile_click(row, col)

    def handle_prev_tile(self):
        """Delegate to tile handler"""
        return self.tile.handle_prev_tile()

    def handle_next_tile(self):
        """Delegate to tile handler"""
        return self.tile.handle_next_tile()

    def handle_classify_tile(self, row: int, col: int, classification: str):
        """Delegate to tile handler"""
        return self.tile.handle_classify_tile(row, col, classification)

    # ========================================================================
    # ROI OPERATIONS
    # ========================================================================

    def handle_roi_select_toggle(self, selecting: bool):
        """Delegate to ROI handler"""
        return self.roi.handle_roi_select_toggle(selecting)

    def handle_roi_analyze(self):
        """Delegate to ROI handler"""
        return self.roi.handle_roi_analyze()

    def handle_roi_clear(self):
        """Delegate to ROI handler"""
        return self.roi.handle_roi_clear()


# Export the main class
__all__ = ['EventHandlers']
