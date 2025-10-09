"""
ROI Selector Mixin
==================

Mixin for ROI (Region of Interest) selection functionality.
"""

from matplotlib.patches import Rectangle
from typing import Callable, Optional, Tuple


class ROISelectorMixin:
    """
    Mixin for ROI selection functionality.

    Provides:
    - Interactive ROI drawing (click & drag)
    - Multiple ROI selection
    - ROI highlighting and deletion
    - Keyboard shortcuts (Delete key)

    Requires:
    - self.ax (matplotlib axes)
    - self.canvas (FigureCanvas)
    - self.coord_transformer (CoordinateTransformer)
    - self.grid_config (optional, for title updates)
    """

    def _init_roi_selector(self):
        """Initialize ROI selector state"""
        self.roi_selecting = False
        self.roi_start = None
        self.roi_temp_rect = None  # Temporary rectangle while dragging
        self.roi_rectangles = []  # List of permanent ROI rectangles
        self.selected_roi_rects = []  # List of selected ROI rectangles
        self.roi_callback: Optional[Callable[[Tuple[int, int, int, int]], None]] = None

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

        if hasattr(self, "grid_config") and self.grid_config:
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

    def _handle_roi_mouse_press(self, event):
        """
        Handle mouse press for ROI selection.

        Args:
            event: Mouse event

        Returns:
            True if handled, False otherwise
        """
        if not self.roi_selecting:
            return False

        if event.inaxes != self.ax:
            return True  # Consume event even if outside axes

        click_x, click_y = event.xdata, event.ydata

        # Check if clicking on an existing ROI rectangle (for selection)
        clicked_roi = self._find_roi_at_point(click_x, click_y)
        if clicked_roi is not None:
            print(f"🎯 Clicked on ROI: {clicked_roi}")
            # Toggle selection of this ROI
            self._toggle_roi_selection(clicked_roi, event)
            return True

        print(f"📭 Clicked on empty space - starting new ROI")

        # Clear all selections when clicking empty space (not on ROI)
        self._clear_all_selections()

        # Start drawing new ROI
        self.roi_start = (click_x, click_y)

        # Remove previous temporary rectangle if exists
        if self.roi_temp_rect:
            self.roi_temp_rect.remove()
            self.roi_temp_rect = None

        return True

    def _handle_roi_mouse_move(self, event):
        """
        Handle mouse move for ROI selection.

        Args:
            event: Mouse event

        Returns:
            True if handled, False otherwise
        """
        if not self.roi_selecting or not self.roi_start or event.inaxes != self.ax:
            return False

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

        return True

    def _handle_roi_mouse_release(self, event):
        """
        Handle mouse release for ROI selection.

        Args:
            event: Mouse event

        Returns:
            True if handled, False otherwise
        """
        if not self.roi_selecting or not self.roi_start or event.inaxes != self.ax:
            return False

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
            svg_coords = self.coord_transformer.transform_display_to_svg(
                (x1, y1, x2, y2)
            )
            print(f"🔄 ROI transform: Display ({x1},{y1},{x2},{y2}) → SVG {svg_coords}")
            self.roi_callback(svg_coords)

        # Reset start point (keep selecting mode active for multiple ROIs)
        self.roi_start = None

        return True

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

    def _handle_roi_key_press(self, event):
        """
        Handle keyboard events for ROI deletion.

        Args:
            event: Keyboard event

        Returns:
            True if handled, False otherwise
        """
        if event.key == "delete" or event.key == "backspace":
            # Delete all selected ROIs
            if self.selected_roi_rects:
                count = len(self.selected_roi_rects)
                print(f"🗑️  Deleting {count} selected ROI(s)")
                for roi_rect in self.selected_roi_rects[:]:  # Copy list
                    roi_rect.remove()
                    self.roi_rectangles.remove(roi_rect)
                self.selected_roi_rects.clear()
                self.canvas.draw()
                return True

        return False
