"""
ROI Calculator Module
=====================

Calculate tile/ROI overlaps and manage ROI-related calculations.
"""

from typing import List, Tuple
from ..app_state.state_manager import ROIRegion, TileMetadata, GridConfig


class ROICalculator:
    """Calculate ROI and tile relationships"""
    
    @staticmethod
    def check_overlap(rect1_bounds: Tuple[float, float, float, float],
                     rect2_bounds: Tuple[float, float, float, float]) -> bool:
        """
        Check if two rectangles overlap.
        
        Args:
            rect1_bounds: (x_min, y_min, x_max, y_max)
            rect2_bounds: (x_min, y_min, x_max, y_max)
            
        Returns:
            True if rectangles overlap
        """
        r1_x_min, r1_y_min, r1_x_max, r1_y_max = rect1_bounds
        r2_x_min, r2_y_min, r2_x_max, r2_y_max = rect2_bounds
        
        # Check if rectangles do NOT overlap, then invert
        no_overlap = (r1_x_max <= r2_x_min or r1_x_min >= r2_x_max or
                     r1_y_max <= r2_y_min or r1_y_min >= r2_y_max)
        
        return not no_overlap
    
    def get_tiles_in_roi(self, roi_region: ROIRegion, tiles_data: List[TileMetadata],
                        grid_config: GridConfig, image_size: Tuple[int, int]) -> List[int]:
        """
        Find all tiles that overlap with a single ROI region.
        
        Args:
            roi_region: ROI region to check
            tiles_data: List of all tiles
            grid_config: Grid configuration
            image_size: (width, height) of image
            
        Returns:
            List of tile indices that overlap with ROI
        """
        roi_tiles = []
        
        img_width, img_height = image_size
        rows, cols = grid_config.rows, grid_config.cols
        overlap = grid_config.overlap / 100.0
        
        step_width = img_width / cols
        step_height = img_height / rows
        tile_width = step_width * (1 + overlap)
        tile_height = step_height * (1 + overlap)
        
        # ROI bounds
        roi_x_min = min(roi_region.start[0], roi_region.end[0])
        roi_x_max = max(roi_region.start[0], roi_region.end[0])
        roi_y_min = min(roi_region.start[1], roi_region.end[1])
        roi_y_max = max(roi_region.start[1], roi_region.end[1])
        roi_bounds = (roi_x_min, roi_y_min, roi_x_max, roi_y_max)
        
        # Check each tile
        for i, tile_data in enumerate(tiles_data):
            row, col = tile_data.row, tile_data.col
            
            # Calculate tile bounds
            tile_x_min = col * step_width
            tile_x_max = tile_x_min + tile_width
            tile_y_min = row * step_height
            tile_y_max = tile_y_min + tile_height
            tile_bounds = (tile_x_min, tile_y_min, tile_x_max, tile_y_max)
            
            if self.check_overlap(tile_bounds, roi_bounds):
                roi_tiles.append(i)
        
        return roi_tiles
    
    def get_tiles_in_all_rois(self, roi_regions: List[ROIRegion],
                              tiles_data: List[TileMetadata],
                              grid_config: GridConfig,
                              image_size: Tuple[int, int]) -> List[int]:
        """
        Find all tiles that overlap with ANY ROI region.
        
        Args:
            roi_regions: List of ROI regions
            tiles_data: List of all tiles
            grid_config: Grid configuration
            image_size: (width, height) of image
            
        Returns:
            Sorted list of unique tile indices
        """
        all_tiles = set()
        
        for roi_region in roi_regions:
            tiles_in_roi = self.get_tiles_in_roi(roi_region, tiles_data, 
                                                 grid_config, image_size)
            all_tiles.update(tiles_in_roi)
        
        return sorted(list(all_tiles))

