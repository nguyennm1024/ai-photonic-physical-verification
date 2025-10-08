"""
Analysis Panel Component
========================

Analysis progress tracking.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class AnalysisPanel(ttk.Frame):
    """
    Analysis panel - Display analysis progress.
    
    Contains:
    - Progress bar
    - Progress label
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize analysis panel.
        
        Args:
            parent: Parent tkinter widget
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)
        
        # Setup UI
        self._setup_widgets()
    
    def _setup_widgets(self):
        """Create and layout widgets"""
        # Header label
        header = ttk.Label(
            self,
            text="Analysis Results",
            font=('TkDefaultFont', 12, 'bold')
        )
        header.pack(pady=(0, 5))
        
        # Progress section
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=300
        )
        self.progress_bar.pack(fill=tk.X, pady=2)
        
        # Progress label
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.pack(pady=2)
    
    def set_progress(self, value: int, maximum: int = 100):
        """
        Update progress bar.
        
        Args:
            value: Current progress value
            maximum: Maximum progress value
        """
        self.progress_bar['maximum'] = maximum
        self.progress_bar['value'] = value
    
    def set_progress_text(self, text: str):
        """
        Update progress label text.
        
        Args:
            text: Progress text to display
        """
        self.progress_label.config(text=text)
    
    def reset_progress(self):
        """Reset progress bar and label"""
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Ready")

