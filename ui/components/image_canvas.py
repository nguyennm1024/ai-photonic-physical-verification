"""
Image Canvas Component
======================

Matplotlib-based canvas for displaying layout images with ROI selection.
"""

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Rectangle
from typing import Callable, Optional, Tuple
import matplotlib.pyplot as plt


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
        self.selected_roi_rects = []  # List of selected ROI rectangles for multiple selection
        self.roi_callback: Optional[Callable[[Tuple[int, int, int, int]], None]] = None
        
        # Tile selection state
        self.tile_click_callback: Optional[Callable[[int, int], None]] = None  # (row, col)
        self.grid_config = None  # Store grid config for tile selection
        
        # Current image
        self.current_image = None
        
        # Setup matplotlib
        self._setup_canvas()
    
    def _setup_canvas(self):
        """Create matplotlib figure and canvas"""
        # Create figure with white background
        self.figure = Figure(figsize=(8, 8), dpi=100, facecolor='white')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Layout View", fontsize=12, fontweight='bold')
        self.ax.set_facecolor('white')
        self.ax.axis('off')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        
        # Canvas widget (NO toolbar - cleaner interface)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Bind mouse events for ROI selection and tile click
        self.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self._on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
        
        # Bind keyboard events for ROI deletion
        self.canvas.mpl_connect('key_press_event', self._on_key_press)
    
    def display_image(self, image, grid_config=None):
        """
        Display an image on the canvas.
        
        Args:
            image: PIL Image or numpy array
            grid_config: Optional GridConfig to overlay tile grid
        """
        self.current_image = image
        self.grid_config = grid_config  # Store for tile selection
        
        self.ax.clear()
        self.ax.set_facecolor('white')
        self.ax.imshow(image)
        self.ax.axis('off')
        
        # Draw grid overlay if provided
        if grid_config:
            self._draw_grid_overlay(image, grid_config)
            self.ax.set_title(f"Layout View - {grid_config.rows}x{grid_config.cols} Grid - Click tile to view", 
                            fontsize=12, fontweight='bold')
        else:
            self.ax.set_title("Layout View", fontsize=12, fontweight='bold')
        
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
        if hasattr(image, 'shape'):
            height, width = image.shape[:2]
        else:
            width, height = image.size
        
        # Calculate tile size
        tile_width = width / grid_config.cols
        tile_height = height / grid_config.rows
        
        # Draw vertical lines (very subtle)
        for i in range(grid_config.cols + 1):
            x = i * tile_width
            self.ax.axvline(x=x, color='lightblue', linewidth=0.3, alpha=0.3, linestyle=':')
        
        # Draw horizontal lines (very subtle)
        for i in range(grid_config.rows + 1):
            y = i * tile_height
            self.ax.axhline(y=y, color='lightblue', linewidth=0.3, alpha=0.3, linestyle=':')
        
        # Add subtle text in corner
        self.ax.text(
            10, 20,
            f"{grid_config.rows}×{grid_config.cols} grid",
            color='gray',
            fontsize=9,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.7, edgecolor='lightgray', linewidth=1)
        )
    
    def clear_image(self):
        """Clear the displayed image"""
        self.ax.clear()
        self.ax.axis('off')
        self.ax.set_title("Layout View")
        self.canvas.draw()
        self.current_image = None
    
    def enable_roi_selection(self, callback: Callable[[Tuple[int, int, int, int]], None]):
        """
        Enable ROI selection mode.
        
        Args:
            callback: Function to call with (x1, y1, x2, y2) when ROI is selected
        """
        self.roi_selecting = True
        self.roi_callback = callback
        self.ax.set_title("ROI Mode - Draw rectangles | Click to select | Ctrl+Click for multiple | Delete key to remove", 
                        fontsize=11, fontweight='bold')
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
            self.ax.set_title(f"Layout View - {self.grid_config.rows}x{self.grid_config.cols} Grid - Click tile to view", 
                            fontsize=12, fontweight='bold')
        else:
            self.ax.set_title("Layout View", fontsize=12, fontweight='bold')
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
        """Handle mouse press for ROI selection/selection or tile click"""
        if event.inaxes != self.ax:
            return
        
        click_x, click_y = event.xdata, event.ydata
        
        # Check if clicking on an existing ROI rectangle (for selection)
        clicked_roi = self._find_roi_at_point(click_x, click_y)
        if clicked_roi is not None:
            # Toggle selection of this ROI (Ctrl+Click for multiple selection)
            self._toggle_roi_selection(clicked_roi, event)
            return
        
        # Handle ROI drawing mode (start drawing new ROI)
        if self.roi_selecting:
            # Clear all selections when starting to draw new ROI
            self._clear_all_selections()
            
            # Start drawing new ROI
            self.roi_start = (click_x, click_y)
            
            # Remove previous temporary rectangle if exists
            if self.roi_temp_rect:
                self.roi_temp_rect.remove()
                self.roi_temp_rect = None
            return
        
        # Handle tile click (only if grid is configured and NOT in ROI mode)
        if self.grid_config and self.tile_click_callback and not self.roi_selecting:
            # Calculate which tile was clicked
            if hasattr(self.current_image, 'shape'):
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
            edgecolor='red',
            linewidth=2,
            linestyle='--',
            alpha=0.7
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
        
        # Create permanent ROI rectangle
        width = x2 - x1
        height = y2 - y1
        roi_rect = Rectangle(
            (x1, y1),
            width,
            height,
            fill=False,
            edgecolor='red',
            linewidth=2,
            linestyle='-',
            alpha=1.0
        )
        self.ax.add_patch(roi_rect)
        self.roi_rectangles.append(roi_rect)
        self.canvas.draw()
        
        # Call callback
        if self.roi_callback:
            self.roi_callback((x1, y1, x2, y2))
        
        # Reset start point (keep selecting mode active for multiple ROIs)
        self.roi_start = None
    
    def draw_roi_rectangle(self, x1: int, y1: int, x2: int, y2: int, color: str = 'red'):
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
            linestyle='-'
        )
        self.ax.add_patch(roi_rect)
        self.roi_rectangles.append(roi_rect)
        self.canvas.draw()
    
    def clear_roi_rectangle(self):
        """Clear all ROI rectangles from canvas (alias for clear_all_rois)"""
        self.clear_all_rois()
    
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
        for roi_rect in self.roi_rectangles:
            # Get rectangle bounds
            rect_x = roi_rect.get_x()
            rect_y = roi_rect.get_y()
            rect_width = roi_rect.get_width()
            rect_height = roi_rect.get_height()
            
            # Check if point is inside rectangle
            if (rect_x <= x <= rect_x + rect_width and 
                rect_y <= y <= rect_y + rect_height):
                return roi_rect
        
        return None
    
    def _toggle_roi_selection(self, roi_rect, event):
        """
        Toggle selection of an ROI rectangle.
        Supports multiple selection with Ctrl+Click.
        
        Args:
            roi_rect: Rectangle object to toggle
            event: Mouse event (to check for Ctrl key)
        """
        # Check if Ctrl key is pressed for multiple selection
        ctrl_pressed = event.key == 'control' or (hasattr(event, 'button') and event.button == 3)
        
        if roi_rect in self.selected_roi_rects:
            # Deselect this ROI
            self._deselect_single_roi(roi_rect)
            print(f"❌ ROI deselected")
        else:
            # Select this ROI
            if not ctrl_pressed:
                # Clear all other selections if Ctrl not pressed
                self._clear_all_selections()
            
            self._select_single_roi(roi_rect)
            print(f"✅ ROI selected ({len(self.selected_roi_rects)} total)")
    
    def _select_single_roi(self, roi_rect):
        """Select a single ROI rectangle (highlight it)."""
        if roi_rect not in self.selected_roi_rects:
            self.selected_roi_rects.append(roi_rect)
            roi_rect.set_edgecolor('yellow')
            roi_rect.set_linewidth(3)
            self.canvas.draw()
    
    def _deselect_single_roi(self, roi_rect):
        """Deselect a single ROI rectangle."""
        if roi_rect in self.selected_roi_rects:
            self.selected_roi_rects.remove(roi_rect)
            roi_rect.set_edgecolor('red')
            roi_rect.set_linewidth(2)
            self.canvas.draw()
    
    def _clear_all_selections(self):
        """Clear all ROI selections."""
        for roi_rect in self.selected_roi_rects:
            roi_rect.set_edgecolor('red')
            roi_rect.set_linewidth(2)
        self.selected_roi_rects.clear()
        self.canvas.draw()
    
    def _on_key_press(self, event):
        """
        Handle keyboard events.
        
        Args:
            event: Keyboard event
        """
        if event.key == 'delete' or event.key == 'backspace':
            # Delete all selected ROIs
            if self.selected_roi_rects:
                count = len(self.selected_roi_rects)
                print(f"🗑️  Deleting {count} selected ROI(s)")
                for roi_rect in self.selected_roi_rects[:]:  # Copy list to avoid modification during iteration
                    roi_rect.remove()
                    self.roi_rectangles.remove(roi_rect)
                self.selected_roi_rects.clear()
                self.canvas.draw()
                print(f"✅ {count} ROI(s) deleted")

