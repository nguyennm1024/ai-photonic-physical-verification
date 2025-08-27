"""
GDS File Loader

This module handles loading and validation of GDS (GDSII) files.
It provides functionality to load GDS files and extract basic information.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from tkinter import filedialog, messagebox

try:
    import gdspy
    GDSPY_AVAILABLE = True
except ImportError:
    GDSPY_AVAILABLE = False
    gdspy = None


class GDSLoader:
    """
    Handles loading and validation of GDS files.
    
    This class provides functionality to:
    - Load GDS files through file dialog
    - Validate GDS file structure
    - Extract file information
    - Check file compatibility
    """
    
    def __init__(self):
        """Initialize the GDS loader"""
        self.current_gds_path: Optional[str] = None
        self.gds_library: Optional[Any] = None
        self.file_info: Optional[Dict[str, Any]] = None
    
    def is_gdspy_available(self) -> bool:
        """
        Check if gdspy library is available.
        
        Returns:
            True if gdspy is available, False otherwise
        """
        return GDSPY_AVAILABLE
    
    def load_gds_file_dialog(self, initial_dir: str = None) -> Optional[str]:
        """
        Open file dialog to select a GDS file.
        
        Args:
            initial_dir: Initial directory for file dialog
            
        Returns:
            Selected file path or None if cancelled
        """
        # Use current working directory if no initial directory specified
        if initial_dir is None:
            import os
            initial_dir = os.getcwd()
            
        file_path = filedialog.askopenfilename(
            title="Select GDS File",
            filetypes=[("GDS files", "*.gds *.GDS"), ("All files", "*.*")],
            initialdir=initial_dir
        )
        
        if file_path:
            return self.load_gds_file(file_path)
        
        return None
    
    def load_gds_file(self, file_path: str) -> Optional[str]:
        """
        Load a GDS file and validate its structure.
        
        Args:
            file_path: Path to the GDS file
            
        Returns:
            File path if successful, None if failed
        """
        if not self.is_gdspy_available():
            messagebox.showerror("Error", "gdspy library not available")
            return None
        
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            return None
        
        try:
            # Load GDS library (simple approach like original)
            self.gds_library = gdspy.GdsLibrary(infile=file_path)
            self.current_gds_path = file_path
            
            # Extract basic file information
            self.file_info = self._extract_basic_file_info(file_path)
            
            return file_path
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GDS file: {str(e)}")
            return None
    
    def _extract_basic_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Extract basic information from the GDS file (simplified approach).
        
        Args:
            file_path: Path to the GDS file
            
        Returns:
            Dictionary containing basic file information
        """
        file_info = {
            'path': file_path,
            'name': Path(file_path).name,
            'size_mb': os.path.getsize(file_path) / (1024 * 1024),
            'cells': [],
            'layers': [],
            'datatypes': []
        }
        
        if self.gds_library:
            # Get basic cell information
            for cell_name, cell in self.gds_library.cells.items():
                cell_info = {
                    'name': cell_name,
                    'bounding_box': cell.get_bounding_box()
                }
                file_info['cells'].append(cell_info)
            
            # Get layer and datatype information from first cell
            if file_info['cells']:
                first_cell = self.gds_library.cells[file_info['cells'][0]['name']]
                polygons = first_cell.get_polygons(by_spec=True)
                layers = set()
                datatypes = set()
                
                for (layer, datatype) in polygons.keys():
                    layers.add(layer)
                    datatypes.add(datatype)
                
                file_info['layers'] = sorted(list(layers))
                file_info['datatypes'] = sorted(list(datatypes))
        
        return file_info
    
    def get_file_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the currently loaded GDS file.
        
        Returns:
            File information dictionary or None if no file loaded
        """
        return self.file_info
    
    def get_file_display_info(self) -> str:
        """
        Get formatted file information for display.
        
        Returns:
            Formatted string with file information
        """
        if not self.file_info:
            return "No file loaded"
        
        info = self.file_info
        return f"{info['name']} ({info['size_mb']:.1f} MB)"
    
    def get_cells(self) -> list:
        """
        Get list of cell names in the GDS file.
        
        Returns:
            List of cell names
        """
        if not self.gds_library:
            return []
        
        return list(self.gds_library.cells.keys())
    
    def get_first_cell(self) -> Optional[Any]:
        """
        Get the first cell from the GDS library.
        
        Returns:
            First cell object or None if no cells
        """
        if not self.gds_library:
            return None
        
        cell_names = list(self.gds_library.cells.keys())
        if not cell_names:
            return None
        
        return self.gds_library.cells[cell_names[0]]
    
    def get_cell_bounding_box(self, cell_name: Optional[str] = None) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        Get bounding box of a cell.
        
        Args:
            cell_name: Name of the cell (uses first cell if None)
            
        Returns:
            Bounding box as ((x1, y1), (x2, y2)) or None if not found
        """
        if not self.gds_library:
            return None
        
        if cell_name is None:
            cell = self.get_first_cell()
        else:
            cell = self.gds_library.cells.get(cell_name)
        
        if cell:
            return cell.get_bounding_box()
        
        return None
    
    def get_polygons_by_layer(self, cell_name: Optional[str] = None) -> Dict[Tuple[int, int], list]:
        """
        Get polygons grouped by layer and datatype.
        
        Args:
            cell_name: Name of the cell (uses first cell if None)
            
        Returns:
            Dictionary mapping (layer, datatype) to list of polygons
        """
        if not self.gds_library:
            return {}
        
        if cell_name is None:
            cell = self.get_first_cell()
        else:
            cell = self.gds_library.cells.get(cell_name)
        
        if cell:
            return cell.get_polygons(by_spec=True)
        
        return {}
    
    def validate_gds_structure(self) -> Tuple[bool, list]:
        """
        Validate the GDS file structure (simplified approach).
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.gds_library:
            errors.append("No GDS library loaded")
            return False, errors
        
        # Check if there are any cells
        if not self.gds_library.cells:
            errors.append("No cells found in GDS file")
            return False, errors
        
        # Check if first cell has content (simple check like original)
        first_cell = self.get_first_cell()
        if first_cell:
            bbox = first_cell.get_bounding_box()
            if bbox is None:
                errors.append("First cell appears to be empty")
        
        return len(errors) == 0, errors
    
    def clear(self):
        """Clear the currently loaded GDS file"""
        self.current_gds_path = None
        self.gds_library = None
        self.file_info = None
    
    def is_loaded(self) -> bool:
        """
        Check if a GDS file is currently loaded.
        
        Returns:
            True if a file is loaded, False otherwise
        """
        return self.current_gds_path is not None and self.gds_library is not None
