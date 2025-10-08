"""
Modern UI Theme
===============

Modern styling for the layout verification application.
"""

import tkinter as tk
from tkinter import ttk


class ModernTheme:
    """Apply modern styling to the application"""
    
    # Color palette - Modern, clean design with good contrast
    COLORS = {
        'primary': '#1976D2',      # Material Blue (darker for better contrast)
        'primary_dark': '#0D47A1',
        'primary_light': '#BBDEFB',
        'secondary': '#F57C00',    # Material Orange (darker)
        'success': '#388E3C',      # Material Green (darker)
        'warning': '#D84315',      # Material Deep Orange (darker)
        'error': '#C62828',        # Material Red (darker)
        'background': '#F5F5F5',   # Light gray background
        'surface': '#FFFFFF',      # White surface
        'text_primary': '#000000', # Pure black for maximum contrast
        'text_secondary': '#424242',  # Dark gray
        'border': '#BDBDBD',       # Medium gray border
        'hover': '#E8E8E8',        # Hover background
    }
    
    @classmethod
    def apply(cls, root: tk.Tk):
        """
        Apply modern theme to the application.
        
        Args:
            root: Root tkinter window
        """
        style = ttk.Style()
        
        # Force light theme regardless of system appearance
        try:
            # Use 'clam' theme as base - it's consistent across platforms
            available_themes = style.theme_names()
            if 'clam' in available_themes:
                style.theme_use('clam')
            elif 'alt' in available_themes:
                style.theme_use('alt')
            else:
                style.theme_use('default')
        except:
            pass  # Use default if all fail
        
        # Configure root window - force light background
        root.configure(bg=cls.COLORS['surface'])
        
        # Force option database settings to override system appearance
        root.option_add('*TLabelframe*background', cls.COLORS['surface'])
        root.option_add('*TLabelframe*foreground', cls.COLORS['text_primary'])
        root.option_add('*TFrame*background', cls.COLORS['surface'])
        root.option_add('*TLabel*background', cls.COLORS['surface'])
        root.option_add('*TLabel*foreground', cls.COLORS['text_primary'])
        root.option_add('*TButton*background', cls.COLORS['primary'])
        root.option_add('*TButton*foreground', cls.COLORS['surface'])
        
        # ===== Frames =====
        style.configure('TFrame', background=cls.COLORS['surface'])
        style.configure('TLabelframe', 
                       background=cls.COLORS['surface'], 
                       borderwidth=2, 
                       relief='solid',
                       bordercolor=cls.COLORS['border'])
        style.configure('TLabelframe.Label', 
                       background=cls.COLORS['surface'],
                       foreground=cls.COLORS['text_primary'], 
                       font=('TkDefaultFont', 11, 'bold'))
        
        # ===== Labels =====
        style.configure('TLabel', 
                       background=cls.COLORS['surface'],
                       foreground=cls.COLORS['text_primary'],
                       font=('TkDefaultFont', 10))
        
        # ===== Buttons =====
        style.configure('TButton',
                       padding=(10, 5),
                       background=cls.COLORS['primary'],
                       foreground='white',
                       borderwidth=1,
                       relief='raised',
                       font=('TkDefaultFont', 10, 'bold'))
        
        style.map('TButton',
                 background=[('active', cls.COLORS['primary_dark']),
                            ('pressed', cls.COLORS['primary_dark']),
                            ('disabled', '#CCCCCC'),
                            ('!disabled', cls.COLORS['primary'])],
                 foreground=[('disabled', '#666666'),
                            ('!disabled', 'white')])
        
        # Success button (Continuous)
        style.configure('Success.TButton',
                       padding=(10, 5),
                       relief='flat')
        style.map('Success.TButton',
                 background=[('active', '#66BB6A'),
                            ('!disabled', cls.COLORS['success'])],
                 foreground=[('!disabled', cls.COLORS['surface'])])
        
        # Warning button (Discontinuity)
        style.configure('Warning.TButton',
                       padding=(10, 5),
                       relief='flat')
        style.map('Warning.TButton',
                 background=[('active', '#FF7043'),
                            ('!disabled', cls.COLORS['warning'])],
                 foreground=[('!disabled', cls.COLORS['surface'])])
        
        # Secondary button
        style.configure('Secondary.TButton',
                       padding=(10, 5),
                       relief='flat')
        style.map('Secondary.TButton',
                 background=[('active', '#FFB74D'),
                            ('!disabled', cls.COLORS['secondary'])],
                 foreground=[('!disabled', cls.COLORS['surface'])])
        
        # ===== Entry and Spinbox =====
        style.configure('TEntry',
                       fieldbackground=cls.COLORS['surface'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=1)
        
        style.configure('TSpinbox',
                       fieldbackground=cls.COLORS['surface'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=1,
                       arrowsize=13)
        
        # ===== Progressbar =====
        style.configure('TProgressbar',
                       troughcolor=cls.COLORS['border'],
                       background=cls.COLORS['primary'],
                       borderwidth=0,
                       thickness=8)
        
        # ===== Notebook (Tabs) =====
        style.configure('TNotebook', background=cls.COLORS['background'], borderwidth=0)
        style.configure('TNotebook.Tab',
                       padding=(15, 5),
                       font=('TkDefaultFont', 9))
        style.map('TNotebook.Tab',
                 background=[('selected', cls.COLORS['primary']),
                            ('!selected', cls.COLORS['surface'])],
                 foreground=[('selected', cls.COLORS['surface']),
                            ('!selected', cls.COLORS['text_primary'])])
        
        # ===== Separator =====
        style.configure('TSeparator', background=cls.COLORS['border'])
        
        # ===== Scale/Slider =====
        style.configure('TScale',
                       background=cls.COLORS['background'],
                       troughcolor=cls.COLORS['border'])
        
        return style
    
    @classmethod
    def style_text_widget(cls, text_widget: tk.Text):
        """
        Apply modern styling to a Text widget.
        
        Args:
            text_widget: tkinter Text widget to style
        """
        text_widget.configure(
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_primary'],
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=cls.COLORS['primary'],
            highlightbackground=cls.COLORS['border'],
            font=('TkDefaultFont', 9),
            padx=5,
            pady=5
        )
    
    @classmethod
    def style_listbox(cls, listbox: tk.Listbox):
        """
        Apply modern styling to a Listbox widget.
        
        Args:
            listbox: tkinter Listbox widget to style
        """
        listbox.configure(
            background=cls.COLORS['surface'],
            foreground=cls.COLORS['text_primary'],
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=cls.COLORS['primary'],
            highlightbackground=cls.COLORS['border'],
            selectbackground=cls.COLORS['primary_light'],
            selectforeground=cls.COLORS['text_primary'],
            activestyle='none',
            font=('TkDefaultFont', 9)
        )
    
    @classmethod
    def style_canvas(cls, canvas: tk.Canvas):
        """
        Apply modern styling to a Canvas widget.
        
        Args:
            canvas: tkinter Canvas widget to style
        """
        canvas.configure(
            background=cls.COLORS['surface'],
            highlightthickness=1,
            highlightcolor=cls.COLORS['border'],
            highlightbackground=cls.COLORS['border']
        )
    
    @classmethod
    def create_card(cls, parent, title: str = None, **kwargs) -> ttk.Frame:
        """
        Create a card-style frame (elevated surface).
        
        Args:
            parent: Parent widget
            title: Optional title for the card
            **kwargs: Additional Frame options
            
        Returns:
            Configured Frame widget
        """
        if title:
            card = ttk.LabelFrame(parent, text=title, **kwargs)
        else:
            card = ttk.Frame(parent, **kwargs)
        
        card.configure(relief='raised', borderwidth=1)
        return card
