"""
Tile Cache Module
=================

LRU cache for on-demand generated tiles to reduce regeneration.
"""

from typing import Optional, Dict
from PIL import Image


class TileCache:
    """
    LRU cache for tile images.
    Uses FIFO eviction when cache is full.
    """
    
    def __init__(self, max_size: int = 50):
        """
        Initialize tile cache.
        
        Args:
            max_size: Maximum number of tiles to cache
        """
        self.max_size = max_size
        self.cache: Dict[str, Image.Image] = {}
    
    def get(self, row: int, col: int) -> Optional[Image.Image]:
        """
        Get cached tile or None if not cached.
        
        Args:
            row: Tile row index
            col: Tile column index
            
        Returns:
            PIL Image or None
        """
        key = self._make_key(row, col)
        return self.cache.get(key)
    
    def put(self, row: int, col: int, image: Image.Image):
        """
        Cache tile image (with FIFO eviction if full).
        
        Args:
            row: Tile row index
            col: Tile column index
            image: PIL Image to cache
        """
        # Evict oldest if cache is full
        if len(self.cache) >= self.max_size:
            # Remove first (oldest) entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        key = self._make_key(row, col)
        self.cache[key] = image
    
    def clear(self):
        """Clear all cached tiles"""
        self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)
    
    def _make_key(self, row: int, col: int) -> str:
        """Generate cache key from row and column"""
        return f"{row}_{col}"

