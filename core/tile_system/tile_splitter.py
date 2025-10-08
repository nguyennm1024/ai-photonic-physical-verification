"""
Tile Splitter Module
====================

Calculate tile positions and grid parameters.
"""

from typing import Tuple, Dict
import xml.etree.ElementTree as ET
from ..app_state.state_manager import GridConfig


class TileSplitter:
    """Calculate tile positions and grid layouts"""
    
    def calculate_tile_bounds(self, row: int, col: int, grid_config: GridConfig,
                             svg_path: str) -> Tuple[float, float, float, float]:
        """
        Calculate tile bounds in SVG coordinates.
        
        Args:
            row: Tile row index
            col: Tile column index
            grid_config: Grid configuration
            svg_path: Path to SVG file (to get viewBox)
            
        Returns:
            (x, y, width, height) in SVG coordinates
        """
        # Parse SVG to get viewBox
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        viewbox = root.get('viewBox')
        if viewbox:
            viewbox_x, viewbox_y, viewbox_width, viewbox_height = map(float, viewbox.split())
        else:
            viewbox_x, viewbox_y = 0, 0
            viewbox_width = float(root.get('width', '1000').replace('px', ''))
            viewbox_height = float(root.get('height', '1000').replace('px', ''))
        
        svg_x, svg_y = viewbox_x, viewbox_y
        svg_width, svg_height = viewbox_width, viewbox_height
        
        # Calculate tile parameters
        rows, cols = grid_config.rows, grid_config.cols
        overlap = grid_config.overlap / 100.0
        
        step_width = svg_width / cols
        step_height = svg_height / rows
        tile_width = step_width * (1 + overlap)
        tile_height = step_height * (1 + overlap)
        
        # Calculate tile position
        x = svg_x + col * step_width
        y = svg_y + row * step_height
        
        return (x, y, tile_width, tile_height)
    
    def get_tile_from_coordinates(self, x: float, y: float, 
                                  grid_config: GridConfig, 
                                  svg_path: str) -> Tuple[int, int]:
        """
        Convert pixel coordinates to tile (row, col).
        
        Args:
            x: X coordinate in pixel space
            y: Y coordinate in pixel space
            grid_config: Grid configuration
            svg_path: Path to SVG file
            
        Returns:
            (row, col) tuple
        """
        # Parse SVG to get viewBox
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        viewbox = root.get('viewBox')
        if viewbox:
            viewbox_x, viewbox_y, viewbox_width, viewbox_height = map(float, viewbox.split())
        else:
            viewbox_x, viewbox_y = 0, 0
            viewbox_width = float(root.get('width', '1000').replace('px', ''))
            viewbox_height = float(root.get('height', '1000').replace('px', ''))
        
        svg_width, svg_height = viewbox_width, viewbox_height
        
        rows, cols = grid_config.rows, grid_config.cols
        
        step_width = svg_width / cols
        step_height = svg_height / rows
        
        # Calculate tile indices
        col = int(x / step_width)
        row = int(y / step_height)
        
        # Clamp to valid range
        row = max(0, min(row, rows - 1))
        col = max(0, min(col, cols - 1))
        
        return (row, col)

