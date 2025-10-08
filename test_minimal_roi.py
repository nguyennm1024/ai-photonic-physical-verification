#!/usr/bin/env python3
"""
Minimal test for matplotlib mouse events.
"""

import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle

class MinimalROITest:
    def __init__(self, root):
        self.root = root
        self.roi_rectangles = []
        self.selected_roi_rects = []
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        
        # Create test image
        test_image = np.random.rand(400, 400, 3)
        self.ax.imshow(test_image)
        self.ax.set_xlim(0, 400)
        self.ax.set_ylim(400, 0)  # Flip Y axis
        
        # Add test ROIs
        self._add_test_rois()
        
        self.canvas.draw()
        
    def _add_test_rois(self):
        """Add test ROI rectangles"""
        # ROI 1
        roi1 = Rectangle((50, 50), 100, 80, linewidth=2, edgecolor='red', facecolor='none')
        self.ax.add_patch(roi1)
        self.roi_rectangles.append(roi1)
        
        # ROI 2
        roi2 = Rectangle((200, 100), 120, 90, linewidth=2, edgecolor='red', facecolor='none')
        self.ax.add_patch(roi2)
        self.roi_rectangles.append(roi2)
        
        # ROI 3
        roi3 = Rectangle((100, 250), 80, 100, linewidth=2, edgecolor='red', facecolor='none')
        self.ax.add_patch(roi3)
        self.roi_rectangles.append(roi3)
        
        print(f"📦 Added {len(self.roi_rectangles)} test ROIs")
    
    def _on_mouse_press(self, event):
        """Handle mouse press"""
        if event.inaxes != self.ax:
            return
            
        click_x, click_y = event.xdata, event.ydata
        print(f"🖱️  Mouse press at ({click_x:.1f}, {click_y:.1f})")
        
        # Find clicked ROI
        clicked_roi = self._find_roi_at_point(click_x, click_y)
        if clicked_roi is not None:
            print(f"🎯 Clicked on ROI: {clicked_roi}")
            self._toggle_roi_selection(clicked_roi)
        else:
            print(f"📭 Clicked on empty space")
            self._clear_all_selections()
    
    def _find_roi_at_point(self, x, y):
        """Find ROI rectangle at the given point"""
        print(f"🔍 Checking {len(self.roi_rectangles)} ROIs for point ({x:.1f}, {y:.1f})")
        
        for i, roi_rect in enumerate(self.roi_rectangles):
            rect_x = roi_rect.get_x()
            rect_y = roi_rect.get_y()
            rect_width = roi_rect.get_width()
            rect_height = roi_rect.get_height()
            
            print(f"   ROI {i}: x={rect_x:.1f}, y={rect_y:.1f}, w={rect_width:.1f}, h={rect_height:.1f}")
            
            if (rect_x <= x <= rect_x + rect_width and 
                rect_y <= y <= rect_y + rect_height):
                print(f"   ✅ Point is inside ROI {i}")
                return roi_rect
            else:
                print(f"   ❌ Point is outside ROI {i}")
        
        print(f"   📭 Point not found in any ROI")
        return None
    
    def _toggle_roi_selection(self, roi_rect):
        """Toggle ROI selection"""
        print(f"🔍 ROI clicked: {roi_rect}")
        
        if roi_rect in self.selected_roi_rects:
            self._deselect_single_roi(roi_rect)
            print(f"❌ ROI deselected")
        else:
            self._select_single_roi(roi_rect)
            print(f"✅ ROI selected ({len(self.selected_roi_rects)} total)")
    
    def _select_single_roi(self, roi_rect):
        """Select a single ROI rectangle"""
        if roi_rect not in self.selected_roi_rects:
            self.selected_roi_rects.append(roi_rect)
            roi_rect.set_edgecolor('yellow')
            roi_rect.set_linewidth(3)
            self.canvas.draw()
    
    def _deselect_single_roi(self, roi_rect):
        """Deselect a single ROI rectangle"""
        if roi_rect in self.selected_roi_rects:
            self.selected_roi_rects.remove(roi_rect)
            roi_rect.set_edgecolor('red')
            roi_rect.set_linewidth(2)
            self.canvas.draw()
    
    def _clear_all_selections(self):
        """Clear all ROI selections"""
        for roi_rect in self.selected_roi_rects:
            roi_rect.set_edgecolor('red')
            roi_rect.set_linewidth(2)
        self.selected_roi_rects.clear()
        self.canvas.draw()

def test_minimal_roi():
    """Test minimal ROI selection"""
    print("🧪 Testing Minimal ROI Selection...")
    
    root = tk.Tk()
    root.title("Minimal ROI Test")
    root.geometry("600x500")
    
    app = MinimalROITest(root)
    
    print("📋 Instructions:")
    print("   1. Click on any red rectangle to select it (should turn yellow)")
    print("   2. Click on another rectangle to add it to selection")
    print("   3. Click on empty space to clear all selections")
    print("   4. Watch terminal for debug output")
    print("   5. Close window when done testing")
    
    root.mainloop()

if __name__ == "__main__":
    test_minimal_roi()
