"""
Main Entry Point for Layout Verification App

This module serves as the main entry point for the refactored application.
It maintains the same initialization sequence as the original application.
"""

import tkinter as tk
from tkinter import ttk
from core.app_state.state_manager import AppStateManager
from core.app_state.state_validator import StateValidator
from core.file_manager.file_manager import FileManager


class LayoutVerificationApp:
    """
    Main application class that serves as a facade for the modular components.
    
    This class maintains the same API as the original LayoutVerificationApp
    while delegating functionality to the new modular components.
    """
    
    def __init__(self, root):
        """
        Initialize the main application with GUI root window and set up all state variables.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Interactive Layout Verification System")
        self.root.geometry("1400x900")
        
        # Initialize state management
        self.state_manager = AppStateManager()
        self.state_validator = StateValidator(self.state_manager)
        
        # Initialize file management with configurable output directory
        import os
        # Use current project directory for output, or create an 'output' subdirectory
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        self.file_manager = FileManager(output_directory=output_dir)
        
        # Initialize AI models (placeholder for now)
        self._initialize_ai_models()
        
        # Setup UI (placeholder for now)
        self._setup_ui()
        
        # Start checking queue (placeholder for now)
        self._start_queue_monitoring()
    
    def _initialize_ai_models(self):
        """Initialize AI models (placeholder implementation)"""
        # This will be implemented in Phase 4
        print("🔧 AI models initialization - to be implemented in Phase 4")
    
    def _setup_ui(self):
        """Setup the user interface (placeholder implementation)"""
        # This will be implemented in Phase 6
        print("🔧 UI setup - to be implemented in Phase 6")
        
        # Create a simple placeholder UI for Phase 1 testing
        self._create_placeholder_ui()
    
    def _create_placeholder_ui(self):
        """Create a simple placeholder UI for Phase 1 testing"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Layout Verification App - Phase 1", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Status information
        status_frame = ttk.LabelFrame(main_frame, text="Application Status")
        status_frame.pack(fill=tk.X, pady=10)
        
        # State summary
        state_summary = self.state_manager.get_state_summary()
        
        # File state
        file_info = ttk.Label(
            status_frame, 
            text=f"GDS File: {state_summary['file_state']['gds_path'] or 'None'}"
        )
        file_info.pack(anchor=tk.W, padx=10, pady=5)
        
        # Tile state
        tile_info = ttk.Label(
            status_frame, 
            text=f"Tiles: {state_summary['tile_state']['total_tiles']} total"
        )
        tile_info.pack(anchor=tk.W, padx=10, pady=5)
        
        # Analysis state
        analysis_info = ttk.Label(
            status_frame, 
            text=f"Analysis: {state_summary['analysis_state']['state']}"
        )
        analysis_info.pack(anchor=tk.W, padx=10, pady=5)
        
        # ROI state
        roi_info = ttk.Label(
            status_frame, 
            text=f"ROI Mode: {state_summary['roi_state']['mode']}"
        )
        roi_info.pack(anchor=tk.W, padx=10, pady=5)
        
        # Phase information
        phase_frame = ttk.LabelFrame(main_frame, text="Refactoring Progress")
        phase_frame.pack(fill=tk.X, pady=10)
        
        phase_info = ttk.Label(
            phase_frame,
            text="✅ Phase 1: Core Infrastructure and State Management - COMPLETED\n"
                 "✅ Phase 2: File Management System - COMPLETED\n"
                 "🔧 Phase 3: Tile System Architecture - PENDING\n"
                 "🔧 Phase 4: AI Analysis System - PENDING\n"
                 "🔧 Phase 5: ROI System - PENDING\n"
                 "🔧 Phase 6: UI Component Extraction - PENDING\n"
                 "🔧 Phase 7: Integration and Facade Pattern - PENDING\n"
                 "🔧 Phase 8: Optimization and Cleanup - PENDING"
        )
        phase_info.pack(anchor=tk.W, padx=10, pady=10)
        
        # Test buttons
        test_frame = ttk.LabelFrame(main_frame, text="Phase 1 & 2 Tests")
        test_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            test_frame, 
            text="Test State Validation", 
            command=self._test_state_validation
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            test_frame, 
            text="Test State Changes", 
            command=self._test_state_changes
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            test_frame, 
            text="Reset State", 
            command=self._reset_state
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # File management tests
        file_test_frame = ttk.LabelFrame(main_frame, text="File Management Tests")
        file_test_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            file_test_frame, 
            text="Load GDS File", 
            command=self._test_load_gds
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            file_test_frame, 
            text="Generate SVG", 
            command=self._test_generate_svg
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            file_test_frame, 
            text="Test File Validation", 
            command=self._test_file_validation
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Status bar
        self.status_bar = ttk.Label(
            self.root, 
            text="Phase 2: File Management System Ready", 
            relief=tk.SUNKEN
        )
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def _test_state_validation(self):
        """Test state validation functionality"""
        is_valid, errors = self.state_validator.validate_complete_state()
        if is_valid:
            self.status_bar.config(text="✅ State validation passed")
        else:
            error_msg = "; ".join(errors[:3])  # Show first 3 errors
            if len(errors) > 3:
                error_msg += f" (+{len(errors) - 3} more)"
            self.status_bar.config(text=f"❌ State validation failed: {error_msg}")
    
    def _test_state_changes(self):
        """Test state change functionality"""
        # Test setting some state values
        self.state_manager.current_gds_path = "/test/path/file.gds"
        self.state_manager.current_svg_path = "/test/path/file.svg"
        self.status_bar.config(text="✅ State changes applied - check validation")
    
    def _reset_state(self):
        """Reset application state"""
        self.state_manager.reset_file_state()
        self.state_manager.reset_analysis_state()
        self.state_manager.reset_roi_state()
        self.file_manager.reset()
        self.status_bar.config(text="✅ Application state reset")
    
    def _test_load_gds(self):
        """Test GDS file loading"""
        success = self.file_manager.load_gds_file_dialog()
        if success:
            file_info = self.file_manager.get_file_display_info()
            self.status_bar.config(text=f"✅ GDS loaded: {file_info}")
        else:
            self.status_bar.config(text="❌ GDS loading failed or cancelled")
    
    def _test_generate_svg(self):
        """Test SVG generation"""
        can_generate, errors = self.file_manager.can_generate_svg()
        if not can_generate:
            error_msg = "; ".join(errors[:2])
            self.status_bar.config(text=f"❌ Cannot generate SVG: {error_msg}")
            return
        
        success = self.file_manager.generate_svg()
        if success:
            svg_info = self.file_manager.get_svg_display_info()
            self.status_bar.config(text=f"✅ SVG generated: {svg_info}")
        else:
            self.status_bar.config(text="❌ SVG generation failed")
    
    def _test_file_validation(self):
        """Test file validation"""
        is_valid, errors = self.file_manager.validate_current_state()
        if is_valid:
            self.status_bar.config(text="✅ File validation passed")
        else:
            error_msg = "; ".join(errors[:2])
            self.status_bar.config(text=f"❌ File validation failed: {error_msg}")
    
    def _start_queue_monitoring(self):
        """Start the analysis queue monitoring (placeholder implementation)"""
        # This will be implemented in Phase 1.4
        print("🔧 Queue monitoring - to be implemented in Phase 1.4")


def main():
    """
    Main application entry point with window configuration and styling.
    
    This function maintains the exact same initialization sequence as the original
    application while using the new modular architecture.
    """
    # Create Tkinter root window
    root = tk.Tk()
    
    # Configure UI styling
    style = ttk.Style()
    style.configure('Success.TButton', foreground='green')
    style.configure('Warning.TButton', foreground='red')
    
        # Initialize main application (triggers __init__)
    LayoutVerificationApp(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (1400 // 2)
    y = (root.winfo_screenheight() // 2) - (900 // 2)
    root.geometry(f"1400x900+{x}+{y}")
    
    # Start event loop (blocks until window closed)
    root.mainloop()


if __name__ == "__main__":
    main()
