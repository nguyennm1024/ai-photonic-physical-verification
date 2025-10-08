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
        Check if two rectangles overlap (ANY overlap, including partial).

        This detects:
        - Full overlap (one rectangle inside another)
        - Partial overlap (rectangles intersect)
        - Edge touching is NOT considered overlap

        Args:
            rect1_bounds: (x_min, y_min, x_max, y_max)
            rect2_bounds: (x_min, y_min, x_max, y_max)

        Returns:
            True if rectangles overlap (fully or partially)
        """
        r1_x_min, r1_y_min, r1_x_max, r1_y_max = rect1_bounds
        r2_x_min, r2_y_min, r2_x_max, r2_y_max = rect2_bounds

        # Check if rectangles do NOT overlap, then invert
        # Rectangles don't overlap if one is completely to the side of the other
        no_overlap = (r1_x_max <= r2_x_min or  # rect1 is completely left of rect2
                     r1_x_min >= r2_x_max or   # rect1 is completely right of rect2
                     r1_y_max <= r2_y_min or   # rect1 is completely above rect2
                     r1_y_min >= r2_y_max)     # rect1 is completely below rect2

        return not no_overlap
    
    def get_tiles_in_roi(self, roi_region: ROIRegion, tiles_data: List[TileMetadata],
                        grid_config: GridConfig, image_size: Tuple[int, int]) -> List[int]:
        """
        Find all tiles that overlap with a single ROI region.

        Includes tiles with ANY overlap (partial or full) with the ROI.

        Args:
            roi_region: ROI region to check
            tiles_data: List of all tiles
            grid_config: Grid configuration
            image_size: (width, height) of image

        Returns:
            List of tile indices that overlap with ROI (includes partial overlaps)
        """
        roi_tiles = []

        img_width, img_height = image_size
        rows, cols = grid_config.rows, grid_config.cols
        overlap = grid_config.overlap / 100.0

        print(f"📐 Image dimensions: {img_width}×{img_height} (W×H)")
        print(f"📏 Grid config: {rows} rows × {cols} cols")

        step_width = img_width / cols
        step_height = img_height / rows
        tile_width = step_width * (1 + overlap)
        tile_height = step_height * (1 + overlap)

        print(f"📦 Tile size: {tile_width:.1f}×{tile_height:.1f} (W×H)")
        print(f"📍 Step size: {step_width:.1f}×{step_height:.1f} (W×H)")

        # ROI bounds
        roi_x_min = min(roi_region.start[0], roi_region.end[0])
        roi_x_max = max(roi_region.start[0], roi_region.end[0])
        roi_y_min = min(roi_region.start[1], roi_region.end[1])
        roi_y_max = max(roi_region.start[1], roi_region.end[1])
        roi_bounds = (roi_x_min, roi_y_min, roi_x_max, roi_y_max)

        print(f"🔍 ROI bounds: ({roi_x_min:.1f}, {roi_y_min:.1f}) to ({roi_x_max:.1f}, {roi_y_max:.1f})")
        print(f"   ROI width: {roi_x_max - roi_x_min:.1f}, height: {roi_y_max - roi_y_min:.1f}")

        # Check each tile for ANY overlap (partial or full)
        for i, tile_data in enumerate(tiles_data):
            row, col = tile_data.row, tile_data.col

            # Calculate tile bounds (includes tile overlap if configured)
            tile_x_min = col * step_width
            tile_x_max = tile_x_min + tile_width
            tile_y_min = row * step_height
            tile_y_max = tile_y_min + tile_height
            tile_bounds = (tile_x_min, tile_y_min, tile_x_max, tile_y_max)

            # Check for ANY overlap (partial or full)
            if self.check_overlap(tile_bounds, roi_bounds):
                roi_tiles.append(i)
                print(f"  ✅ Tile ({row},{col}) index {i} overlaps ROI - bounds: ({tile_x_min:.1f}, {tile_y_min:.1f}) to ({tile_x_max:.1f}, {tile_y_max:.1f})")

        print(f"📊 Total tiles overlapping with ROI: {len(roi_tiles)}")
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

