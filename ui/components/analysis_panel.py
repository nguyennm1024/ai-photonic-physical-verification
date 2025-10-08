"""
Analysis Panel Component
========================

Analysis results display with progress tracking.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional


class AnalysisPanel(ttk.Frame):
    """
    Analysis panel - Display analysis results and progress.
    
    Contains:
    - Progress bar
    - Progress label
    - Scrolled text area for results
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
        
        # Results text area
        results_frame = ttk.LabelFrame(self, text="Detailed Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=('Courier', 9)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
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
    
    def append_result(self, text: str, tag: Optional[str] = None):
        """
        Append text to results area.
        
        Args:
            text: Text to append
            tag: Optional tag for styling
        """
        self.results_text.insert(tk.END, text + '\n', tag)
        self.results_text.see(tk.END)
    
    def clear_results(self):
        """Clear all results text"""
        self.results_text.delete(1.0, tk.END)
    
    def set_results(self, text: str):
        """
        Set results text (replaces existing).
        
        Args:
            text: Text to display
        """
        self.clear_results()
        self.results_text.insert(1.0, text)
    
    def get_results(self) -> str:
        """
        Get current results text.
        
        Returns:
            Current text content
        """
        return self.results_text.get(1.0, tk.END)
    
    def configure_tags(self):
        """Configure text tags for styling"""
        self.results_text.tag_configure('header', font=('TkDefaultFont', 11, 'bold'))
        self.results_text.tag_configure('error', foreground='red')
        self.results_text.tag_configure('warning', foreground='orange')
        self.results_text.tag_configure('success', foreground='green')
        self.results_text.tag_configure('info', foreground='blue')
    
    def reset_progress(self):
        """Reset progress bar and label"""
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Ready")

