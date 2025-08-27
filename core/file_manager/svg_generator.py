"""
SVG Generator

This module handles conversion from GDS files to SVG format.
It provides functionality to convert GDS layouts to SVG for visualization.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List


class SVGGenerator:
    """
    Handles conversion from GDS to SVG format.
    
    This class provides functionality to:
    - Convert GDS layouts to SVG
    - Generate SVG with proper viewBox
    - Apply color mapping to layers
    - Handle coordinate transformations
    """
    
    def __init__(self, output_directory: str = None):
        """Initialize the SVG generator"""
        # Use current working directory if no output directory specified
        if output_directory is None:
            import os
            self.output_directory = os.getcwd()
        else:
            self.output_directory = output_directory
            
        self.color_palette = [
            '#FF0000', '#00FF00', '#0000FF', 
            '#FFFF00', '#FF00FF', '#00FFFF'
        ]
    
    def set_output_directory(self, directory: str):
        """
        Set the output directory for generated SVG files.
        
        Args:
            directory: Output directory path
        """
        self.output_directory = directory
    
    def generate_svg_from_gds(self, gds_library: Any, output_path: str) -> bool:
        """
        Generate SVG from GDS library.
        
        Args:
            gds_library: Loaded GDS library
            output_path: Output SVG file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the first cell
            cell_names = list(gds_library.cells.keys())
            if not cell_names:
                raise ValueError("No cells found in GDS file")
            
            cell = gds_library.cells[cell_names[0]]
            
            # Get bounding box
            bbox = cell.get_bounding_box()
            if bbox is None:
                raise ValueError("Cell appears to be empty")
            
            # Generate SVG content
            svg_content = self._create_svg_content(cell, bbox)
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Write SVG file
            with open(output_path, 'w') as f:
                f.write(svg_content)
            
            return True
            
        except Exception as e:
            print(f"Error generating SVG: {e}")
            return False
    
    def _create_svg_content(self, cell: Any, bbox: Tuple[Tuple[float, float], Tuple[float, float]]) -> str:
        """
        Create SVG content from GDS cell.
        
        Args:
            cell: GDS cell object
            bbox: Bounding box ((x1, y1), (x2, y2))
            
        Returns:
            SVG content as string
        """
        width = bbox[1][0] - bbox[0][0]
        height = bbox[1][1] - bbox[0][1]
        
        # Create SVG header
        svg_lines = []
        svg_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg_lines.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{bbox[0][0]} {-bbox[1][1]} {width} {height}" '
            f'width="{width}" height="{height}">'
        )
        svg_lines.append('<g transform="scale(1,-1)">')
        
        # Get polygons and convert to SVG
        polygons = cell.get_polygons(by_spec=True)
        
        for (layer, datatype), polys in polygons.items():
            color = self.color_palette[layer % len(self.color_palette)]
            for poly in polys:
                if len(poly) > 2:
                    points_str = ' '.join([f"{pt[0]},{pt[1]}" for pt in poly])
                    svg_lines.append(
                        f'<polygon points="{points_str}" '
                        f'fill="{color}" fill-opacity="0.7" '
                        f'stroke="{color}" stroke-width="0.1" />'
                    )
        
        svg_lines.append('</g>')
        svg_lines.append('</svg>')
        
        return '\n'.join(svg_lines)
    
    def get_svg_dimensions(self, svg_path: str) -> Dict[str, float]:
        """
        Get dimensions from SVG file.
        
        Args:
            svg_path: Path to SVG file
            
        Returns:
            Dictionary with x, y, width, height
        """
        try:
            with open(svg_path, 'r') as f:
                content = f.read(8192)  # Read first 8KB for header
            
            import re
            viewbox_match = re.search(r'viewBox="([^"]*)"', content)
            if viewbox_match:
                parts = [float(x) for x in viewbox_match.group(1).split()]
                return {
                    'x': parts[0], 
                    'y': parts[1], 
                    'width': parts[2], 
                    'height': parts[3]
                }
            
            return {'x': 0, 'y': 0, 'width': 1000, 'height': 1000}
            
        except Exception as e:
            print(f"Error parsing SVG dimensions: {e}")
            return {'x': 0, 'y': 0, 'width': 1000, 'height': 1000}
    
    def get_svg_dimensions_alternative(self, svg_path: str) -> Dict[str, float]:
        """
        Alternative method to get SVG dimensions using XML parsing.
        
        Args:
            svg_path: Path to SVG file
            
        Returns:
            Dictionary with width, height
        """
        if not os.path.exists(svg_path):
            return {'width': 1000, 'height': 1000}
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(svg_path)
            root = tree.getroot()
            
            # Try to get viewBox first
            viewbox = root.get('viewBox')
            if viewbox:
                parts = viewbox.strip().split()
                if len(parts) == 4:
                    return {
                        'width': float(parts[2]),
                        'height': float(parts[3])
                    }
            
            # Fallback to width/height attributes
            width = root.get('width', '1000')
            height = root.get('height', '1000')
            
            # Remove units if present
            width = float(width.replace('px', '').replace('pt', '').replace('mm', ''))
            height = float(height.replace('px', '').replace('pt', '').replace('mm', ''))
            
            return {'width': width, 'height': height}
            
        except Exception as e:
            print(f"Error getting SVG dimensions: {e}")
            return {'width': 1000, 'height': 1000}
    
    def validate_svg_file(self, svg_path: str) -> Tuple[bool, List[str]]:
        """
        Validate generated SVG file.
        
        Args:
            svg_path: Path to SVG file
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not os.path.exists(svg_path):
            errors.append("SVG file does not exist")
            return False, errors
        
        file_size = os.path.getsize(svg_path)
        if file_size < 1000:  # Less than 1KB
            errors.append("SVG file is too small (likely empty or corrupted)")
        
        try:
            with open(svg_path, 'r') as f:
                content = f.read()
                
            if not content.strip().startswith('<?xml'):
                errors.append("SVG file does not start with XML declaration")
            
            if '<svg' not in content:
                errors.append("SVG file does not contain SVG element")
            
            if '</svg>' not in content:
                errors.append("SVG file does not have closing SVG tag")
                
        except Exception as e:
            errors.append(f"Error reading SVG file: {e}")
        
        return len(errors) == 0, errors
    
    def get_output_path(self, gds_path: str) -> str:
        """
        Generate output SVG path from GDS path.
        
        Args:
            gds_path: Path to GDS file
            
        Returns:
            Output SVG path
        """
        base_name = Path(gds_path).stem
        return os.path.join(self.output_directory, f"{base_name}_layout.svg")
