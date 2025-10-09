"""
File Handler Module
===================

Handles GDS file loading and SVG conversion operations.
"""

from pathlib import Path
from .base_handler import BaseHandler


class FileHandler(BaseHandler):
    """
    Handler for file operations.

    Responsibilities:
    - Load GDS files
    - Convert GDS to SVG
    - Parse SVG dimensions
    - Update state with file paths
    """

    def handle_load_gds(self, file_path: str):
        """
        Handle GDS file loading.

        Args:
            file_path: Path to GDS file
        """
        try:
            # Update UI
            self._call_ui('update_status', "Loading GDS file...")
            self._call_ui('update_file_info', file_path)

            # Load GDS
            gds_lib = self.gds_loader.load_gds(file_path)

            # Update state
            self.state.set_gds_path(file_path)

            # Clear previous state
            self.state.reset()
            self.state.set_gds_path(file_path)  # Re-set after reset

            # Auto-generate SVG
            self._call_ui('update_status', "Converting to SVG...")
            self.handle_generate_svg(gds_lib, file_path)

        except Exception as e:
            self.show_error("Error", f"Failed to load GDS: {str(e)}")
            self._call_ui('update_status', f"Error: {str(e)}")

    def handle_generate_svg(self, gds_lib, gds_path: str):
        """
        Handle SVG generation from GDS.

        Args:
            gds_lib: GDS library object
            gds_path: Path to GDS file
        """
        try:
            # Generate SVG
            svg_path = self.svg_converter.convert_gds_to_svg(
                gds_lib,
                gds_path,
                output_dir="./"
            )

            # Update state
            self.state.set_svg_path(svg_path)

            # Parse dimensions
            dimensions = self.svg_parser.parse_dimensions(svg_path)

            # Update UI
            self._call_ui('update_status', f"✅ SVG ready: {Path(svg_path).name}")

            # Load full SVG image for display (optional - may need rsvg-convert)
            try:
                # For now, just show success message
                # Loading full SVG would require SVG to PNG conversion
                pass
            except Exception as e:
                print(f"Warning: Could not load SVG for display: {e}")

        except Exception as e:
            self.show_error("Error", f"Failed to generate SVG: {str(e)}")
            self._call_ui('update_status', f"Error: {str(e)}")
