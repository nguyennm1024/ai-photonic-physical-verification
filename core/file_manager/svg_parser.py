"""
SVG Parser Module
=================

Parse SVG files for dimensions, viewBox, and content analysis.
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple


class SVGParser:
    """Parse SVG files and extract metadata"""
    
    def parse_dimensions(self, svg_path: str) -> Dict[str, float]:
        """
        Extract SVG dimensions from file.
        
        Args:
            svg_path: Path to SVG file
            
        Returns:
            Dict with keys 'x', 'y', 'width', 'height' (viewBox coordinates)
        """
        try:
            with open(svg_path, 'r') as f:
                content = f.read(8192)  # Read first 8KB for header
            
            # Try to find viewBox attribute
            viewbox_match = re.search(r'viewBox="([^"]*)"', content)
            if viewbox_match:
                parts = [float(x) for x in viewbox_match.group(1).split()]
                if len(parts) == 4:
                    return {
                        'x': parts[0],
                        'y': parts[1],
                        'width': parts[2],
                        'height': parts[3]
                    }
            
            # Fallback to width/height attributes
            width_match = re.search(r'width="([^"]*)"', content)
            height_match = re.search(r'height="([^"]*)"', content)
            
            if width_match and height_match:
                width_str = width_match.group(1)
                height_str = height_match.group(1)
                
                # Remove units
                width = float(re.sub(r'[^\d.-]', '', width_str) or '1000')
                height = float(re.sub(r'[^\d.-]', '', height_str) or '1000')
                
                return {'x': 0, 'y': 0, 'width': width, 'height': height}
            
            # Default fallback
            return {'x': 0, 'y': 0, 'width': 1000, 'height': 1000}
            
        except Exception as e:
            print(f"Error parsing SVG dimensions: {e}")
            return {'x': 0, 'y': 0, 'width': 1000, 'height': 1000}
    
    def parse_viewbox(self, svg_path: str) -> Tuple[float, float, float, float]:
        """
        Extract viewBox parameters from SVG.
        
        Args:
            svg_path: Path to SVG file
            
        Returns:
            (x, y, width, height) tuple
        """
        dims = self.parse_dimensions(svg_path)
        return (dims['x'], dims['y'], dims['width'], dims['height'])
    
    def get_svg_dimensions_from_tree(self, svg_path: str) -> Dict[str, float]:
        """
        Get SVG dimensions by parsing XML tree.
        
        Args:
            svg_path: Path to SVG file
            
        Returns:
            Dict with 'width' and 'height' keys
        """
        try:
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
            width_val = float(str(width).replace('px', '').replace('pt', '').replace('mm', ''))
            height_val = float(str(height).replace('px', '').replace('pt', '').replace('mm', ''))
            
            return {'width': width_val, 'height': height_val}
            
        except Exception as e:
            print(f"Error getting SVG dimensions: {e}")
            return {'width': 1000, 'height': 1000}
    
    def analyze_content_bounds(self, svg_path: str) -> Optional[Tuple[float, float, float, float]]:
        """
        Analyze actual content bounds in the SVG to identify empty regions.
        
        Args:
            svg_path: Path to SVG file
            
        Returns:
            (x_min, y_min, width, height) of content bounds, or None if analysis fails
        """
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            
            # Find all polygons, paths, and rectangles
            polygons = root.findall('.//{http://www.w3.org/2000/svg}polygon')
            paths = root.findall('.//{http://www.w3.org/2000/svg}path')
            rects = root.findall('.//{http://www.w3.org/2000/svg}rect')
            
            all_x = []
            all_y = []
            
            # Process polygons
            for poly in polygons:
                points = poly.get('points', '')
                if points:
                    coords = points.replace(',', ' ').split()
                    for i in range(0, len(coords)-1, 2):
                        try:
                            x, y = float(coords[i]), float(coords[i+1])
                            all_x.append(x)
                            all_y.append(y)
                        except (ValueError, IndexError):
                            continue
            
            # Process rectangles
            for rect in rects:
                try:
                    x = float(rect.get('x', 0))
                    y = float(rect.get('y', 0))
                    width = float(rect.get('width', 0))
                    height = float(rect.get('height', 0))
                    all_x.extend([x, x + width])
                    all_y.extend([y, y + height])
                except (ValueError, TypeError):
                    continue
            
            if all_x and all_y:
                content_x_min = min(all_x)
                content_x_max = max(all_x)
                content_y_min = min(all_y)
                content_y_max = max(all_y)
                
                # Add small padding
                padding = 50
                content_x_min -= padding
                content_y_min -= padding
                content_width = (content_x_max - content_x_min) + 2 * padding
                content_height = (content_y_max - content_y_min) + 2 * padding
                
                return (content_x_min, content_y_min, content_width, content_height)
                
        except Exception as e:
            print(f"Warning: Could not analyze content bounds: {e}")
        
        return None

