"""
Image Canvas Component
======================

Matplotlib-based canvas for displaying layout images with ROI selection.
"""

import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from tkinter import ttk
from typing import Callable, Optional, Tuple


class ImageCanvas(ttk.Frame):
    """
    Image canvas - Matplotlib canvas for image display and ROI selection.

    Features:
    - Display layout images
    - Interactive ROI selection (click & drag)
    - Zoom/pan controls
    - ROI visualization
    """

    def __init__(self, parent, **kwargs):
        """
        Initialize image canvas.

        Args:
            parent: Parent tkinter widget
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)

        # ROI selection state
        self.roi_selecting = False
        self.roi_start = None
        self.roi_temp_rect = None  # Temporary rectangle while dragging
        self.roi_rectangles = []  # List of permanent ROI rectangles
        self.selected_roi_rects = (
            []
        )  # List of selected ROI rectangles for multiple selection
        self.roi_callback: Optional[Callable[[Tuple[int, int, int, int]], None]] = None

        # Tile selection state
        self.tile_click_callback: Optional[
            Callable[[int, int], None]
        ] = None  # (row, col)
        self.grid_config = None  # Store grid config for tile selection

        # Tile analysis status overlay
        self.tile_status_rects = {}  # Dictionary: (row, col) -> Rectangle patch
        self.tiles_analysis_status = (
            {}
        )  # Dictionary: (row, col) -> {'classification': str, 'analyzed': bool}

        # Current image
        self.current_image = None
        self.svg_dimensions = (
            None  # Original SVG dimensions for coordinate transformation
        )

        # Setup matplotlib
        self._setup_canvas()

    def _setup_canvas(self):
        """Create matplotlib figure and canvas"""
        # Defer importing TkAgg backend until runtime so module import doesn't
        # immediately require a working Tcl/Tk installation.
        try:
            from matplotlib.backends.backend_tkagg import (
                FigureCanvasTkAgg,  # type: ignore
            )
        except Exception as e:
            raise RuntimeError(
                "Matplotlib TkAgg backend could not be loaded. This application requires Tcl/Tk.\n"
                "On macOS with Homebrew:\n"
                "  brew install tcl-tk\n"
                "Then ensure environment variables are set before running:\n"
                "  export TCL_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tcl9.0:/opt/homebrew/opt/tcl-tk/lib/tcl8.6\n"
                "  export TK_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tk9.0:/opt/homebrew/opt/tcl-tk/lib/tk8.6\n"
                "  export PATH=/opt/homebrew/opt/tcl-tk/bin:$PATH\n"
                "If using uv-managed Python, upgrade it: uv python upgrade --reinstall\n"
                "You can test Tk availability with: python3 -m tkinter"
            ) from e
        # Create figure with white background - maximize space usage
        self.figure = Figure(figsize=(10, 10), dpi=100, facecolor="white")
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Layout View", fontsize=12, fontweight="bold")
        self.ax.set_facecolor("white")
        self.ax.axis("off")

        # Adjust subplot to use maximum space (reduce margins)
        self.figure.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.02)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()

        # Canvas widget (NO toolbar - cleaner interface)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Make figure responsive to window resize
        def on_resize(event):
            if event.width > 1 and event.height > 1:
                # Update figure size based on widget size
                width_inches = event.width / self.figure.dpi
                height_inches = event.height / self.figure.dpi
                self.figure.set_size_inches(width_inches, height_inches, forward=False)
                self.canvas.draw_idle()

        canvas_widget.bind("<Configure>", on_resize)

        # Bind mouse events for ROI selection and tile click
        self.canvas.mpl_connect("button_press_event", self._on_mouse_press)
        self.canvas.mpl_connect("button_release_event", self._on_mouse_release)
        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)

        # Bind keyboard events for ROI deletion
        self.canvas.mpl_connect("key_press_event", self._on_key_press)

        # Test: Add a simple click handler to verify events work
        print("🔧 Mouse events bound to canvas")

    def display_image(self, image, grid_config=None, svg_dimensions=None):
        """
        Display an image on the canvas.

        Args:
            image: PIL Image or numpy array
            grid_config: Optional GridConfig to overlay tile grid
            svg_dimensions: Original SVG dimensions dict with 'width' and 'height'
        """
        self.current_image = image
        self.grid_config = grid_config  # Store for tile selection
        if svg_dimensions:
            self.svg_dimensions = svg_dimensions
            print(
                f"📐 Stored SVG dimensions: {svg_dimensions['width']}×{svg_dimensions['height']}"
            )

        self.ax.clear()
        self.ax.set_facecolor("white")
        self.ax.imshow(image)
        self.ax.axis("off")

        # Draw grid overlay if provided
        if grid_config:
            self._draw_grid_overlay(image, grid_config)
            self.ax.set_title(
                f"Layout View - {grid_config.rows}x{grid_config.cols} Grid - Click tile to view",
                fontsize=12,
                fontweight="bold",
            )
        else:
            self.ax.set_title("Layout View", fontsize=12, fontweight="bold")

        self.canvas.draw()

    def _draw_grid_overlay(self, image, grid_config):
        """
        Draw a semi-transparent grid overlay on the image.

        Args:
            image: PIL Image or numpy array
            grid_config: GridConfig with rows, cols, overlap
        """
        import numpy as np

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

    def clear_image(self):
        """Clear the displayed image"""
        self.ax.clear()
        self.ax.axis("off")
        self.ax.set_title("Layout View")
        self.canvas.draw()
        self.current_image = None

    def enable_roi_selection(
        self, callback: Callable[[Tuple[int, int, int, int]], None]
    ):
        """
        Enable ROI selection mode.

        Args:
            callback: Function to call with (x1, y1, x2, y2) when ROI is selected
        """
        self.roi_selecting = True
        self.roi_callback = callback
        self.ax.set_title(
            "ROI Mode - Draw rectangles | Click ROI to select | Click empty space to clear | Delete key to remove",
            fontsize=11,
            fontweight="bold",
        )
        self.canvas.draw()

    def disable_roi_selection(self):
        """Disable ROI selection mode (keeps drawn ROIs visible)"""
        self.roi_selecting = False
        self.roi_callback = None

        # Remove temporary rectangle if any
        if self.roi_temp_rect:
            self.roi_temp_rect.remove()
            self.roi_temp_rect = None

        if self.grid_config:
            self.ax.set_title(
                f"Layout View - {self.grid_config.rows}x{self.grid_config.cols} Grid - Click tile to view",
                fontsize=12,
                fontweight="bold",
            )
        else:
            self.ax.set_title("Layout View", fontsize=12, fontweight="bold")
        self.canvas.draw()

    def clear_all_rois(self):
        """Clear all ROI rectangles from canvas"""
        for roi_rect in self.roi_rectangles:
            roi_rect.remove()
        self.roi_rectangles.clear()
        self.selected_roi_rects.clear()

        if self.roi_temp_rect:
            self.roi_temp_rect.remove()
            self.roi_temp_rect = None

        self.canvas.draw()

    def bind_tile_click(self, callback: Callable[[int, int], None]):
        """
        Bind callback for tile clicks.

        Args:
            callback: Function to call with (row, col) when tile is clicked
        """
        self.tile_click_callback = callback

    def _on_mouse_press(self, event):
        """Handle mouse press for ROI selection or tile click"""
        print("🖱️  MOUSE PRESS EVENT TRIGGERED!")

        if event.inaxes != self.ax:
            print("❌ Click outside axes")
            return

        click_x, click_y = event.xdata, event.ydata
        print(f"🖱️  Mouse press at ({click_x:.1f}, {click_y:.1f})")

        # Handle ROI drawing mode (start drawing new ROI)
        if self.roi_selecting:
            # Check if clicking on an existing ROI rectangle (for selection) - ONLY in ROI mode
            clicked_roi = self._find_roi_at_point(click_x, click_y)
            if clicked_roi is not None:
                print(f"🎯 Clicked on ROI: {clicked_roi}")
                # Toggle selection of this ROI
                self._toggle_roi_selection(clicked_roi, event)
                return
            else:
                print(f"📭 Clicked on empty space - starting new ROI")

            # Clear all selections when clicking empty space (not on ROI)
            self._clear_all_selections()

            # Start drawing new ROI
            self.roi_start = (click_x, click_y)

            # Remove previous temporary rectangle if exists
            if self.roi_temp_rect:
                self.roi_temp_rect.remove()
                self.roi_temp_rect = None
            return

        # When NOT in ROI selection mode, always handle as tile click
        # ROI boxes are NOT selectable - click goes through to tiles
        if self.grid_config and self.tile_click_callback:
            # Calculate which tile was clicked
            if hasattr(self.current_image, "shape"):
                height, width = self.current_image.shape[:2]
            else:
                width, height = self.current_image.size

            tile_width = width / self.grid_config.cols
            tile_height = height / self.grid_config.rows

            col = int(click_x / tile_width)
            row = int(click_y / tile_height)

            # Ensure within bounds
            col = max(0, min(col, self.grid_config.cols - 1))
            row = max(0, min(row, self.grid_config.rows - 1))

            print(f"🖱️  Tile click detected: row={row}, col={col}")

            # Call the callback with row, col
            self.tile_click_callback(row, col)

    def _on_mouse_move(self, event):
        """Handle mouse move for ROI selection"""
        if not self.roi_selecting or not self.roi_start or event.inaxes != self.ax:
            return

        # Update temporary rectangle
        x1, y1 = self.roi_start
        x2, y2 = event.xdata, event.ydata

        # Remove old temporary rectangle
        if self.roi_temp_rect:
            self.roi_temp_rect.remove()

        # Draw new temporary rectangle
        width = x2 - x1
        height = y2 - y1
        self.roi_temp_rect = Rectangle(
            (x1, y1),
            width,
            height,
            fill=False,
            edgecolor="blue",
            linewidth=2,
            linestyle="--",
            alpha=0.7,
        )
        self.ax.add_patch(self.roi_temp_rect)
        self.canvas.draw()

    def _on_mouse_release(self, event):
        """Handle mouse release for ROI selection"""
        if not self.roi_selecting or not self.roi_start or event.inaxes != self.ax:
            return

        # Get coordinates
        x1, y1 = self.roi_start
        x2, y2 = event.xdata, event.ydata

        # Ensure x1 < x2 and y1 < y2
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])

        # Convert to integers
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        # Remove temporary rectangle
        if self.roi_temp_rect:
            self.roi_temp_rect.remove()
            self.roi_temp_rect = None

        # Create permanent ROI rectangle (blue to avoid confusion with red discontinuity tiles)
        width = x2 - x1
        height = y2 - y1
        roi_rect = Rectangle(
            (x1, y1),
            width,
            height,
            fill=False,
            edgecolor="blue",
            linewidth=2,
            linestyle="-",
            alpha=1.0,
        )
        self.ax.add_patch(roi_rect)
        self.roi_rectangles.append(roi_rect)
        self.canvas.draw()

        # Call callback with transformed coordinates (display → SVG)
        if self.roi_callback:
            # Transform from display space to SVG space
            svg_coords = self._transform_display_to_svg((x1, y1, x2, y2))
            print(f"🔄 ROI transform: Display ({x1},{y1},{x2},{y2}) → SVG {svg_coords}")
            self.roi_callback(svg_coords)

        # Reset start point (keep selecting mode active for multiple ROIs)
        self.roi_start = None

    def draw_roi_rectangle(
        self, x1: int, y1: int, x2: int, y2: int, color: str = "red"
    ):
        """
        Draw an ROI rectangle on the canvas (adds to existing ROIs).

        Args:
            x1, y1: Top-left corner
            x2, y2: Bottom-right corner
            color: Rectangle color
        """
        # Draw new rectangle
        width = x2 - x1
        height = y2 - y1
        roi_rect = Rectangle(
            (x1, y1),
            width,
            height,
            fill=False,
            edgecolor=color,
            linewidth=2,
            linestyle="-",
        )
        self.ax.add_patch(roi_rect)
        self.roi_rectangles.append(roi_rect)
        self.canvas.draw()

    def clear_roi_rectangle(self):
        """Clear all ROI rectangles from canvas (alias for clear_all_rois)"""
        self.clear_all_rois()

    def update_tile_status(
        self, row: int, col: int, classification: str, analyzed: bool = True
    ):
        """
        Update visual status of a tile on the layout.

        Args:
            row: Tile row
            col: Tile column
            classification: 'continuity' or 'discontinuity'
            analyzed: Whether tile has been analyzed
        """
        if not self.grid_config or not self.current_image or not self.svg_dimensions:
            print(
                f"⚠️ Cannot update tile status: grid={self.grid_config is not None}, image={self.current_image is not None}, svg_dims={self.svg_dimensions is not None}"
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
        svg_width = self.svg_dimensions["width"]
        svg_height = self.svg_dimensions["height"]

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
        if "discontinuity" in classification.lower():
            color = "red"
            alpha = 0.3
        else:
            color = "green"
            alpha = 0.25

        # Draw status rectangle with border
        from matplotlib.patches import Rectangle

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

    def clear_tile_status(self):
        """Clear all tile status overlays"""
        for rect in self.tile_status_rects.values():
            rect.remove()
        self.tile_status_rects.clear()
        self.tiles_analysis_status.clear()
        self.canvas.draw()

    def _transform_display_to_svg(self, display_coords):
        """
        Transform coordinates from display image space to original SVG space.

        Args:
            display_coords: (x1, y1, x2, y2) in display image coordinates

        Returns:
            (x1, y1, x2, y2) in SVG coordinates
        """
        if not self.svg_dimensions or not self.current_image:
            print("⚠️ Cannot transform - missing SVG dimensions or image")
            return display_coords

        # Get display image size
        if hasattr(self.current_image, "shape"):
            display_height, display_width = self.current_image.shape[:2]
        else:
            display_width, display_height = self.current_image.size

        # Get SVG size
        svg_width = self.svg_dimensions["width"]
        svg_height = self.svg_dimensions["height"]

        # Calculate scale factors
        scale_x = svg_width / display_width
        scale_y = svg_height / display_height

        print(
            f"🔄 Transform: Display {display_width}×{display_height} → SVG {svg_width}×{svg_height}"
        )
        print(f"   Scale factors: x={scale_x:.3f}, y={scale_y:.3f}")

        # Transform coordinates
        x1, y1, x2, y2 = display_coords
        svg_x1 = x1 * scale_x
        svg_y1 = y1 * scale_y
        svg_x2 = x2 * scale_x
        svg_y2 = y2 * scale_y

        return (svg_x1, svg_y1, svg_x2, svg_y2)

    def _transform_svg_to_display(self, svg_coords):
        """
        Transform coordinates from SVG space to display image space.

        Args:
            svg_coords: (x1, y1, x2, y2) in SVG coordinates

        Returns:
            (x1, y1, x2, y2) in display image coordinates
        """
        if not self.svg_dimensions or not self.current_image:
            return svg_coords

        # Get display image size
        if hasattr(self.current_image, "shape"):
            display_height, display_width = self.current_image.shape[:2]
        else:
            display_width, display_height = self.current_image.size

        # Get SVG size
        svg_width = self.svg_dimensions["width"]
        svg_height = self.svg_dimensions["height"]

        # Calculate scale factors
        scale_x = display_width / svg_width
        scale_y = display_height / svg_height

        # Transform coordinates
        x1, y1, x2, y2 = svg_coords
        display_x1 = x1 * scale_x
        display_y1 = y1 * scale_y
        display_x2 = x2 * scale_x
        display_y2 = y2 * scale_y

        return (display_x1, display_y1, display_x2, display_y2)

    def refresh(self):
        """Refresh the canvas"""
        self.canvas.draw()

    def _find_roi_at_point(self, x, y):
        """
        Find ROI rectangle at the given point.

        Args:
            x, y: Point coordinates

        Returns:
            Rectangle object if found, None otherwise
        """
        print(
            f"🔍 Checking {len(self.roi_rectangles)} ROIs for point ({x:.1f}, {y:.1f})"
        )

        for i, roi_rect in enumerate(self.roi_rectangles):
            # Get rectangle bounds
            rect_x = roi_rect.get_x()
            rect_y = roi_rect.get_y()
            rect_width = roi_rect.get_width()
            rect_height = roi_rect.get_height()

            print(
                f"   ROI {i}: x={rect_x:.1f}, y={rect_y:.1f}, w={rect_width:.1f}, h={rect_height:.1f}"
            )

            # Check if point is inside rectangle
            if (
                rect_x <= x <= rect_x + rect_width
                and rect_y <= y <= rect_y + rect_height
            ):
                print(f"   ✅ Point is inside ROI {i}")
                return roi_rect
            else:
                print(f"   ❌ Point is outside ROI {i}")

        print(f"   📭 Point not found in any ROI")
        return None

    def _toggle_roi_selection(self, roi_rect, event):
        """
        Toggle selection of an ROI rectangle.
        Simple approach: Click ROI to add to selection, click empty space to clear all.

        Args:
            roi_rect: Rectangle object to toggle
            event: Mouse event
        """
        print(f"🔍 ROI clicked: {roi_rect}")

        if roi_rect in self.selected_roi_rects:
            # Deselect this ROI
            self._deselect_single_roi(roi_rect)
            print(f"❌ ROI deselected")
        else:
            # Add this ROI to selection (don't clear others)
            self._select_single_roi(roi_rect)
            print(f"✅ ROI selected ({len(self.selected_roi_rects)} total)")

    def _select_single_roi(self, roi_rect):
        """Select a single ROI rectangle (highlight it)."""
        if roi_rect not in self.selected_roi_rects:
            self.selected_roi_rects.append(roi_rect)
            roi_rect.set_edgecolor("yellow")
            roi_rect.set_linewidth(3)
            self.canvas.draw()

    def _deselect_single_roi(self, roi_rect):
        """Deselect a single ROI rectangle."""
        if roi_rect in self.selected_roi_rects:
            self.selected_roi_rects.remove(roi_rect)
            roi_rect.set_edgecolor("blue")  # Blue for unselected ROI
            roi_rect.set_linewidth(2)
            self.canvas.draw()

    def _clear_all_selections(self):
        """Clear all ROI selections."""
        for roi_rect in self.selected_roi_rects:
            roi_rect.set_edgecolor("blue")  # Blue for unselected ROI
            roi_rect.set_linewidth(2)
        self.selected_roi_rects.clear()
        self.canvas.draw()

    def _on_key_press(self, event):
        """
        Handle keyboard events.

        Args:
            event: Keyboard event
        """
        if event.key == "delete" or event.key == "backspace":
            # Delete all selected ROIs
            if self.selected_roi_rects:
                count = len(self.selected_roi_rects)
                print(f"🗑️  Deleting {count} selected ROI(s)")
                for roi_rect in self.selected_roi_rects[
                    :
                ]:  # Copy list to avoid modification during iteration
                    roi_rect.remove()
                    self.roi_rectangles.remove(roi_rect)
                self.selected_roi_rects.clear()
                self.canvas.draw()
                print(f"✅ {count} ROI(s) deleted")
