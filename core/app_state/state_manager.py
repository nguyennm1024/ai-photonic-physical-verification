"""
State Manager Module
====================

Centralized application state management.
Single source of truth for all application state.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class TileMetadata:
    """Metadata for a single tile"""
    filename: str
    row: int
    col: int
    path: Optional[str] = None  # None for virtual tiles
    virtual: bool = False
    analyzed: bool = False
    ai_result: Optional[str] = None
    classification: Optional[str] = None  # 'continuity' or 'discontinuity'
    user_classification: Optional[str] = None
    tile_type: str = 'content'


@dataclass
class GridConfig:
    """Grid configuration for tile splitting"""
    rows: int
    cols: int
    overlap: float  # Percentage (0-50)
    resolution: int = 512
    total_tiles: int = 0


@dataclass
class ROIRegion:
    """Single ROI region data"""
    id: int
    start: tuple  # (x, y) in image coordinates
    end: tuple
    color: str
    hex_color: str
    alpha: float
    rectangle: Optional[object] = None  # matplotlib Rectangle patch


@dataclass
class ApplicationState:
    """
    Centralized application state.
    All mutable state should be managed through StateManager.
    """
    # File paths
    current_gds_path: Optional[str] = None
    current_svg_path: Optional[str] = None
    current_tiles_dir: Optional[str] = None
    
    # Tile data
    tiles_data: List[TileMetadata] = field(default_factory=list)
    grid_config: Optional[GridConfig] = None
    current_tile_index: int = 0
    
    # Analysis state
    analyzed_tiles: Dict = field(default_factory=dict)
    flagged_tiles: List[int] = field(default_factory=list)
    
    # ROI state
    roi_regions: List[ROIRegion] = field(default_factory=list)
    roi_tile_indices: List[int] = field(default_factory=list)
    
    # Display state
    original_image: Optional[object] = None  # PIL Image
    svg_dimensions: Optional[Dict] = None
    flagged_tiles_displayed: bool = False
    
    # Analysis control
    analysis_running: bool = False
    analysis_paused: bool = False


class StateManager:
    """
    Manage application state with validation.
    Provides clean API for state access and modification.
    """
    
    def __init__(self):
        """Initialize with default state"""
        self.state = ApplicationState()
    
    def reset(self):
        """Reset all state to initial values"""
        self.state = ApplicationState()
    
    def reset_analysis(self):
        """Reset only analysis-related state"""
        self.state.analyzed_tiles = {}
        self.state.flagged_tiles = []
        self.state.analysis_running = False
        self.state.analysis_paused = False
        
        # Reset tile analysis status
        for tile in self.state.tiles_data:
            tile.analyzed = False
            tile.ai_result = None
            tile.classification = None
    
    def reset_roi(self):
        """Reset ROI-related state"""
        self.state.roi_regions = []
        self.state.roi_tile_indices = []
    
    def load_gds_file(self, file_path: str):
        """Update state when GDS file is loaded"""
        self.state.current_gds_path = file_path
        # Reset dependent state
        self.state.current_svg_path = None
        self.state.current_tiles_dir = None
        self.state.tiles_data = []
        self.reset_analysis()
    
    def set_gds_path(self, file_path: str):
        """Set GDS file path without resetting other state"""
        self.state.current_gds_path = file_path
    
    def get_gds_path(self) -> Optional[str]:
        """Get current GDS file path"""
        return self.state.current_gds_path
    
    def set_svg_path(self, svg_path: str, svg_dimensions: Optional[Dict] = None):
        """Update state when SVG is generated"""
        self.state.current_svg_path = svg_path
        if svg_dimensions:
            self.state.svg_dimensions = svg_dimensions
    
    def get_svg_path(self) -> Optional[str]:
        """Get current SVG file path"""
        return self.state.current_svg_path
    
    def set_grid_config(self, grid_config: GridConfig):
        """Update grid configuration"""
        self.state.grid_config = grid_config
    
    def create_grid_config(self, rows: int, cols: int, overlap: int) -> GridConfig:
        """
        Create and set grid configuration.
        
        Args:
            rows: Number of rows
            cols: Number of columns
            overlap: Overlap in pixels
            
        Returns:
            Created GridConfig
        """
        grid_config = GridConfig(
            rows=rows,
            cols=cols,
            overlap=overlap,
            total_tiles=rows * cols
        )
        self.set_grid_config(grid_config)
        return grid_config
    
    def add_tile_metadata(self, row: int, col: int, ai_result: str):
        """
        Add or update tile metadata.
        
        Args:
            row: Tile row
            col: Tile column
            ai_result: AI analysis result
        """
        # Find or create tile metadata
        tile_found = False
        for tile in self.state.tiles_data:
            if tile.row == row and tile.col == col:
                tile.ai_result = ai_result
                tile.analyzed = True
                tile_found = True
                break
        
        if not tile_found:
            # Create new tile metadata
            tile = TileMetadata(
                filename=f"tile_{row}_{col}",
                row=row,
                col=col,
                virtual=True,
                analyzed=True,
                ai_result=ai_result
            )
            self.state.tiles_data.append(tile)
    
    def set_tiles_data(self, tiles_data: List[TileMetadata]):
        """Update tiles data"""
        self.state.tiles_data = tiles_data
        self.state.current_tile_index = 0
    
    def add_flagged_tile(self, tile_index: int):
        """Add a tile to flagged list"""
        if tile_index not in self.state.flagged_tiles:
            self.state.flagged_tiles.append(tile_index)
    
    def get_summary(self) -> Dict:
        """
        Get analysis summary statistics.
        
        Returns:
            Dict with summary stats
        """
        total_tiles = len(self.state.tiles_data)
        analyzed_tiles = sum(1 for tile in self.state.tiles_data if tile.analyzed)
        flagged_tiles = len(self.state.flagged_tiles)
        
        classified_continuous = sum(1 for tile in self.state.tiles_data 
                                   if tile.user_classification == 'continuous')
        classified_discontinuity = sum(1 for tile in self.state.tiles_data 
                                      if tile.user_classification == 'discontinuity')
        
        return {
            'total_tiles': total_tiles,
            'analyzed_tiles': analyzed_tiles,
            'flagged_tiles': flagged_tiles,
            'classified_continuous': classified_continuous,
            'classified_discontinuity': classified_discontinuity
        }
    
    def get_current_tile(self) -> Optional[TileMetadata]:
        """Get currently selected tile"""
        if 0 <= self.state.current_tile_index < len(self.state.tiles_data):
            return self.state.tiles_data[self.state.current_tile_index]
        return None
    
    def navigate_to_tile(self, tile_index: int) -> bool:
        """
        Navigate to a specific tile.
        
        Returns:
            True if navigation successful, False otherwise
        """
        if 0 <= tile_index < len(self.state.tiles_data):
            self.state.current_tile_index = tile_index
            return True
        return False
    
    def next_tile(self) -> bool:
        """Move to next tile"""
        if self.state.current_tile_index < len(self.state.tiles_data) - 1:
            self.state.current_tile_index += 1
            return True
        return False
    
    def previous_tile(self) -> bool:
        """Move to previous tile"""
        if self.state.current_tile_index > 0:
            self.state.current_tile_index -= 1
            return True
        return False
    
    def add_roi_region(self, roi_region: ROIRegion):
        """Add a new ROI region"""
        self.state.roi_regions.append(roi_region)
    
    def remove_last_roi(self) -> Optional[ROIRegion]:
        """Remove and return the last ROI region"""
        if self.state.roi_regions:
            return self.state.roi_regions.pop()
        return None
    
    def clear_all_roi(self):
        """Clear all ROI regions"""
        self.state.roi_regions = []
        self.state.roi_tile_indices = []

