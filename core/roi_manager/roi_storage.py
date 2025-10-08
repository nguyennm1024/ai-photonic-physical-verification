"""
ROI Storage Module
==================

Manage multiple ROI regions with color assignment.
"""

from typing import Optional, List, Tuple
from ..app_state.state_manager import ROIRegion


class ROIStorage:
    """Manage multiple ROI regions"""
    
    # Color palette for ROI regions
    COLOR_PALETTE = [
        {'name': 'red', 'hex': '#FF6B6B', 'alpha': 0.18},
        {'name': 'orange', 'hex': '#FF9F43', 'alpha': 0.18},
        {'name': 'yellow', 'hex': '#FFA502', 'alpha': 0.20},
        {'name': 'green', 'hex': '#26DE81', 'alpha': 0.18},
        {'name': 'cyan', 'hex': '#2BCBBA', 'alpha': 0.18},
        {'name': 'blue', 'hex': '#3742FA', 'alpha': 0.18},
        {'name': 'purple', 'hex': '#A55EEA', 'alpha': 0.18},
        {'name': 'pink', 'hex': '#FF3838', 'alpha': 0.18}
    ]
    
    def __init__(self):
        """Initialize ROI storage"""
        self.regions: List[ROIRegion] = []
        self.counter = 0
    
    def add_region(self, start: Tuple[float, float], end: Tuple[float, float]) -> ROIRegion:
        """
        Add new ROI region with auto-assigned color.
        
        Args:
            start: (x, y) start coordinates
            end: (x, y) end coordinates
            
        Returns:
            Created ROIRegion object
        """
        # Select color from palette
        color_info = self.COLOR_PALETTE[len(self.regions) % len(self.COLOR_PALETTE)]
        
        roi_region = ROIRegion(
            id=self.counter,
            start=start,
            end=end,
            color=color_info['name'],
            hex_color=color_info['hex'],
            alpha=color_info['alpha'],
            rectangle=None
        )
        
        self.regions.append(roi_region)
        self.counter += 1
        
        return roi_region
    
    def remove_last(self) -> Optional[ROIRegion]:
        """Remove and return most recent ROI"""
        if self.regions:
            return self.regions.pop()
        return None
    
    def clear_all(self):
        """Clear all ROI regions"""
        self.regions.clear()
    
    def get_all(self) -> List[ROIRegion]:
        """Get all ROI regions"""
        return self.regions.copy()
    
    def count(self) -> int:
        """Get number of ROI regions"""
        return len(self.regions)

