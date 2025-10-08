#!/usr/bin/env python3
"""
Comprehensive test for ROI selection functionality.
This script will test the actual main application.
"""

import subprocess
import time
import sys

def test_main_app():
    """Test the main application ROI selection"""
    print("🧪 Testing Main Application ROI Selection...")
    print("📋 Manual Test Instructions:")
    print("   1. Run: python main.py")
    print("   2. Load a GDS file")
    print("   3. Generate a grid (3x3)")
    print("   4. Click 'Select ROIs' button")
    print("   5. Draw 3 rectangles")
    print("   6. Click on rectangle #1 - should turn yellow")
    print("   7. Click on rectangle #2 - should turn yellow (keep #1 yellow)")
    print("   8. Click on rectangle #3 - should turn yellow (keep #1,#2 yellow)")
    print("   9. Click on empty space - all should turn red")
    print("   10. Click rectangle #1 again - should turn yellow")
    print("   11. Press Delete key - selected rectangle should disappear")
    print("")
    print("🔍 Watch terminal output for debug messages:")
    print("   - '🖱️ Mouse press at (x, y)'")
    print("   - '🎯 Clicked on ROI: <Rectangle>'")
    print("   - '📭 Clicked on empty space'")
    print("   - '✅ ROI selected (N total)'")
    print("   - '❌ ROI deselected'")
    print("")
    
    # Ask user to run the test
    response = input("Press Enter to start the main application for testing, or 'q' to quit: ")
    if response.lower() == 'q':
        return
    
    print("🚀 Starting main application...")
    print("   (Close the application window when done testing)")
    
    try:
        # Run the main application
        result = subprocess.run([sys.executable, "main.py"], 
                              capture_output=False, 
                              text=True)
        print(f"✅ Application exited with code: {result.returncode}")
    except KeyboardInterrupt:
        print("⏹️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    test_main_app()
