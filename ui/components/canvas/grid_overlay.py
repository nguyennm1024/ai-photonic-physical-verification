"""
Grid Overlay Mixin
==================

Mixin for drawing grid overlays on canvas.
"""


class GridOverlayMixin:
    """
    Mixin for grid overlay functionality.

    Provides methods to draw tile grid overlays on the canvas.
    Requires: self.ax (matplotlib axes)
    """

    def _draw_grid_overlay(self, image, grid_config):
        """
        Draw a semi-transparent grid overlay on the image.

        Args:
            image: PIL Image or numpy array
            grid_config: GridConfig with rows, cols, overlap
        """
        # Get image dimensions
        if hasattr(image, "shape"):
            height, width = image.shape[:2]
        else:
            width, height = image.size

        # Calculate tile size
        tile_width = width / grid_config.cols
        tile_height = height / grid_config.rows

        # Draw vertical lines (very subtle)
        for i in range(grid_config.cols + 1):
            x = i * tile_width
            self.ax.axvline(
                x=x, color="lightblue", linewidth=0.3, alpha=0.3, linestyle=":"
            )

        # Draw horizontal lines (very subtle)
        for i in range(grid_config.rows + 1):
            y = i * tile_height
            self.ax.axhline(
                y=y, color="lightblue", linewidth=0.3, alpha=0.3, linestyle=":"
            )

        # Add subtle text in corner
        self.ax.text(
            10,
            20,
            f"{grid_config.rows}×{grid_config.cols} grid",
            color="gray",
            fontsize=9,
            bbox=dict(
                boxstyle="round",
                facecolor="white",
                alpha=0.7,
                edgecolor="lightgray",
                linewidth=1,
            ),
        )
