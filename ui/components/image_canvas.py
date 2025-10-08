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
        self.roi_rect = None
        self.roi_callback: Optional[Callable[[Tuple[int, int, int, int]], None]] = None
        
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
        
        # Bind mouse events for ROI selection
        self.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self._on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
    
    def display_image(self, image, grid_config=None):
        """
        Display an image on the canvas.
        
        Args:
            image: PIL Image or numpy array
            grid_config: Optional GridConfig to overlay tile grid
        """
        self.current_image = image
        self.ax.clear()
        self.ax.set_facecolor('white')
        self.ax.imshow(image)
        self.ax.axis('off')
        
        # Draw grid overlay if provided
        if grid_config:
            self._draw_grid_overlay(image, grid_config)
            self.ax.set_title(f"Layout View - {grid_config.rows}x{grid_config.cols} Grid", 
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
        
        # Draw vertical lines
        for i in range(grid_config.cols + 1):
            x = i * tile_width
            self.ax.axvline(x=x, color='cyan', linewidth=0.5, alpha=0.6, linestyle='--')
        
        # Draw horizontal lines
        for i in range(grid_config.rows + 1):
            y = i * tile_height
            self.ax.axhline(y=y, color='cyan', linewidth=0.5, alpha=0.6, linestyle='--')
        
        # Add text in corner
        self.ax.text(
            10, 20,
            f"Tile Grid: {grid_config.rows}×{grid_config.cols} ({grid_config.overlap}% overlap)",
            color='cyan',
            fontsize=10,
            fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='cyan')
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
        self.ax.set_title("Layout View - Click & Drag to Select ROI")
        self.canvas.draw()
    
    def disable_roi_selection(self):
        """Disable ROI selection mode"""
        self.roi_selecting = False
        self.roi_callback = None
        self.ax.set_title("Layout View")
        self.canvas.draw()
    
    def _on_mouse_press(self, event):
        """Handle mouse press for ROI selection"""
        if not self.roi_selecting or event.inaxes != self.ax:
            return
        
        self.roi_start = (event.xdata, event.ydata)
        
        # Remove previous rectangle if exists
        if self.roi_rect:
            self.roi_rect.remove()
            self.roi_rect = None
    
    def _on_mouse_move(self, event):
        """Handle mouse move for ROI selection"""
        if not self.roi_selecting or not self.roi_start or event.inaxes != self.ax:
            return
        
        # Update rectangle
        x1, y1 = self.roi_start
        x2, y2 = event.xdata, event.ydata
        
        # Remove old rectangle
        if self.roi_rect:
            self.roi_rect.remove()
        
        # Draw new rectangle
        width = x2 - x1
        height = y2 - y1
        self.roi_rect = Rectangle(
            (x1, y1),
            width,
            height,
            fill=False,
            edgecolor='red',
            linewidth=2,
            linestyle='--'
        )
        self.ax.add_patch(self.roi_rect)
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
        
        # Call callback
        if self.roi_callback:
            self.roi_callback((x1, y1, x2, y2))
        
        # Reset
        self.roi_start = None
    
    def draw_roi_rectangle(self, x1: int, y1: int, x2: int, y2: int, color: str = 'red'):
        """
        Draw an ROI rectangle on the canvas.
        
        Args:
            x1, y1: Top-left corner
            x2, y2: Bottom-right corner
            color: Rectangle color
        """
        # Remove old rectangle
        if self.roi_rect:
            self.roi_rect.remove()
        
        # Draw new rectangle
        width = x2 - x1
        height = y2 - y1
        self.roi_rect = Rectangle(
            (x1, y1),
            width,
            height,
            fill=False,
            edgecolor=color,
            linewidth=2,
            linestyle='--'
        )
        self.ax.add_patch(self.roi_rect)
        self.canvas.draw()
    
    def clear_roi_rectangle(self):
        """Clear ROI rectangle from canvas"""
        if self.roi_rect:
            self.roi_rect.remove()
            self.roi_rect = None
            self.canvas.draw()
    
    def refresh(self):
        """Refresh the canvas"""
        self.canvas.draw()

