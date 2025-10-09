"""
Coordinate Transformer
======================

Utility for transforming coordinates between display and SVG space.
"""

from typing import Dict, Optional, Tuple


class CoordinateTransformer:
    """
    Transform coordinates between display image space and SVG space.

    Handles scaling between the rendered display image and the original
    SVG coordinate system.
    """

    def __init__(self):
        """Initialize transformer"""
        self.svg_dimensions: Optional[Dict] = None
        self.current_image = None

    def set_svg_dimensions(self, svg_dimensions: Dict):
        """
        Set SVG dimensions for transformation.

        Args:
            svg_dimensions: Dict with 'width' and 'height' keys
        """
        self.svg_dimensions = svg_dimensions

    def set_current_image(self, image):
        """
        Set current display image.

        Args:
            image: PIL Image or numpy array
        """
        self.current_image = image

    def _get_image_size(self) -> Tuple[int, int]:
        """
        Get display image size.

        Returns:
            (width, height) tuple
        """
        if hasattr(self.current_image, "shape"):
            # Numpy array: shape is (height, width, channels)
            display_height, display_width = self.current_image.shape[:2]
        else:
            # PIL Image: size is (width, height)
            display_width, display_height = self.current_image.size

        return display_width, display_height

    def transform_display_to_svg(
        self, display_coords: Tuple[float, float, float, float]
    ) -> Tuple[float, float, float, float]:
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
        display_width, display_height = self._get_image_size()

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

    def transform_svg_to_display(
        self, svg_coords: Tuple[float, float, float, float]
    ) -> Tuple[float, float, float, float]:
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
        display_width, display_height = self._get_image_size()

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

    def get_scale_factors(self) -> Tuple[float, float]:
        """
        Get current scale factors from SVG to display.

        Returns:
            (scale_x, scale_y) tuple, or (1.0, 1.0) if not available
        """
        if not self.svg_dimensions or not self.current_image:
            return (1.0, 1.0)

        display_width, display_height = self._get_image_size()
        svg_width = self.svg_dimensions["width"]
        svg_height = self.svg_dimensions["height"]

        scale_x = display_width / svg_width
        scale_y = display_height / svg_height

        return (scale_x, scale_y)
