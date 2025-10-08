#!/usr/bin/env python3
"""
Direct test of ROI detection logic.
"""

import numpy as np
from matplotlib.patches import Rectangle

def test_roi_detection():
    """Test ROI detection logic directly"""
    print("🧪 Testing ROI Detection Logic...")
    
    # Create test ROIs
    roi_rectangles = []
    
    # ROI 1: (50, 50) with size 100x80
    roi1 = Rectangle((50, 50), 100, 80, linewidth=2, edgecolor='red', facecolor='none')
    roi_rectangles.append(roi1)
    
    # ROI 2: (200, 100) with size 120x90  
    roi2 = Rectangle((200, 100), 120, 90, linewidth=2, edgecolor='red', facecolor='none')
    roi_rectangles.append(roi2)
    
    # ROI 3: (100, 250) with size 80x100
    roi3 = Rectangle((100, 250), 80, 100, linewidth=2, edgecolor='red', facecolor='none')
    roi_rectangles.append(roi3)
    
    print(f"📦 Created {len(roi_rectangles)} test ROIs")
    
    def find_roi_at_point(x, y):
        """Find ROI rectangle at the given point"""
        print(f"🔍 Checking {len(roi_rectangles)} ROIs for point ({x:.1f}, {y:.1f})")
        
        for i, roi_rect in enumerate(roi_rectangles):
            # Get rectangle bounds
            rect_x = roi_rect.get_x()
            rect_y = roi_rect.get_y()
            rect_width = roi_rect.get_width()
            rect_height = roi_rect.get_height()
            
            print(f"   ROI {i}: x={rect_x:.1f}, y={rect_y:.1f}, w={rect_width:.1f}, h={rect_height:.1f}")
            
            # Check if point is inside rectangle
            if (rect_x <= x <= rect_x + rect_width and 
                rect_y <= y <= rect_y + rect_height):
                print(f"   ✅ Point is inside ROI {i}")
                return roi_rect
            else:
                print(f"   ❌ Point is outside ROI {i}")
        
        print(f"   📭 Point not found in any ROI")
        return None
    
    # Test points
    test_points = [
        (100, 90),   # Should be inside ROI 1
        (260, 145),  # Should be inside ROI 2  
        (140, 300),  # Should be inside ROI 3
        (10, 10),    # Should be outside all
        (300, 300),  # Should be outside all
    ]
    
    for x, y in test_points:
        print(f"\n🎯 Testing point ({x}, {y}):")
        result = find_roi_at_point(x, y)
        if result:
            print(f"   ✅ Found ROI: {result}")
        else:
            print(f"   ❌ No ROI found")

if __name__ == "__main__":
    test_roi_detection()
