"""
Grid Configuration Panel Component
===================================

Grid configuration controls for tile system parameters.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict


class GridConfigPanel(ttk.LabelFrame):
    """
    Grid configuration section - Set tile grid parameters.
    
    Controls:
    - Grid Size (rows/cols)
    - Tile Overlap
    - Generate Grid button
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize grid config panel.
        
        Args:
            parent: Parent tkinter widget
            **kwargs: Additional LabelFrame options
        """
        super().__init__(parent, text="2. Grid Configuration", **kwargs)
        
        # Callback for generate button
        self.generate_callback: Optional[Callable] = None
        
        # Setup UI
        self._setup_widgets()
    
    def _setup_widgets(self):
        """Create and layout widgets"""
        # All controls in ONE compact row
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Rows
        ttk.Label(controls_frame, text="Rows:").pack(side=tk.LEFT, padx=(0, 2))
        self.rows_var = tk.IntVar(value=3)
        self.rows_spinbox = ttk.Spinbox(
            controls_frame,
            from_=1,
            to=50,
            textvariable=self.rows_var,
            width=5
        )
        self.rows_spinbox.pack(side=tk.LEFT, padx=2)
        
        # Columns
        ttk.Label(controls_frame, text="Cols:").pack(side=tk.LEFT, padx=(8, 2))
        self.cols_var = tk.IntVar(value=3)
        self.cols_spinbox = ttk.Spinbox(
            controls_frame,
            from_=1,
            to=50,
            textvariable=self.cols_var,
            width=5
        )
        self.cols_spinbox.pack(side=tk.LEFT, padx=2)
        
        # Overlap
        ttk.Label(controls_frame, text="Overlap:").pack(side=tk.LEFT, padx=(8, 2))
        self.overlap_var = tk.IntVar(value=10)
        self.overlap_spinbox = ttk.Spinbox(
            controls_frame,
            from_=0,
            to=50,
            textvariable=self.overlap_var,
            width=5
        )
        self.overlap_spinbox.pack(side=tk.LEFT, padx=2)
        ttk.Label(controls_frame, text="%").pack(side=tk.LEFT)
        
        # Info label (for grid info)
        self.info_label = ttk.Label(self, text="")
        self.info_label.pack(padx=5, pady=2)
    
    def bind_generate_command(self, callback: Callable[[int, int, int], None]):
        """
        Bind callback for generate button.
        
        Args:
            callback: Function to call with (rows, cols, overlap)
        """
        self.generate_callback = callback
    
    def _on_generate_clicked(self):
        """Handle generate button click"""
        if self.generate_callback:
            rows = self.rows_var.get()
            cols = self.cols_var.get()
            overlap = self.overlap_var.get()
            self.generate_callback(rows, cols, overlap)
    
    def get_config(self) -> Dict[str, int]:
        """
        Get current grid configuration.
        
        Returns:
            Dictionary with rows, cols, overlap
        """
        return {
            'rows': self.rows_var.get(),
            'cols': self.cols_var.get(),
            'overlap': self.overlap_var.get()
        }
    
    def set_config(self, rows: int, cols: int, overlap: int):
        """
        Set grid configuration values.
        
        Args:
            rows: Number of rows
            cols: Number of columns
            overlap: Overlap in pixels
        """
        self.rows_var.set(rows)
        self.cols_var.set(cols)
        self.overlap_var.set(overlap)
    
    def set_info(self, message: str):
        """
        Update info label.
        
        Args:
            message: Info message to display
        """
        self.info_label.config(text=message)
    
    def clear_info(self):
        """Clear info label"""
        self.info_label.config(text="")
    
    def enable(self):
        """Enable all controls"""
        self.rows_spinbox.config(state='normal')
        self.cols_spinbox.config(state='normal')
        self.overlap_spinbox.config(state='normal')
        self.generate_button.config(state='normal')
    
    def disable(self):
        """Disable all controls"""
        self.rows_spinbox.config(state='disabled')
        self.cols_spinbox.config(state='disabled')
        self.overlap_spinbox.config(state='disabled')
        self.generate_button.config(state='disabled')

