"""
App State Module
================

Centralized application state management and validation.
"""

from .state_manager import StateManager, ApplicationState, TileMetadata, GridConfig, ROIRegion
from .state_validator import StateValidator

__all__ = ['StateManager', 'ApplicationState', 'StateValidator', 'TileMetadata', 'GridConfig', 'ROIRegion']
