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
        self.classify_callback: Optional[Callable[[int, int, str], None]] = None

        # Current state
        self.current_image_ref = None  # Keep reference to prevent garbage collection
        self.current_tile_row: Optional[int] = None
        self.current_tile_col: Optional[int] = None
        
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

        # Status indicator - colored dots for analysis result
        status_indicator_frame = ttk.Frame(result_frame)
        status_indicator_frame.pack(fill=tk.X, padx=5, pady=(5, 2))

        self.status_label = ttk.Label(
            status_indicator_frame,
            text="",
            font=('TkDefaultFont', 9, 'bold')
        )
        self.status_label.pack(side=tk.LEFT)

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

        self.no_waveguide_button = ttk.Button(
            btn_container,
            text="🔍 No waveguide",
            command=lambda: self._on_classify_clicked('no_waveguide'),
            state='disabled',
            width=18
        )
        self.no_waveguide_button.pack(side=tk.LEFT, padx=5)
    
    def bind_prev_command(self, callback: Callable[[], None]):
        """Bind callback for previous button"""
        self.prev_callback = callback
    
    def bind_next_command(self, callback: Callable[[], None]):
        """Bind callback for next button"""
        self.next_callback = callback
    
    def bind_classify_command(self, callback: Callable[[int, int, str], None]):
        """Bind callback for classification (row, col, classification)"""
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
        print(f"🖱️  Classification button clicked: {classification}")
        print(f"   Current tile: row={self.current_tile_row}, col={self.current_tile_col}")
        print(f"   Callback bound: {self.classify_callback is not None}")

        if self.classify_callback and self.current_tile_row is not None and self.current_tile_col is not None:
            print(f"   ✅ Calling classify callback with ({self.current_tile_row}, {self.current_tile_col}, '{classification}')")
            self.classify_callback(self.current_tile_row, self.current_tile_col, classification)
        else:
            if not self.classify_callback:
                print(f"   ❌ No callback bound!")
            if self.current_tile_row is None or self.current_tile_col is None:
                print(f"   ❌ No current tile selected!")
    
    def display_tile(self, image: Image.Image, row: int, col: int, index: int, ai_result: str = "", classification: str = None, is_user_classification: bool = False):
        """
        Display tile for review.

        Args:
            image: PIL Image of the tile
            row: Tile row
            col: Tile column
            index: Tile index
            ai_result: AI analysis result text
            classification: Classification result ('continuity', 'discontinuity', 'no_waveguide')
            is_user_classification: Whether this is a user classification (shows [USER] tag)
        """
        # Store current tile coordinates for classification
        self.current_tile_row = row
        self.current_tile_col = col
        print(f"📍 Tile review: Stored current tile coordinates - row={row}, col={col}")

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
        
        # Update AI result and status indicator
        self.ai_result_text.delete('1.0', tk.END)
        if ai_result:
            self.ai_result_text.insert('1.0', ai_result)
            # Determine status from classification if available
            if classification:
                # Use public method if user classification (shows [USER] tag)
                if is_user_classification:
                    self.update_status_indicator(classification)
                else:
                    self._update_status_indicator(classification)
            else:
                self.status_label.config(text="", foreground='black')
        else:
            self.ai_result_text.insert('1.0', "No AI analysis available")
            self.status_label.config(text="", foreground='black')
        
        # Enable buttons
        self.prev_button.config(state='normal')
        self.next_button.config(state='normal')
        self.continuous_button.config(state='normal')
        self.discontinuity_button.config(state='normal')
        self.no_waveguide_button.config(state='normal')
    
    def clear_display(self):
        """Clear tile display"""
        self.tile_image_label.config(image='', text="No tile selected")
        self.current_image_ref = None
        self.current_tile_row = None
        self.current_tile_col = None
        self.tile_info_label.config(text="")
        self.ai_result_text.delete('1.0', tk.END)
        self.status_label.config(text="", foreground='black')
        self.disable_all()
    
    def enable_all(self):
        """Enable all controls"""
        self.prev_button.config(state='normal')
        self.next_button.config(state='normal')
        self.continuous_button.config(state='normal')
        self.discontinuity_button.config(state='normal')
        self.no_waveguide_button.config(state='normal')
    
    def disable_all(self):
        """Disable all controls"""
        self.prev_button.config(state='disabled')
        self.next_button.config(state='disabled')
        self.continuous_button.config(state='disabled')
        self.discontinuity_button.config(state='disabled')
        self.no_waveguide_button.config(state='disabled')
    
    def _update_status_indicator(self, classification: str):
        """
        Update the status indicator based on AI classification.

        Args:
            classification: AI classification result ('continuity', 'discontinuity', 'no_waveguide')
        """
        classification_lower = classification.lower().strip()

        # Map classification to status
        if classification_lower == 'discontinuity':
            self.status_label.config(text="🔴 Discontinuity", foreground='red')
        elif classification_lower == 'no_waveguide':
            self.status_label.config(text="🟠 No waveguide", foreground='orange')
        elif classification_lower == 'continuity':
            self.status_label.config(text="🟢 Continuity", foreground='green')
        else:
            # Unknown classification - show neutral
            self.status_label.config(text="⚪ Analyzed", foreground='gray')

    def update_status_indicator(self, classification: str):
        """
        Public method to update status indicator (for user classification).

        Args:
            classification: Classification result ('continuity', 'discontinuity', 'no_waveguide')
        """
        print(f"📊 TileReviewPanel.update_status_indicator() called with: {classification}")
        classification_lower = classification.lower().strip()

        # Map classification to status - show as USER OVERRIDE
        if classification_lower == 'discontinuity':
            self.status_label.config(text="🔴 Discontinuity [USER]", foreground='red')
            print(f"   ✅ Status label updated to: 🔴 Discontinuity [USER]")
        elif classification_lower == 'no_waveguide':
            self.status_label.config(text="🟠 No waveguide [USER]", foreground='orange')
            print(f"   ✅ Status label updated to: 🟠 No waveguide [USER]")
        elif classification_lower in ['continuity', 'continuous']:
            self.status_label.config(text="🟢 Continuity [USER]", foreground='green')
            print(f"   ✅ Status label updated to: 🟢 Continuity [USER]")
        else:
            # Unknown classification
            self.status_label.config(text="⚪ Classified [USER]", foreground='gray')
            print(f"   ⚠️  Status label updated to: ⚪ Classified [USER] (unknown: {classification})")

    def highlight_classification(self, classification: Optional[str]):
        """
        Highlight the given classification button.

        Args:
            classification: 'continuous', 'discontinuity', or None
        """
        # Reset both buttons (this would need custom styling)
        # For now, just enable/disable as needed
        pass
