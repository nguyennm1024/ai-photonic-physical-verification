"""
Tile Review Panel Component
============================

Review AI analysis results and classify tiles.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from PIL import Image, ImageTk


class TileReviewPanel(ttk.LabelFrame):
    """
    Tile review section - Navigate and classify analyzed tiles.
    
    Shows:
    - Current tile image
    - Tile info (row, col, index)
    - AI analysis result
    - Classification buttons (Continuous/Discontinuity)
    - Navigation buttons (Previous/Next)
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize tile review panel.
        
        Args:
            parent: Parent tkinter widget
            **kwargs: Additional LabelFrame options
        """
        super().__init__(parent, text="4. Tile Display & Classification", **kwargs)
        
        # Callbacks
        self.prev_callback: Optional[Callable] = None
        self.next_callback: Optional[Callable] = None
        self.classify_callback: Optional[Callable[[str], None]] = None
        
        # Current state
        self.current_image_ref = None  # Keep reference to prevent garbage collection
        
        # Setup UI
        self._setup_widgets()
    
    def _setup_widgets(self):
        """Create and layout widgets"""
        # Tile image display - LARGER (takes most space)
        self.image_frame = ttk.Frame(self)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 2))

        self.tile_image_label = ttk.Label(
            self.image_frame,
            text="No tile selected\n\nProcess tiles to see results",
            anchor='center',
            justify='center'
        )
        self.tile_image_label.pack(fill=tk.BOTH, expand=True)

        # Tile info
        self.tile_info_label = ttk.Label(
            self,
            text="",
            font=('TkDefaultFont', 10, 'bold'),
            anchor='center'
        )
        self.tile_info_label.pack(pady=2)

        # AI result text - moderate size
        result_frame = ttk.LabelFrame(self, text="AI Analysis")
        result_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=(2, 5))

        # Scrolled text for AI result
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.ai_result_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            height=5,
            font=('TkDefaultFont', 9)
        )
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.ai_result_text.yview)
        self.ai_result_text.configure(yscrollcommand=scrollbar.set)
        self.ai_result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Navigation and classification buttons - compact spacing
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Navigation
        nav_frame = ttk.Frame(button_frame)
        nav_frame.pack(side=tk.TOP, fill=tk.X, pady=3)
        
        self.prev_button = ttk.Button(
            nav_frame,
            text="◀ Previous",
            command=self._on_prev_clicked,
            state='disabled',
            width=12
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(nav_frame, text="Navigate Tiles", font=('TkDefaultFont', 9)).pack(side=tk.LEFT, expand=True)
        
        self.next_button = ttk.Button(
            nav_frame,
            text="Next ▶",
            command=self._on_next_clicked,
            state='disabled',
            width=12
        )
        self.next_button.pack(side=tk.RIGHT, padx=5)
        
        # Classification buttons
        classify_frame = ttk.Frame(button_frame)
        classify_frame.pack(side=tk.TOP, fill=tk.X, pady=3)

        ttk.Label(classify_frame, text="User Classification:", font=('TkDefaultFont', 9, 'bold')).pack(side=tk.TOP, pady=2)
        
        btn_container = ttk.Frame(classify_frame)
        btn_container.pack()
        
        self.continuous_button = ttk.Button(
            btn_container,
            text="✓ Continuous",
            command=lambda: self._on_classify_clicked('continuous'),
            state='disabled',
            width=18
        )
        self.continuous_button.pack(side=tk.LEFT, padx=5)
        
        self.discontinuity_button = ttk.Button(
            btn_container,
            text="⚠ Discontinuity",
            command=lambda: self._on_classify_clicked('discontinuity'),
            state='disabled',
            width=18
        )
        self.discontinuity_button.pack(side=tk.LEFT, padx=5)
    
    def bind_prev_command(self, callback: Callable[[], None]):
        """Bind callback for previous button"""
        self.prev_callback = callback
    
    def bind_next_command(self, callback: Callable[[], None]):
        """Bind callback for next button"""
        self.next_callback = callback
    
    def bind_classify_command(self, callback: Callable[[str], None]):
        """Bind callback for classification"""
        self.classify_callback = callback
    
    def _on_prev_clicked(self):
        """Handle previous button click"""
        if self.prev_callback:
            self.prev_callback()
    
    def _on_next_clicked(self):
        """Handle next button click"""
        if self.next_callback:
            self.next_callback()
    
    def _on_classify_clicked(self, classification: str):
        """Handle classification button click"""
        if self.classify_callback:
            self.classify_callback(classification)
    
    def display_tile(self, image: Image.Image, row: int, col: int, index: int, ai_result: str = ""):
        """
        Display tile for review.
        
        Args:
            image: PIL Image of the tile
            row: Tile row
            col: Tile column
            index: Tile index
            ai_result: AI analysis result text
        """
        # Display image
        try:
            # Resize to fit - use available space (larger now)
            # Get current label size
            self.tile_image_label.update_idletasks()
            label_width = max(self.tile_image_label.winfo_width(), 200)
            label_height = max(self.tile_image_label.winfo_height(), 200)

            # Calculate display size maintaining aspect ratio - allow larger images
            display_size = (min(label_width - 10, 400), min(label_height - 10, 400))
            image_resized = image.copy()
            image_resized.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image_resized)
            self.current_image_ref = photo  # Keep reference
            self.tile_image_label.config(image=photo, text="")
        except Exception as e:
            self.tile_image_label.config(text=f"Error displaying image:\n{e}")
        
        # Update tile info
        self.tile_info_label.config(text=f"Tile #{index} (Row {row}, Col {col})")
        
        # Update AI result
        self.ai_result_text.delete('1.0', tk.END)
        if ai_result:
            self.ai_result_text.insert('1.0', ai_result)
        else:
            self.ai_result_text.insert('1.0', "No AI analysis available")
        
        # Enable buttons
        self.prev_button.config(state='normal')
        self.next_button.config(state='normal')
        self.continuous_button.config(state='normal')
        self.discontinuity_button.config(state='normal')
    
    def clear_display(self):
        """Clear tile display"""
        self.tile_image_label.config(image='', text="No tile selected")
        self.current_image_ref = None
        self.tile_info_label.config(text="")
        self.ai_result_text.delete('1.0', tk.END)
        self.disable_all()
    
    def enable_all(self):
        """Enable all controls"""
        self.prev_button.config(state='normal')
        self.next_button.config(state='normal')
        self.continuous_button.config(state='normal')
        self.discontinuity_button.config(state='normal')
    
    def disable_all(self):
        """Disable all controls"""
        self.prev_button.config(state='disabled')
        self.next_button.config(state='disabled')
        self.continuous_button.config(state='disabled')
        self.discontinuity_button.config(state='disabled')
    
    def highlight_classification(self, classification: Optional[str]):
        """
        Highlight the given classification button.
        
        Args:
            classification: 'continuous', 'discontinuity', or None
        """
        # Reset both buttons (this would need custom styling)
        # For now, just enable/disable as needed
        pass
