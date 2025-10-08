"""
Processing Buttons Component
=============================

AI analysis control buttons.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class ProcessingButtons(ttk.LabelFrame):
    """
    Processing section - AI analysis control buttons.
    
    Buttons:
    - Process All Tiles (parallel)
    - Cancel Processing
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize processing buttons.
        
        Args:
            parent: Parent tkinter widget
            **kwargs: Additional LabelFrame options
        """
        super().__init__(parent, text="3. Processing", **kwargs)
        
        # Callbacks
        self.generate_callback: Optional[Callable] = None
        self.process_all_callback: Optional[Callable] = None
        self.select_roi_callback: Optional[Callable] = None
        self.process_roi_callback: Optional[Callable] = None
        self.cancel_callback: Optional[Callable] = None
        
        # State for ROI selection mode
        self.roi_selecting = False
        
        # Setup UI
        self._setup_widgets()
    
    def _setup_widgets(self):
        """Create and layout widgets"""
        # Row 1: Generate Grid + Process All Tiles
        row1 = ttk.Frame(self)
        row1.pack(fill=tk.X, padx=5, pady=3)
        
        self.generate_button = ttk.Button(
            row1,
            text="Generate Grid",
            command=self._on_generate_clicked
        )
        self.generate_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.process_all_button = ttk.Button(
            row1,
            text="Process All Tiles",
            command=self._on_process_all_clicked
        )
        self.process_all_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Row 2: Select ROIs + Process Selected Regions
        row2 = ttk.Frame(self)
        row2.pack(fill=tk.X, padx=5, pady=3)
        
        self.select_roi_button = ttk.Button(
            row2,
            text="Select ROIs",
            command=self._on_select_roi_clicked
        )
        self.select_roi_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.process_roi_button = ttk.Button(
            row2,
            text="Process Selected Regions",
            command=self._on_process_roi_clicked
        )
        self.process_roi_button.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Row 3: Cancel Processing
        self.cancel_button = ttk.Button(
            self,
            text="Cancel Processing",
            command=self._on_cancel_clicked,
            state='disabled'
        )
        self.cancel_button.pack(padx=5, pady=3, fill=tk.X)

        # Status label - wrappable
        self.status_label = ttk.Label(self, text="", wraplength=300)
        self.status_label.pack(padx=5, pady=2, fill=tk.X)
    
    def bind_generate_command(self, callback: Callable[[], None]):
        """
        Bind callback for generate grid button.
        
        Args:
            callback: Function to call when generate grid is clicked
        """
        self.generate_callback = callback
    
    def bind_process_all_command(self, callback: Callable[[], None]):
        """
        Bind callback for process all button.
        
        Args:
            callback: Function to call when process all is clicked
        """
        self.process_all_callback = callback
    
    def bind_select_roi_command(self, callback: Callable[[bool], None]):
        """
        Bind callback for select ROI button (toggle).
        
        Args:
            callback: Function to call with selection state (True/False)
        """
        self.select_roi_callback = callback
    
    def bind_process_roi_command(self, callback: Callable[[], None]):
        """
        Bind callback for process ROI button.
        
        Args:
            callback: Function to call when process ROI is clicked
        """
        self.process_roi_callback = callback
    
    def bind_cancel_command(self, callback: Callable[[], None]):
        """
        Bind callback for cancel button.
        
        Args:
            callback: Function to call when cancel is clicked
        """
        self.cancel_callback = callback
    
    def _on_generate_clicked(self):
        """Handle generate grid button click"""
        if self.generate_callback:
            self.generate_callback()
    
    def _on_process_all_clicked(self):
        """Handle process all button click"""
        if self.process_all_callback:
            self.process_all_callback()
    
    def _on_select_roi_clicked(self):
        """Handle select ROI button click (toggle)"""
        self.roi_selecting = not self.roi_selecting
        if self.roi_selecting:
            self.select_roi_button.config(text="✓ Selecting ROIs")
        else:
            self.select_roi_button.config(text="Select ROIs")
        
        if self.select_roi_callback:
            self.select_roi_callback(self.roi_selecting)
    
    def _on_process_roi_clicked(self):
        """Handle process ROI button click"""
        if self.process_roi_callback:
            self.process_roi_callback()
    
    def _on_cancel_clicked(self):
        """Handle cancel button click"""
        if self.cancel_callback:
            self.cancel_callback()
    
    def set_status(self, message: str):
        """
        Update status label.
        
        Args:
            message: Status message to display
        """
        self.status_label.config(text=message)
    
    def set_processing_state(self):
        """Set UI to processing state (disable process, enable cancel)"""
        self.process_all_button.config(state='disabled')
        self.process_roi_button.config(state='disabled')
        self.cancel_button.config(state='normal')
    
    def set_idle_state(self):
        """Set UI to idle state (enable process, disable cancel)"""
        self.process_all_button.config(state='normal')
        self.process_roi_button.config(state='normal')
        self.cancel_button.config(state='disabled')
    
    def enable(self):
        """Enable processing controls"""
        self.set_idle_state()
    
    def disable(self):
        """Disable all controls"""
        self.process_all_button.config(state='disabled')
        self.process_roi_button.config(state='disabled')
        self.cancel_button.config(state='disabled')

