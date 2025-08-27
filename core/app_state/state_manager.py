"""
Application State Manager

This module manages the application state for the Layout Verification App.
It centralizes all state variables and provides methods for state management.
"""

import queue
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class AnalysisState(Enum):
    """Enumeration for analysis states"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class ROIMode(Enum):
    """Enumeration for ROI modes"""
    NAVIGATION = "navigation"
    DRAWING = "drawing"


@dataclass
class ROIRegion:
    """Data class for ROI region information"""
    id: int
    start: Tuple[float, float]
    end: Tuple[float, float]
    rectangle: Any = None  # Matplotlib patch object
    color: str = "red"
    hex: str = "#FF6B6B"
    alpha: float = 0.18


@dataclass
class TileData:
    """Data class for tile information"""
    filename: str
    path: Optional[str] = None
    row: int = 0
    col: int = 0
    analyzed: bool = False
    ai_result: Optional[str] = None
    user_classification: Optional[str] = None
    tile_type: str = "content"
    virtual: bool = False


@dataclass
class GridConfig:
    """Data class for grid configuration"""
    rows: int = 0
    cols: int = 0
    overlap: float = 0.0
    total_tiles: int = 0
    resolution: int = 512


class AppStateManager:
    """
    Centralized application state manager.
    
    This class manages all state variables that were previously scattered
    throughout the LayoutVerificationApp class. It provides a clean interface
    for state management and validation.
    """
    
    def __init__(self):
        """Initialize the application state manager with default values"""
        # File management state
        self._current_gds_path: Optional[str] = None
        self._current_svg_path: Optional[str] = None
        self._current_tiles_dir: Optional[str] = None
        self._svg_dimensions: Optional[Dict[str, float]] = None
        
        # Tile management state
        self._tiles_data: List[TileData] = []
        self._current_tile_index: int = 0
        self._analyzed_tiles: Dict[int, Any] = {}
        self._flagged_tiles: List[int] = []
        self._original_image: Optional[Any] = None
        
        # Virtual tile system
        self._virtual_tiles: bool = True
        self._tile_cache: Dict[str, Any] = {}
        self._max_cache_size: int = 50
        self._grid_config: Optional[GridConfig] = None
        
        # AI models
        self._ai_analyzer: Optional[Any] = None
        self._ai_classifier: Optional[Any] = None
        
        # Threading state
        self._analysis_queue: queue.Queue = queue.Queue()
        self._analysis_running: bool = False
        self._analysis_paused: bool = False
        
        # ROI system state
        self._roi_mode: ROIMode = ROIMode.NAVIGATION
        self._roi_start: Optional[Tuple[float, float]] = None
        self._roi_end: Optional[Tuple[float, float]] = None
        self._drawing_roi: bool = False
        self._roi_regions: List[ROIRegion] = []
        self._roi_counter: int = 0
        self._current_roi_preview: Optional[Any] = None
        
        # Display state
        self._flagged_tiles_displayed: bool = False
        
        # State change callbacks
        self._state_change_callbacks: List[callable] = []
    
    # =============================================================================
    # File Management Properties
    # =============================================================================
    
    @property
    def current_gds_path(self) -> Optional[str]:
        """Get the current GDS file path"""
        return self._current_gds_path
    
    @current_gds_path.setter
    def current_gds_path(self, value: Optional[str]):
        """Set the current GDS file path"""
        self._current_gds_path = value
        self._notify_state_change('current_gds_path', value)
    
    @property
    def current_svg_path(self) -> Optional[str]:
        """Get the current SVG file path"""
        return self._current_svg_path
    
    @current_svg_path.setter
    def current_svg_path(self, value: Optional[str]):
        """Set the current SVG file path"""
        self._current_svg_path = value
        self._notify_state_change('current_svg_path', value)
    
    @property
    def current_tiles_dir(self) -> Optional[str]:
        """Get the current tiles directory"""
        return self._current_tiles_dir
    
    @current_tiles_dir.setter
    def current_tiles_dir(self, value: Optional[str]):
        """Set the current tiles directory"""
        self._current_tiles_dir = value
        self._notify_state_change('current_tiles_dir', value)
    
    @property
    def svg_dimensions(self) -> Optional[Dict[str, float]]:
        """Get the SVG dimensions"""
        return self._svg_dimensions
    
    @svg_dimensions.setter
    def svg_dimensions(self, value: Optional[Dict[str, float]]):
        """Set the SVG dimensions"""
        self._svg_dimensions = value
        self._notify_state_change('svg_dimensions', value)
    
    # =============================================================================
    # Tile Management Properties
    # =============================================================================
    
    @property
    def tiles_data(self) -> List[TileData]:
        """Get the tiles data list"""
        return self._tiles_data
    
    @tiles_data.setter
    def tiles_data(self, value: List[TileData]):
        """Set the tiles data list"""
        self._tiles_data = value
        self._notify_state_change('tiles_data', value)
    
    @property
    def current_tile_index(self) -> int:
        """Get the current tile index"""
        return self._current_tile_index
    
    @current_tile_index.setter
    def current_tile_index(self, value: int):
        """Set the current tile index"""
        if value < 0:
            value = 0
        elif self._tiles_data and value >= len(self._tiles_data):
            value = len(self._tiles_data) - 1
        self._current_tile_index = value
        self._notify_state_change('current_tile_index', value)
    
    @property
    def analyzed_tiles(self) -> Dict[int, Any]:
        """Get the analyzed tiles dictionary"""
        return self._analyzed_tiles
    
    @analyzed_tiles.setter
    def analyzed_tiles(self, value: Dict[int, Any]):
        """Set the analyzed tiles dictionary"""
        self._analyzed_tiles = value
        self._notify_state_change('analyzed_tiles', value)
    
    @property
    def flagged_tiles(self) -> List[int]:
        """Get the flagged tiles list"""
        return self._flagged_tiles
    
    @flagged_tiles.setter
    def flagged_tiles(self, value: List[int]):
        """Set the flagged tiles list"""
        self._flagged_tiles = value
        self._notify_state_change('flagged_tiles', value)
    
    @property
    def original_image(self) -> Optional[Any]:
        """Get the original image"""
        return self._original_image
    
    @original_image.setter
    def original_image(self, value: Optional[Any]):
        """Set the original image"""
        self._original_image = value
        self._notify_state_change('original_image', value)
    
    # =============================================================================
    # Virtual Tile System Properties
    # =============================================================================
    
    @property
    def virtual_tiles(self) -> bool:
        """Get the virtual tiles flag"""
        return self._virtual_tiles
    
    @virtual_tiles.setter
    def virtual_tiles(self, value: bool):
        """Set the virtual tiles flag"""
        self._virtual_tiles = value
        self._notify_state_change('virtual_tiles', value)
    
    @property
    def tile_cache(self) -> Dict[str, Any]:
        """Get the tile cache"""
        return self._tile_cache
    
    @tile_cache.setter
    def tile_cache(self, value: Dict[str, Any]):
        """Set the tile cache"""
        self._tile_cache = value
        self._notify_state_change('tile_cache', value)
    
    @property
    def max_cache_size(self) -> int:
        """Get the maximum cache size"""
        return self._max_cache_size
    
    @max_cache_size.setter
    def max_cache_size(self, value: int):
        """Set the maximum cache size"""
        if value < 1:
            value = 1
        self._max_cache_size = value
        self._notify_state_change('max_cache_size', value)
    
    @property
    def grid_config(self) -> Optional[GridConfig]:
        """Get the grid configuration"""
        return self._grid_config
    
    @grid_config.setter
    def grid_config(self, value: Optional[GridConfig]):
        """Set the grid configuration"""
        self._grid_config = value
        self._notify_state_change('grid_config', value)
    
    # =============================================================================
    # AI Models Properties
    # =============================================================================
    
    @property
    def ai_analyzer(self) -> Optional[Any]:
        """Get the AI analyzer model"""
        return self._ai_analyzer
    
    @ai_analyzer.setter
    def ai_analyzer(self, value: Optional[Any]):
        """Set the AI analyzer model"""
        self._ai_analyzer = value
        self._notify_state_change('ai_analyzer', value)
    
    @property
    def ai_classifier(self) -> Optional[Any]:
        """Get the AI classifier model"""
        return self._ai_classifier
    
    @ai_classifier.setter
    def ai_classifier(self, value: Optional[Any]):
        """Set the AI classifier model"""
        self._ai_classifier = value
        self._notify_state_change('ai_classifier', value)
    
    # =============================================================================
    # Threading Properties
    # =============================================================================
    
    @property
    def analysis_queue(self) -> queue.Queue:
        """Get the analysis queue"""
        return self._analysis_queue
    
    @property
    def analysis_running(self) -> bool:
        """Get the analysis running flag"""
        return self._analysis_running
    
    @analysis_running.setter
    def analysis_running(self, value: bool):
        """Set the analysis running flag"""
        self._analysis_running = value
        self._notify_state_change('analysis_running', value)
    
    @property
    def analysis_paused(self) -> bool:
        """Get the analysis paused flag"""
        return self._analysis_paused
    
    @analysis_paused.setter
    def analysis_paused(self, value: bool):
        """Set the analysis paused flag"""
        self._analysis_paused = value
        self._notify_state_change('analysis_paused', value)
    
    # =============================================================================
    # ROI System Properties
    # =============================================================================
    
    @property
    def roi_mode(self) -> ROIMode:
        """Get the ROI mode"""
        return self._roi_mode
    
    @roi_mode.setter
    def roi_mode(self, value: ROIMode):
        """Set the ROI mode"""
        self._roi_mode = value
        self._notify_state_change('roi_mode', value)
    
    @property
    def roi_start(self) -> Optional[Tuple[float, float]]:
        """Get the ROI start coordinates"""
        return self._roi_start
    
    @roi_start.setter
    def roi_start(self, value: Optional[Tuple[float, float]]):
        """Set the ROI start coordinates"""
        self._roi_start = value
        self._notify_state_change('roi_start', value)
    
    @property
    def roi_end(self) -> Optional[Tuple[float, float]]:
        """Get the ROI end coordinates"""
        return self._roi_end
    
    @roi_end.setter
    def roi_end(self, value: Optional[Tuple[float, float]]):
        """Set the ROI end coordinates"""
        self._roi_end = value
        self._notify_state_change('roi_end', value)
    
    @property
    def drawing_roi(self) -> bool:
        """Get the drawing ROI flag"""
        return self._drawing_roi
    
    @drawing_roi.setter
    def drawing_roi(self, value: bool):
        """Set the drawing ROI flag"""
        self._drawing_roi = value
        self._notify_state_change('drawing_roi', value)
    
    @property
    def roi_regions(self) -> List[ROIRegion]:
        """Get the ROI regions list"""
        return self._roi_regions
    
    @roi_regions.setter
    def roi_regions(self, value: List[ROIRegion]):
        """Set the ROI regions list"""
        self._roi_regions = value
        self._notify_state_change('roi_regions', value)
    
    @property
    def roi_counter(self) -> int:
        """Get the ROI counter"""
        return self._roi_counter
    
    @roi_counter.setter
    def roi_counter(self, value: int):
        """Set the ROI counter"""
        self._roi_counter = value
        self._notify_state_change('roi_counter', value)
    
    @property
    def current_roi_preview(self) -> Optional[Any]:
        """Get the current ROI preview"""
        return self._current_roi_preview
    
    @current_roi_preview.setter
    def current_roi_preview(self, value: Optional[Any]):
        """Set the current ROI preview"""
        self._current_roi_preview = value
        self._notify_state_change('current_roi_preview', value)
    
    # =============================================================================
    # Display Properties
    # =============================================================================
    
    @property
    def flagged_tiles_displayed(self) -> bool:
        """Get the flagged tiles displayed flag"""
        return self._flagged_tiles_displayed
    
    @flagged_tiles_displayed.setter
    def flagged_tiles_displayed(self, value: bool):
        """Set the flagged tiles displayed flag"""
        self._flagged_tiles_displayed = value
        self._notify_state_change('flagged_tiles_displayed', value)
    
    # =============================================================================
    # State Management Methods
    # =============================================================================
    
    def reset_analysis_state(self):
        """Reset all analysis-related state"""
        self._tiles_data = []
        self._current_tile_index = 0
        self._analyzed_tiles = {}
        self._flagged_tiles = []
        self._original_image = None
        self._grid_config = None
        self._tile_cache = {}
        self._analysis_running = False
        self._analysis_paused = False
        self._flagged_tiles_displayed = False
        self._notify_state_change('reset_analysis', None)
    
    def reset_file_state(self):
        """Reset all file-related state"""
        self._current_gds_path = None
        self._current_svg_path = None
        self._current_tiles_dir = None
        self._svg_dimensions = None
        self._notify_state_change('reset_files', None)
    
    def reset_roi_state(self):
        """Reset all ROI-related state"""
        self._roi_mode = ROIMode.NAVIGATION
        self._roi_start = None
        self._roi_end = None
        self._drawing_roi = False
        self._roi_regions = []
        self._roi_counter = 0
        self._current_roi_preview = None
        self._notify_state_change('reset_roi', None)
    
    def get_analysis_state(self) -> AnalysisState:
        """Get the current analysis state"""
        if self._analysis_running and not self._analysis_paused:
            return AnalysisState.RUNNING
        elif self._analysis_running and self._analysis_paused:
            return AnalysisState.PAUSED
        elif self._analyzed_tiles and not self._analysis_running:
            return AnalysisState.COMPLETED
        else:
            return AnalysisState.IDLE
    
    def add_state_change_callback(self, callback: callable):
        """Add a callback function to be called when state changes"""
        self._state_change_callbacks.append(callback)
    
    def remove_state_change_callback(self, callback: callable):
        """Remove a callback function"""
        if callback in self._state_change_callbacks:
            self._state_change_callbacks.remove(callback)
    
    def _notify_state_change(self, property_name: str, value: Any):
        """Notify all registered callbacks of state changes"""
        for callback in self._state_change_callbacks:
            try:
                callback(property_name, value)
            except Exception as e:
                print(f"Error in state change callback: {e}")
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current state"""
        return {
            'file_state': {
                'gds_path': self._current_gds_path,
                'svg_path': self._current_svg_path,
                'tiles_dir': self._current_tiles_dir,
                'svg_dimensions': self._svg_dimensions
            },
            'tile_state': {
                'total_tiles': len(self._tiles_data),
                'current_index': self._current_tile_index,
                'analyzed_count': len(self._analyzed_tiles),
                'flagged_count': len(self._flagged_tiles),
                'virtual_tiles': self._virtual_tiles,
                'cache_size': len(self._tile_cache),
                'grid_config': self._grid_config
            },
            'analysis_state': {
                'state': self.get_analysis_state().value,
                'running': self._analysis_running,
                'paused': self._analysis_paused,
                'ai_analyzer_available': self._ai_analyzer is not None,
                'ai_classifier_available': self._ai_classifier is not None
            },
            'roi_state': {
                'mode': self._roi_mode.value,
                'regions_count': len(self._roi_regions),
                'drawing': self._drawing_roi
            },
            'display_state': {
                'flagged_displayed': self._flagged_tiles_displayed
            }
        }
