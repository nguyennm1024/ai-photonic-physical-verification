"""
File Controls Component
=======================

File loading controls for GDS file selection and info display.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from typing import Callable, Optional


class FileControls(ttk.LabelFrame):
    """
    File operations section - Load GDS files and display info.
    
    Displays:
    - Load GDS File button
    - File info label (name and size)
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize file controls.
        
        Args:
            parent: Parent tkinter widget
            **kwargs: Additional LabelFrame options
        """
        super().__init__(parent, text="1. File Operations", **kwargs)
        
        # Callback for load button
        self.load_callback: Optional[Callable] = None
        
        # Setup UI
        self._setup_widgets()
    
    def _setup_widgets(self):
        """Create and layout widgets"""
        # Load button
        self.load_button = ttk.Button(
            self,
            text="Load GDS File",
            command=self._on_load_clicked
        )
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)

        # File info label (wraplength will be set dynamically)
        self.file_info_label = ttk.Label(self, text="No file loaded", wraplength=250)
        self.file_info_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
    
    def bind_load_command(self, callback: Callable[[str], None]):
        """
        Bind callback for load button.
        
        Args:
            callback: Function to call with selected file path
        """
        self.load_callback = callback
    
    def _on_load_clicked(self):
        """Handle load button click - show file dialog"""
        file_path = filedialog.askopenfilename(
            title="Select GDS File",
            filetypes=[("GDS files", "*.gds *.GDS"), ("All files", "*.*")],
            initialdir="./data/"
        )
        
        if file_path and self.load_callback:
            self.load_callback(file_path)
    
    def set_file_info(self, file_path: str):
        """
        Update file info display.
        
        Args:
            file_path: Path to loaded file
        """
        path = Path(file_path)
        size_mb = path.stat().st_size / (1024 * 1024)
        self.file_info_label.config(text=f"{path.name} ({size_mb:.1f} MB)")
    
    def clear_file_info(self):
        """Clear file info display"""
        self.file_info_label.config(text="No file loaded")
    
    def enable(self):
        """Enable the load button"""
        self.load_button.config(state='normal')
    
    def disable(self):
        """Disable the load button"""
        self.load_button.config(state='disabled')

