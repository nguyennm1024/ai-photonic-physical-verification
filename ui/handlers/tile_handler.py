"""
Tile Handler Module
===================

Handles tile display, navigation, and classification operations.
"""

from .base_handler import BaseHandler


class TileHandler(BaseHandler):
    """
    Handler for tile operations.

    Responsibilities:
    - Handle tile clicks from layout
    - Display tiles in review panel
    - Navigate between tiles (prev/next)
    - Handle user classification
    """

    def handle_tile_click(self, row: int, col: int):
        """
        Handle tile click from layout.

        Args:
            row: Tile row
            col: Tile column
        """
        print(f"🖱️  Tile clicked: row={row}, col={col}")

        # Store current displayed tile for navigation
        self.current_displayed_tile = (row, col)

        try:
            # Get grid config
            grid_config = self.state.get_grid_config()
            if not grid_config:
                print("❌ No grid configured")
                self.show_warning("No Grid", "Please generate a grid first")
                return

            # Calculate tile index
            tile_index = row * grid_config.cols + col
            print(f"📍 Tile index: {tile_index}")

            # Generate the tile image
            svg_path = self.state.get_svg_path()
            if not svg_path:
                print("❌ No SVG path available")
                self.show_warning("No File", "Please load a GDS file first")
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

                is_user_classification = False
                for tile in self.state.state.tiles_data:
                    if tile.row == row and tile.col == col:
                        print(f"   Found tile metadata: analyzed={tile.analyzed}, has_result={bool(tile.ai_result)}")
                        if tile.analyzed and tile.ai_result:
                            ai_result = tile.ai_result
                            # User classification overrides AI classification
                            classification = tile.user_classification or tile.classification
                            is_user_classification = tile.user_classification is not None
                            tile_metadata = tile
                            print(f"   ✅ Using AI result (length: {len(ai_result)} chars)")
                            print(f"   Classification: {classification} (user={tile.user_classification}, ai={tile.classification})")
                            print(f"   Is user classification: {is_user_classification}")
                        break

                if not tile_metadata:
                    print(f"   ⚠️ No analysis found for tile ({row},{col})")

                # Display in tile review panel
                print(f"✅ Displaying tile in Section 4...")
                self._call_ui('display_tile_review', tile_image, row, col, tile_index, ai_result, classification, is_user_classification)

                # Update focused tile with purple border
                self._call_ui('update_focused_tile', row, col)

                self._call_ui('update_status', f"✅ Displaying tile {tile_index} (row {row}, col {col})")
                print(f"✅ Tile {tile_index} displayed successfully!")
            else:
                print(f"❌ Failed to generate tile ({row}, {col})")
                self.show_error("Error", f"Failed to generate tile at row {row}, col {col}")

        except Exception as e:
            print(f"❌ Error handling tile click: {e}")
            import traceback
            traceback.print_exc()
            self.show_error("Error", f"Failed to display tile: {str(e)}")

    def handle_prev_tile(self):
        """Handle previous tile navigation"""
        grid_config = self.state.get_grid_config()
        if not grid_config:
            self.show_warning("No Grid", "Please generate a grid first")
            return

        # Get current tile from review panel (stored in tile_handler during last click)
        if not hasattr(self, 'current_displayed_tile'):
            self.show_info("No Tile", "Please click a tile first")
            return

        current_row, current_col = self.current_displayed_tile
        current_index = current_row * grid_config.cols + current_col

        # Navigate to previous tile
        if current_index > 0:
            prev_index = current_index - 1
            prev_row = prev_index // grid_config.cols
            prev_col = prev_index % grid_config.cols

            print(f"⬅️  Navigating to previous tile: ({current_row},{current_col}) → ({prev_row},{prev_col})")
            self.handle_tile_click(prev_row, prev_col)
        else:
            self.show_info("First Tile", "Already at the first tile")

    def handle_next_tile(self):
        """Handle next tile navigation"""
        grid_config = self.state.get_grid_config()
        if not grid_config:
            self.show_warning("No Grid", "Please generate a grid first")
            return

        # Get current tile from review panel (stored in tile_handler during last click)
        if not hasattr(self, 'current_displayed_tile'):
            self.show_info("No Tile", "Please click a tile first")
            return

        current_row, current_col = self.current_displayed_tile
        current_index = current_row * grid_config.cols + current_col
        total_tiles = grid_config.rows * grid_config.cols

        # Navigate to next tile
        if current_index < total_tiles - 1:
            next_index = current_index + 1
            next_row = next_index // grid_config.cols
            next_col = next_index % grid_config.cols

            print(f"➡️  Navigating to next tile: ({current_row},{current_col}) → ({next_row},{next_col})")
            self.handle_tile_click(next_row, next_col)
        else:
            self.show_info("Last Tile", "Already at the last tile")

    def handle_classify_tile(self, row: int, col: int, classification: str):
        """
        Handle user classification of current tile.

        Args:
            row: Tile row
            col: Tile column
            classification: 'continuous', 'discontinuity', or 'no_waveguide'
        """
        print(f"🏷️  User classification: tile ({row},{col}) → {classification}")

        try:
            # Save user classification to state (this overrides AI classification)
            self.state.set_user_classification(row, col, classification)

            # Update visual indicators on canvas
            print(f"   🎨 Updating tile status on canvas...")
            self._call_ui('update_tile_status', row, col, classification, analyzed=True)

            # Update status indicator in review panel
            print(f"   📋 Updating status indicator in review panel with: {classification}")
            self._call_ui('update_tile_review_status', classification)
            print(f"   ✅ Status indicator update callback called")

            # Update status bar
            self._call_ui('update_status', f"✅ Tile ({row},{col}) classified as: {classification}")

            print(f"✅ User classification saved and UI updated")

        except Exception as e:
            print(f"❌ Error saving classification: {e}")
            import traceback
            traceback.print_exc()
            self.show_error("Error", f"Failed to save classification: {str(e)}")
