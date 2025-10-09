"""
Image Canvas Component
======================

Matplotlib-based canvas for displaying layout images with interactive features.

This module uses composition to combine specialized functionality:
- CoordinateTransformer: SVG ↔ display space transformation
- GridOverlayMixin: Grid visualization
- ROISelectorMixin: ROI drawing and selection
- TileOverlayMixin: Tile status visualization
"""

import tkinter as tk
from matplotlib.figure import Figure
from tkinter import ttk

from .coordinate_transform import CoordinateTransformer
from .grid_overlay import GridOverlayMixin
from .roi_selector import ROISelectorMixin
from .tile_overlay import TileOverlayMixin


class ImageCanvas(GridOverlayMixin, ROISelectorMixin, TileOverlayMixin, ttk.Frame):
    """
    Image canvas - Matplotlib canvas for image display and interaction.

    Features (via mixins):
    - Display layout images
    - Interactive ROI selection (click & drag)
    - Tile status visualization
    - Zoom/pan controls
    - Coordinate transformation
    """

    def __init__(self, parent, **kwargs):
        """
        Initialize image canvas.

        Args:
            parent: Parent tkinter widget
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)

        # Grid configuration (for tile selection)
        self.grid_config = None

        # Current image
        self.current_image = None

        # Coordinate transformer
        self.coord_transformer = CoordinateTransformer()

        # Initialize mixin states
        self._init_roi_selector()
        self._init_tile_overlay()

        # Setup matplotlib canvas
        self._setup_canvas()

    def _setup_canvas(self):
        """Create matplotlib figure and canvas"""
        # Defer importing TkAgg backend until runtime
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except Exception as e:
            raise RuntimeError(
                "❌ Matplotlib TkAgg backend could not be loaded. This application requires Tcl/Tk.\n\n"
                "📦 INSTALLATION INSTRUCTIONS:\n\n"
                "macOS with Homebrew:\n"
                "  1. Install Tcl/Tk:\n"
                "     brew install tcl-tk\n\n"
                "  2. Set environment variables (add to ~/.zshrc or ~/.bash_profile):\n"
                "     export TCL_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tcl9.0:/opt/homebrew/opt/tcl-tk/lib/tcl8.6\n"
                "     export TK_LIBRARY=/opt/homebrew/opt/tcl-tk/lib/tk9.0:/opt/homebrew/opt/tcl-tk/lib/tk8.6\n"
                "     export PATH=/opt/homebrew/opt/tcl-tk/bin:$PATH\n\n"
                "  3. Reload shell configuration:\n"
                "     source ~/.zshrc  # or source ~/.bash_profile\n\n"
                "  4. If using uv-managed Python, reinstall Python:\n"
                "     uv python uninstall\n"
                "     uv python install\n\n"
                "Linux (Ubuntu/Debian):\n"
                "  sudo apt-get update\n"
                "  sudo apt-get install python3-tk\n\n"
                "Linux (Fedora/RHEL):\n"
                "  sudo dnf install python3-tkinter\n\n"
                "🧪 TEST:\n"
                "  python3 -m tkinter\n"
                "  (Should open a small Tk window if installed correctly)\n"
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

        # Bind mouse events
        self.canvas.mpl_connect("button_press_event", self._on_mouse_press)
        self.canvas.mpl_connect("button_release_event", self._on_mouse_release)
        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)

        # Bind keyboard events
        self.canvas.mpl_connect("key_press_event", self._on_key_press)

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

        # Update coordinate transformer
        self.coord_transformer.set_current_image(image)
        if svg_dimensions:
            self.coord_transformer.set_svg_dimensions(svg_dimensions)
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

    def clear_image(self):
        """Clear the displayed image"""
        self.ax.clear()
        self.ax.axis("off")
        self.ax.set_title("Layout View")
        self.canvas.draw()
        self.current_image = None
        self.grid_config = None

    def refresh(self):
        """Refresh the canvas"""
        self.canvas.draw()

    # ========================================================================
    # MOUSE EVENT ROUTING
    # ========================================================================

    def _on_mouse_press(self, event):
        """Handle mouse press - route to appropriate handler"""
        print("🖱️  MOUSE PRESS EVENT TRIGGERED!")

        if event.inaxes != self.ax:
            print("❌ Click outside axes")
            return

        click_x, click_y = event.xdata, event.ydata
        print(f"🖱️  Mouse press at ({click_x:.1f}, {click_y:.1f})")

        # Try ROI handler first (if in ROI mode)
        if self._handle_roi_mouse_press(event):
            return

        # Otherwise handle as tile click
        if self.grid_config and self.tile_click_callback:
            tile_coords = self._detect_tile_click(click_x, click_y)
            if tile_coords:
                row, col = tile_coords
                print(f"🖱️  Tile click detected: row={row}, col={col}")
                self.tile_click_callback(row, col)

    def _on_mouse_move(self, event):
        """Handle mouse move - route to ROI handler"""
        self._handle_roi_mouse_move(event)

    def _on_mouse_release(self, event):
        """Handle mouse release - route to ROI handler"""
        self._handle_roi_mouse_release(event)

    def _on_key_press(self, event):
        """Handle keyboard events - route to ROI handler"""
        self._handle_roi_key_press(event)
