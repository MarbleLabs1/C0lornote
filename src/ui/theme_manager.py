"""
C0lorNote Theme Manager

This module handles application theming, including light and dark mode support,
custom styling for widgets, and integration with ttkthemes.
"""

import os
import sys
import logging
import subprocess
import tkinter as tk
from tkinter import ttk, font
from typing import Dict, Any, Optional, Tuple

# Import application settings
from src.config import settings


class ThemeManager:
    """
    Manages application themes, including light and dark mode support.
    Provides consistent styling for all UI elements with a modern macOS-inspired look.
    """
    
    # Define light theme colors
    LIGHT_THEME = {
        "bg": "#FFFFFF",  # Background color
        "fg": "#000000",  # Foreground (text) color
        "sidebar_bg": "#F2F2F2",  # Sidebar background
        "sidebar_fg": "#333333",  # Sidebar text
        "item_bg": "#FFFFFF",  # Note item background
        "item_selected_bg": "#E5F3FF",  # Selected note background
        "item_hover_bg": "#F5F5F5",  # Hover note background
        "item_active_bg": "#CCE8FF",  # Active note background
        "toolbar_bg": "#F7F7F7",  # Toolbar background
        "border": "#E0E0E0",  # Border color
        "accent": "#0078D7",  # Accent color (buttons, links)
        "accent_hover": "#0063B1",  # Accent hover
        "error": "#D73A49",  # Error color
        "success": "#28A745",  # Success color
        "warning": "#F9C22E",  # Warning color
        "info": "#0366D6",  # Info color
        "note_colors": {  # Background colors for colored notes
            "default": "#FFFFFF",
            "red": "#FFEBEE",
            "orange": "#FFF3E0",
            "yellow": "#FFFDE7",
            "green": "#E8F5E9",
            "blue": "#E3F2FD",
            "purple": "#F3E5F5",
            "brown": "#EFEBE9",
            "gray": "#F5F5F5"
        }
    }
    
    # Define dark theme colors
    DARK_THEME = {
        "bg": "#2D2D2D",  # Background color
        "fg": "#F5F5F5",  # Foreground (text) color
        "sidebar_bg": "#252525",  # Sidebar background
        "sidebar_fg": "#E0E0E0",  # Sidebar text
        "item_bg": "#333333",  # Note item background
        "item_selected_bg": "#3A3A3A",  # Selected note background
        "item_hover_bg": "#404040",  # Hover note background
        "item_active_bg": "#454545",  # Active note background
        "toolbar_bg": "#363636",  # Toolbar background
        "border": "#505050",  # Border color
        "accent": "#0078D7",  # Accent color (buttons, links)
        "accent_hover": "#2B88D8",  # Accent hover
        "error": "#F85149",  # Error color
        "success": "#3FB950",  # Success color
        "warning": "#F8E3A1",  # Warning color
        "info": "#58A6FF",  # Info color
        "note_colors": {  # Background colors for colored notes in dark mode
            "default": "#333333",
            "red": "#4A2525",
            "orange": "#4A3525",
            "yellow": "#4A4A25",
            "green": "#254A25",
            "blue": "#25254A",
            "purple": "#4A254A",
            "brown": "#3D3025",
            "gray": "#404040"
        }
    }
    
    # Define ttk themes that work well with light and dark mode
    TTK_THEMES = {
        "light": "arc",  # Light theme
        "dark": "equilux"  # Dark theme
    }
    
    def __init__(self, root, app_settings: Dict[str, Any]):
        """
        Initialize the theme manager
        
        Args:
            root: The root tkinter window (ThemedTk instance)
            app_settings: Application settings dictionary
        """
        self.root = root
        self.app_settings = app_settings
        self.current_theme_mode = None
        self.style = ttk.Style()
        
        # Determine initial theme based on settings
        self.use_system_theme = app_settings.get("use_system_theme", True)
        self.dark_mode = app_settings.get("dark_mode", False)
        
        # Initialize themes
        self.initialize_themes()
        
        # Apply initial theme
        self.apply_theme()
        
        # Set up custom fonts
        self.setup_fonts()
    
    def initialize_themes(self):
        """Initialize available themes and styles"""
        # Get available ttk themes
        available_themes = self.style.theme_names()
        logging.info(f"Available ttk themes: {', '.join(available_themes)}")
        
        # Fall back to default themes if preferred themes are not available
        if self.TTK_THEMES["light"] not in available_themes:
            self.TTK_THEMES["light"] = "clam"
        
        if self.TTK_THEMES["dark"] not in available_themes:
            if "equilux" in available_themes:
                self.TTK_THEMES["dark"] = "equilux"
            elif "black" in available_themes:
                self.TTK_THEMES["dark"] = "black"
            else:
                self.TTK_THEMES["dark"] = self.TTK_THEMES["light"]
    
    def get_system_theme(self) -> str:
        """
        Detect the system theme (light or dark)
        
        Returns:
            str: "light" or "dark"
        """
        try:
            # Check for common desktop environments and their theme settings
            if sys.platform == "linux":
                # GNOME
                try:
                    result = subprocess.run(
                        ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                        capture_output=True, text=True, check=False
                    )
                    if "dark" in result.stdout.lower():
                        return "dark"
                except Exception:
                    pass
                
                # Try GTK theme
                try:
                    result = subprocess.run(
                        ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                        capture_output=True, text=True, check=False
                    )
                    if "dark" in result.stdout.lower():
                        return "dark"
                except Exception:
                    pass
                
                # KDE Plasma
                try:
                    if os.path.exists(os.path.expanduser("~/.config/kdeglobals")):
                        with open(os.path.expanduser("~/.config/kdeglobals"), "r") as f:
                            content = f.read()
                            if "ColorScheme=Breeze Dark" in content:
                                return "dark"
                except Exception:
                    pass
            
            elif sys.platform == "darwin":  # macOS
                try:
                    result = subprocess.run(
                        ["defaults", "read", "-g", "AppleInterfaceStyle"],
                        capture_output=True, text=True, check=False
                    )
                    if "Dark" in result.stdout:
                        return "dark"
                except Exception:
                    pass
            
            elif sys.platform == "win32":  # Windows
                try:
                    import winreg
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    winreg.CloseKey(key)
                    if value == 0:
                        return "dark"
                except Exception:
                    pass
        
        except Exception as e:
            logging.warning(f"Failed to detect system theme: {e}")
        
        # Default to light if cannot detect
        return "light"
    
    def apply_theme(self, theme_mode: Optional[str] = None):
        """
        Apply the specified theme or use the theme based on settings
        
        Args:
            theme_mode (str, optional): "light" or "dark". If None, uses the current settings
        """
        # Determine theme mode to use
        if theme_mode is None:
            if self.use_system_theme:
                theme_mode = self.get_system_theme()
            else:
                theme_mode = "dark" if self.dark_mode else "light"
        
        # Store the current theme mode
        self.current_theme_mode = theme_mode
        
        # Apply the ttk theme
        ttk_theme = self.TTK_THEMES["dark"] if theme_mode == "dark" else self.TTK_THEMES["light"]
        
        try:
            self.root.set_theme(ttk_theme)
        except Exception as e:
            logging.error(f"Failed to set ttk theme '{ttk_theme}': {e}")
            # Fall back to a basic theme
            try:
                self.style.theme_use("clam")
            except Exception:
                pass
        
        # Apply additional styling based on the selected theme
        theme_colors = self.DARK_THEME if theme_mode == "dark" else self.LIGHT_THEME
        
        # Configure TTK styles for custom widgets
        self.style.configure("TLabel", background=theme_colors["bg"], foreground=theme_colors["fg"])
        self.style.configure("TFrame", background=theme_colors["bg"])
        self.style.configure("TButton", background=theme_colors["accent"], foreground="white")
        self.style.map("TButton", 
                      background=[("active", theme_colors["accent_hover"]), 
                                 ("disabled", theme_colors["border"])])
        
        # Sidebar styles
        self.style.configure("Sidebar.TFrame", background=theme_colors["sidebar_bg"])
        self.style.configure("Sidebar.TLabel", background=theme_colors["sidebar_bg"], 
                            foreground=theme_colors["sidebar_fg"])
        self.style.configure("Sidebar.TButton", background=theme_colors["sidebar_bg"])
        
        # Toolbar styles
        self.style.configure("Toolbar.TFrame", background=theme_colors["toolbar_bg"])
        self.style.configure("Toolbar.TButton", background=theme_colors["toolbar_bg"])
        
        # Note list styles
        self.style.configure("NoteItem.TFrame", background=theme_colors["item_bg"])
        self.style.configure("NoteItem.TLabel", background=theme_colors["item_bg"], 
                            foreground=theme_colors["fg"])
        
        # Configure the root window
        self.root.configure(background=theme_colors["bg"])
        
        # Configure colors on all existing ttk widgets
        for widget in self.root.winfo_children():
            self._configure_widget_theme(widget, theme_colors)
    
    def _configure_widget_theme(self, widget, theme_colors: Dict[str, str]):
        """
        Recursively configure theme for all widgets
        
        Args:
            widget: The widget to configure
            theme_colors: Dictionary of theme colors
        """
        try:
            # Configure based on widget type
            widget_name = widget.winfo_class()
            
            if widget_name in ("Frame", "Labelframe", "TFrame", "TLabelframe"):
                widget.configure(background=theme_colors["bg"])
            
            elif widget_name in ("Label", "TLabel"):
                widget.configure(background=theme_colors["bg"], foreground=theme_colors["fg"])
            
            elif widget_name in ("Button", "TButton"):
                # Skip configurating buttons directly as they're handled by the style
                pass
            
            elif widget_name in ("Entry", "TEntry"):
                # For text input fields
                if hasattr(widget, "configure"):
                    widget.configure(background=theme_colors["bg"], foreground=theme_colors["fg"], 
                                   insertbackground=theme_colors["fg"])
            
            elif widget_name == "Text":
                widget.configure(background=theme_colors["bg"], foreground=theme_colors["fg"],
                               insertbackground=theme_colors["fg"])
            
            elif widget_name in ("Listbox", "TListbox"):
                widget.configure(background=theme_colors["bg"], foreground=theme_colors["fg"],
                               selectbackground=theme_colors["accent"], 
                               selectforeground="white")
        
        except Exception:
            # Some widgets might not support all configurations
            pass
        
        # Process children recursively
        try:
            for child in widget.winfo_children():
                self._configure_widget_theme(child, theme_colors)
        except Exception:
            pass
    
    def setup_fonts(self):
        """Set up custom fonts for the application"""
        # Get font settings from application settings
        note_font_family = self.app_settings.get("note_font_family", "DejaVu Sans")
        note_font_size = self.app_settings.get("note_font_size", 11)
        editor_font_family = self.app_settings.get("editor_font_family", "DejaVu Sans Mono")
        editor_font_size = self.app_settings.get("editor_font_size", 12)
        sidebar_font_family = self.app_settings.get("sidebar_font_family", "DejaVu Sans")
        sidebar_font_size = self.app_settings.get("sidebar_font_size", 10)
        
        # Create named fonts
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family=note_font_family, size=note_font_size)
        
        self.text_font = font.Font(family=editor_font_family, size=editor_font_size)
        self.sidebar_font = font.Font(family=sidebar_font_family, size=sidebar_font_size)
        self.bold_font = font.Font(family=note_font_family, size=note_font_size, weight="bold")
        self.heading_font = font.Font(family=note_font_family, size=note_font_size + 4, weight="bold")
        self.small_font = font.Font(family=note_font_family, size=note_font_size - 2)
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        # Determine the opposite of the current theme
        new_mode = "light" if self.current_theme_mode == "dark" else "dark"
        
        # Update settings
        self.dark_mode = (new_mode == "dark")
        self.use_system_theme = False
        
        # Apply the new theme
        self.apply_theme(new_mode)
        
        # Save settings
        self.save_theme_settings()

    def save_theme_settings(self):
        """Save theme settings to application settings"""
        self.app_settings["dark_mode"] = self.dark_mode
        self.app_settings["use_system_theme"] = self.use_system_theme
        settings.save_settings(self.app_settings)
        
    def follow_system_theme(self, follow: bool = True):
        """
        Enable or disable following the system theme
        
        Args:
            follow (bool): Whether to follow system theme
        """
        self.use_system_theme = follow
        
        # Apply theme based on system if follow is True
        if follow:
            self.apply_theme(self.get_system_theme())
        
        # Save settings
        self.save_theme_settings()
    
    def set_theme(self, dark_mode: bool):
        """
        Set theme to light or dark mode
        
        Args:
            dark_mode (bool): Whether to use dark mode
        """
        self.dark_mode = dark_mode
        self.use_system_theme = False
        
        # Apply the theme
        self.apply_theme("dark" if dark_mode else "light")
        
        # Save settings
        self.save_theme_settings()
    
    def get_current_theme_colors(self) -> Dict[str, str]:
        """
        Get the current theme colors
        
        Returns:
            Dict[str, str]: Dictionary of color values
        """
        return self.DARK_THEME if self.current_theme_mode == "dark" else self.LIGHT_THEME
    
    def get_note_color(self, color_name: str) -> str:
        """
        Get the color value for a note color name based on current theme
        
        Args:
            color_name (str): Name of the color ("default", "red", etc.)
            
        Returns:
            str: Hex color value
        """
        colors = self.get_current_theme_colors()["note_colors"]
        return colors.get(color_name, colors["default"])
