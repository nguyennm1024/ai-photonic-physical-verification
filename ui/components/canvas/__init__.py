"""
Canvas Module
=============

Modular canvas components for layout visualization.

This module provides a refactored ImageCanvas component built using
composition and mixins for better maintainability.

Components:
- ImageCanvas: Main canvas widget (core + mixins)
- CoordinateTransformer: Utility for coordinate transformations
- GridOverlayMixin: Grid visualization
- ROISelectorMixin: ROI drawing and selection
- TileOverlayMixin: Tile status visualization

Architecture:
The ImageCanvas class inherits from multiple mixins to compose
its functionality, following the single responsibility principle.
"""

from .coordinate_transform import CoordinateTransformer
from .grid_overlay import GridOverlayMixin
from .image_canvas import ImageCanvas
from .roi_selector import ROISelectorMixin
from .tile_overlay import TileOverlayMixin

# Export main class
__all__ = [
    "ImageCanvas",
    "CoordinateTransformer",
    "GridOverlayMixin",
    "ROISelectorMixin",
    "TileOverlayMixin",
]
