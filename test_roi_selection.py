#!/usr/bin/env python3
"""
Test script for multiple ROI selection functionality.
"""

import tkinter as tk
from ui.components.image_canvas import ImageCanvas
from ui.modern_theme import ModernTheme
import numpy as np
from matplotlib.patches import Rectangle

def test_roi_selection():
    """Test ROI selection functionality"""
    print("🧪 Testing ROI Selection...")
    
    # Create main window
    root = tk.Tk()
    root.title("ROI Selection Test")
    ModernTheme.apply(root)
    
    # Create image canvas
    canvas_frame = ImageCanvas(root)
    canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create a test image
    test_image = np.random.rand(400, 400, 3)
    canvas_frame.display_image(test_image)
    
    # Add some test ROI rectangles
    print("📦 Adding test ROI rectangles...")
    
    # ROI 1
    roi1 = Rectangle((50, 50), 100, 80, linewidth=2, edgecolor='red', facecolor='none')
    canvas_frame.ax.add_patch(roi1)
    canvas_frame.roi_rectangles.append(roi1)
    
    # ROI 2
    roi2 = Rectangle((200, 100), 120, 90, linewidth=2, edgecolor='red', facecolor='none')
    canvas_frame.ax.add_patch(roi2)
    canvas_frame.roi_rectangles.append(roi2)
    
    # ROI 3
    roi3 = Rectangle((100, 250), 80, 100, linewidth=2, edgecolor='red', facecolor='none')
    canvas_frame.ax.add_patch(roi3)
    canvas_frame.roi_rectangles.append(roi3)
    
    canvas_frame.canvas.draw()
    
    # Enable ROI selection
    def roi_callback(coords):
        print(f"🎯 ROI callback called with: {coords}")
    
    canvas_frame.enable_roi_selection(roi_callback)
    
    print("✅ Test setup complete!")
    print("📋 Instructions:")
    print("   1. Click on any red rectangle to select it (should turn yellow)")
    print("   2. Click on another rectangle to add it to selection")
    print("   3. Click on empty space to clear all selections")
    print("   4. Press Delete key to remove selected rectangles")
    print("   5. Close window when done testing")
    
    # Add instructions label
    instructions = tk.Label(root, text="Click rectangles to select multiple ROIs. Click empty space to clear. Press Delete to remove.", 
                          font=('TkDefaultFont', 10), wraplength=400)
    instructions.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_roi_selection()
