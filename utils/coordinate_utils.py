"""
Coordinate Transformation Utilities
====================================

Transform coordinates between SVG space and image pixel space.
Critical for accurate tile navigation and ROI calculations.
"""

from typing import Tuple, Dict


class CoordinateTransformer:
    """
    Transform coordinates between different coordinate systems.
    
    SVG coordinate system: Uses viewBox coordinates (may have offset)
    Image pixel system: Display coordinates (0,0 at top-left)
    """
    
    @staticmethod
    def svg_to_pixel(svg_x: float, svg_y: float, svg_dims: Dict, 
                     image_size: Tuple[int, int]) -> Tuple[float, float]:
        """
        Convert SVG coordinates to image pixel coordinates.
        
        Args:
            svg_x: X coordinate in SVG space
            svg_y: Y coordinate in SVG space
            svg_dims: Dict with keys 'x', 'y', 'width', 'height' (viewBox)
            image_size: (width, height) of image in pixels
            
        Returns:
            (pixel_x, pixel_y) tuple
        """
        img_width, img_height = image_size
        svg_x_offset = svg_dims.get('x', 0)
        svg_y_offset = svg_dims.get('y', 0)
        svg_width = svg_dims['width']
        svg_height = svg_dims['height']
        
        # Transform from SVG space to pixel space
        relative_x = svg_x - svg_x_offset
        relative_y = svg_y - svg_y_offset
        
        pixel_x = relative_x * (img_width / svg_width)
        pixel_y = relative_y * (img_height / svg_height)
        
        return (pixel_x, pixel_y)
    
    @staticmethod
    def pixel_to_svg(pixel_x: float, pixel_y: float, svg_dims: Dict,
                     image_size: Tuple[int, int]) -> Tuple[float, float]:
        """
        Convert image pixel coordinates to SVG coordinates.
        
        Args:
            pixel_x: X coordinate in pixel space
            pixel_y: Y coordinate in pixel space
            svg_dims: Dict with keys 'x', 'y', 'width', 'height' (viewBox)
            image_size: (width, height) of image in pixels
            
        Returns:
            (svg_x, svg_y) tuple
        """
        img_width, img_height = image_size
        svg_x_offset = svg_dims.get('x', 0)
        svg_y_offset = svg_dims.get('y', 0)
        svg_width = svg_dims['width']
        svg_height = svg_dims['height']
        
        # Transform from pixel space to SVG space
        svg_x = svg_x_offset + pixel_x * (svg_width / img_width)
        svg_y = svg_y_offset + pixel_y * (svg_height / img_height)
        
        return (svg_x, svg_y)
    
    @staticmethod
    def tile_to_pixel_bounds(row: int, col: int, grid_config: 'GridConfig',
                             svg_dims: Dict, image_size: Tuple[int, int]) -> Tuple[float, float, float, float]:
        """
        Get tile bounds in pixel coordinates.
        
        Args:
            row: Tile row index
            col: Tile column index
            grid_config: Grid configuration object
            svg_dims: SVG dimensions dict
            image_size: (width, height) of image
            
        Returns:
            (x, y, width, height) in pixel coordinates
        """
        img_width, img_height = image_size
        svg_width = svg_dims['width']
        svg_height = svg_dims['height']
        
        rows = grid_config.rows
        cols = grid_config.cols
        overlap = grid_config.overlap / 100.0
        
        # Calculate in SVG space
        svg_step_width = svg_width / cols
        svg_step_height = svg_height / rows
        svg_tile_width = svg_step_width * (1 + overlap)
        svg_tile_height = svg_step_height * (1 + overlap)
        
        # Transform to pixel space
        step_width = svg_step_width * (img_width / svg_width)
        step_height = svg_step_height * (img_height / svg_height)
        tile_width = svg_tile_width * (img_width / svg_width)
        tile_height = svg_tile_height * (img_height / svg_height)
        
        x = col * step_width
        y = row * step_height
        
        return (x, y, tile_width, tile_height)

