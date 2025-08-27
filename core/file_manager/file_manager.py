"""
File Manager

This module coordinates file operations including GDS loading and SVG generation.
It provides a unified interface for file management operations.
"""

from typing import Optional, Dict, Any, Tuple
from .gds_loader import GDSLoader
from .svg_generator import SVGGenerator


class FileManager:
    """
    Coordinates file operations for the Layout Verification App.
    
    This class provides a unified interface for:
    - GDS file loading and validation
    - SVG generation from GDS files
    - File information management
    - Error handling and status reporting
    """
    
    def __init__(self, output_directory: str = None):
        """Initialize the file manager"""
        self.gds_loader = GDSLoader()
        self.svg_generator = SVGGenerator(output_directory)
        self.current_gds_path: Optional[str] = None
        self.current_svg_path: Optional[str] = None
        self.svg_dimensions: Optional[Dict[str, float]] = None
    
    def load_gds_file_dialog(self, initial_dir: str = "/Users/aitomatic/Project/nexus/data/") -> bool:
        """
        Load a GDS file through file dialog.
        
        Args:
            initial_dir: Initial directory for file dialog
            
        Returns:
            True if successful, False otherwise
        """
        file_path = self.gds_loader.load_gds_file_dialog(initial_dir)
        if file_path:
            self.current_gds_path = file_path
            return True
        return False
    
    def load_gds_file(self, file_path: str) -> bool:
        """
        Load a GDS file directly.
        
        Args:
            file_path: Path to the GDS file
            
        Returns:
            True if successful, False otherwise
        """
        result = self.gds_loader.load_gds_file(file_path)
        if result:
            self.current_gds_path = file_path
            return True
        return False
    
    def generate_svg(self) -> bool:
        """
        Generate SVG from the currently loaded GDS file.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.current_gds_path:
            return False
        
        if not self.gds_loader.is_loaded():
            return False
        
        # Generate output path
        self.current_svg_path = self.svg_generator.get_output_path(self.current_gds_path)
        
        # Generate SVG
        success = self.svg_generator.generate_svg_from_gds(
            self.gds_loader.gds_library, 
            self.current_svg_path
        )
        
        if success:
            # Parse SVG dimensions
            self.svg_dimensions = self.svg_generator.get_svg_dimensions(self.current_svg_path)
            
            # Validate generated SVG
            is_valid, errors = self.svg_generator.validate_svg_file(self.current_svg_path)
            if not is_valid:
                print(f"SVG validation warnings: {errors}")
        
        return success
    
    def get_file_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the currently loaded GDS file.
        
        Returns:
            File information dictionary or None if no file loaded
        """
        return self.gds_loader.get_file_info()
    
    def get_file_display_info(self) -> str:
        """
        Get formatted file information for display.
        
        Returns:
            Formatted string with file information
        """
        return self.gds_loader.get_file_display_info()
    
    def get_svg_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the generated SVG file.
        
        Returns:
            SVG information dictionary or None if no SVG generated
        """
        if not self.current_svg_path:
            return None
        
        import os
        from pathlib import Path
        
        svg_info = {
            'path': self.current_svg_path,
            'name': Path(self.current_svg_path).name,
            'size_kb': os.path.getsize(self.current_svg_path) / 1024,
            'dimensions': self.svg_dimensions
        }
        
        return svg_info
    
    def get_svg_display_info(self) -> str:
        """
        Get formatted SVG information for display.
        
        Returns:
            Formatted string with SVG information
        """
        svg_info = self.get_svg_info()
        if not svg_info:
            return "No SVG generated"
        
        return f"{svg_info['name']} ({svg_info['size_kb']:.1f} KB)"
    
    def get_svg_dimensions(self) -> Optional[Dict[str, float]]:
        """
        Get SVG dimensions.
        
        Returns:
            SVG dimensions dictionary or None if not available
        """
        return self.svg_dimensions
    
    def validate_current_state(self) -> Tuple[bool, list]:
        """
        Validate the current file state.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check GDS file
        if not self.current_gds_path:
            errors.append("No GDS file loaded")
        elif not self.gds_loader.is_loaded():
            errors.append("GDS file is not properly loaded")
        else:
            # Validate GDS structure
            is_valid, gds_errors = self.gds_loader.validate_gds_structure()
            if not is_valid:
                errors.extend(gds_errors)
        
        # Check SVG file
        if self.current_svg_path:
            if not self.svg_generator.validate_svg_file(self.current_svg_path)[0]:
                errors.append("Generated SVG file is invalid")
        
        return len(errors) == 0, errors
    
    def can_generate_svg(self) -> Tuple[bool, list]:
        """
        Check if SVG can be generated.
        
        Returns:
            Tuple of (can_generate, list_of_reasons_why_not)
        """
        errors = []
        
        if not self.current_gds_path:
            errors.append("No GDS file loaded")
        
        if not self.gds_loader.is_loaded():
            errors.append("GDS file is not properly loaded")
        
        if not self.gds_loader.is_gdspy_available():
            errors.append("gdspy library not available")
        
        # Validate GDS structure
        is_valid, gds_errors = self.gds_loader.validate_gds_structure()
        if not is_valid:
            errors.extend(gds_errors)
        
        return len(errors) == 0, errors
    
    def reset(self):
        """Reset all file state"""
        self.current_gds_path = None
        self.current_svg_path = None
        self.svg_dimensions = None
        self.gds_loader.clear()
    
    def is_gds_loaded(self) -> bool:
        """
        Check if a GDS file is loaded.
        
        Returns:
            True if GDS file is loaded, False otherwise
        """
        return self.gds_loader.is_loaded()
    
    def is_svg_generated(self) -> bool:
        """
        Check if SVG file is generated.
        
        Returns:
            True if SVG is generated, False otherwise
        """
        return self.current_svg_path is not None
    
    def get_gds_library(self):
        """
        Get the loaded GDS library.
        
        Returns:
            GDS library object or None if not loaded
        """
        return self.gds_loader.gds_library
    
    def get_first_cell(self):
        """
        Get the first cell from the loaded GDS file.
        
        Returns:
            First cell object or None if not loaded
        """
        return self.gds_loader.get_first_cell()
    
    def get_cell_bounding_box(self, cell_name: Optional[str] = None):
        """
        Get bounding box of a cell.
        
        Args:
            cell_name: Name of the cell (uses first cell if None)
            
        Returns:
            Bounding box or None if not found
        """
        return self.gds_loader.get_cell_bounding_box(cell_name)
    
    def get_polygons_by_layer(self, cell_name: Optional[str] = None):
        """
        Get polygons grouped by layer and datatype.
        
        Args:
            cell_name: Name of the cell (uses first cell if None)
            
        Returns:
            Dictionary mapping (layer, datatype) to list of polygons
        """
        return self.gds_loader.get_polygons_by_layer(cell_name)
