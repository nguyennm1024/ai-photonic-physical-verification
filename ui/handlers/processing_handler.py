"""
Processing Handler Module
=========================

Handles AI analysis and tile processing operations.
"""

import time
import threading
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor
from .base_handler import BaseHandler


class ProcessingHandler(BaseHandler):
    """
    Handler for AI processing operations.

    Responsibilities:
    - Process all tiles with AI analysis
    - Process ROI-selected tiles
    - Manage parallel processing with thread pool
    - Handle processing cancellation
    - Update progress and results
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Processing state
        self.processing = False
        self.selected_tiles: Optional[List[int]] = None
        self.executor: Optional[ThreadPoolExecutor] = None

    def handle_process_all_tiles(self):
        """Handle processing all tiles with AI analysis"""
        if not self.gemini or not self.analyzer:
            self.show_error("Error", "AI analyzer not initialized")
            return

        grid_config = self.state.state.grid_config
        if not grid_config:
            self.show_error("Error", "Please create a grid first")
            return

        # Start processing all tiles
        self.processing = True
        self.selected_tiles = None  # Process all
        self._call_ui('update_status', "Processing all tiles...")

        # Process in background thread
        thread = threading.Thread(target=self._process_tiles_worker, daemon=True)
        thread.start()

    def handle_process_roi_tiles(self):
        """Handle processing only tiles that overlap with ROI regions"""
        if not self.gemini or not self.analyzer:
            self.show_error("Error", "AI analyzer not initialized")
            return

        grid_config = self.state.state.grid_config
        if not grid_config:
            self.show_error("Error", "Please create a grid first")
            return

        # Get ROI regions
        roi_regions = self.roi_storage.get_all()
        if not roi_regions:
            self.show_warning("Warning", "No ROI regions selected. Please draw ROI rectangles first.")
            return

        # Get image size (use SVG dimensions or default)
        svg_path = self.state.get_svg_path()
        if not svg_path:
            self.show_error("Error", "No SVG file loaded")
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
            self.show_warning("Warning", "No tiles overlap with selected ROI regions")
            return

        # Confirm
        from tkinter import messagebox
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
