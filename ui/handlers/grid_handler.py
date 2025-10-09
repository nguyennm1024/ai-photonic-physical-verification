"""
Grid Handler Module
===================

Handles grid generation and tile configuration operations.
"""

import os
import tempfile
from PIL import Image
from .base_handler import BaseHandler


class GridHandler(BaseHandler):
    """
    Handler for grid operations.

    Responsibilities:
    - Generate virtual tile grids
    - Create tile metadata
    - Display layout with grid overlay
    """

    def handle_generate_grid(self, rows: int, cols: int, overlap: int):
        """
        Handle virtual grid generation.

        Args:
            rows: Number of rows
            cols: Number of columns
            overlap: Overlap in pixels
        """
        try:
            svg_path = self.state.get_svg_path()
            if not svg_path:
                self.show_error("Error", "Please load a GDS file first")
                return

            self._call_ui('update_status', f"Creating {rows}x{cols} virtual grid...")

            # Create virtual grid
            grid_config = self.state.create_grid_config(rows, cols, overlap)

            # Create virtual tiles metadata
            tiles_data = self.tile_gen.create_virtual_tiles(grid_config)
            self.state.set_tiles_data(tiles_data)

            # Load and display the full layout image with grid overlay
            try:
                # Convert SVG to PNG for display
                temp_png = tempfile.mktemp(suffix='.png')

                # Try using rsvg-convert or inkscape
                result = self.svg_converter.svg_to_png(svg_path, temp_png, resolution=2048)

                if result and os.path.exists(temp_png):
                    image = Image.open(temp_png)
                    # Display image with grid overlay and SVG dimensions
                    svg_dimensions = self.svg_parser.parse_dimensions(svg_path)
                    self._call_ui('display_image', image, grid_config, svg_dimensions)
                    os.unlink(temp_png)
                    print(f"✅ Layout displayed with {rows}x{cols} tile grid overlay")
                else:
                    print("⚠️  Could not display layout (install rsvg-convert or inkscape)")
            except Exception as e:
                print(f"⚠️  Could not display layout image: {e}")

            # Clear any previous tile status overlays
            self._call_ui('clear_tile_status')

            # Update UI
            self._call_ui('update_grid_info', f"Grid: {rows}x{cols} ({rows*cols} virtual tiles)")
            self._call_ui('update_status', f"✅ Virtual grid created: {rows}x{cols} - Draw ROI or process tiles")

        except Exception as e:
            self.show_error("Error", f"Failed to create grid: {str(e)}")
            self._call_ui('update_status', f"Error: {str(e)}")
