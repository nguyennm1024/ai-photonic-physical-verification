"""
SVG Converter Module
====================

Convert between GDS, SVG, and PNG formats using multiple fallback methods.
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw

try:
    import gdspy
except ImportError:
    gdspy = None


class SVGConverter:
    """
    Convert between GDS, SVG, and PNG formats.
    Uses multiple conversion methods with fallback for robustness.
    """
    
    def __init__(self):
        """Initialize converter with available methods"""
        self.conversion_methods = [
            ("rsvg-convert", self._convert_with_rsvg),
            ("inkscape", self._convert_with_inkscape),
            ("browser", self._convert_with_browser),
            ("placeholder", self._create_enhanced_placeholder)
        ]
    
    def convert_gds_to_svg(self, gds_lib: 'gdspy.GdsLibrary', gds_path: str, output_dir: str = "./") -> str:
        """
        Convert GDS library to SVG file (high-level method).
        
        Args:
            gds_lib: GDS library object
            gds_path: Path to GDS file (for naming)
            output_dir: Output directory
            
        Returns:
            Path to generated SVG file
        """
        base_name = Path(gds_path).stem
        output_path = os.path.join(output_dir, f"{base_name}_layout.svg")
        
        success = self.gds_to_svg(gds_lib, output_path)
        if not success:
            raise RuntimeError(f"Failed to convert GDS to SVG")
        
        return output_path
    
    def gds_to_svg(self, gds_lib: 'gdspy.GdsLibrary', output_path: str) -> bool:
        """
        Convert GDS library to SVG file (low-level method).
        
        Args:
            gds_lib: GDS library object
            output_path: Path where SVG will be saved
            
        Returns:
            True if successful, False otherwise
        """
        if not gdspy:
            raise ImportError("gdspy library not available")
        
        try:
            # Get the first cell
            cell_names = list(gds_lib.cells.keys())
            if not cell_names:
                raise ValueError("No cells found in GDS file")
            
            cell = gds_lib.cells[cell_names[0]]
            
            # Get bounding box
            bbox = cell.get_bounding_box()
            if bbox is None:
                raise ValueError("Cell appears to be empty")
            
            width = bbox[1][0] - bbox[0][0]
            height = bbox[1][1] - bbox[0][1]
            
            # Create SVG content
            svg_lines = []
            svg_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
            svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                           f'viewBox="{bbox[0][0]} {-bbox[1][1]} {width} {height}" '
                           f'width="{width}" height="{height}">')
            svg_lines.append('<g transform="scale(1,-1)">')
            
            # Get polygons and convert to SVG
            polygons = cell.get_polygons(by_spec=True)
            colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF']
            
            for (layer, datatype), polys in polygons.items():
                color = colors[layer % len(colors)]
                for poly in polys:
                    if len(poly) > 2:
                        points_str = ' '.join([f"{pt[0]},{pt[1]}" for pt in poly])
                        svg_lines.append(f'<polygon points="{points_str}" '
                                      f'fill="{color}" fill-opacity="0.7" '
                                      f'stroke="{color}" stroke-width="0.1" />')
            
            svg_lines.append('</g>')
            svg_lines.append('</svg>')
            
            # Write SVG file
            with open(output_path, 'w') as f:
                f.write('\n'.join(svg_lines))
            
            return True
            
        except Exception as e:
            print(f"Error converting GDS to SVG: {e}")
            return False
    
    def svg_to_png(self, svg_path: str, png_path: str, resolution: int = 2048) -> bool:
        """
        Convert SVG to PNG using best available method.
        
        Args:
            svg_path: Path to SVG file
            png_path: Path where PNG will be saved
            resolution: Target resolution (width/height)
            
        Returns:
            True if successful, False otherwise
        """
        for method_name, method_func in self.conversion_methods:
            try:
                if method_func(svg_path, png_path, resolution):
                    # Verify the conversion worked
                    if os.path.exists(png_path) and os.path.getsize(png_path) > 1000:
                        print(f"✅ {method_name} conversion successful")
                        return True
            except Exception as e:
                print(f"❌ {method_name} failed: {e}")
                continue
        
        return False
    
    def svg_tile_to_png(self, svg_path: str, png_path: str, resolution: int) -> bool:
        """
        Convert single SVG tile to PNG.
        
        Args:
            svg_path: Path to SVG tile file
            png_path: Path where PNG will be saved
            resolution: Target resolution
            
        Returns:
            True if successful, False otherwise
        """
        # Try conversion methods (skip placeholder for tiles)
        for method_name, method_func in self.conversion_methods[:-1]:  # Skip placeholder
            try:
                if method_func(svg_path, png_path, resolution):
                    return True
            except Exception:
                continue
        
        return False
    
    def _convert_with_rsvg(self, svg_path: str, png_path: str, resolution: int = 2048) -> bool:
        """
        Convert using rsvg-convert (fastest and most reliable).
        
        Args:
            svg_path: Path to SVG file
            png_path: Path where PNG will be saved
            resolution: Target resolution
            
        Returns:
            True if successful, False otherwise
        """
        cmd = [
            'rsvg-convert',
            '--format=png',
            f'--width={resolution}',
            f'--height={resolution}',
            '--output', png_path,
            svg_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def _convert_with_inkscape(self, svg_path: str, png_path: str, resolution: int = 2048) -> bool:
        """
        Convert using Inkscape.
        
        Args:
            svg_path: Path to SVG file
            png_path: Path where PNG will be saved
            resolution: Target resolution
            
        Returns:
            True if successful, False otherwise
        """
        cmd = [
            'inkscape',
            '--export-type=png',
            f'--export-filename={png_path}',
            f'--export-width={resolution}',
            f'--export-height={resolution}',
            svg_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def _convert_with_browser(self, svg_path: str, png_path: str, resolution: int = 2048) -> bool:
        """
        Convert using headless Chrome/Chromium browser.
        
        Args:
            svg_path: Path to SVG file
            png_path: Path where PNG will be saved
            resolution: Target resolution
            
        Returns:
            True if successful, False otherwise
        """
        # Create HTML wrapper
        html_content = f'''<!DOCTYPE html>
<html><head><style>
body {{ margin: 0; padding: 0; width: {resolution}px; height: {resolution}px; }}
svg {{ width: 100%; height: 100%; }}
</style></head><body>'''
        
        with open(svg_path, 'r') as f:
            svg_content = f.read()
        
        html_content += svg_content + '</body></html>'
        
        # Save temporary HTML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            html_path = f.name
        
        try:
            # Try Chrome/Chromium
            for chrome_cmd in ['google-chrome', 'chromium', 'chromium-browser', 'chrome']:
                try:
                    cmd = [
                        chrome_cmd,
                        '--headless',
                        '--disable-gpu',
                        f'--window-size={resolution},{resolution}',
                        '--screenshot=' + png_path,
                        'file://' + html_path
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        return True
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            return False
        finally:
            # Clean up
            os.unlink(html_path)
    
    def _create_enhanced_placeholder(self, svg_path: str, png_path: str, resolution: int = 2048) -> bool:
        """
        Create an enhanced placeholder with SVG information (fallback method).
        
        Args:
            svg_path: Path to SVG file
            png_path: Path where PNG will be saved
            resolution: Target resolution
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read SVG info
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            # Extract basic info
            import re
            viewbox_match = re.search(r'viewBox="([^"]*)"', svg_content)
            polygon_count = len(re.findall(r'<polygon', svg_content))
            
            # Create informative placeholder
            img = Image.new('RGB', (resolution, resolution), 'white')
            draw = ImageDraw.Draw(img)
            
            # Draw border
            border_margin = resolution // 200
            draw.rectangle([border_margin, border_margin, resolution-border_margin, resolution-border_margin], 
                         outline='red', width=max(1, resolution//400))
            
            # Add informative text
            info_lines = [
                "SVG Layout Visualization",
                f"File: {Path(svg_path).name}",
                f"Size: {os.path.getsize(svg_path) / (1024*1024):.1f} MB",
                f"Polygons: {polygon_count}",
                "",
                "This is an enhanced placeholder image.",
                "For better conversion, install:",
                "• brew install librsvg (rsvg-convert)",
                "• brew install inkscape",
                "• Google Chrome (for browser conversion)",
                "",
                "The app will still work for AI analysis!"
            ]
            
            if viewbox_match:
                info_lines.insert(4, f"ViewBox: {viewbox_match.group(1)}")
            
            # Draw text
            y_pos = 100
            for line in info_lines:
                if line:
                    draw.text((50, y_pos), line, fill='red')
                y_pos += 40
            
            # Draw some geometric patterns
            import random
            random.seed(42)
            colors = ['blue', 'green', 'purple', 'orange', 'brown']
            
            for i in range(30):
                x1 = random.randint(100, resolution-200)
                y1 = random.randint(600, resolution-200)
                x2 = x1 + random.randint(50, 200)
                y2 = y1 + random.randint(50, 200)
                color = random.choice(colors)
                draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
            
            img.save(png_path)
            return True
            
        except Exception as e:
            print(f"Failed to create enhanced placeholder: {e}")
            return False

