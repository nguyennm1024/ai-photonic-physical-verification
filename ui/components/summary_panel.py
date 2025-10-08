"""
Summary Panel Component
=======================

Processing summary statistics display.
"""

import tkinter as tk
from tkinter import ttk


class SummaryPanel(ttk.LabelFrame):
    """
    Summary panel - Display processing statistics and summary.
    
    Shows:
    - Total tiles processed
    - Tiles with issues
    - Clean tiles
    - Processing time
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize summary panel.
        
        Args:
            parent: Parent tkinter widget
            **kwargs: Additional LabelFrame options
        """
        super().__init__(parent, text="Processing Summary", **kwargs)
        
        # Setup UI
        self._setup_widgets()
    
    def _setup_widgets(self):
        """Create and layout widgets"""
        # Create labels in grid
        # Total tiles
        ttk.Label(self, text="Total Tiles:").grid(
            row=0, column=0, sticky='w', padx=5, pady=2
        )
        self.total_label = ttk.Label(self, text="0")
        self.total_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Tiles with issues
        ttk.Label(self, text="Issues Found:").grid(
            row=1, column=0, sticky='w', padx=5, pady=2
        )
        self.issues_label = ttk.Label(self, text="0", foreground='red')
        self.issues_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Clean tiles
        ttk.Label(self, text="Clean Tiles:").grid(
            row=2, column=0, sticky='w', padx=5, pady=2
        )
        self.clean_label = ttk.Label(self, text="0", foreground='green')
        self.clean_label.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        # Processing time
        ttk.Label(self, text="Processing Time:").grid(
            row=3, column=0, sticky='w', padx=5, pady=2
        )
        self.time_label = ttk.Label(self, text="0s")
        self.time_label.grid(row=3, column=1, sticky='w', padx=5, pady=2)
        
        # Status
        ttk.Label(self, text="Status:").grid(
            row=4, column=0, sticky='w', padx=5, pady=2
        )
        self.status_label = ttk.Label(self, text="Idle")
        self.status_label.grid(row=4, column=1, sticky='w', padx=5, pady=2)
    
    def update_summary(
        self,
        total: int = 0,
        issues: int = 0,
        clean: int = 0,
        time_elapsed: float = 0.0
    ):
        """
        Update summary statistics.
        
        Args:
            total: Total tiles processed
            issues: Number of tiles with issues
            clean: Number of clean tiles
            time_elapsed: Processing time in seconds
        """
        self.total_label.config(text=str(total))
        self.issues_label.config(text=str(issues))
        self.clean_label.config(text=str(clean))
        self.time_label.config(text=f"{time_elapsed:.1f}s")
    
    def set_status(self, status: str):
        """
        Update status label.
        
        Args:
            status: Status text to display
        """
        self.status_label.config(text=status)
    
    def reset(self):
        """Reset all values to zero"""
        self.total_label.config(text="0")
        self.issues_label.config(text="0")
        self.clean_label.config(text="0")
        self.time_label.config(text="0s")
        self.status_label.config(text="Idle")

