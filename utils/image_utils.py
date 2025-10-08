"""
Image Processing Utilities
===========================

Helper functions for image manipulation and display.
"""

from typing import Tuple
from PIL import Image


class ImageUtils:
    """Image processing helper functions"""
    
    @staticmethod
    def resize_for_display(image: Image.Image, max_size: Tuple[int, int]) -> Image.Image:
        """
        Resize image to fit within max_size while maintaining aspect ratio.
        
        Args:
            image: PIL Image to resize
            max_size: (max_width, max_height) tuple
            
        Returns:
            Resized PIL Image
        """
        # Calculate scaling factor
        width_ratio = max_size[0] / image.width
        height_ratio = max_size[1] / image.height
        scale_factor = min(width_ratio, height_ratio, 1.0)  # Don't upscale
        
        if scale_factor < 1.0:
            new_width = int(image.width * scale_factor)
            new_height = int(image.height * scale_factor)
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    @staticmethod
    def create_thumbnail(image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """
        Create a thumbnail of the image.
        
        Args:
            image: PIL Image
            size: (width, height) for thumbnail
            
        Returns:
            Thumbnail PIL Image
        """
        # Use thumbnail method (modifies in-place, so copy first)
        img_copy = image.copy()
        img_copy.thumbnail(size, Image.Resampling.LANCZOS)
        return img_copy
    
    @staticmethod
    def ensure_rgb(image: Image.Image) -> Image.Image:
        """
        Ensure image is in RGB mode (convert if needed).
        
        Args:
            image: PIL Image
            
        Returns:
            RGB PIL Image
        """
        if image.mode != 'RGB':
            return image.convert('RGB')
        return image

