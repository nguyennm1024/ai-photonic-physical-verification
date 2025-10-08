"""
Tile Generator Module
=====================

Generate tiles from SVG (virtual or physical) with on-demand caching.
"""

import os
import tempfile
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple
from PIL import Image
from ..app_state.state_manager import TileMetadata, GridConfig
from ..file_manager.svg_converter import SVGConverter
from .tile_cache import TileCache


class TileGenerator:
    """
    Generate tiles from SVG layouts.
    Supports both virtual tiles (on-demand) and physical tile files.
    """
    
    def __init__(self, svg_converter: SVGConverter, tile_cache: Optional[TileCache] = None):
        """
        Initialize tile generator.
        
        Args:
            svg_converter: SVG converter instance
            tile_cache: Optional tile cache (creates new if not provided)
        """
        self.svg_converter = svg_converter
        self.tile_cache = tile_cache if tile_cache else TileCache(max_size=50)
    
    def create_virtual_tiles(self, grid_config: GridConfig) -> List[TileMetadata]:
        """
        Create virtual tile metadata without generating physical files.
        
        Args:
            grid_config: Grid configuration
            
        Returns:
            List of TileMetadata objects
        """
        tiles_data = []
        rows, cols = grid_config.rows, grid_config.cols
        
        for row in range(rows):
            for col in range(cols):
                tile_data = TileMetadata(
                    filename=f"tile_{row:03d}_{col:03d}.png",
                    row=row,
                    col=col,
                    path=None,  # No physical path
                    virtual=True,
                    analyzed=False,
                    tile_type='virtual'
                )
                tiles_data.append(tile_data)
        
        print(f"📊 Created {len(tiles_data)} virtual tiles ({rows}×{cols})")
        return tiles_data
    
    def generate_tile_on_demand(self, svg_path: str, row: int, col: int,
                               grid_config: GridConfig) -> Optional[Image.Image]:
        """
        Generate a single tile on-demand and return PIL Image.
        Uses caching to avoid regeneration.
        
        Args:
            svg_path: Path to source SVG file
            row: Tile row index
            col: Tile column index
            grid_config: Grid configuration
            
        Returns:
            PIL Image or None if generation fails
        """
        # Check cache first
        cached_image = self.tile_cache.get(row, col)
        if cached_image:
            return cached_image
        
        try:
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
            resolution = grid_config.resolution
            
            step_width = svg_width / cols
            step_height = svg_height / rows
            tile_width = step_width * (1 + overlap)
            tile_height = step_height * (1 + overlap)
            
            # Calculate tile position
            x = svg_x + col * step_width
            y = svg_y + row * step_height
            
            print(f"🔍 Generating tile ({row}, {col})")
            print(f"   Tile position: x={x:.1f}, y={y:.1f}, size: {tile_width:.1f}×{tile_height:.1f}")
            
            # Create temporary SVG tile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as temp_svg:
                self._create_svg_tile(svg_path, temp_svg.name, x, y, tile_width, tile_height)
                temp_svg_path = temp_svg.name
            
            # Convert to PNG in memory
            tile_image = self._convert_svg_to_image(temp_svg_path, resolution)
            
            # Clean up temp file
            os.unlink(temp_svg_path)
            
            if tile_image:
                # Cache the tile
                self.tile_cache.put(row, col, tile_image)
                return tile_image
            
        except Exception as e:
            print(f"❌ Error generating tile ({row}, {col}): {e}")
            return None
        
        return None
    
    def _create_svg_tile(self, source_svg: str, dest_svg: str,
                        x: float, y: float, width: float, height: float):
        """
        Create SVG tile by setting viewBox to crop region.
        
        Args:
            source_svg: Path to source SVG
            dest_svg: Path where tile SVG will be saved
            x, y, width, height: Tile bounds in SVG coordinates
        """
        tree = ET.parse(source_svg)
        root = tree.getroot()
        
        # Set viewBox to crop the desired region
        root.set('viewBox', f"{x} {y} {width} {height}")
        root.set('width', str(width))
        root.set('height', str(height))
        
        # Write tile SVG
        tree.write(dest_svg, encoding='utf-8', xml_declaration=True)
    
    def _convert_svg_to_image(self, svg_path: str, resolution: int) -> Optional[Image.Image]:
        """
        Convert SVG to PIL Image and return image object.
        
        Args:
            svg_path: Path to SVG file
            resolution: Target resolution
            
        Returns:
            PIL Image or None
        """
        try:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_png:
                temp_png_path = temp_png.name
            
            # Use SVG converter
            success = self.svg_converter.svg_tile_to_png(svg_path, temp_png_path, resolution)
            
            if success and os.path.exists(temp_png_path):
                # Load image into memory
                image = Image.open(temp_png_path)
                image_copy = image.copy()  # Create copy to avoid file handle issues
                image.close()
                os.unlink(temp_png_path)
                return image_copy
            else:
                if os.path.exists(temp_png_path):
                    os.unlink(temp_png_path)
                return None
                
        except Exception as e:
            print(f"Error converting SVG to image: {e}")
            return None
    
    def clear_cache(self):
        """Clear the tile cache"""
        self.tile_cache.clear()

