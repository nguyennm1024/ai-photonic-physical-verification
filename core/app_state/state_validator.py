"""
Application State Validator

This module provides validation methods for the application state.
It ensures data integrity and provides helpful error messages.
"""

from typing import List, Tuple
from .state_manager import AppStateManager, TileData, GridConfig, ROIRegion


class StateValidator:
    """
    Validator for application state.
    
    This class provides validation methods to ensure the application state
    is consistent and valid before performing operations.
    """
    
    def __init__(self, state_manager: AppStateManager):
        """Initialize the state validator with a state manager"""
        self.state_manager = state_manager
    
    def validate_file_state(self) -> Tuple[bool, List[str]]:
        """
        Validate the current file state.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if GDS file is loaded
        if not self.state_manager.current_gds_path:
            errors.append("No GDS file is currently loaded")
        
        # Check if SVG file exists
        if (self.state_manager.current_gds_path and 
                not self.state_manager.current_svg_path):
            errors.append("SVG file has not been generated from GDS file")
        
        # Check if SVG dimensions are available
        if (self.state_manager.current_svg_path and 
                not self.state_manager.svg_dimensions):
            errors.append("SVG dimensions have not been parsed")
        
        return len(errors) == 0, errors
    
    def validate_tile_state(self) -> Tuple[bool, List[str]]:
        """
        Validate the current tile state.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if tiles data exists
        if not self.state_manager.tiles_data:
            errors.append("No tiles data available")
            return False, errors
        
        # Check if current tile index is valid
        if self.state_manager.current_tile_index < 0:
            errors.append("Current tile index is negative")
        elif (self.state_manager.current_tile_index >= 
                len(self.state_manager.tiles_data)):
            errors.append("Current tile index is out of bounds")
        
        # Check if grid configuration is valid
        if self.state_manager.grid_config:
            grid = self.state_manager.grid_config
            if grid.rows <= 0 or grid.cols <= 0:
                errors.append("Grid configuration has invalid dimensions")
            if grid.overlap < 0 or grid.overlap > 50:
                errors.append("Grid overlap must be between 0 and 50 percent")
            if grid.resolution not in [512, 1024, 2048, 4096]:
                errors.append("Grid resolution must be 512, 1024, 2048, or 4096")
        
        return len(errors) == 0, errors
    
    def validate_analysis_state(self) -> Tuple[bool, List[str]]:
        """
        Validate the current analysis state.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if AI models are available
        if not self.state_manager.ai_analyzer:
            errors.append("AI analyzer model is not available")
        if not self.state_manager.ai_classifier:
            errors.append("AI classifier model is not available")
        
        # Check for conflicting analysis states
        if (self.state_manager.analysis_running and 
                self.state_manager.analysis_paused):
            errors.append("Analysis cannot be both running and paused")
        
        return len(errors) == 0, errors
    
    def validate_roi_state(self) -> Tuple[bool, List[str]]:
        """
        Validate the current ROI state.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if ROI drawing state is consistent
        if self.state_manager.drawing_roi:
            if not self.state_manager.roi_start:
                errors.append("ROI drawing started but no start coordinates")
            if self.state_manager.roi_mode.value != "drawing":
                errors.append("ROI drawing active but not in drawing mode")
        
        # Check ROI regions for consistency
        for i, region in enumerate(self.state_manager.roi_regions):
            if region.start and region.end:
                # Check if start coordinates are less than end coordinates
                if region.start[0] > region.end[0] or region.start[1] > region.end[1]:
                    errors.append(f"ROI region {i} has invalid coordinate order")
        
        return len(errors) == 0, errors
    
    def validate_tile_data(self, tile_data: TileData) -> Tuple[bool, List[str]]:
        """
        Validate a single tile data object.
        
        Args:
            tile_data: The tile data to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if not tile_data.filename:
            errors.append("Tile filename is required")
        
        if tile_data.row < 0:
            errors.append("Tile row must be non-negative")
        
        if tile_data.col < 0:
            errors.append("Tile column must be non-negative")
        
        # Check classification values
        if tile_data.user_classification and tile_data.user_classification not in ["continuous", "discontinuity"]:
            errors.append("User classification must be 'continuous' or 'discontinuity'")
        
        return len(errors) == 0, errors
    
    def validate_grid_config(self, grid_config: GridConfig) -> Tuple[bool, List[str]]:
        """
        Validate a grid configuration object.
        
        Args:
            grid_config: The grid configuration to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check grid dimensions
        if grid_config.rows <= 0:
            errors.append("Grid rows must be positive")
        
        if grid_config.cols <= 0:
            errors.append("Grid columns must be positive")
        
        # Check overlap percentage
        if grid_config.overlap < 0:
            errors.append("Grid overlap cannot be negative")
        elif grid_config.overlap > 50:
            errors.append("Grid overlap cannot exceed 50%")
        
        # Check resolution
        valid_resolutions = [512, 1024, 2048, 4096]
        if grid_config.resolution not in valid_resolutions:
            errors.append(f"Grid resolution must be one of: {valid_resolutions}")
        
        # Check total tiles calculation
        expected_total = grid_config.rows * grid_config.cols
        if grid_config.total_tiles != expected_total:
            errors.append(f"Total tiles ({grid_config.total_tiles}) does not match rows×cols ({expected_total})")
        
        return len(errors) == 0, errors
    
    def validate_roi_region(self, roi_region: ROIRegion) -> Tuple[bool, List[str]]:
        """
        Validate a ROI region object.
        
        Args:
            roi_region: The ROI region to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if roi_region.id < 0:
            errors.append("ROI region ID must be non-negative")
        
        if not roi_region.start:
            errors.append("ROI region start coordinates are required")
        
        if not roi_region.end:
            errors.append("ROI region end coordinates are required")
        
        # Check coordinate validity
        if roi_region.start and roi_region.end:
            if len(roi_region.start) != 2:
                errors.append("ROI start coordinates must have exactly 2 values")
            if len(roi_region.end) != 2:
                errors.append("ROI end coordinates must have exactly 2 values")
            
            # Check if coordinates are numeric
            try:
                float(roi_region.start[0])
                float(roi_region.start[1])
                float(roi_region.end[0])
                float(roi_region.end[1])
            except (ValueError, TypeError):
                errors.append("ROI coordinates must be numeric")
        
        # Check color values
        if roi_region.alpha < 0 or roi_region.alpha > 1:
            errors.append("ROI alpha value must be between 0 and 1")
        
        return len(errors) == 0, errors
    
    def validate_complete_state(self) -> Tuple[bool, List[str]]:
        """
        Validate the complete application state.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate each state component
        file_valid, file_errors = self.validate_file_state()
        if not file_valid:
            errors.extend(file_errors)
        
        tile_valid, tile_errors = self.validate_tile_state()
        if not tile_valid:
            errors.extend(tile_errors)
        
        analysis_valid, analysis_errors = self.validate_analysis_state()
        if not analysis_valid:
            errors.extend(analysis_errors)
        
        roi_valid, roi_errors = self.validate_roi_state()
        if not roi_valid:
            errors.extend(roi_errors)
        
        return len(errors) == 0, errors
    
    def can_start_analysis(self) -> Tuple[bool, List[str]]:
        """
        Check if analysis can be started.
        
        Returns:
            Tuple of (can_start, list_of_reasons_why_not)
        """
        errors = []
        
        # Check file state
        file_valid, file_errors = self.validate_file_state()
        if not file_valid:
            errors.extend(file_errors)
        
        # Check tile state
        tile_valid, tile_errors = self.validate_tile_state()
        if not tile_valid:
            errors.extend(tile_errors)
        
        # Check analysis state
        if self.state_manager.analysis_running:
            errors.append("Analysis is already running")
        
        if self.state_manager.analysis_paused:
            errors.append("Analysis is paused - resume instead of starting")
        
        # Check AI models
        if not self.state_manager.ai_analyzer:
            errors.append("AI analyzer model is not available")
        
        if not self.state_manager.ai_classifier:
            errors.append("AI classifier model is not available")
        
        return len(errors) == 0, errors
    
    def can_create_tiles(self) -> Tuple[bool, List[str]]:
        """
        Check if tiles can be created.
        
        Returns:
            Tuple of (can_create, list_of_reasons_why_not)
        """
        errors = []
        
        # Check file state
        file_valid, file_errors = self.validate_file_state()
        if not file_valid:
            errors.extend(file_errors)
        
        # Check if tiles already exist
        if self.state_manager.tiles_data:
            errors.append("Tiles already exist - clear existing tiles first")
        
        return len(errors) == 0, errors
    
    def can_draw_roi(self) -> Tuple[bool, List[str]]:
        """
        Check if ROI drawing can be started.
        
        Returns:
            Tuple of (can_draw, list_of_reasons_why_not)
        """
        errors = []
        
        # Check if tiles exist
        if not self.state_manager.tiles_data:
            errors.append("No tiles available for ROI drawing")
        
        # Check if already drawing
        if self.state_manager.drawing_roi:
            errors.append("Already drawing ROI - finish current drawing first")
        
        return len(errors) == 0, errors
