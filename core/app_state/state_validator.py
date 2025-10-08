"""
State Validator Module
======================

Validate state transitions and operations before they occur.
"""

from typing import Tuple
from .state_manager import ApplicationState


class StateValidator:
    """Validate application state transitions"""
    
    @staticmethod
    def can_split_tiles(state: ApplicationState) -> Tuple[bool, str]:
        """
        Check if tiles can be split.
        
        Returns:
            (is_valid, error_message)
        """
        if not state.current_svg_path:
            return (False, "Please generate SVG first")
        
        return (True, "")
    
    @staticmethod
    def can_start_analysis(state: ApplicationState) -> Tuple[bool, str]:
        """
        Check if AI analysis can start.
        
        Returns:
            (is_valid, error_message)
        """
        if not state.tiles_data:
            return (False, "Please split SVG into tiles first")
        
        if state.analysis_running:
            return (False, "Analysis is already running")
        
        return (True, "")
    
    @staticmethod
    def can_analyze_roi(state: ApplicationState) -> Tuple[bool, str]:
        """
        Check if ROI analysis can start.
        
        Returns:
            (is_valid, error_message)
        """
        if not state.roi_regions:
            return (False, "Please draw at least one ROI region first")
        
        if not state.tiles_data:
            return (False, "Please split SVG into tiles first")
        
        if state.analysis_running:
            return (False, "Analysis is already running")
        
        return (True, "")
    
    @staticmethod
    def validate_grid_config(rows: int, cols: int, overlap: float) -> Tuple[bool, str]:
        """
        Validate grid configuration parameters.
        
        Returns:
            (is_valid, error_message)
        """
        if rows < 1 or cols < 1:
            return (False, "Grid dimensions must be positive")
        
        if overlap < 0 or overlap > 50:
            return (False, "Overlap must be between 0 and 50%")
        
        total_tiles = rows * cols
        if total_tiles > 1000:
            return (False, f"Grid too large ({total_tiles} tiles). Maximum recommended: 1000")
        
        return (True, "")
    
    @staticmethod
    def can_export_results(state: ApplicationState) -> Tuple[bool, str]:
        """
        Check if results can be exported.
        
        Returns:
            (is_valid, error_message)
        """
        if not state.tiles_data:
            return (False, "No results to export")
        
        return (True, "")
    
    @staticmethod
    def can_navigate_tiles(state: ApplicationState) -> Tuple[bool, str]:
        """
        Check if tile navigation is possible.
        
        Returns:
            (is_valid, error_message)
        """
        if not state.tiles_data:
            return (False, "No tiles available for navigation")
        
        return (True, "")

