#!/usr/bin/env python3
"""
Interactive Layout Verification App
==================================

A comprehensive GUI application for GDS layout verification using AI analysis.

Features:
- Load GDS files and convert to SVG
- Split layouts into tiles for analysis  
- AI-powered discontinuity detection using Gemini
- Interactive user feedback and classification
- Original image display with bounding box highlighting

Author: William
Date: 2025-08-27
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from PIL import Image, ImageTk, ImageDraw
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches

# Import existing modules
try:
    import gdspy
except ImportError:
    print("Warning: gdspy not available")
    gdspy = None

try:
    import google.generativeai as genai
except ImportError:
    print("Warning: google-generativeai not available")
    genai = None


class LayoutVerificationApp:
    """Main application class for layout verification"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Layout Verification System")
        self.root.geometry("1400x900")
        
        # Application state
        self.current_gds_path = None
        self.current_svg_path = None
        self.current_tiles_dir = None
        self.tiles_data = []
        self.current_tile_index = 0
        self.analyzed_tiles = {}
        self.flagged_tiles = []
        self.original_image = None
        self.svg_dimensions = None
        
        # On-demand tile generation
        self.virtual_tiles = True  # Use virtual tiles instead of pre-generated files
        self.tile_cache = {}  # Memory cache for generated tiles
        self.max_cache_size = 50  # Maximum tiles to keep in memory
        self.grid_config = None
        
        # AI analyzer and classifier
        self.ai_analyzer = None
        self.ai_classifier = None
        if genai:
            try:
                api_key = os.getenv('GOOGLE_API_KEY')
                if not api_key:
                    print("❌ GOOGLE_API_KEY environment variable not set")
                    print("💡 Set environment variable: export GOOGLE_API_KEY=your_api_key")
                    self.ai_analyzer = None
                    self.ai_classifier = None
                else:
                    genai.configure(api_key=api_key)
                    self.ai_analyzer = genai.GenerativeModel('gemini-2.5-pro')  # For detailed analysis
                    self.ai_classifier = genai.GenerativeModel('gemini-2.5-flash')  # For classification
                    print("✅ Initialized Gemini models: Pro (analysis) + Flash (classification)")
            except Exception as e:
                print(f"❌ Failed to initialize Gemini: {e}")
                self.ai_analyzer = None
                self.ai_classifier = None
        
        # Threading
        self.analysis_queue = queue.Queue()
        self.analysis_running = False
        self.analysis_paused = False
        
        # Region of Interest (ROI) selection - Multiple ROIs support
        self.roi_mode = False
        self.roi_start = None
        self.roi_end = None
        self.drawing_roi = False
        
        # Multiple ROI regions storage
        self.roi_regions = []  # List of {'start': (x,y), 'end': (x,y), 'rectangle': patch_obj, 'id': int}
        self.roi_counter = 0   # Unique ID for each ROI
        self.current_roi_preview = None  # Preview while drawing
        
        # Flagged tiles display state
        self.flagged_tiles_displayed = False  # Track if flagged tiles are currently shown
        
        # Setup UI
        self.setup_ui()
        
        # Start checking queue
        self.check_analysis_queue()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls and Tile View
        left_panel = ttk.Frame(main_paned)
        main_paned.add(left_panel, weight=1)
        
        # Right panel - Original Image with Bounding Box
        right_panel = ttk.Frame(main_paned)
        main_paned.add(right_panel, weight=1)
        
        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def setup_left_panel(self, parent):
        """Setup left panel with controls and tile viewer"""
        # File operations section
        file_frame = ttk.LabelFrame(parent, text="1. File Operations")
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(file_frame, text="Load GDS File", 
                  command=self.load_gds_file).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.file_info_label = ttk.Label(file_frame, text="No file loaded")
        self.file_info_label.pack(side=tk.LEFT, padx=10)
        
        # Processing section
        process_frame = ttk.LabelFrame(parent, text="2. Processing Controls")
        process_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Grid configuration
        grid_config_frame = ttk.Frame(process_frame)
        grid_config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(grid_config_frame, text="Grid Size:").pack(side=tk.LEFT)
        self.grid_rows_var = tk.StringVar(value="10")
        ttk.Entry(grid_config_frame, textvariable=self.grid_rows_var, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Label(grid_config_frame, text="×").pack(side=tk.LEFT)
        self.grid_cols_var = tk.StringVar(value="10")
        ttk.Entry(grid_config_frame, textvariable=self.grid_cols_var, width=3).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(grid_config_frame, text="Overlap %:").pack(side=tk.LEFT, padx=(10, 2))
        self.overlap_var = tk.StringVar(value="0")
        ttk.Entry(grid_config_frame, textvariable=self.overlap_var, width=5).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(grid_config_frame, text="Tile Resolution:").pack(side=tk.LEFT, padx=(10, 2))
        self.tile_resolution_var = tk.StringVar(value="512")
        resolution_combo = ttk.Combobox(grid_config_frame, textvariable=self.tile_resolution_var, 
                                       values=["512", "1024", "2048", "4096"], width=6, state="readonly")
        resolution_combo.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(grid_config_frame, text="Max CPU Cores:").pack(side=tk.LEFT, padx=(10, 2))
        max_cores = multiprocessing.cpu_count()
        self.max_cores_var = tk.StringVar(value="8")
        cores_combo = ttk.Combobox(grid_config_frame, textvariable=self.max_cores_var, 
                                  values=[str(i) for i in range(1, max_cores + 1)], width=4, state="readonly")
        cores_combo.pack(side=tk.LEFT, padx=2)
        
        # Add CPU info label with tooltip
        info_label = ttk.Label(grid_config_frame, text=f"(System: {max_cores} cores)", 
                              foreground="gray")
        info_label.pack(side=tk.LEFT, padx=(2, 0))
        
        # Add tooltip functionality
        def create_tooltip(widget, text):
            def on_enter(event):
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                label = tk.Label(tooltip, text=text, background="lightyellow", 
                               relief="solid", borderwidth=1, font=("Arial", 9))
                label.pack()
                widget.tooltip = tooltip
            
            def on_leave(event):
                if hasattr(widget, 'tooltip'):
                    widget.tooltip.destroy()
                    del widget.tooltip
            
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
        create_tooltip(cores_combo, 
                      "Lower values: Conserve CPU for other tasks\\n" +
                      "Higher values: Faster tile processing\\n" +
                      "Recommended: 4-8 cores for most workflows")
        
        # Process buttons
        button_frame = ttk.Frame(process_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Split to Tiles", 
                  command=self.split_to_tiles).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Start AI Analysis", 
                  command=self.start_ai_analysis).pack(side=tk.LEFT, padx=5)
        
        # Stop/Resume button
        self.stop_resume_button = ttk.Button(button_frame, text="⏸️ Stop", 
                                           command=self.toggle_analysis_state)
        self.stop_resume_button.pack(side=tk.LEFT, padx=5)
        
        # ROI controls - Multiple regions support
        roi_frame = ttk.Frame(process_frame)
        roi_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # ROI drawing controls
        roi_draw_frame = ttk.Frame(roi_frame)
        roi_draw_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(roi_draw_frame, text="Regions of Interest:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.roi_toggle_button = ttk.Button(roi_draw_frame, text="📐 Draw ROI", 
                                          command=self.toggle_roi_mode)
        self.roi_toggle_button.pack(side=tk.LEFT, padx=5)
        
        self.roi_count_label = ttk.Label(roi_draw_frame, text="(0 regions)")
        self.roi_count_label.pack(side=tk.LEFT, padx=5)
        
        self.roi_status_label = ttk.Label(roi_draw_frame, text="🖱️ Navigation Mode", 
                                        foreground="green")
        self.roi_status_label.pack(side=tk.LEFT, padx=10)
        
        # ROI management controls
        roi_manage_frame = ttk.Frame(roi_frame)
        roi_manage_frame.pack(fill=tk.X)
        
        self.clear_last_roi_button = ttk.Button(roi_manage_frame, text="↶ Undo Last", 
                                              command=self.clear_last_roi)
        self.clear_last_roi_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_all_roi_button = ttk.Button(roi_manage_frame, text="🗑️ Clear All", 
                                             command=self.clear_all_roi)
        self.clear_all_roi_button.pack(side=tk.LEFT, padx=5)
        
        self.analyze_roi_button = ttk.Button(roi_manage_frame, text="🎯 Analyze All ROI", 
                                           command=self.analyze_all_roi)
        self.analyze_roi_button.pack(side=tk.LEFT, padx=5)
        
        # Analysis section
        analysis_frame = ttk.LabelFrame(parent, text="3. AI Analysis & Review")
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Progress and status
        progress_frame = ttk.Frame(analysis_frame)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=2)
        
        self.analysis_status_label = ttk.Label(progress_frame, text="No analysis started")
        self.analysis_status_label.pack()
        
        # Current tile display
        tile_display_frame = ttk.Frame(analysis_frame)
        tile_display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tile image
        self.tile_image_label = ttk.Label(tile_display_frame, text="No tile selected")
        self.tile_image_label.pack(pady=10)
        
        # Tile info
        self.tile_info_label = ttk.Label(tile_display_frame, text="", 
                                        font=("Arial", 10, "bold"))
        self.tile_info_label.pack(pady=5)
        
        # AI analysis result
        self.ai_result_text = tk.Text(tile_display_frame, height=6, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(tile_display_frame, orient=tk.VERTICAL, 
                                 command=self.ai_result_text.yview)
        self.ai_result_text.configure(yscrollcommand=scrollbar.set)
        self.ai_result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # User decision buttons
        decision_frame = ttk.Frame(analysis_frame)
        decision_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(decision_frame, text="◀ Previous Tile", 
                  command=self.previous_tile).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(decision_frame, text="✓ Continuous", 
                  command=lambda: self.classify_tile("continuous"),
                  style="Success.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(decision_frame, text="⚠ Discontinuity", 
                  command=lambda: self.classify_tile("discontinuity"),
                  style="Warning.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(decision_frame, text="Next Tile ▶", 
                  command=self.next_tile).pack(side=tk.LEFT, padx=5)
        
        # Summary section
        summary_frame = ttk.LabelFrame(parent, text="4. Analysis Summary")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.summary_label = ttk.Label(summary_frame, text="No analysis completed")
        self.summary_label.pack(padx=5, pady=5)
        
        ttk.Button(summary_frame, text="Export Results", 
                  command=self.export_results).pack(padx=5, pady=5)
    
    def setup_right_panel(self, parent):
        """Setup right panel for original image display"""
        # Original image section
        image_frame = ttk.LabelFrame(parent, text="Original Layout with Highlighted Regions")
        image_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create matplotlib figure for image display
        # Create figure with smooth rendering settings
        self.fig = Figure(figsize=(8, 8), dpi=100, facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # Enable anti-aliasing and smooth rendering
        self.fig.patch.set_alpha(1.0)
        import matplotlib
        matplotlib.rcParams['lines.antialiased'] = True
        matplotlib.rcParams['patch.antialiased'] = True
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, image_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add click event handlers for navigation and ROI drawing
        self.canvas.mpl_connect('button_press_event', self.on_image_click)
        self.canvas.mpl_connect('button_release_event', self.on_image_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_image_motion)
        
        # Image controls
        controls_frame = ttk.Frame(image_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Fit to Window", 
                  command=self.fit_image_to_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Show All Flagged", 
                  command=self.show_all_flagged).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Clear Highlights", 
                  command=self.clear_highlights).pack(side=tk.LEFT, padx=5)
    
    def load_gds_file(self):
        """Load a GDS file and automatically convert to SVG"""
        file_path = filedialog.askopenfilename(
            title="Select GDS File",
            filetypes=[("GDS files", "*.gds *.GDS"), ("All files", "*.*")],
            initialdir="/Users/aitomatic/Project/nexus/data/"
        )
        
        if file_path:
            self.current_gds_path = file_path
            file_name = Path(file_path).name
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            self.file_info_label.config(text=f"{file_name} ({file_size:.1f} MB)")
            self.status_bar.config(text=f"Loaded GDS file: {file_name}")
            
            # Reset state
            self.current_svg_path = None
            self.current_tiles_dir = None
            self.tiles_data = []
            self.analyzed_tiles = {}
            self.flagged_tiles = []
            
            # Automatically convert to SVG
            self.root.after(100, self.generate_svg)  # Small delay for UI update
    
    def generate_svg(self):
        """Generate SVG from GDS file"""
        if not self.current_gds_path:
            messagebox.showerror("Error", "Please load a GDS file first")
            return
        
        if not gdspy:
            messagebox.showerror("Error", "gdspy library not available")
            return
        
        try:
            self.status_bar.config(text="🔄 Converting GDS to SVG...")
            self.root.update()
            
            # Load GDS file
            gds_lib = gdspy.GdsLibrary(infile=self.current_gds_path)
            
            # Get output path
            base_name = Path(self.current_gds_path).stem
            self.current_svg_path = f"/Users/aitomatic/Project/nexus/{base_name}_layout.svg"
            
            # Convert to SVG (using logic from render_image.py)
            self.convert_gds_to_svg(gds_lib, self.current_svg_path)
            
            # Parse SVG dimensions for later use
            self.svg_dimensions = self.parse_svg_dimensions(self.current_svg_path)
            
            # Update UI to show SVG is ready
            svg_file_name = Path(self.current_svg_path).name
            svg_size = os.path.getsize(self.current_svg_path) / 1024  # KB
            self.status_bar.config(text=f"✅ SVG ready: {svg_file_name} ({svg_size:.1f} KB) - Ready for tile splitting!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate SVG: {str(e)}")
            self.status_bar.config(text="SVG generation failed")
    
    def convert_gds_to_svg(self, gds_lib, output_path):
        """Convert GDS library to SVG (simplified version of render_image.py logic)"""
        # Get the first cell or top cell
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
    
    def parse_svg_dimensions(self, svg_path):
        """Parse SVG dimensions (simplified version)"""
        try:
            with open(svg_path, 'r') as f:
                content = f.read(8192)  # Read first 8KB for header
            
            import re
            viewbox_match = re.search(r'viewBox="([^"]*)"', content)
            if viewbox_match:
                parts = [float(x) for x in viewbox_match.group(1).split()]
                return {'x': parts[0], 'y': parts[1], 'width': parts[2], 'height': parts[3]}
            
            return {'x': 0, 'y': 0, 'width': 1000, 'height': 1000}
            
        except Exception as e:
            print(f"Error parsing SVG dimensions: {e}")
            return {'x': 0, 'y': 0, 'width': 1000, 'height': 1000}
    
    def get_svg_dimensions(self):
        """Get SVG dimensions for tile calculations"""
        if not self.current_svg_path or not os.path.exists(self.current_svg_path):
            return {'width': 1000, 'height': 1000}
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(self.current_svg_path)
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
    
    def generate_tile_on_demand(self, row, col):
        """Generate a single tile on-demand and cache it"""
        if not self.current_svg_path or not self.grid_config:
            return None
        
        # Create cache key
        cache_key = f"{row}_{col}"
        
        # Check if tile is already cached
        if cache_key in self.tile_cache:
            return self.tile_cache[cache_key]
        
        try:
            # Get SVG viewBox coordinates (same as original working method)
            import xml.etree.ElementTree as ET
            tree = ET.parse(self.current_svg_path)
            root = tree.getroot()
            
            # Get SVG viewBox or width/height (exact same logic as create_tiles)
            viewbox = root.get('viewBox')
            if viewbox:
                viewbox_x, viewbox_y, viewbox_width, viewbox_height = map(float, viewbox.split())
            else:
                viewbox_x, viewbox_y = 0, 0
                viewbox_width = float(root.get('width', '1000').replace('px', ''))
                viewbox_height = float(root.get('height', '1000').replace('px', ''))
            
            # Use ViewBox coordinates (same as original working method)
            svg_x, svg_y = viewbox_x, viewbox_y
            svg_width, svg_height = viewbox_width, viewbox_height
            
            # Calculate tile parameters
            rows, cols = self.grid_config['rows'], self.grid_config['cols']
            overlap = self.grid_config['overlap'] / 100.0
            resolution = self.grid_config.get('resolution', 512)
            
            step_width = svg_width / cols
            step_height = svg_height / rows
            tile_width = step_width * (1 + overlap)
            tile_height = step_height * (1 + overlap)
            
            # Calculate tile position (with viewBox offset, same as original method)
            x = svg_x + col * step_width
            y = svg_y + row * step_height
            
            # Debug output
            print(f"🔍 Generating tile ({row}, {col})")
            print(f"   SVG viewBox: ({svg_x:.1f}, {svg_y:.1f}) {svg_width:.1f}×{svg_height:.1f}")
            print(f"   Tile position: x={x:.1f}, y={y:.1f} (includes viewBox offset)")
            print(f"   Tile size: {tile_width:.1f}×{tile_height:.1f}")
            print(f"   Step size: {step_width:.1f}×{step_height:.1f}")
            print(f"   Coverage: {tile_width/svg_width*100:.1f}% width, {tile_height/svg_height*100:.1f}% height")
            
            # Generate tile using existing methods
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as temp_svg:
                # Create tile SVG
                self.create_svg_tile(self.current_svg_path, temp_svg.name, x, y, tile_width, tile_height)
                temp_svg_path = temp_svg.name
            
            # Convert to PNG in memory
            tile_image = self.convert_svg_to_image(temp_svg_path, resolution)
            
            # Clean up temp file
            os.unlink(temp_svg_path)
            
            if tile_image:
                # Manage cache size
                if len(self.tile_cache) >= self.max_cache_size:
                    # Remove oldest cache entry (FIFO)
                    oldest_key = next(iter(self.tile_cache))
                    del self.tile_cache[oldest_key]
                
                # Cache the tile image
                self.tile_cache[cache_key] = tile_image
                return tile_image
            
        except Exception as e:
            print(f"Error generating tile ({row}, {col}): {e}")
            return None
        
        return None
    
    def convert_svg_to_image(self, svg_path, resolution):
        """Convert SVG to PIL Image and return image object"""
        try:
            import tempfile
            import os
            from PIL import Image
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_png:
                temp_png_path = temp_png.name
            
            # Use existing convert_svg_tile_to_png method
            success = self.convert_svg_tile_to_png(svg_path, temp_png_path, resolution)
            
            if success and os.path.exists(temp_png_path):
                # Load image into memory
                image = Image.open(temp_png_path)
                # Create a copy to avoid file handle issues
                image_copy = image.copy()
                image.close()
                os.unlink(temp_png_path)
                return image_copy
            else:
                if os.path.exists(temp_png_path):
                    os.unlink(temp_png_path)
                return None
            
        except Exception as e:
            print(f"Error converting SVG to image: {e}")
            return None
    
    def create_virtual_tiles(self):
        """Create virtual tile metadata without generating physical files"""
        if not self.grid_config:
            return 0
        
        rows, cols = self.grid_config['rows'], self.grid_config['cols']
        total_tiles = rows * cols
        
        print(f"📋 Creating virtual tile grid: {rows}×{cols} = {total_tiles} tiles")
        return total_tiles
    
    def load_virtual_tiles_data(self):
        """Load virtual tiles data for AI analysis"""
        if not self.grid_config:
            return
        
        self.tiles_data = []
        rows, cols = self.grid_config['rows'], self.grid_config['cols']
        
        for row in range(rows):
            for col in range(cols):
                # Create virtual tile entry (no physical path)
                tile_data = {
                    'filename': f"tile_{row:03d}_{col:03d}.png",
                    'path': None,  # No physical file path
                    'row': row,
                    'col': col,
                    'ai_result': None,
                    'user_classification': None,
                    'analyzed': False,
                    'tile_type': 'virtual',
                    'virtual': True  # Flag to indicate this is a virtual tile
                }
                self.tiles_data.append(tile_data)
        
        print(f"📊 Loaded {len(self.tiles_data)} virtual tiles for on-demand analysis")
        
        if self.tiles_data:
            self.current_tile_index = 0
            self.update_summary()
            
            # Load and display the original layout image
            self.load_original_image()
            
            self.display_current_tile()  # Auto-display the first tile
            print(f"🎯 Auto-displaying virtual tile #1 of {len(self.tiles_data)}")
    
    def load_original_image(self):
        """Load and display the original SVG as background image"""
        import os
        import tempfile
        from PIL import Image
        import numpy as np
        
        if not self.current_svg_path or not os.path.exists(self.current_svg_path):
            return
        
        try:
            # Convert SVG to image for display
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_png:
                temp_png_path = temp_png.name
            
            # Convert SVG to PNG using high resolution for good quality
            success = self.convert_svg_tile_to_png(self.current_svg_path, temp_png_path, 1024)
            
            if success and os.path.exists(temp_png_path):
                # Load image
                image = Image.open(temp_png_path)
                image_array = np.array(image)
                
                # Clear the axes and display the image at full size
                self.ax.clear()
                # Use image pixel coordinates for display (full size)
                self.ax.imshow(image_array, extent=[0, image.width, image.height, 0])
                self.ax.set_aspect('equal')
                self.ax.axis('off')
                
                # Store image info for tile calculations and navigation
                self.original_image_width = image.width
                self.original_image_height = image.height
                self.original_image = image  # Store for navigation
                
                # Update the canvas
                self.canvas.draw_idle()
                self.canvas.flush_events()
                
                print(f"🖼️ Loaded original layout image: {image.width}×{image.height}")
                
                # Clean up temp file
                os.unlink(temp_png_path)
            else:
                print("⚠️ Failed to convert SVG to display image")
                if os.path.exists(temp_png_path):
                    os.unlink(temp_png_path)
                    
        except Exception as e:
            print(f"Error loading original image: {e}")
    
    def split_to_tiles(self):
        """Create virtual tile grid (on-demand generation)"""
        if not self.current_svg_path or not os.path.exists(self.current_svg_path):
            messagebox.showerror("Error", "Please generate SVG first")
            return
        
        try:
            # Get grid configuration
            rows = int(self.grid_rows_var.get())
            cols = int(self.grid_cols_var.get())
            overlap = float(self.overlap_var.get())
            
            if rows < 1 or cols < 1:
                raise ValueError("Grid dimensions must be positive")
            
            if overlap < 0 or overlap > 50:
                raise ValueError("Overlap must be between 0 and 50%")
            
            # Check for very large grids that might cause performance issues
            total_tiles = rows * cols
            if total_tiles > 1000:
                response = messagebox.askyesno(
                    "Large Grid Warning", 
                    f"You're about to create {total_tiles} tiles. This may take a long time and use significant memory.\n\nContinue anyway?",
                    icon='warning'
                )
                if not response:
                    return
            
            self.status_bar.config(text="Splitting SVG into tiles...")
            self.root.update()
            
            # Create tiles directory
            base_name = Path(self.current_svg_path).stem
            self.current_tiles_dir = f"{base_name}_tiles"
            
            # Store grid configuration
            self.grid_config = {
                'rows': rows,
                'cols': cols,
                'overlap': overlap,
                'total_tiles': rows * cols
            }
            
            # Create virtual tiles (no physical files generated)
            resolution = int(getattr(self, 'resolution_var', tk.StringVar(value='512')).get())
            self.grid_config['resolution'] = resolution
            
            tiles_created = self.create_virtual_tiles()
            img_info = self.get_svg_dimensions()
            
            if tiles_created > 0:
                # Final progress update
                self.progress_var.set(100)
                self.root.update()
                
                self.load_virtual_tiles_data()
                
                success_msg = f"✅ Virtual grid: {rows}×{cols} ({total_tiles} tiles) - On-demand generation enabled"
                self.status_bar.config(text=success_msg)
                print(f"💾 Memory cache: Max {self.max_cache_size} tiles")
                
                # Warn if significantly fewer tiles were created than expected
                expected_tiles = rows * cols
                if tiles_created < expected_tiles * 0.5:
                    messagebox.showwarning(
                        "Tile Creation Warning",
                        f"Only {tiles_created} out of {expected_tiles} expected tiles were created.\n\n"
                        f"This usually happens when the grid is too fine for the image size.\n"
                        f"Consider using a smaller grid (e.g., {min(20, rows//2)}×{min(20, cols//2)}) or adding overlap."
                    )
            else:
                # Provide helpful error message
                expected_tiles = rows * cols
                avg_tile_size = min(img_info['width'] // cols, img_info['height'] // rows)
                
                error_msg = f"No tiles were created from {expected_tiles} expected tiles.\n\n"
                error_msg += f"The calculated tile size ({avg_tile_size}×{avg_tile_size} pixels) is too small.\n\n"
                error_msg += "Suggestions:\n"
                error_msg += f"• Use a smaller grid (try {max(5, rows//5)}×{max(5, cols//5)})\n"
                error_msg += "• Add overlap (try 10-20%)\n"
                error_msg += "• Use a higher resolution SVG"
                
                raise ValueError(error_msg)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to split tiles: {str(e)}")
            self.status_bar.config(text="Tile splitting failed")
    
    def create_tiles(self, rows, cols, overlap_percent):
        """Create tiles by splitting SVG directly to preserve vector quality"""
        import xml.etree.ElementTree as ET
        
        # Parse the SVG to get dimensions
        tree = ET.parse(self.current_svg_path)
        root = tree.getroot()
        
        # Get SVG viewBox or width/height
        viewbox = root.get('viewBox')
        if viewbox:
            viewbox_x, viewbox_y, viewbox_width, viewbox_height = map(float, viewbox.split())
        else:
            viewbox_x, viewbox_y = 0, 0
            viewbox_width = float(root.get('width', '1000').replace('px', ''))
            viewbox_height = float(root.get('height', '1000').replace('px', ''))
        
        # Use ViewBox for exact spatial correspondence (user requirement)
        # Each tile shows exactly what appears in that spatial region
        svg_x, svg_y = viewbox_x, viewbox_y
        svg_width, svg_height = viewbox_width, viewbox_height
        
        print(f"📐 Exact spatial division of ViewBox: ({svg_x:.1f}, {svg_y:.1f}) {svg_width:.1f}×{svg_height:.1f}")
        
        # Optional: Analyze content for information only (don't change grid)
        content_bounds = self.analyze_content_bounds(root)
        if content_bounds:
            content_x, content_y, content_width, content_height = content_bounds
            print(f"📊 Content info: ({content_x:.1f}, {content_y:.1f}) {content_width:.1f}×{content_height:.1f}")
            
            # Calculate how much of each tile will have content
            step_width = svg_width / cols
            step_height = svg_height / rows
            empty_tiles = 0
            for row in range(rows):
                for col in range(cols):
                    tile_x = svg_x + col * step_width
                    tile_y = svg_y + row * step_height
                    tile_x_end = tile_x + step_width
                    tile_y_end = tile_y + step_height
                    
                    # Check overlap with content
                    has_content = not (tile_x_end < content_x or tile_x > content_x + content_width or
                                     tile_y_end < content_y or tile_y > content_y + content_height)
                    if not has_content:
                        empty_tiles += 1
            
            if empty_tiles > 0:
                print(f"⚠️  Note: {empty_tiles}/{rows*cols} tiles may be mostly empty (exact spatial division)")
        else:
            print("📊 Content analysis failed, proceeding with ViewBox division")
        
        # Calculate tile dimensions in content coordinates
        overlap_factor = overlap_percent / 100.0
        step_width = svg_width / cols
        step_height = svg_height / rows
        tile_width = step_width * (1 + overlap_factor)
        tile_height = step_height * (1 + overlap_factor)
        
        # Create organized directory structure
        os.makedirs(self.current_tiles_dir, exist_ok=True)
        
        # All tiles go in main directory
        self.content_tiles_dir = None
        self.empty_tiles_dir = None
        
        # Prepare tile tasks for parallel processing
        tile_tasks = []
        resolution = int(self.tile_resolution_var.get())
        min_tile_size = max(10, min(50, min(svg_width / cols, svg_height / rows) * 0.8))
        
        for row in range(rows):
            for col in range(cols):
                # Calculate tile position for exact spatial correspondence
                x = svg_x + col * step_width
                y = svg_y + row * step_height
                
                # Ensure tile doesn't go beyond ViewBox bounds
                actual_tile_width = min(tile_width, svg_x + svg_width - x)
                actual_tile_height = min(tile_height, svg_y + svg_height - y)
                
                if actual_tile_width > min_tile_size and actual_tile_height > min_tile_size:
                    tile_tasks.append({
                        'row': row,
                        'col': col,
                        'x': x,
                        'y': y,
                        'width': actual_tile_width,
                        'height': actual_tile_height,
                        'resolution': resolution,
                        'source_svg': self.current_svg_path,
                        'output_dir': self.current_tiles_dir
                    })
        
        print(f"🚀 Processing {len(tile_tasks)} tiles in parallel...")
        
        # Initialize progress
        self.progress_var.set(0)
        self.status_bar.config(text="Starting tile creation...")
        self.root.update()
        
        # Parallel tile processing
        tiles_created = self.process_tiles_parallel(tile_tasks)
        
        # Create a reference full image for bounding box display
        full_png_path = self.current_svg_path.replace('.svg', '_full.png')
        if self.convert_svg_to_png(self.current_svg_path, full_png_path):
            self.original_image = Image.open(full_png_path)
        
        # Return tiles created and SVG info for error reporting
        svg_info = {'width': svg_width, 'height': svg_height}
        return tiles_created, svg_info
    
    def analyze_content_bounds(self, svg_root):
        """Analyze the actual content bounds in the SVG to avoid empty tiles"""
        try:
            # Find all polygons and get their coordinate bounds
            polygons = svg_root.findall('.//{http://www.w3.org/2000/svg}polygon')
            paths = svg_root.findall('.//{http://www.w3.org/2000/svg}path')
            rects = svg_root.findall('.//{http://www.w3.org/2000/svg}rect')
            
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
                
                # Add small padding to ensure we don't clip content
                padding = 50  # SVG units
                content_x_min -= padding
                content_y_min -= padding
                content_width = (content_x_max - content_x_min) + 2 * padding
                content_height = (content_y_max - content_y_min) + 2 * padding
                
                return (content_x_min, content_y_min, content_width, content_height)
                
        except Exception as e:
            print(f"Warning: Could not analyze content bounds: {e}")
            
        return None
    
    def process_tiles_parallel(self, tile_tasks):
        """Process tiles in parallel using ThreadPoolExecutor"""
        import time
        
        # Get user-configured maximum cores
        try:
            user_max_cores = int(self.max_cores_var.get())
        except (ValueError, AttributeError):
            user_max_cores = min(8, multiprocessing.cpu_count())
        
        # Intelligent worker count based on task complexity and user preference
        if len(tile_tasks) < 10:
            max_workers = min(4, len(tile_tasks), user_max_cores)  # Small grids: fewer workers
        elif len(tile_tasks) < 50:
            max_workers = min(6, user_max_cores)  # Medium grids: moderate workers
        else:
            max_workers = min(8, user_max_cores)  # Large grids: respect user limit
        
        successful_tiles = 0
        failed_tiles = 0
        start_time = time.time()
        
        print(f"📊 Using {max_workers}/{user_max_cores} parallel workers for {len(tile_tasks)} tiles")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tile creation tasks
            future_to_tile = {
                executor.submit(self.create_single_tile, task): task 
                for task in tile_tasks
            }
            
            # Process completed tasks with progress tracking
            for completed, future in enumerate(as_completed(future_to_tile), 1):
                task = future_to_tile[future]
                try:
                    result = future.result()
                    if result['success']:
                        successful_tiles += 1
                    else:
                        failed_tiles += 1
                        
                    # Progress reporting
                    progress = completed / len(tile_tasks) * 100
                    elapsed = time.time() - start_time
                    
                    # Update progress bar
                    self.progress_var.set(progress)
                    
                    # Update status bar
                    if elapsed > 0:
                        rate = completed / elapsed
                        eta = (len(tile_tasks) - completed) / rate if rate > 0 else 0
                        self.status_bar.config(
                            text=f"Creating tiles: {completed}/{len(tile_tasks)} ({progress:.0f}%) - {rate:.1f}/s - ETA: {eta:.0f}s"
                        )
                    else:
                        self.status_bar.config(text=f"Creating tiles: {completed}/{len(tile_tasks)} ({progress:.0f}%)")
                    
                    self.root.update()
                    
                except Exception as e:
                    print(f"Failed to create tile ({task['row']},{task['col']}): {e}")
                    failed_tiles += 1
        
        total_time = time.time() - start_time
        rate = successful_tiles / total_time if total_time > 0 else 0
        
        print(f"✅ Tile creation completed in {total_time:.2f}s ({rate:.1f} tiles/s)")
        print(f"   🟡 Successful tiles: {successful_tiles}")
        if failed_tiles > 0:
            print(f"   ❌ Failed tiles: {failed_tiles}")
        
        # Update final status
        self.progress_var.set(100)
        success_msg = f"✅ Created {successful_tiles} tiles in {total_time:.1f}s"
        if failed_tiles > 0:
            success_msg += f" ({failed_tiles} failed)"
        self.status_bar.config(text=success_msg)
        self.root.update()
        
        return successful_tiles
    
    def create_single_tile(self, task):
        """Create a single tile PNG from SVG viewport"""
        try:
            # Create tile paths
            tile_svg_path = os.path.join(task['output_dir'], f"tile_{task['row']:03d}_{task['col']:03d}.svg")
            tile_png_path = os.path.join(task['output_dir'], f"tile_{task['row']:03d}_{task['col']:03d}.png")
            
            # Create SVG tile with viewport
            self.create_svg_tile(task['source_svg'], tile_svg_path, 
                               task['x'], task['y'], task['width'], task['height'])
            
            # Convert to PNG
            conversion_success = self.convert_svg_tile_to_png(tile_svg_path, tile_png_path, task['resolution'])
            
            if not conversion_success:
                # Clean up and fail
                if os.path.exists(tile_svg_path):
                    os.remove(tile_svg_path)
                return {'success': False, 'row': task['row'], 'col': task['col']}
            
            # Clean up temporary SVG file
            if os.path.exists(tile_svg_path):
                os.remove(tile_svg_path)
            
            # Return success
            return {'success': True, 'row': task['row'], 'col': task['col']}
            
        except Exception as e:
            print(f"Error creating tile {task['row']:03d}_{task['col']:03d}: {e}")
            return {'success': False, 'row': task['row'], 'col': task['col']}
    
    def create_svg_tile(self, source_svg_path, tile_svg_path, x, y, width, height):
        """Create a tile SVG by setting viewBox to crop the region"""
        import xml.etree.ElementTree as ET
        
        # Parse the source SVG
        tree = ET.parse(source_svg_path)
        root = tree.getroot()
        
        # Set the viewBox to crop the desired region
        root.set('viewBox', f"{x} {y} {width} {height}")
        
        # Set the SVG dimensions to match the tile
        root.set('width', str(width))
        root.set('height', str(height))
        
        # Write the tile SVG
        tree.write(tile_svg_path, encoding='utf-8', xml_declaration=True)
    
    def convert_svg_tile_to_png(self, svg_path, png_path, resolution):
        """Convert a single SVG tile to PNG at specified resolution"""
        # Try different conversion methods in order of preference
        conversion_methods = [
            self._convert_with_rsvg,
            self._convert_with_inkscape,
            self._convert_with_browser
        ]
        
        for method_func in conversion_methods:
            try:
                if method_func(svg_path, png_path, resolution):
                    return True
            except Exception:
                continue
        
        return False
    
    def convert_svg_to_png(self, svg_path, png_path):
        """Convert SVG to PNG using multiple fallback methods"""
        import subprocess
        import tempfile
        import re
        
        # Try different conversion methods in order of preference
        conversion_methods = [
            ("rsvg-convert", self._convert_with_rsvg),
            ("inkscape", self._convert_with_inkscape),
            ("browser", self._convert_with_browser),
            ("enhanced_placeholder", self._create_enhanced_placeholder)
        ]
        
        for method_name, method_func in conversion_methods:
            try:
                self.status_bar.config(text=f"Converting with {method_name}...")
                self.root.update()
                
                if method_func(svg_path, png_path, 2048):
                    # Verify the conversion worked
                    if os.path.exists(png_path) and os.path.getsize(png_path) > 1000:
                        print(f"✅ {method_name} conversion successful")
                        return True
                        
            except Exception as e:
                print(f"❌ {method_name} failed: {e}")
                continue
        
        return False
    
    def _convert_with_rsvg(self, svg_path, png_path, resolution=2048):
        """Convert using rsvg-convert"""
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
    
    def _convert_with_inkscape(self, svg_path, png_path, resolution=2048):
        """Convert using Inkscape"""
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
    
    def _convert_with_browser(self, svg_path, png_path, resolution=2048):
        """Convert using headless browser"""
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
    
    def _create_enhanced_placeholder(self, svg_path, png_path, resolution=2048):
        """Create an enhanced placeholder with SVG information"""
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
            border_margin = resolution // 200  # Scale border based on resolution
            draw.rectangle([border_margin, border_margin, resolution-border_margin, resolution-border_margin], outline='red', width=max(1, resolution//400))
            
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
            
            # Draw some geometric patterns to simulate layout
            import random
            random.seed(42)  # Reproducible
            colors = ['blue', 'green', 'purple', 'orange', 'brown']
            
            for i in range(30):
                x1 = random.randint(100, 1800)
                y1 = random.randint(600, 1800)
                x2 = x1 + random.randint(50, 200)
                y2 = y1 + random.randint(50, 200)
                color = random.choice(colors)
                draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
            
            img.save(png_path)
            return True
            
        except Exception as e:
            print(f"Failed to create enhanced placeholder: {e}")
            return False
    
    def load_tiles_data(self):
        """Load information about created tiles for AI analysis"""
        if not self.current_tiles_dir:
            return
        
        self.tiles_data = []
        
        # Load all tiles from main directory
        if not os.path.exists(self.current_tiles_dir):
            print(f"Warning: Tiles directory not found: {self.current_tiles_dir}")
            return
        
        # Get all PNG files in tiles directory
        for filename in sorted(os.listdir(self.current_tiles_dir)):
            if filename.endswith('.png') and filename.startswith('tile_'):
                tile_path = os.path.join(self.current_tiles_dir, filename)
                
                # Parse tile position from filename
                parts = filename.replace('.png', '').split('_')
                if len(parts) >= 3:
                    try:
                        row = int(parts[1])
                        col = int(parts[2])
                        
                        self.tiles_data.append({
                            'filename': filename,
                            'path': tile_path,
                            'row': row,
                            'col': col,
                            'analyzed': False,
                            'ai_result': None,
                            'user_classification': None,
                            'tile_type': 'content'  # Mark as content tile
                        })
                    except ValueError:
                        continue
        
        print(f"📊 Loaded {len(self.tiles_data)} tiles for AI analysis")
        
        if self.tiles_data:
            self.current_tile_index = 0
            self.update_summary()
            # Auto-display the first tile
            self.display_current_tile()
            print(f"🎯 Auto-displaying tile #1 of {len(self.tiles_data)}")
    
    def start_ai_analysis(self):
        """Start AI analysis from current tile index"""
        if not self.tiles_data:
            messagebox.showerror("Error", "Please split SVG into tiles first")
            return
        
        if not self.ai_analyzer or not self.ai_classifier:
            print(f"🔍 Debug: ai_analyzer={self.ai_analyzer}, ai_classifier={self.ai_classifier}")
            api_key = os.getenv('GOOGLE_API_KEY')
            print(f"🔍 Debug: API key available={bool(api_key)}")
            if not api_key:
                messagebox.showerror("API Key Missing", 
                                   "GOOGLE_API_KEY environment variable not set.\n\n"
                                   "Please set your Google API key:\n"
                                   "export GOOGLE_API_KEY=your_api_key\n\n"
                                   "Then restart the application.")
            else:
                messagebox.showerror("AI Models Error", 
                                   "AI models not available.\n\n"
                                   "Check terminal for initialization errors.")
            return
        
        if self.analysis_running:
            messagebox.showinfo("Info", "Analysis already running")
            return
        
        # Show confirmation with start position info
        start_index = getattr(self, 'current_tile_index', 0)
        total_tiles = len(self.tiles_data)
        
        if start_index > 0:
            result = messagebox.askyesno(
                "AI Analysis Start Position", 
                f"Start AI analysis from current tile #{start_index + 1} of {total_tiles}?\n\n"
                f"This will analyze {total_tiles - start_index} remaining tiles.\n"
                f"Click 'No' to start from the beginning."
            )
            if not result:
                start_index = 0
        
        # Store start index for analysis thread
        self.analysis_start_index = start_index
        
        # Start analysis in background thread
        self.analysis_running = True
        self.analysis_paused = False
        self.progress_var.set(0)
        
        # Reset stop/resume button to stop state
        self.stop_resume_button.config(text="⏸️ Stop")
        
        print(f"🤖 Starting AI analysis from tile #{start_index + 1}/{total_tiles}")
        
        analysis_thread = threading.Thread(target=self.run_ai_analysis, daemon=True)
        analysis_thread.start()
    
    def toggle_analysis_state(self):
        """Toggle between stop and resume for AI analysis"""
        if not self.analysis_running:
            # No analysis is running, nothing to stop/resume
            messagebox.showinfo("Info", "No AI analysis is currently running")
            return
        
        if self.analysis_paused:
            # Resume analysis
            self.analysis_paused = False
            self.stop_resume_button.config(text="⏸️ Stop")
            self.analysis_status_label.config(text="AI analysis resumed...")
            print("▶️ AI analysis resumed")
        else:
            # Pause analysis
            self.analysis_paused = True
            self.stop_resume_button.config(text="▶️ Resume")
            self.analysis_status_label.config(text="AI analysis paused - Click Resume to continue")
            print("⏸️ AI analysis paused")
    
    def run_ai_analysis(self):
        """Run AI analysis in background thread"""
        try:
            total_tiles = len(self.tiles_data)
            
            # The prompt from gemini_physical_verification_demo.py
            prompt = """
You are a photonics layout verification expert. Given a cropped image of a photonic integrated circuit (PIC) layout block, your task is to detect and explain any discontinuities in waveguide structures.
📌 Context:
The image is cropped from a larger layout, so cut-off shapes at the image border are not considered discontinuities.

🚨 CRITICAL FIRST STEP - IDENTIFY ACTUAL WAVEGUIDES:
Before analyzing for discontinuities, you MUST first determine if this image contains actual waveguides:
- If you see only repetitive grid patterns, + (plus) shapes, ▭ rectangles, or regular background structures with no clear channel/gap patterns, then there are NO waveguides to analyze → report "continuity"
- Waveguides are hollow channels/gaps between colored material boundaries where light travels
- Background grid elements are NOT waveguides and should be completely ignored
- Only proceed with discontinuity analysis if you can clearly identify actual waveguide channels

In this image:
The colored shapes (e.g., teal) represent drawn material (e.g., silicon).
The waveguide is the entire hollow region between these colored boundaries, where light is guided — this could be white or any other color. However, you must to discriminate waveguide with background.
The waveguide must be relatively smooth and continuous. If there is a mismatch between two connectors, then it is potentially discontinuity. However, if the mismatch appears to be due to a resolution issue, then it is okay, meaning if the other segments are smooth but suddenly one segment is mismatched, then that is the problem.
Tapering is not a discontinuity, meaning that the waveguide tapering smoothly is not a problem. 
🔍 Your Tasks:
Focus on the geometric shape and alignment of the waveguide region (remember to discriminate waveguide with background) — i.e., the gap between the colored boundaries that forms the optical channel.
Do not just check if the area is unbroken. Instead, assess if the waveguide:
Shows any offset, step, or misalignment across tiles or segments. Some misalignment is intentional in design, so if you're sure it's because of design, it's not discontinuity.
Has a sudden change in width or slope, and it's not because of design.
Breaks its smooth curvature or continuity, even if the space looks connected, especially in the connector area.
If you detect a discontinuity:
Describe it clearly (e.g., "step offset in the lower boundary at center", or "break in alignment across stitched tiles")
Remember, it's unacceptable to miss any non-smoothness, if any non-smoothness is found, it's a discontinuity.
If the waveguide is fully continuous and smoothly aligned (no non-smoothness, even smallest found), say so explicitly — but only after verifying smoothness in both shape and position. 
⚠️ Critical Warning:
Do not assume the presence of space means continuity. A slight step or misalignment in shape — even if small — may cause significant optical discontinuity.
Your judgment must focus on geometric alignment and smooth shape continuity, not just presence of empty space.
You must focus on what you can see, do not imagine, assume, or hallucinate.
You must discriminate waveguide and background, they could be the same color, but they are different.
The + (plus, sometime look like T because of crop) and ▭ (rectangle, sometimes look like U or reversed U due to crop) are background, not waveguide, you must ignore them, you must just focus on the waveguide.
Background is not discontinuity.
"""
            
            # Start from specified index (or 0 if not set)
            start_index = getattr(self, 'analysis_start_index', 0)
            
            for i in range(start_index, len(self.tiles_data)):
                if not self.analysis_running:
                    break
                
                # Check for pause state and wait if paused
                while self.analysis_paused and self.analysis_running:
                    import time
                    time.sleep(0.1)  # Wait 100ms before checking again
                
                # Check again if analysis was stopped while paused
                if not self.analysis_running:
                    break
                
                tile_data = self.tiles_data[i]
                
                try:
                    # Load image (on-demand generation for virtual tiles)
                    from PIL import Image
                    if tile_data.get('virtual', False):
                        # Generate tile on-demand for analysis
                        image = self.generate_tile_on_demand(tile_data['row'], tile_data['col'])
                        if image is None:
                            raise Exception("Failed to generate virtual tile for analysis")
                    else:
                        # Load from file path (legacy support)
                        image = Image.open(tile_data['path'])
                    
                    # Step 1: Analyze with Gemini Pro (detailed analysis)
                    response = self.ai_analyzer.generate_content([prompt, image])
                    ai_result = response.text
                    
                    # Step 2: Ask Gemini Flash to classify the result as one word
                    classification_prompt = f"""Based on this photonic layout analysis result, provide EXACTLY ONE WORD classification:

Analysis result: {ai_result}

Instructions:
- If the analysis indicates any discontinuity, misalignment, step, break, gap, or problem, respond with: discontinuity
- If the analysis indicates the waveguide is continuous, smooth, and properly aligned, respond with: continuity
- Respond with ONLY ONE WORD, no explanation, no punctuation, just: discontinuity OR continuity"""
                    
                    classification_response = self.ai_classifier.generate_content([classification_prompt])
                    classification = classification_response.text.strip().lower()
                    
                    # Ensure we get a valid classification
                    if 'discontinuity' in classification:
                        final_classification = 'discontinuity'
                    elif 'continuity' in classification:
                        final_classification = 'continuity'
                    else:
                        # Fallback to original keyword detection
                        result_lower = ai_result.lower()
                        potential_discontinuity = any(word in result_lower for word in [
                            'discontinuity', 'discontinuous', 'step offset', 'misalignment', 
                            'break', 'gap', 'not continuous', 'problem', 'defect'
                        ])
                        final_classification = 'discontinuity' if potential_discontinuity else 'continuity'
                    
                    # Store both detailed result and classification
                    tile_data['ai_result'] = ai_result
                    tile_data['classification'] = final_classification
                    tile_data['analyzed'] = True
                    
                    # Flag tiles with discontinuity
                    if final_classification == 'discontinuity':
                        self.flagged_tiles.append(i)
                    
                    # Update progress (relative to tiles being analyzed)
                    tiles_to_analyze = total_tiles - start_index
                    current_tile_in_batch = i - start_index + 1
                    progress = (current_tile_in_batch / tiles_to_analyze) * 100
                    self.analysis_queue.put(('progress', progress, i + 1, total_tiles, start_index))
                    
                except Exception as e:
                    tile_data['ai_result'] = f"Analysis failed: {str(e)}"
                    tile_data['analyzed'] = True
                    self.analysis_queue.put(('error', str(e)))
            
            self.analysis_queue.put(('complete', len(self.flagged_tiles), start_index, total_tiles))
            
        except Exception as e:
            self.analysis_queue.put(('error', str(e)))
        finally:
            self.analysis_running = False
            self.analysis_paused = False
            # Reset button to initial state
            self.stop_resume_button.config(text="⏸️ Stop")
    
    def check_analysis_queue(self):
        """Check for updates from analysis thread"""
        try:
            while True:
                msg_type, *args = self.analysis_queue.get_nowait()
                
                if msg_type == 'progress':
                    if len(args) >= 4:  # New format with start_index
                        progress, current, total, start_index = args
                        self.progress_var.set(progress)
                        self.analysis_status_label.config(
                            text=f"Analyzing tile {current}/{total} (from #{start_index + 1}, {progress:.1f}%)")
                        
                        # Auto-advance to the tile being analyzed
                        tile_index = current - 1  # Convert to 0-based index
                        if tile_index < len(self.tiles_data) and tile_index != self.current_tile_index:
                            self.current_tile_index = tile_index
                            self.display_current_tile()
                            print(f"🎯 Auto-advanced to tile #{current}")
                            
                    else:  # Old format fallback
                        progress, current, total = args
                        self.progress_var.set(progress)
                        self.analysis_status_label.config(
                            text=f"Analyzing tile {current}/{total} ({progress:.1f}%)")
                        
                        # Auto-advance to the tile being analyzed
                        tile_index = current - 1  # Convert to 0-based index
                        if tile_index < len(self.tiles_data) and tile_index != self.current_tile_index:
                            self.current_tile_index = tile_index
                            self.display_current_tile()
                            print(f"🎯 Auto-advanced to tile #{current}")
                
                elif msg_type == 'complete':
                    if len(args) >= 3:  # New format with start position
                        flagged_count, start_index, total_tiles = args
                        tiles_analyzed = total_tiles - start_index
                        self.analysis_status_label.config(
                            text=f"Analysis complete! {flagged_count} tiles flagged (analyzed {tiles_analyzed} tiles from #{start_index + 1})")
                    else:  # Old format fallback
                        flagged_count = args[0]
                        self.analysis_status_label.config(
                            text=f"Analysis complete! {flagged_count} tiles flagged for review")
                    
                    # Show first flagged tile if any
                    if self.flagged_tiles:
                        self.current_tile_index = self.flagged_tiles[0]
                        self.display_current_tile()
                    
                    self.update_summary()
                
                elif msg_type == 'error':
                    error_msg = args[0]
                    self.analysis_status_label.config(text=f"Analysis error: {error_msg}")
                
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_analysis_queue)
    
    def display_current_tile(self):
        """Display the current tile for user review"""
        if not self.tiles_data or self.current_tile_index >= len(self.tiles_data):
            return
        
        tile_data = self.tiles_data[self.current_tile_index]
        
        try:
            # Load tile image (on-demand generation for virtual tiles)
            if tile_data.get('virtual', False):
                # Generate tile on-demand
                image = self.generate_tile_on_demand(tile_data['row'], tile_data['col'])
                if image is None:
                    raise Exception("Failed to generate virtual tile")
            else:
                # Load from file path (legacy support)
                image = Image.open(tile_data['path'])
            
            # Resize for display
            image = image.resize((300, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            self.tile_image_label.config(image=photo, text="")
            self.tile_image_label.image = photo  # Keep a reference
            
            # Update tile info with AI classification
            info_text = f"Tile ({tile_data['row']}, {tile_data['col']}) - {tile_data['filename']}"
            
            # Add AI classification if available
            if tile_data.get('classification'):
                classification = tile_data['classification']
                if classification == 'discontinuity':
                    info_text += f" - AI: 🔴 DISCONTINUITY"
                else:
                    info_text += f" - AI: 🟢 CONTINUITY"
            
            # Add user classification if available
            if tile_data['user_classification']:
                info_text += f" - User: {tile_data['user_classification']}"
            
            self.tile_info_label.config(text=info_text)
            
            # Update AI result
            self.ai_result_text.delete(1.0, tk.END)
            if tile_data['ai_result']:
                # Show detailed analysis result
                result_text = tile_data['ai_result']
                
                # Add classification summary at the top
                if tile_data.get('classification'):
                    classification = tile_data['classification'].upper()
                    if classification == 'DISCONTINUITY':
                        result_text = f"🔴 AI CLASSIFICATION: {classification}\n\n" + result_text
                    else:
                        result_text = f"🟢 AI CLASSIFICATION: {classification}\n\n" + result_text
                
                self.ai_result_text.insert(1.0, result_text)
            else:
                self.ai_result_text.insert(1.0, "Not analyzed yet")
            
            # Highlight current tile in original image if available
            if self.original_image and self.grid_config:
                self.highlight_tile_in_original(tile_data['row'], tile_data['col'], 
                                               preserve_flagged=self.flagged_tiles_displayed)
            
        except Exception as e:
            self.tile_info_label.config(text=f"Error loading tile: {str(e)}")
    
    def highlight_tile_in_original(self, row, col, preserve_flagged=False):
        """Highlight the specified tile in the original image"""
        if not self.original_image or not self.grid_config:
            return
        
        try:
            # Clear previous plot
            self.ax.clear()
            self.ax.axis('off')
            
            # Display original image
            # Display image at full size using image coordinates
            import numpy as np
            image_array = np.array(self.original_image)
            self.ax.imshow(image_array, extent=[0, self.original_image.width, self.original_image.height, 0], aspect='equal')
            
            # Redraw ROI regions after clearing
            self.redraw_roi_regions()
            
            # Redraw flagged tiles if preserving them
            if preserve_flagged and self.flagged_tiles:
                self.redraw_flagged_tiles()
            
            # Calculate tile position with coordinate transformation
            img_width, img_height = self.original_image.size
            svg_dims = self.get_svg_dimensions()
            svg_width, svg_height = svg_dims['width'], svg_dims['height']
            
            rows, cols = self.grid_config['rows'], self.grid_config['cols']
            overlap = self.grid_config['overlap'] / 100.0
            
            # Calculate in SVG space then transform to image space
            svg_step_width = svg_width / cols
            svg_step_height = svg_height / rows
            
            # Transform to image coordinates for display
            step_width = svg_step_width * (img_width / svg_width)
            step_height = svg_step_height * (img_height / svg_height)
            tile_width = step_width * (1 + overlap)
            tile_height = step_height * (1 + overlap)
            
            x = col * step_width
            y = row * step_height
            
            # Create bounding box
            rect = patches.Rectangle((x, y), tile_width, tile_height,
                                   linewidth=3, edgecolor='red', facecolor='none')
            self.ax.add_patch(rect)
            
            # Add label
            self.ax.text(x + tile_width/2, y - 20, f"Tile ({row}, {col})",
                        ha='center', va='bottom', fontsize=12, color='red',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            self.ax.set_title(f"Original Layout - Highlighting Tile ({row}, {col}) | 🖱️ Click to navigate")
            
            # Update canvas
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error highlighting tile: {e}")
    
    def classify_tile(self, classification):
        """Classify the current tile as continuous or discontinuity"""
        if not self.tiles_data or self.current_tile_index >= len(self.tiles_data):
            return
        
        tile_data = self.tiles_data[self.current_tile_index]
        tile_data['user_classification'] = classification
        
        # Update display
        self.display_current_tile()
        self.update_summary()
        
        # Automatically move to next flagged tile
        self.next_flagged_tile()
    
    def previous_tile(self):
        """Go to previous tile"""
        if self.tiles_data and self.current_tile_index > 0:
            self.current_tile_index -= 1
            self.display_current_tile()
    
    def next_tile(self):
        """Go to next tile"""
        if self.tiles_data and self.current_tile_index < len(self.tiles_data) - 1:
            self.current_tile_index += 1
            self.display_current_tile()
    
    def next_flagged_tile(self):
        """Go to next flagged tile"""
        current_flagged_index = None
        for i, flagged_index in enumerate(self.flagged_tiles):
            if flagged_index == self.current_tile_index:
                current_flagged_index = i
                break
        
        if current_flagged_index is not None and current_flagged_index < len(self.flagged_tiles) - 1:
            self.current_tile_index = self.flagged_tiles[current_flagged_index + 1]
            self.display_current_tile()
    
    def show_all_flagged(self):
        """Show all flagged tiles with bounding boxes"""
        if not self.original_image or not self.grid_config or not self.flagged_tiles:
            return
        
        try:
            # Clear previous plot
            self.ax.clear()
            self.ax.axis('off')
            
            # Display original image
            # Display image at full size using image coordinates
            import numpy as np
            image_array = np.array(self.original_image)
            self.ax.imshow(image_array, extent=[0, self.original_image.width, self.original_image.height, 0], aspect='equal')
            
            # Redraw ROI regions after clearing
            self.redraw_roi_regions()
            
            # Calculate tile dimensions
            img_width, img_height = self.original_image.size
            rows, cols = self.grid_config['rows'], self.grid_config['cols']
            overlap = self.grid_config['overlap'] / 100.0
            
            step_width = img_width // cols
            step_height = img_height // rows
            tile_width = step_width * (1 + overlap)
            tile_height = step_height * (1 + overlap)
            
            # Highlight all flagged tiles
            for flagged_index in self.flagged_tiles:
                tile_data = self.tiles_data[flagged_index]
                row, col = tile_data['row'], tile_data['col']
                
                x = col * step_width
                y = row * step_height
                
                # Color based on user classification
                if tile_data['user_classification'] == 'discontinuity':
                    color = 'red'
                elif tile_data['user_classification'] == 'continuous':
                    color = 'green'
                else:
                    color = 'orange'  # Unclassified
                
                rect = patches.Rectangle((x, y), tile_width, tile_height,
                                       linewidth=2, edgecolor=color, facecolor='none')
                self.ax.add_patch(rect)
            
            self.ax.set_title(f"All Flagged Tiles ({len(self.flagged_tiles)} total) | 🖱️ Click to navigate")
            
            # Set flag to indicate flagged tiles are displayed
            self.flagged_tiles_displayed = True
            
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error showing flagged tiles: {e}")
    
    def clear_highlights(self):
        """Clear all highlights from the original image"""
        if self.original_image:
            self.ax.clear()
            self.ax.axis('off')
            # Display image at full size using image coordinates
            import numpy as np
            image_array = np.array(self.original_image)
            self.ax.imshow(image_array, extent=[0, self.original_image.width, self.original_image.height, 0], aspect='equal')
            
            # Redraw ROI regions after clearing
            self.redraw_roi_regions()
            
            # Reset flagged tiles display state
            self.flagged_tiles_displayed = False
            
            self.ax.set_title("Original Layout | 🖱️ Click on any area to navigate to that tile")
            self.canvas.draw()
    
    def fit_image_to_window(self):
        """Fit the original image to the window"""
        if self.original_image:
            self.ax.set_xlim(0, self.original_image.size[0])
            self.ax.set_ylim(self.original_image.size[1], 0)
            self.canvas.draw()
    
    def on_image_click(self, event):
        """Handle clicks on the original image for navigation or ROI drawing"""
        if not self.original_image:
            return
            
        # Check if click is within the image axes
        if event.inaxes != self.ax:
            return
            
        # Get click coordinates
        click_x, click_y = event.xdata, event.ydata
        if click_x is None or click_y is None:
            return
        
        if self.roi_mode:
            # ROI drawing mode - start drawing
            self.roi_start = (click_x, click_y)
            self.drawing_roi = True
            
            # Reset motion tracking for smooth animation
            if hasattr(self, '_last_preview_pos'):
                delattr(self, '_last_preview_pos')
            
            print(f"🎯 ROI start: ({click_x:.0f}, {click_y:.0f})")
            return
        
        # Navigation mode (when NOT in ROI mode)
        if not self.grid_config or not self.tiles_data:
            return
            
        try:
            # Transform click coordinates from image pixels to SVG coordinates
            # Must account for viewBox offset (same as tile generation)
            img_width, img_height = self.original_image.size
            
            # Get SVG viewBox coordinates (same as tile generation)
            import xml.etree.ElementTree as ET
            tree = ET.parse(self.current_svg_path)
            root = tree.getroot()
            
            viewbox = root.get('viewBox')
            if viewbox:
                viewbox_x, viewbox_y, viewbox_width, viewbox_height = map(float, viewbox.split())
            else:
                viewbox_x, viewbox_y = 0, 0
                viewbox_width = float(root.get('width', '1000').replace('px', ''))
                viewbox_height = float(root.get('height', '1000').replace('px', ''))
            
            svg_x_offset, svg_y_offset = viewbox_x, viewbox_y
            svg_width, svg_height = viewbox_width, viewbox_height
            
            # Transform click coordinates to SVG space (accounting for viewBox offset)
            svg_x = svg_x_offset + click_x * (svg_width / img_width)
            svg_y = svg_y_offset + click_y * (svg_height / img_height)
            
            rows, cols = self.grid_config['rows'], self.grid_config['cols']
            overlap = self.grid_config['overlap'] / 100.0
            
            # Calculate tile dimensions in SVG coordinates (same logic as tile generation)
            step_width = svg_width / cols
            step_height = svg_height / rows
            tile_width = step_width * (1 + overlap)
            tile_height = step_height * (1 + overlap)
            
            # Find which tile contains the click point using SVG coordinates
            # Subtract offset to get relative position within the viewBox
            relative_x = svg_x - svg_x_offset
            relative_y = svg_y - svg_y_offset
            
            clicked_row = int(relative_y // step_height)
            clicked_col = int(relative_x // step_width)
            
            # Debug navigation
            print(f"🖱️ Navigation Debug:")
            print(f"   Click: ({click_x:.1f}, {click_y:.1f}) in image pixels")
            print(f"   SVG viewBox: ({svg_x_offset:.1f}, {svg_y_offset:.1f}) {svg_width:.1f}×{svg_height:.1f}")
            print(f"   Transformed: ({svg_x:.1f}, {svg_y:.1f}) in SVG absolute")
            print(f"   Relative: ({relative_x:.1f}, {relative_y:.1f}) in viewBox")
            print(f"   Grid: {rows}×{cols}, step: {step_width:.1f}×{step_height:.1f}")
            print(f"   Calculated tile: ({clicked_row}, {clicked_col})")
            
            # Clamp to valid range
            clicked_row = max(0, min(clicked_row, rows - 1))
            clicked_col = max(0, min(clicked_col, cols - 1))
            print(f"   Final tile: ({clicked_row}, {clicked_col})")
            
            # Verify the tile generation will use correct coordinates
            expected_x = svg_x_offset + clicked_col * step_width
            expected_y = svg_y_offset + clicked_row * step_height
            print(f"   Expected tile region: x={expected_x:.1f}, y={expected_y:.1f} in SVG absolute")
            
            # Find the tile in tiles_data that matches this position
            target_tile_index = None
            for i, tile_data in enumerate(self.tiles_data):
                if tile_data['row'] == clicked_row and tile_data['col'] == clicked_col:
                    target_tile_index = i
                    break
            
            if target_tile_index is not None:
                # Navigate to the clicked tile
                self.current_tile_index = target_tile_index
                self.display_current_tile()
                print(f"🎯 Clicked navigation: Jumped to tile ({clicked_row}, {clicked_col}) - Index {target_tile_index}")
            else:
                print(f"⚠️ No tile found at position ({clicked_row}, {clicked_col})")
                
        except Exception as e:
            print(f"Error in click navigation: {e}")
    
    def on_image_release(self, event):
        """Handle mouse release for ROI drawing"""
        if not self.roi_mode or not self.drawing_roi or not self.roi_start:
            return
            
        # Check if release is within the image axes
        if event.inaxes != self.ax:
            return
            
        # Get release coordinates
        release_x, release_y = event.xdata, event.ydata
        if release_x is None or release_y is None:
            return
        
        self.roi_end = (release_x, release_y)
        self.drawing_roi = False
        
        # Draw the final ROI rectangle
        self.draw_roi_rectangle()
        
        # Safe debug output
        if self.roi_start and self.roi_end:
            print(f"🎯 ROI complete: ({self.roi_start[0]:.0f}, {self.roi_start[1]:.0f}) to ({self.roi_end[0]:.0f}, {self.roi_end[1]:.0f})")
        else:
            print("🎯 ROI completed (coordinates unavailable)")
    
    def on_image_motion(self, event):
        """Handle mouse motion for smooth ROI preview with throttling"""
        if not self.roi_mode or not self.drawing_roi or not self.roi_start:
            return
            
        # Check if motion is within the image axes
        if event.inaxes != self.ax:
            return
            
        # Get current coordinates
        current_x, current_y = event.xdata, event.ydata
        if current_x is None or current_y is None:
            return
        
        # Throttle updates to reduce lag (only update if moved significantly)
        if hasattr(self, '_last_preview_pos'):
            last_x, last_y = self._last_preview_pos
            # Only update if moved at least 2 pixels to reduce unnecessary redraws
            if abs(current_x - last_x) < 2 and abs(current_y - last_y) < 2:
                return
        
        # Store current position for throttling
        self._last_preview_pos = (current_x, current_y)
        
        # Draw smooth preview rectangle
        self.draw_roi_preview(current_x, current_y)
    
    def toggle_roi_mode(self):
        """Toggle ROI drawing mode for multiple regions"""
        if self.roi_mode:
            # Cancel ROI mode - clear only the preview, keep existing regions
            if self.current_roi_preview:
                self.current_roi_preview.remove()
                self.current_roi_preview = None
            
            self.roi_mode = False
            self.drawing_roi = False
            self.roi_start = None
            self.roi_end = None
            
            self.roi_toggle_button.config(text="📐 Draw ROI")
            self.roi_status_label.config(text="🖱️ Navigation Mode", foreground="green")
            
            # Reset cursor to default for navigation
            self.canvas.get_tk_widget().config(cursor="")
            
            # Force redraw to ensure existing ROI regions remain visible
            self.canvas.draw_idle()
            self.canvas.flush_events()
            
            region_count = len(self.roi_regions)
            print(f"🚫 ROI drawing mode cancelled - Navigation enabled ({region_count} regions preserved)")
        else:
            # Enter ROI mode
            self.roi_mode = True
            self.drawing_roi = False
            self.roi_toggle_button.config(text="🚫 Cancel ROI")
            self.roi_status_label.config(text="📐 Drawing Mode", foreground="blue")
            
            # Change cursor to crosshair for better visual feedback
            self.canvas.get_tk_widget().config(cursor="crosshair")
            
            print("🎯 ROI drawing mode: Click and drag to add regions")
    
    def draw_roi_preview(self, current_x, current_y):
        """Draw smooth preview rectangle while dragging with optimized performance"""
        if not self.roi_start:
            return
            
        # Calculate rectangle parameters first to avoid unnecessary work
        x = min(self.roi_start[0], current_x)
        y = min(self.roi_start[1], current_y)
        width = abs(current_x - self.roi_start[0])
        height = abs(current_y - self.roi_start[1])
        
        # Skip redraw if rectangle is too small (reduces flicker)
        if width < 3 or height < 3:
            return
        
        # Efficient preview update - only remove if we have one
        if self.current_roi_preview:
            self.current_roi_preview.remove()
            self.current_roi_preview = None
        
        # Create smooth preview rectangle with optimized settings
        import matplotlib.patches as patches
        self.current_roi_preview = patches.Rectangle((x, y), width, height,
                                                   linewidth=2, edgecolor='#4A90E2', 
                                                   facecolor='#4A90E2', alpha=0.2,
                                                   linestyle='-', antialiased=True,
                                                   joinstyle='round', capstyle='round')
        self.ax.add_patch(self.current_roi_preview)
        
        # Use blit for super smooth animation (much faster than draw_idle)
        self.canvas.draw_idle()
        self.canvas.flush_events()
    
    def draw_roi_rectangle(self):
        """Draw the final ROI rectangle and add to collection"""
        if not self.roi_start or not self.roi_end:
            return
        
        # Remove preview if exists
        if self.current_roi_preview:
            self.current_roi_preview.remove()
            self.current_roi_preview = None
        
        # Calculate rectangle parameters
        x = min(self.roi_start[0], self.roi_end[0])
        y = min(self.roi_start[1], self.roi_end[1])
        width = abs(self.roi_end[0] - self.roi_start[0])
        height = abs(self.roi_end[1] - self.roi_start[1])
        
        # Only create if rectangle has meaningful size
        if width > 5 and height > 5:
            # Generate smooth color palette with hex codes for better rendering
            color_palette = [
                {'name': 'red', 'hex': '#FF6B6B', 'alpha': 0.18},
                {'name': 'orange', 'hex': '#FF9F43', 'alpha': 0.18},
                {'name': 'yellow', 'hex': '#FFA502', 'alpha': 0.20},
                {'name': 'green', 'hex': '#26DE81', 'alpha': 0.18},
                {'name': 'cyan', 'hex': '#2BCBBA', 'alpha': 0.18},
                {'name': 'blue', 'hex': '#3742FA', 'alpha': 0.18},
                {'name': 'purple', 'hex': '#A55EEA', 'alpha': 0.18},
                {'name': 'pink', 'hex': '#FF3838', 'alpha': 0.18}
            ]
            
            color_info = color_palette[len(self.roi_regions) % len(color_palette)]
            color_name = color_info['name']
            color_hex = color_info['hex']
            color_alpha = color_info['alpha']
            
            # Draw smooth final rectangle with rounded appearance
            import matplotlib.patches as patches
            roi_rectangle = patches.Rectangle((x, y), width, height,
                                            linewidth=2.5, edgecolor=color_hex, 
                                            facecolor=color_hex, alpha=color_alpha,
                                            antialiased=True, joinstyle='round', 
                                            capstyle='round')
            self.ax.add_patch(roi_rectangle)
            
            # Add to ROI regions collection
            roi_data = {
                'id': self.roi_counter,
                'start': self.roi_start,
                'end': self.roi_end,
                'rectangle': roi_rectangle,
                'color': color_name,
                'hex': color_hex,
                'alpha': color_alpha
            }
            self.roi_regions.append(roi_data)
            self.roi_counter += 1
            
            # Update UI
            self.update_roi_count()
            
            print(f"🎯 ROI #{roi_data['id']} added: ({x:.0f}, {y:.0f}) {width:.0f}×{height:.0f} [{color_name}]")
        
        # Reset drawing state but stay in ROI mode for next rectangle
        self.roi_start = None
        self.roi_end = None
        self.drawing_roi = False
        
        # Reset motion tracking for next ROI
        if hasattr(self, '_last_preview_pos'):
            delattr(self, '_last_preview_pos')
        
        # Force smooth canvas update with optimized performance
        self.canvas.draw_idle()
        self.canvas.flush_events()
    
    def update_roi_count(self):
        """Update the ROI count display"""
        count = len(self.roi_regions)
        self.roi_count_label.config(text=f"({count} region{'s' if count != 1 else ''})")
    
    def refresh_roi_display(self):
        """Ensure all ROI regions remain visible on the canvas"""
        # This method ensures ROI regions stay visible during navigation
        # All ROI rectangles should already be added to self.ax, so just refresh
        if self.roi_regions:
            self.canvas.draw_idle()
            self.canvas.flush_events()
            print(f"🔄 Refreshed {len(self.roi_regions)} ROI regions display")
    
    def redraw_roi_regions(self):
        """Redraw all ROI regions after axes clear"""
        if not self.roi_regions:
            return
            
        import matplotlib.patches as patches
        
        # Redraw each ROI region
        for roi_data in self.roi_regions:
            x = min(roi_data['start'][0], roi_data['end'][0])
            y = min(roi_data['start'][1], roi_data['end'][1])
            width = abs(roi_data['end'][0] - roi_data['start'][0])
            height = abs(roi_data['end'][1] - roi_data['start'][1])
            
            # Create new rectangle patch (old one was cleared)
            roi_rectangle = patches.Rectangle((x, y), width, height,
                                            linewidth=2.5, edgecolor=roi_data['hex'], 
                                            facecolor=roi_data['hex'], alpha=roi_data['alpha'],
                                            antialiased=True, joinstyle='round', 
                                            capstyle='round')
            self.ax.add_patch(roi_rectangle)
            
            # Update the reference to the new rectangle
            roi_data['rectangle'] = roi_rectangle
    
    def redraw_flagged_tiles(self):
        """Redraw flagged tile highlights after axes clear"""
        if not self.flagged_tiles or not self.grid_config:
            return
            
        import matplotlib.patches as patches
        
        # Calculate tile dimensions
        img_width, img_height = self.original_image.size
        rows, cols = self.grid_config['rows'], self.grid_config['cols']
        overlap = self.grid_config['overlap'] / 100.0
        
        step_width = img_width // cols
        step_height = img_height // rows
        tile_width = int(step_width * (1 + overlap))
        tile_height = int(step_height * (1 + overlap))
        
        # Redraw each flagged tile
        for tile_index in self.flagged_tiles:
            if tile_index < len(self.tiles_data):
                tile_data = self.tiles_data[tile_index]
                row, col = tile_data['row'], tile_data['col']
                
                # Calculate tile position
                x = col * step_width
                y = row * step_height
                
                # Create highlight rectangle for flagged tile
                rect = patches.Rectangle((x, y), tile_width, tile_height, 
                                       linewidth=3, edgecolor='red', 
                                       facecolor='red', alpha=0.3)
                self.ax.add_patch(rect)
    
    def clear_last_roi(self):
        """Remove the most recently added ROI"""
        if not self.roi_regions:
            print("ℹ️ No ROI regions to remove")
            return
        
        # Remove the last ROI
        last_roi = self.roi_regions.pop()
        last_roi['rectangle'].remove()
        
        self.update_roi_count()
        self.canvas.draw_idle()
        
        print(f"↶ Removed ROI #{last_roi['id']} [{last_roi['color']}]")
    
    def clear_all_roi(self):
        """Clear all ROI regions"""
        if not self.roi_regions:
            print("ℹ️ No ROI regions to clear")
            return
        
        # Remove all ROI rectangles from display
        for roi_data in self.roi_regions:
            roi_data['rectangle'].remove()
        
        # Clear the list
        count = len(self.roi_regions)
        self.roi_regions.clear()
        
        # Reset other state
        if self.current_roi_preview:
            self.current_roi_preview.remove()
            self.current_roi_preview = None
            
        self.roi_start = None
        self.roi_end = None
        self.roi_mode = False
        self.drawing_roi = False
        self.roi_toggle_button.config(text="📐 Draw ROI")
        self.roi_status_label.config(text="🖱️ Navigation Mode", foreground="green")
        
        # Reset tile indices if they exist
        if hasattr(self, 'roi_tile_indices'):
            self.roi_tile_indices = []
        
        self.update_roi_count()
        self.canvas.draw_idle()
        
        print(f"🗑️ Cleared all {count} ROI regions")
    
    def clear_roi(self):
        """Clear the ROI rectangle and reset all ROI state"""
        # Remove visual elements
        if self.roi_rectangle:
            self.roi_rectangle.remove()
            self.roi_rectangle = None
        
        if hasattr(self, 'roi_preview') and self.roi_preview:
            self.roi_preview.remove()
            self.roi_preview = None
            
        # Reset all ROI state variables
        self.roi_start = None
        self.roi_end = None
        self.roi_mode = False
        self.drawing_roi = False
        
        # Reset ROI tile indices if they exist
        if hasattr(self, 'roi_tile_indices'):
            self.roi_tile_indices = []
        
        # Reset button text
        self.roi_toggle_button.config(text="📐 Draw ROI")
        
        # Force canvas redraw
        self.canvas.draw_idle()
        self.canvas.flush_events()
        
        print("🗑️ ROI cleared - ready for new selection")
    
    def analyze_all_roi(self):
        """Analyze tiles within all ROI regions"""
        if not self.roi_regions:
            messagebox.showwarning("Multi-ROI Analysis", "Please draw at least one ROI region first")
            return
            
        if not self.tiles_data:
            messagebox.showerror("Error", "Please split SVG into tiles first")
            return
            
        if not self.ai_analyzer or not self.ai_classifier:
            messagebox.showerror("Error", "AI models not available")
            return
        
        # Collect all tiles that overlap with any ROI region
        all_roi_tiles = set()  # Use set to avoid duplicates
        
        img_width, img_height = self.original_image.size
        rows, cols = self.grid_config['rows'], self.grid_config['cols']
        overlap = self.grid_config['overlap'] / 100.0
        
        step_width = img_width / cols
        step_height = img_height / rows
        tile_width = step_width * (1 + overlap)
        tile_height = step_height * (1 + overlap)
        
        roi_details = []
        
        # Process each ROI region
        for roi_idx, roi_data in enumerate(self.roi_regions):
            roi_x_min = min(roi_data['start'][0], roi_data['end'][0])
            roi_x_max = max(roi_data['start'][0], roi_data['end'][0])
            roi_y_min = min(roi_data['start'][1], roi_data['end'][1])
            roi_y_max = max(roi_data['start'][1], roi_data['end'][1])
            
            roi_tiles_for_this_region = []
            
            # Find tiles for this specific ROI
            for i, tile_data in enumerate(self.tiles_data):
                row, col = tile_data['row'], tile_data['col']
                
                # Calculate tile bounds
                tile_x_min = col * step_width
                tile_x_max = tile_x_min + tile_width
                tile_y_min = row * step_height
                tile_y_max = tile_y_min + tile_height
                
                # Check overlap with this ROI
                x_overlap = not (tile_x_max <= roi_x_min or tile_x_min >= roi_x_max)
                y_overlap = not (tile_y_max <= roi_y_min or tile_y_min >= roi_y_max)
                
                if x_overlap and y_overlap:
                    all_roi_tiles.add(i)
                    roi_tiles_for_this_region.append(i)
            
            roi_details.append({
                'id': roi_data['id'],
                'color': roi_data['color'], 
                'tiles': roi_tiles_for_this_region,
                'bounds': (roi_x_min, roi_y_min, roi_x_max, roi_y_max)
            })
        
        all_roi_tiles = sorted(list(all_roi_tiles))  # Convert back to sorted list
        
        if not all_roi_tiles:
            messagebox.showwarning("Multi-ROI Analysis", "No tiles found within any of the selected regions")
            return
        
        # Show summary and confirm
        summary_text = f"Analyze {len(all_roi_tiles)} tiles across {len(self.roi_regions)} ROI regions?\\n\\n"
        for roi_detail in roi_details:
            summary_text += f"ROI #{roi_detail['id']} [{roi_detail['color']}]: {len(roi_detail['tiles'])} tiles\\n"
        
        result = messagebox.askyesno("Multi-ROI Analysis", summary_text)
        
        if result:
            # Store all ROI tiles and start analysis
            self.roi_tile_indices = all_roi_tiles
            self.start_roi_analysis()
    
    def analyze_roi(self):
        """Analyze only tiles within the ROI region"""
        if not self.roi_start or not self.roi_end:
            messagebox.showwarning("ROI Analysis", "Please draw a ROI rectangle first")
            return
            
        if not self.tiles_data:
            messagebox.showerror("Error", "Please split SVG into tiles first")
            return
            
        if not self.ai_analyzer or not self.ai_classifier:
            messagebox.showerror("Error", "AI models not available")
            return
        
        # Calculate ROI bounds
        roi_x_min = min(self.roi_start[0], self.roi_end[0])
        roi_x_max = max(self.roi_start[0], self.roi_end[0])
        roi_y_min = min(self.roi_start[1], self.roi_end[1])
        roi_y_max = max(self.roi_start[1], self.roi_end[1])
        
        # Find tiles that overlap with ROI (even partially)
        roi_tiles = []
        img_width, img_height = self.original_image.size
        rows, cols = self.grid_config['rows'], self.grid_config['cols']
        overlap = self.grid_config['overlap'] / 100.0
        
        step_width = img_width / cols
        step_height = img_height / rows
        tile_width = step_width * (1 + overlap)
        tile_height = step_height * (1 + overlap)
        
        for i, tile_data in enumerate(self.tiles_data):
            row, col = tile_data['row'], tile_data['col']
            
            # Calculate tile bounds (including overlap)
            tile_x_min = col * step_width
            tile_x_max = tile_x_min + tile_width
            tile_y_min = row * step_height
            tile_y_max = tile_y_min + tile_height
            
            # Check if tile rectangle overlaps with ROI rectangle
            # Two rectangles overlap if they intersect on both X and Y axes
            x_overlap = not (tile_x_max <= roi_x_min or tile_x_min >= roi_x_max)
            y_overlap = not (tile_y_max <= roi_y_min or tile_y_min >= roi_y_max)
            
            if x_overlap and y_overlap:
                roi_tiles.append(i)
        
        if not roi_tiles:
            messagebox.showwarning("ROI Analysis", "No tiles found within the selected region")
            return
        
        # Confirm ROI analysis
        result = messagebox.askyesno(
            "ROI Analysis", 
            f"Analyze {len(roi_tiles)} tiles within the selected region?\n\n"
            f"This will analyze only the tiles inside the red rectangle."
        )
        
        if result:
            # Store ROI tiles and start analysis
            self.roi_tile_indices = roi_tiles
            self.start_roi_analysis()
    
    def start_roi_analysis(self):
        """Start AI analysis for ROI tiles only"""
        if self.analysis_running:
            messagebox.showinfo("Info", "Analysis already running")
            return
        
        # Start analysis in background thread
        self.analysis_running = True
        self.analysis_paused = False
        self.progress_var.set(0)
        
        # Reset stop/resume button to stop state
        self.stop_resume_button.config(text="⏸️ Stop")
        
        print(f"🎯 Starting ROI analysis on {len(self.roi_tile_indices)} tiles")
        
        analysis_thread = threading.Thread(target=self.run_roi_analysis, daemon=True)
        analysis_thread.start()
    
    def run_roi_analysis(self):
        """Run AI analysis on ROI tiles in parallel"""
        try:
            roi_tiles_count = len(self.roi_tile_indices)
            
            # Determine optimal number of parallel workers
            try: 
                user_max_cores = int(self.max_cores_var.get())
            except (ValueError, AttributeError): 
                user_max_cores = min(8, multiprocessing.cpu_count())
            
            # Scale workers based on ROI size
            if roi_tiles_count < 5:
                max_workers = min(2, roi_tiles_count, user_max_cores)
            elif roi_tiles_count < 20:
                max_workers = min(4, user_max_cores)
            else:
                max_workers = min(6, user_max_cores)
            
            print(f"🚀 ROI Analysis: Using {max_workers}/{user_max_cores} parallel workers for {roi_tiles_count} tiles")
            
            # Create analysis tasks
            analysis_tasks = []
            for idx, tile_index in enumerate(self.roi_tile_indices):
                task = {
                    'tile_index': tile_index,
                    'roi_idx': idx,
                    'tile_data': self.tiles_data[tile_index]
                }
                analysis_tasks.append(task)
            
            # Process tiles in parallel
            from concurrent.futures import ThreadPoolExecutor, as_completed
            import time
            
            successful_analyses = 0
            failed_analyses = 0
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all analysis tasks
                future_to_task = {
                    executor.submit(self.analyze_single_roi_tile, task): task 
                    for task in analysis_tasks
                }
                
                # Process completed analyses
                for completed, future in enumerate(as_completed(future_to_task), 1):
                    if not self.analysis_running:
                        break
                        
                    task = future_to_task[future]
                    
                    try:
                        result = future.result()
                        
                        if result['success']:
                            successful_analyses += 1
                            
                            # Update tile data
                            tile_data = self.tiles_data[result['tile_index']]
                            tile_data['ai_result'] = result['ai_result']
                            tile_data['classification'] = result['classification']
                            tile_data['analyzed'] = True
                            
                            # Flag tiles with discontinuity
                            if result['classification'] == 'discontinuity':
                                if result['tile_index'] not in self.flagged_tiles:
                                    self.flagged_tiles.append(result['tile_index'])
                        else:
                            failed_analyses += 1
                            # Update with error
                            tile_data = self.tiles_data[result['tile_index']]
                            tile_data['ai_result'] = result.get('error', 'Analysis failed')
                            tile_data['analyzed'] = True
                        
                        # Update progress
                        progress = (completed / roi_tiles_count) * 100
                        self.analysis_queue.put(('progress', progress, result['tile_index'] + 1, len(self.tiles_data), 0))
                        
                    except Exception as e:
                        failed_analyses += 1
                        print(f"Error processing ROI tile {task['tile_index']}: {e}")
                        self.analysis_queue.put(('error', str(e)))
            
            # Report results
            total_time = time.time() - start_time
            analysis_rate = successful_analyses / total_time if total_time > 0 else 0
            
            print(f"⚡ ROI Analysis completed in {total_time:.2f}s ({analysis_rate:.1f} tiles/s)")
            print(f"   ✅ Successful: {successful_analyses}")
            if failed_analyses > 0:
                print(f"   ❌ Failed: {failed_analyses}")
            
            # Count flagged tiles in ROI
            roi_flagged = sum(1 for i in self.roi_tile_indices if i in self.flagged_tiles)
            self.analysis_queue.put(('complete', roi_flagged, 0, roi_tiles_count))
            
        except Exception as e:
            self.analysis_queue.put(('error', str(e)))
        finally:
            self.analysis_running = False
            self.analysis_paused = False
            # Reset button to initial state
            self.stop_resume_button.config(text="⏸️ Stop")
    
    def analyze_single_roi_tile(self, task):
        """Analyze a single ROI tile (called by parallel workers)"""
        tile_index = task['tile_index']
        tile_data = task['tile_data']
        
        # Check if analysis should stop
        if not self.analysis_running:
            return {'success': False, 'tile_index': tile_index, 'error': 'Analysis stopped'}
        
        # Check for pause state and wait if paused
        while self.analysis_paused and self.analysis_running:
            import time
            time.sleep(0.1)
        
        # Check again if analysis was stopped while paused
        if not self.analysis_running:
            return {'success': False, 'tile_index': tile_index, 'error': 'Analysis stopped'}
        
        try:
            # AI analysis prompt (same as original)
            prompt = """
You are a photonics layout verification expert. Given a cropped image of a photonic integrated circuit (PIC) layout block, your task is to detect and explain any discontinuities in waveguide structures.
📌 Context:
The image is cropped from a larger layout, so cut-off shapes at the image border are not considered discontinuities.

🚨 CRITICAL FIRST STEP - IDENTIFY ACTUAL WAVEGUIDES:
Before analyzing for discontinuities, you MUST first determine if this image contains actual waveguides:
- If you see only repetitive grid patterns, + (plus) shapes, ▭ rectangles, or regular background structures with no clear channel/gap patterns, then there are NO waveguides to analyze → report "continuity"
- Waveguides are hollow channels/gaps between colored material boundaries where light travels
- Background grid elements are NOT waveguides and should be completely ignored
- Only proceed with discontinuity analysis if you can clearly identify actual waveguide channels

In this image:
The colored shapes (e.g., teal) represent drawn material (e.g., silicon).
The waveguide is the entire hollow region between these colored boundaries, where light is guided — this could be white or any other color. However, you must to discriminate waveguide with background.
The waveguide must be relatively smooth and continuous. If there is a mismatch between two connectors, then it is potentially discontinuity. However, if the mismatch appears to be due to a resolution issue, then it is okay, meaning if the other segments are smooth but suddenly one segment is mismatched, then that is the problem.
Tapering is not a discontinuity, meaning that the waveguide tapering smoothly is not a problem. 
🔍 Your Tasks:
Focus on the geometric shape and alignment of the waveguide region (remember to discriminate waveguide with background) — i.e., the gap between the colored boundaries that forms the optical channel.
Do not just check if the area is unbroken. Instead, assess if the waveguide:
Shows any offset, step, or misalignment across tiles or segments. Some misalignment is intentional in design, so if you're sure it's because of design, it's not discontinuity.
Has a sudden change in width or slope, and it's not because of design.
Breaks its smooth curvature or continuity, even if the space looks connected, especially in the connector area.
If you detect a discontinuity:
Describe it clearly (e.g., "step offset in the lower boundary at center", or "break in alignment across stitched tiles")
Remember, it's unacceptable to miss any non-smoothness, if any non-smoothness is found, it's a discontinuity.
If the waveguide is fully continuous and smoothly aligned (no non-smoothness, even smallest found), say so explicitly — but only after verifying smoothness in both shape and position. 
⚠️ Critical Warning:
Do not assume the presence of space means continuity. A slight step or misalignment in shape — even if small — may cause significant optical discontinuity.
Your judgment must focus on geometric alignment and smooth shape continuity, not just presence of empty space.
You must focus on what you can see, do not imagine, assume, or hallucinate.
You must discriminate waveguide and background, they could be the same color, but they are different.
The + shapes and rectangle shapes are background, not waveguide, please ignore them, just focus on the waveguide.
"""
            
            # Load image (on-demand generation for virtual tiles)
            from PIL import Image
            if tile_data.get('virtual', False):
                # Generate tile on-demand for analysis
                image = self.generate_tile_on_demand(tile_data['row'], tile_data['col'])
                if image is None:
                    raise Exception("Failed to generate virtual tile for analysis")
            else:
                # Load from file path (legacy support)
                image = Image.open(tile_data['path'])
            
            # Step 1: Analyze with Gemini Pro (detailed analysis)
            response = self.ai_analyzer.generate_content([prompt, image])
            ai_result = response.text
            
            # Step 2: Ask Gemini Flash to classify the result as one word
            classification_prompt = f"""Based on this photonic layout analysis result, provide EXACTLY ONE WORD classification:

Analysis result: {ai_result}

Instructions:
- If the analysis indicates there are no waveguides, respond with: continuity
- If the analysis indicates any discontinuity, misalignment, step, break, gap, or problem, respond with: discontinuity
- If the analysis indicates the waveguide is continuous, smooth, and properly aligned, respond with: continuity
- Respond with ONLY ONE WORD, no explanation, no punctuation, just: discontinuity OR continuity"""
            
            classification_response = self.ai_classifier.generate_content([classification_prompt])
            classification = classification_response.text.strip().lower()
            
            # Ensure we get a valid classification
            if 'discontinuity' in classification:
                final_classification = 'discontinuity'
            elif 'continuity' in classification:
                final_classification = 'continuity'
            else:
                # Fallback to original keyword detection
                result_lower = ai_result.lower()
                potential_discontinuity = any(word in result_lower for word in [
                    'discontinuity', 'discontinuous', 'step offset', 'misalignment', 
                    'break', 'gap', 'not continuous', 'problem', 'defect'
                ])
                final_classification = 'discontinuity' if potential_discontinuity else 'continuity'
            
            return {
                'success': True,
                'tile_index': tile_index,
                'ai_result': ai_result,
                'classification': final_classification
            }
            
        except Exception as e:
            return {
                'success': False,
                'tile_index': tile_index,
                'error': f"Analysis failed: {str(e)}"
            }
    
    def update_summary(self):
        """Update the analysis summary"""
        if not self.tiles_data:
            self.summary_label.config(text="No tiles created")
            return
        
        total_tiles = len(self.tiles_data)
        analyzed_tiles = sum(1 for tile in self.tiles_data if tile['analyzed'])
        flagged_tiles = len(self.flagged_tiles)
        
        classified_continuous = sum(1 for tile in self.tiles_data 
                                  if tile['user_classification'] == 'continuous')
        classified_discontinuity = sum(1 for tile in self.tiles_data 
                                     if tile['user_classification'] == 'discontinuity')
        
        summary_text = (f"Total: {total_tiles} tiles | "
                       f"Analyzed: {analyzed_tiles} | "
                       f"Flagged: {flagged_tiles} | "
                       f"Continuous: {classified_continuous} | "
                       f"Discontinuity: {classified_discontinuity}")
        
        self.summary_label.config(text=summary_text)
    
    def export_results(self):
        """Export analysis results to a file"""
        if not self.tiles_data:
            messagebox.showinfo("Info", "No results to export")
            return
        
        try:
            # Prepare results data
            results = {
                'gds_file': self.current_gds_path,
                'svg_file': self.current_svg_path,
                'grid_config': self.grid_config,
                'analysis_summary': {
                    'total_tiles': len(self.tiles_data),
                    'flagged_tiles': len(self.flagged_tiles),
                    'classified_continuous': sum(1 for tile in self.tiles_data 
                                               if tile['user_classification'] == 'continuous'),
                    'classified_discontinuity': sum(1 for tile in self.tiles_data 
                                                  if tile['user_classification'] == 'discontinuity')
                },
                'tiles': []
            }
            
            # Add tile details
            for i, tile in enumerate(self.tiles_data):
                tile_result = {
                    'index': i,
                    'filename': tile['filename'],
                    'row': tile['row'],
                    'col': tile['col'],
                    'analyzed': tile['analyzed'],
                    'flagged': i in self.flagged_tiles,
                    'user_classification': tile['user_classification'],
                    'ai_result': tile['ai_result']
                }
                results['tiles'].append(tile_result)
            
            # Save to file
            output_file = filedialog.asksaveasfilename(
                title="Save Analysis Results",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
                
                messagebox.showinfo("Success", f"Results exported to {output_file}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")


def main():
    """Main application entry point"""
    root = tk.Tk()
    
    # Configure button styles
    style = ttk.Style()
    style.configure('Success.TButton', foreground='green')
    style.configure('Warning.TButton', foreground='red')
    
    app = LayoutVerificationApp(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (1400 // 2)
    y = (root.winfo_screenheight() // 2) - (900 // 2)
    root.geometry(f"1400x900+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
