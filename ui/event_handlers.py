"""
Event Handlers Module
=====================

Event handlers that bridge UI components and core business logic.
"""

from pathlib import Path
from typing import Optional, Callable
import tkinter as tk
from tkinter import messagebox
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.file_manager import GDSLoader, SVGConverter, SVGParser
from core.tile_system import TileGenerator, TileCache
from core.ai_analyzer import GeminiClient, AnalysisEngine
from core.roi_manager import ROIStorage, ROICalculator
from core.app_state import StateManager, ApplicationState


class EventHandlers:
    """
    Event handlers for the layout verification application.
    
    This class acts as a bridge between UI components and core business logic,
    handling all user interactions and coordinating between modules.
    """
    
    def __init__(
        self,
        state_manager: StateManager,
        gds_loader: GDSLoader,
        svg_converter: SVGConverter,
        svg_parser: SVGParser,
        tile_generator: TileGenerator,
        tile_cache: TileCache,
        gemini_client: Optional[GeminiClient],
        analysis_engine: Optional[AnalysisEngine],
        roi_storage: ROIStorage,
        roi_calculator: ROICalculator
    ):
        """
        Initialize event handlers.
        
        Args:
            state_manager: Application state manager
            gds_loader: GDS file loader
            svg_converter: SVG converter
            svg_parser: SVG parser
            tile_generator: Tile generator
            tile_cache: Tile cache
            gemini_client: Gemini AI client (optional)
            analysis_engine: AI analysis engine (optional)
            roi_storage: ROI storage
            roi_calculator: ROI calculator
        """
        self.state = state_manager
        self.gds_loader = gds_loader
        self.svg_converter = svg_converter
        self.svg_parser = svg_parser
        self.tile_gen = tile_generator
        self.tile_cache = tile_cache
        self.gemini = gemini_client
        self.analyzer = analysis_engine
        self.roi_storage = roi_storage
        self.roi_calc = roi_calculator
        
        # UI update callbacks (set by UI components)
        self.ui_callbacks = {
            'update_file_info': None,
            'update_status': None,
            'update_grid_info': None,
            'set_progress': None,
            # 'append_result': None,  # Removed - detailed results no longer displayed
            'display_image': None,
            'enable_roi_selection': None,
            'disable_roi_selection': None,
            'add_roi_to_list': None,
            'update_summary': None,
            'display_tile_review': None,
            'update_tile_status': None,
            'clear_tile_status': None,
        }
        
        # Processing state
        self.processing = False
        self.executor: Optional[ThreadPoolExecutor] = None
        
    def bind_ui_callback(self, name: str, callback: Callable):
        """
        Bind a UI update callback.
        
        Args:
            name: Callback name
            callback: Callback function
        """
        if name in self.ui_callbacks:
            self.ui_callbacks[name] = callback
    
    def _call_ui(self, name: str, *args, **kwargs):
        """
        Call a UI callback if bound.
        
        Args:
            name: Callback name
            *args, **kwargs: Arguments to pass
        """
        if self.ui_callbacks.get(name):
            self.ui_callbacks[name](*args, **kwargs)
    
    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================
    
    def handle_load_gds(self, file_path: str):
        """
        Handle GDS file loading.
        
        Args:
            file_path: Path to GDS file
        """
        try:
            # Update UI
            self._call_ui('update_status', "Loading GDS file...")
            self._call_ui('update_file_info', file_path)
            
            # Load GDS
            gds_lib = self.gds_loader.load_gds(file_path)
            
            # Update state
            self.state.set_gds_path(file_path)
            
            # Clear previous state
            self.state.reset()
            self.state.set_gds_path(file_path)  # Re-set after reset
            
            # Auto-generate SVG
            self._call_ui('update_status', "Converting to SVG...")
            self.handle_generate_svg(gds_lib, file_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GDS: {str(e)}")
            self._call_ui('update_status', f"Error: {str(e)}")
    
    def handle_generate_svg(self, gds_lib, gds_path: str):
        """
        Handle SVG generation from GDS.
        
        Args:
            gds_lib: GDS library object
            gds_path: Path to GDS file
        """
        try:
            # Generate SVG
            svg_path = self.svg_converter.convert_gds_to_svg(
                gds_lib,
                gds_path,
                output_dir="./"
            )
            
            # Update state
            self.state.set_svg_path(svg_path)
            
            # Parse dimensions
            dimensions = self.svg_parser.parse_dimensions(svg_path)
            
            # Update UI
            self._call_ui('update_status', f"✅ SVG ready: {Path(svg_path).name}")
            
            # Load full SVG image for display (optional - may need rsvg-convert)
            try:
                # For now, just show success message
                # Loading full SVG would require SVG to PNG conversion
                pass
            except Exception as e:
                print(f"Warning: Could not load SVG for display: {e}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate SVG: {str(e)}")
            self._call_ui('update_status', f"Error: {str(e)}")
    
    # ========================================================================
    # GRID OPERATIONS
    # ========================================================================
    
    def handle_generate_grid(self, rows: int, cols: int, overlap: int):
        """
        Handle virtual grid generation.
        
        Args:
            rows: Number of rows
            cols: Number of columns
            overlap: Overlap in pixels
        """
        try:
            svg_path = self.state.get_svg_path()
            if not svg_path:
                messagebox.showerror("Error", "Please load a GDS file first")
                return
            
            self._call_ui('update_status', f"Creating {rows}x{cols} virtual grid...")
            
            # Create virtual grid
            grid_config = self.state.create_grid_config(rows, cols, overlap)
            
            # Create virtual tiles metadata
            tiles_data = self.tile_gen.create_virtual_tiles(grid_config)
            self.state.set_tiles_data(tiles_data)
            
            # Load and display the full layout image with grid overlay
            try:
                # Try to load the SVG as an image for display
                from PIL import Image
                import tempfile
                import os
                
                # Convert SVG to PNG for display
                temp_png = tempfile.mktemp(suffix='.png')
                
                # Try using rsvg-convert or inkscape
                result = self.svg_converter.svg_to_png(svg_path, temp_png, resolution=2048)
                
                if result and os.path.exists(temp_png):
                    image = Image.open(temp_png)
                    # Display image with grid overlay and SVG dimensions
                    svg_dimensions = self.svg_parser.parse_dimensions(svg_path)
                    self._call_ui('display_image', image, grid_config, svg_dimensions)
                    os.unlink(temp_png)
                    print(f"✅ Layout displayed with {rows}x{cols} tile grid overlay")
                else:
                    print("⚠️  Could not display layout (install rsvg-convert or inkscape)")
            except Exception as e:
                print(f"⚠️  Could not display layout image: {e}")
            
            # Clear any previous tile status overlays
            self._call_ui('clear_tile_status')

            # Update UI
            self._call_ui('update_grid_info', f"Grid: {rows}x{cols} ({rows*cols} virtual tiles)")
            self._call_ui('update_status', f"✅ Virtual grid created: {rows}x{cols} - Draw ROI or process tiles")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create grid: {str(e)}")
            self._call_ui('update_status', f"Error: {str(e)}")
    
    # ========================================================================
    # PROCESSING OPERATIONS
    # ========================================================================
    
    def handle_process_all_tiles(self):
        """Handle processing all tiles with AI analysis"""
        if not self.gemini or not self.analyzer:
            messagebox.showerror("Error", "AI analyzer not initialized")
            return
        
        grid_config = self.state.state.grid_config
        if not grid_config:
            messagebox.showerror("Error", "Please create a grid first")
            return
        
        # Start processing all tiles
        self.processing = True
        self.selected_tiles = None  # Process all
        self._call_ui('update_status', "Processing all tiles...")
        
        # Process in background thread
        import threading
        thread = threading.Thread(target=self._process_tiles_worker, daemon=True)
        thread.start()
    
    def handle_process_roi_tiles(self):
        """Handle processing only tiles that overlap with ROI regions"""
        if not self.gemini or not self.analyzer:
            messagebox.showerror("Error", "AI analyzer not initialized")
            return
        
        grid_config = self.state.state.grid_config
        if not grid_config:
            messagebox.showerror("Error", "Please create a grid first")
            return
        
        # Get ROI regions
        roi_regions = self.roi_storage.get_all()
        if not roi_regions:
            messagebox.showwarning("Warning", "No ROI regions selected. Please draw ROI rectangles first.")
            return
        
        # Get image size (use SVG dimensions or default)
        svg_path = self.state.get_svg_path()
        if not svg_path:
            messagebox.showerror("Error", "No SVG file loaded")
            return
        
        # Get SVG dimensions (original coordinates)
        dimensions = self.svg_parser.parse_dimensions(svg_path)
        svg_width = int(dimensions['width'])
        svg_height = int(dimensions['height'])
        image_size = (svg_width, svg_height)

        print(f"📐 Original SVG dimensions: {svg_width}×{svg_height}")

        # Get tiles that overlap with ROI
        tiles_data = self.state.state.tiles_data
        if not tiles_data:
            # Create virtual tiles if not already created
            tiles_data = self.tile_gen.create_virtual_tiles(grid_config)
            self.state.set_tiles_data(tiles_data)
        
        selected_tile_indices = self.roi_calc.get_tiles_in_all_rois(
            roi_regions, tiles_data, grid_config, image_size
        )
        
        if not selected_tile_indices:
            messagebox.showwarning("Warning", "No tiles overlap with selected ROI regions")
            return
        
        # Confirm
        result = messagebox.askyesno(
            "Process Selected Regions",
            f"Process {len(selected_tile_indices)} tiles that overlap with ROI regions?\n\n"
            f"Only tiles overlapping with your drawn rectangles will be analyzed."
        )
        
        if not result:
            return
        
        # Start processing selected tiles
        self.processing = True
        self.selected_tiles = selected_tile_indices
        self._call_ui('update_status', f"Processing {len(selected_tile_indices)} ROI tiles...")
        
        # Process in background thread
        import threading
        thread = threading.Thread(target=self._process_tiles_worker, daemon=True)
        thread.start()
    
    def _process_tiles_worker(self):
        """Worker thread for tile processing"""
        try:
            grid_config = self.state.state.grid_config
            rows, cols = grid_config.rows, grid_config.cols
            
            # Determine which tiles to process
            if self.selected_tiles is not None:
                # Process only selected tiles
                tiles_to_process = self.selected_tiles
            else:
                # Process all tiles
                tiles_to_process = list(range(rows * cols))
            
            total_tiles = len(tiles_to_process)
            
            # Create thread pool
            max_workers = 4  # Parallel processing
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            
            # Create tasks
            tasks = []
            for tile_index in tiles_to_process:
                if not self.processing:
                    break
                
                row = tile_index // cols
                col = tile_index % cols
                
                future = self.executor.submit(self._process_single_tile, row, col)
                tasks.append((future, row, col))
            
            # Wait for completion
            completed = 0
            issues_count = 0
            clean_count = 0
            start_time = time.time()
            
            for future, row, col in tasks:
                if not self.processing:
                    break
                
                try:
                    result = future.result()
                    completed += 1
                    
                    if result and result.get('has_issues'):
                        issues_count += 1
                    else:
                        clean_count += 1
                    
                    # Update progress
                    progress = int((completed / total_tiles) * 100)
                    elapsed = time.time() - start_time
                    
                    self._call_ui('set_progress', progress, 100)
                    self._call_ui('update_status', f"Processing: {completed}/{total_tiles}")
                    self._call_ui('update_summary', completed, issues_count, clean_count, elapsed)
                    
                except Exception as e:
                    print(f"Error processing tile ({row}, {col}): {e}")
            
            # Cleanup
            self.executor.shutdown(wait=False)
            self.executor = None
            self.processing = False
            
            # Final update
            elapsed = time.time() - start_time
            self._call_ui('update_status', f"✅ Processing complete: {completed}/{total_tiles}")
            self._call_ui('update_summary', completed, issues_count, clean_count, elapsed)
            
        except Exception as e:
            print(f"Error in processing worker: {e}")
            self.processing = False
            self._call_ui('update_status', f"Error: {str(e)}")
    
    def _process_single_tile(self, row: int, col: int):
        """
        Process a single tile with AI analysis.

        Args:
            row: Tile row
            col: Tile column

        Returns:
            Analysis result dictionary
        """
        try:
            # Generate tile image
            svg_path = self.state.get_svg_path()
            grid_config = self.state.state.grid_config

            if not svg_path or not grid_config:
                return None

            # Generate tile at full resolution for AI analysis (512px)
            tile_image = self.tile_gen.generate_tile_on_demand(
                svg_path,
                row,
                col,
                grid_config,
                resolution_override=512  # Full resolution for AI
            )

            if not tile_image:
                return None

            # Perform AI analysis if available
            if self.gemini and self.analyzer:
                try:
                    from core.ai_analyzer.prompts import DISCONTINUITY_ANALYSIS_PROMPT, get_classification_prompt

                    # Step 1: Detailed analysis with Gemini Pro
                    print(f"🤖 Analyzing tile ({row},{col}) with Gemini Pro...")
                    analysis_text = self.gemini.analyze_detailed(
                        tile_image,
                        DISCONTINUITY_ANALYSIS_PROMPT
                    )

                    # Step 2: Binary classification with Gemini Flash
                    print(f"⚡ Classifying tile ({row},{col}) with Gemini Flash...")
                    classification_prompt = get_classification_prompt(analysis_text)
                    classification = self.gemini.classify(
                        analysis_text,
                        classification_prompt
                    )

                    # Determine if there are issues
                    has_issues = 'discontinuity' in classification.lower()

                    result = {
                        'success': True,
                        'has_issues': has_issues,
                        'analysis': analysis_text,
                        'classification': classification,
                        'summary': f"{'⚠️ Discontinuity' if has_issues else '✅ Continuous'}"
                    }

                    print(f"{'⚠️' if has_issues else '✅'} Tile ({row},{col}): {result['summary']}")

                except Exception as ai_error:
                    print(f"❌ AI analysis error for tile ({row},{col}): {ai_error}")
                    result = {
                        'success': False,
                        'has_issues': False,
                        'analysis': f"AI analysis failed: {str(ai_error)}",
                        'summary': 'AI Error'
                    }
            else:
                # No AI available - just mark as processed
                result = {
                    'success': True,
                    'has_issues': False,
                    'analysis': f"Tile ({row}, {col}) - AI not available",
                    'summary': 'No AI'
                }

            # Update state with analysis result and classification
            self.state.add_tile_metadata(
                row,
                col,
                result.get('analysis', ''),
                result.get('classification', None)
            )

            # Update visual status on layout
            if result.get('classification'):
                self._call_ui('update_tile_status', row, col, result.get('classification'))

            # Append result
            # Removed detailed results display - only progress tracking remains
            # self._call_ui('append_result', f"Tile ({row},{col}): {result.get('summary', 'Analyzed')}")

            return result

        except Exception as e:
            print(f"❌ Error processing tile ({row}, {col}): {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def handle_cancel_processing(self):
        """Handle cancellation of processing"""
        self.processing = False
        
        if self.executor:
            self.executor.shutdown(wait=False)
            self.executor = None
        
        self._call_ui('update_status', "Processing cancelled")
    
    # ========================================================================
    # TILE OPERATIONS
    # ========================================================================
    
    def handle_tile_click(self, row: int, col: int):
        """
        Handle tile button click.
        
        Args:
            row: Tile row
            col: Tile column
        """
        try:
            # Generate and display tile image
            svg_path = self.state.get_svg_path()
            grid_config = self.state.state.grid_config
            
            if not svg_path or not grid_config:
                messagebox.showwarning("Warning", "No grid configuration found")
                return
            
            tile_image = self.tile_gen.generate_tile_on_demand(
                svg_path,
                row,
                col,
                grid_config
            )
            
            if tile_image:
                self._call_ui('display_image', tile_image)
                self._call_ui('update_status', f"Displaying tile ({row}, {col})")
            else:
                messagebox.showwarning("Warning", f"Could not generate tile ({row}, {col})")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display tile: {str(e)}")
    
    # ========================================================================
    # TILE NAVIGATION & CLASSIFICATION
    # ========================================================================
    
    def handle_prev_tile(self):
        """Handle previous tile navigation"""
        # TODO: Implement tile navigation
        self._call_ui('update_status', "Previous tile (not yet implemented)")
    
    def handle_next_tile(self):
        """Handle next tile navigation"""
        # TODO: Implement tile navigation
        self._call_ui('update_status', "Next tile (not yet implemented)")
    
    def handle_classify_tile(self, classification: str):
        """
        Handle user classification of current tile.
        
        Args:
            classification: 'continuous' or 'discontinuity'
        """
        # TODO: Implement classification saving
        self._call_ui('update_status', f"Classified as: {classification} (not yet saved)")
    
    # ========================================================================
    # ROI OPERATIONS
    # ========================================================================
    
    def handle_roi_select_toggle(self, selecting: bool):
        """
        Handle ROI selection toggle.
        
        Args:
            selecting: True if starting selection, False if stopping
        """
        if selecting:
            self._call_ui('enable_roi_selection', self._on_roi_selected)
            self._call_ui('update_status', "Click and drag to select ROI")
        else:
            self._call_ui('disable_roi_selection')
            self._call_ui('update_status', "ROI selection cancelled")
    
    def _on_roi_selected(self, coords):
        """
        Callback when ROI is selected.

        Args:
            coords: Tuple of (x1, y1, x2, y2)
        """
        x1, y1, x2, y2 = coords

        # Create ROI
        roi_region = self.roi_storage.add_region((x1, y1), (x2, y2))

        # Update UI
        self._call_ui('add_roi_to_list', f"ROI_{roi_region.id}: ({x1}, {y1}) to ({x2}, {y2})")
        self._call_ui('update_status', f"ROI selected: ROI_{roi_region.id} - Draw more or click 'Select ROI' to exit")
        # Keep ROI selection mode active to allow multiple ROI selections
    
    def handle_roi_analyze(self):
        """Handle ROI analysis"""
        rois = self.roi_storage.get_all()
        
        if not rois:
            messagebox.showwarning("Warning", "No ROI selected")
            return
        
        if not self.gemini or not self.analyzer:
            messagebox.showerror("Error", "AI analyzer not initialized")
            return
        
        # Analyze each ROI
        for region in rois:
            try:
                # Extract ROI image (simplified - would need proper implementation)
                self._call_ui('update_status', f"Analyzing ROI_{region.id}...")
                
                # For now, just show message
            # Removed detailed results display - only progress tracking remains
            # self._call_ui('append_result', f"ROI_{region.id} analysis: (implementation needed)")
                
            except Exception as e:
                print(f"Error analyzing ROI_{region.id}: {e}")
    
    def handle_roi_clear(self):
        """Handle ROI clearing"""
        self.roi_storage.clear_all()
        self._call_ui('update_status', "ROI cleared")
    
    def handle_tile_click(self, row: int, col: int):
        """
        Handle tile click from layout.
        
        Args:
            row: Tile row
            col: Tile column
        """
        print(f"🖱️  Tile clicked: row={row}, col={col}")
        
        try:
            # Get grid config
            grid_config = self.state.get_grid_config()
            if not grid_config:
                print("❌ No grid configured")
                messagebox.showwarning("No Grid", "Please generate a grid first")
                return
            
            # Calculate tile index
            tile_index = row * grid_config.cols + col
            print(f"📍 Tile index: {tile_index}")
            
            # Generate the tile image
            svg_path = self.state.get_svg_path()
            if not svg_path:
                print("❌ No SVG path available")
                messagebox.showwarning("No File", "Please load a GDS file first")
                return
            
            print(f"📄 SVG path: {svg_path}")

            # Check cache first for instant display (384px preview resolution)
            preview_resolution = 384
            cached_tile = self.tile_cache.get(row, col, preview_resolution)
            if cached_tile:
                print(f"⚡ Using cached tile ({row}, {col}) @ {preview_resolution}px - instant!")
                self._call_ui('update_status', f"✅ Tile {tile_index} (row {row}, col {col}) - cached")
                tile_image = cached_tile
            else:
                print(f"🔧 Generating tile on demand...")
                self._call_ui('update_status', f"⏳ Loading tile {tile_index} (row {row}, col {col})...")

                # Generate tile on demand with lower resolution for faster preview
                tile_image = self.tile_gen.generate_tile_on_demand(
                    svg_path=svg_path,
                    row=row,
                    col=col,
                    grid_config=grid_config,
                    resolution_override=preview_resolution  # Lower res for faster click-to-view
                )
            
            print(f"📦 Tile image received: {tile_image is not None}")
            if tile_image:
                print(f"   Image type: {type(tile_image)}")
                print(f"   Image size: {tile_image.size}")
            
            if tile_image:
                # Display tile in review panel
                print(f"🖼️  Processing tile image...")
                
                # Get AI result if available (check if tile has been analyzed)
                ai_result = 'Not yet analyzed - Click "Process All Tiles" or "Process Selected Regions"'
                classification = None

                # Check if this tile has been analyzed
                tile_metadata = None
                print(f"🔍 Checking analysis for tile ({row},{col})")
                print(f"   Total tiles in state: {len(self.state.state.tiles_data)}")

                for tile in self.state.state.tiles_data:
                    if tile.row == row and tile.col == col:
                        print(f"   Found tile metadata: analyzed={tile.analyzed}, has_result={bool(tile.ai_result)}")
                        if tile.analyzed and tile.ai_result:
                            ai_result = tile.ai_result
                            classification = getattr(tile, 'classification', None)
                            tile_metadata = tile
                            print(f"   ✅ Using AI result (length: {len(ai_result)} chars), classification={classification}")
                        break

                if not tile_metadata:
                    print(f"   ⚠️ No analysis found for tile ({row},{col})")

                # Display in tile review panel
                print(f"✅ Displaying tile in Section 4...")
                self._call_ui('display_tile_review', tile_image, row, col, tile_index, ai_result, classification)
                self._call_ui('update_status', f"✅ Displaying tile {tile_index} (row {row}, col {col})")
                print(f"✅ Tile {tile_index} displayed successfully!")
            else:
                print(f"❌ Failed to generate tile ({row}, {col})")
                messagebox.showerror("Error", f"Failed to generate tile at row {row}, col {col}")
                
        except Exception as e:
            print(f"❌ Error handling tile click: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to display tile: {str(e)}")

