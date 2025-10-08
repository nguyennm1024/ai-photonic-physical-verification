"""
GDS Loader Module
=================

Handles loading and basic operations on GDS files.
"""

from typing import Optional
from pathlib import Path

try:
    import gdspy
except ImportError:
    gdspy = None


class GDSLoader:
    """Load and extract information from GDS files"""
    
    def __init__(self):
        """Initialize GDS loader"""
        if gdspy is None:
            print("Warning: gdspy not available")
    
    @staticmethod
    def is_available() -> bool:
        """Check if gdspy is available"""
        return gdspy is not None
    
    def load_gds(self, file_path: str) -> Optional['gdspy.GdsLibrary']:
        """
        Load GDS file and return library.
        
        Args:
            file_path: Path to GDS file
            
        Returns:
            GdsLibrary object or None if loading fails
        """
        if not gdspy:
            raise ImportError("gdspy library not available")
        
        try:
            gds_lib = gdspy.GdsLibrary(infile=file_path)
            return gds_lib
        except Exception as e:
            print(f"Error loading GDS file: {e}")
            return None
    
    def get_cell(self, gds_lib: 'gdspy.GdsLibrary', cell_index: int = 0):
        """
        Get cell from GDS library.
        
        Args:
            gds_lib: GDS library object
            cell_index: Index of cell to get (default 0 = first cell)
            
        Returns:
            Cell object or None
        """
        if not gds_lib:
            return None
        
        cell_names = list(gds_lib.cells.keys())
        if not cell_names:
            raise ValueError("No cells found in GDS file")
        
        if cell_index >= len(cell_names):
            cell_index = 0
        
        return gds_lib.cells[cell_names[cell_index]]
    
    def get_bounding_box(self, cell) -> Optional[tuple]:
        """
        Extract bounding box from cell.
        
        Args:
            cell: GDS cell object
            
        Returns:
            ((min_x, min_y), (max_x, max_y)) or None
        """
        if not cell:
            return None
        
        bbox = cell.get_bounding_box()
        if bbox is None:
            raise ValueError("Cell appears to be empty")
        
        return bbox
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get basic information about a GDS file.
        
        Args:
            file_path: Path to GDS file
            
        Returns:
            Dict with 'size_mb', 'name', 'path' keys
        """
        path = Path(file_path)
        size_bytes = path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        return {
            'name': path.name,
            'path': str(path),
            'size_mb': size_mb
        }

