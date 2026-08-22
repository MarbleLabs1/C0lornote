# -*- coding: utf-8 -*-

"""Temas da aplicacao (Matrix, Dreamcore, Minimalist)."""

from enum import Enum

from PyQt6.QtWidgets import (
    QWidget, QTextEdit
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette
)

class ThemeType(Enum):
    """Theme types available in the application"""
    MATRIX = 0      # Hacker-style green on black
    DREAMCORE = 1   # Surreal pastel colors
    MINIMALIST = 2  # Soft yellow minimalist


class Theme:
    """Class for managing application themes"""
    
    def __init__(self, theme_type: ThemeType = ThemeType.MINIMALIST):
        self.theme_type = theme_type
        
        # Define color schemes for each theme
        self.themes = {
            ThemeType.MATRIX: {
                'name': 'Matrix',
                'main_bg': QColor('#000000'),
                'main_fg': QColor('#00FF00'),
                'accent': QColor('#008F11'),
                'sidebar_bg': QColor('#0D0208'),
                'sidebar_fg': QColor('#3F6844'),
                'editor_bg': QColor('#0D0D0D'),
                'editor_fg': QColor('#00FF41'),
                'toolbar_bg': QColor('#121212'),
                'button_bg': QColor('#003B00'),
                'button_fg': QColor('#00FF41'),
                'border': QColor('#32de84'),
                'highlight': QColor('#59981A'),
                'code_bg': QColor('#002400'),
                'font_family': 'Consolas, "Courier New", monospace',
                'code_font_family': 'Consolas, "Courier New", monospace',
            },
            ThemeType.DREAMCORE: {
                'name': 'Dreamcore',
                'main_bg': QColor('#2D033B'),
                'main_fg': QColor('#E5B8F4'),
                'accent': QColor('#C147E9'),
                'sidebar_bg': QColor('#810CA8'),
                'sidebar_fg': QColor('#F5E9FF'),
                'editor_bg': QColor('#4E0B5E'),
                'editor_fg': QColor('#F7C8FF'),
                'toolbar_bg': QColor('#3A0647'),
                'button_bg': QColor('#9E35CF'),
                'button_fg': QColor('#FFFFFF'),
                'border': QColor('#C147E9'),
                'highlight': QColor('#8249A0'),
                'code_bg': QColor('#3A0647'),
                'font_family': 'Arial, Helvetica, sans-serif',
                'code_font_family': 'Consolas, "Courier New", monospace',
            },
            ThemeType.MINIMALIST: {
                'name': 'Minimalist',
                'main_bg': QColor('#F7F2E7'),
                'main_fg': QColor('#3A3A3A'),
                'accent': QColor('#FFDA79'),
                'sidebar_bg': QColor('#F3EAD5'),
                'sidebar_fg': QColor('#494949'),
                'editor_bg': QColor('#FFFFFF'),
                'editor_fg': QColor('#333333'),
                'toolbar_bg': QColor('#FFF6E0'),
                'button_bg': QColor('#FFDA79'),
                'button_fg': QColor('#333333'),
                'border': QColor('#D9D0B9'),
                'highlight': QColor('#FFC107'),
                'code_bg': QColor('#FFFAF0'),
                'font_family': 'Inter, Arial, sans-serif',
                'code_font_family': 'Fira Code, Consolas, monospace',
            }
        }
    
    def get_current_theme(self):
        """Get the current theme settings"""
        return self.themes[self.theme_type]
    
    def set_theme(self, theme_type: ThemeType):
        """Change the current theme"""
        self.theme_type = theme_type
    
    def apply_theme_to_widget(self, widget: QWidget):
        """Apply the current theme to a widget"""
        theme = self.get_current_theme()
        
        # Create a palette for the widget
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, theme['main_bg'])
        palette.setColor(QPalette.ColorRole.WindowText, theme['main_fg'])
        palette.setColor(QPalette.ColorRole.Base, theme['editor_bg'])
        palette.setColor(QPalette.ColorRole.Text, theme['editor_fg'])
        palette.setColor(QPalette.ColorRole.Button, theme['button_bg'])
        palette.setColor(QPalette.ColorRole.ButtonText, theme['button_fg'])
        palette.setColor(QPalette.ColorRole.Highlight, theme['highlight'])
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor('white'))
        
        # Apply the palette to the widget
        widget.setPalette(palette)
        
        # Apply fonts based on theme
        if isinstance(widget, QTextEdit) and "code_font_family" in theme:
            font = QFont(theme['code_font_family'])
            font.setPointSize(11)
            widget.setFont(font)
        elif "font_family" in theme:
            font = QFont(theme['font_family'])
            font.setPointSize(10)
            widget.setFont(font)
