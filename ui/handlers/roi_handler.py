"""
ROI Handler Module
==================

Handles Region of Interest (ROI) operations.
"""

from .base_handler import BaseHandler


class ROIHandler(BaseHandler):
    """
    Handler for ROI operations.

    Responsibilities:
    - Toggle ROI selection mode
    - Handle ROI region creation
    - Analyze ROI regions
    - Clear ROI regions
    """

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
            self.show_warning("Warning", "No ROI selected")
            return

        if not self.gemini or not self.analyzer:
            self.show_error("Error", "AI analyzer not initialized")
            return

        # Analyze each ROI
        for region in rois:
            try:
                # Extract ROI image (simplified - would need proper implementation)
                self._call_ui('update_status', f"Analyzing ROI_{region.id}...")

                # For now, just show message
                # Note: Full implementation would extract and analyze ROI image region

            except Exception as e:
                print(f"Error analyzing ROI_{region.id}: {e}")

    def handle_roi_clear(self):
        """Handle ROI clearing"""
        self.roi_storage.clear_all()
        self._call_ui('update_status', "ROI cleared")
