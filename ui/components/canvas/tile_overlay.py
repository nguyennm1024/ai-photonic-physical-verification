"""
Tile Overlay Mixin
==================

Mixin for tile status visualization and tile click handling.
"""

from matplotlib.patches import Rectangle
from typing import Callable, Optional


class TileOverlayMixin:
    """
    Mixin for tile overlay functionality.

    Provides:
    - Visual status overlays for tiles (green/red)
    - Tile click detection and callbacks

    Requires:
    - self.ax (matplotlib axes)
    - self.canvas (FigureCanvas)
    - self.grid_config (GridConfig)
    - self.current_image (PIL Image)
    - self.coord_transformer (CoordinateTransformer)
    """

    def _init_tile_overlay(self):
        """Initialize tile overlay state"""
        self.tile_click_callback: Optional[Callable[[int, int], None]] = None
        self.tile_status_rects = {}  # Dictionary: (row, col) -> Rectangle patch
        self.tiles_analysis_status = (
            {}
        )  # Dictionary: (row, col) -> {'classification': str, 'analyzed': bool}
        self.focused_tile_rect = None  # Purple border for currently focused tile
        self.focused_tile_coords = None  # (row, col) of focused tile

    def bind_tile_click(self, callback: Callable[[int, int], None]):
        """
        Bind callback for tile clicks.

        Args:
            callback: Function to call with (row, col) when tile is clicked
        """
        self.tile_click_callback = callback

    def _detect_tile_click(self, x, y):
        """
        Detect if click is on a tile and return tile coordinates.

        Args:
            x, y: Click coordinates in display space

        Returns:
            (row, col) if click is on a tile, None otherwise
        """
        if not self.grid_config or not self.current_image:
            return None

        # Get image dimensions
        if hasattr(self.current_image, "shape"):
            height, width = self.current_image.shape[:2]
        else:
            width, height = self.current_image.size

        # Calculate tile size
        tile_width = width / self.grid_config.cols
        tile_height = height / self.grid_config.rows

        # Determine which tile was clicked
        col = int(x // tile_width)
        row = int(y // tile_height)

        # Validate bounds
        if 0 <= row < self.grid_config.rows and 0 <= col < self.grid_config.cols:
            return (row, col)

        return None

    def update_tile_status(
        self, row: int, col: int, classification: str, analyzed: bool = True
    ):
        """
        Update visual status of a tile on the layout.

        Args:
            row: Tile row
            col: Tile column
            classification: 'continuity', 'discontinuity', or 'no_waveguide'
            analyzed: Whether tile has been analyzed
        """
        if (
            not self.grid_config
            or not self.current_image
            or not self.coord_transformer.svg_dimensions
        ):
            print(
                f"⚠️ Cannot update tile status: grid={self.grid_config is not None}, "
                f"image={self.current_image is not None}, "
                f"svg_dims={self.coord_transformer.svg_dimensions is not None}"
            )
            return

        # Store status
        self.tiles_analysis_status[(row, col)] = {
            "classification": classification,
            "analyzed": analyzed,
        }

        # Get display image dimensions
        if hasattr(self.current_image, "shape"):
            # Numpy array: shape is (height, width, channels)
            display_height, display_width = self.current_image.shape[:2]
        else:
            # PIL Image: size is (width, height)
            display_width, display_height = self.current_image.size

        # Get SVG dimensions
        svg_width = self.coord_transformer.svg_dimensions["width"]
        svg_height = self.coord_transformer.svg_dimensions["height"]

        # Calculate tile bounds in SVG space
        svg_tile_width = svg_width / self.grid_config.cols
        svg_tile_height = svg_height / self.grid_config.rows
        svg_x = col * svg_tile_width
        svg_y = row * svg_tile_height

        # Transform to display space
        scale_x = display_width / svg_width
        scale_y = display_height / svg_height
        x = svg_x * scale_x
        y = svg_y * scale_y
        tile_width = svg_tile_width * scale_x
        tile_height = svg_tile_height * scale_y

        # Remove old rectangle if exists
        if (row, col) in self.tile_status_rects:
            self.tile_status_rects[(row, col)].remove()

        # Determine color based on classification
        # Layout view: green for continuity/no_waveguide, red for discontinuity
        classification_lower = classification.lower()
        if "discontinuity" in classification_lower:
            color = "red"
            alpha = 0.3
        else:  # continuity, continuous, or no_waveguide - all green
            color = "green"
            alpha = 0.25

        # Draw status rectangle with border
        status_rect = Rectangle(
            (x, y),
            tile_width,
            tile_height,
            fill=True,
            facecolor=color,
            edgecolor=color,
            linewidth=2,
            alpha=alpha,
        )
        self.ax.add_patch(status_rect)
        self.tile_status_rects[(row, col)] = status_rect

        # Redraw
        self.canvas.draw()
        print(
            f"🎨 Tile ({row},{col}) highlighted: {color} ({classification}) at position ({x:.0f},{y:.0f})"
        )

    def update_focused_tile(self, row: int, col: int):
        """
        Highlight the currently focused tile with a purple border.

        Args:
            row: Tile row
            col: Tile column
        """
        if (
            not self.grid_config
            or not self.current_image
            or not self.coord_transformer.svg_dimensions
        ):
            print(f"⚠️ Cannot update focused tile: missing grid/image/dimensions")
            return

        # Remove old focus rectangle
        if self.focused_tile_rect:
            self.focused_tile_rect.remove()
            self.focused_tile_rect = None

        # Store focused tile coordinates
        self.focused_tile_coords = (row, col)

        # Get display image dimensions
        if hasattr(self.current_image, "shape"):
            display_height, display_width = self.current_image.shape[:2]
        else:
            display_width, display_height = self.current_image.size

        # Get SVG dimensions
        svg_width = self.coord_transformer.svg_dimensions["width"]
        svg_height = self.coord_transformer.svg_dimensions["height"]

        # Calculate tile bounds in SVG space
        svg_tile_width = svg_width / self.grid_config.cols
        svg_tile_height = svg_height / self.grid_config.rows
        svg_x = col * svg_tile_width
        svg_y = row * svg_tile_height

        # Transform to display space
        scale_x = display_width / svg_width
        scale_y = display_height / svg_height
        x = svg_x * scale_x
        y = svg_y * scale_y
        tile_width = svg_tile_width * scale_x
        tile_height = svg_tile_height * scale_y

        # Draw purple focus border (unfilled, thick)
        focus_rect = Rectangle(
            (x, y),
            tile_width,
            tile_height,
            fill=False,
            edgecolor="purple",
            linewidth=4,
            linestyle="-",
            alpha=1.0,
            zorder=10,  # Draw on top of other overlays
        )
        self.ax.add_patch(focus_rect)
        self.focused_tile_rect = focus_rect

        # Redraw
        self.canvas.draw()
        print(f"🟣 Focused tile ({row},{col}) highlighted with purple border")

    def clear_tile_status(self):
        """Clear all tile status overlays"""
        for rect in self.tile_status_rects.values():
            rect.remove()
        self.tile_status_rects.clear()
        self.tiles_analysis_status.clear()

        # Also clear focus rectangle
        if self.focused_tile_rect:
            self.focused_tile_rect.remove()
            self.focused_tile_rect = None
            self.focused_tile_coords = None

        if hasattr(self, "canvas"):
            self.canvas.draw()
