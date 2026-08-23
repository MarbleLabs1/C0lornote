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

    @staticmethod
    def contrast_on(cor: QColor) -> QColor:
        """Black or white — whichever stays readable on top of `cor`.

        Hard-coding white text made the "New Note" button white-on-pale-yellow
        in the Minimalist theme, which is barely legible.
        """
        luminancia = (
            0.299 * cor.red() + 0.587 * cor.green() + 0.114 * cor.blue()
        ) / 255.0
        return QColor('#1A1A1A') if luminancia > 0.55 else QColor('#FFFFFF')

    def is_light(self) -> bool:
        """True when the theme's main background is a light colour."""
        return self.contrast_on(self.get_current_theme()['main_bg']).lightness() < 128

    def mix(self, a: QColor, b: QColor, fator: float) -> QColor:
        """Blend two colours; `fator` 0.0 gives `a`, 1.0 gives `b`."""
        return QColor(
            round(a.red() + (b.red() - a.red()) * fator),
            round(a.green() + (b.green() - a.green()) * fator),
            round(a.blue() + (b.blue() - a.blue()) * fator),
        )

    def muted_fg(self) -> QColor:
        """Secondary text: present, but a step back from the main colour."""
        theme = self.get_current_theme()
        return self.mix(theme['main_fg'], theme['main_bg'], 0.42)

    def faint_fg(self) -> QColor:
        """Tertiary text, for timestamps and other incidental detail."""
        theme = self.get_current_theme()
        return self.mix(theme['main_fg'], theme['main_bg'], 0.62)

    def heading_fg(self) -> QColor:
        """Colour for section headings, guaranteed to be readable.

        The app title used the accent colour, which on the Minimalist theme is
        pale yellow on a pale background — effectively invisible.
        """
        theme = self.get_current_theme()
        accent = theme['accent']
        fundo = theme['sidebar_bg']
        # Se o acento nao se destaca do fundo, cai para o texto principal.
        diferenca = abs(
            (0.299 * accent.red() + 0.587 * accent.green() + 0.114 * accent.blue())
            - (0.299 * fundo.red() + 0.587 * fundo.green() + 0.114 * fundo.blue())
        )
        return accent if diferenca > 60 else theme['main_fg']

    def scrollbar_qss(self, fundo: QColor = None) -> str:
        """Thin themed scrollbars, replacing the platform default.

        The native Windows bar, with its arrows and hatched thumb, clashes with
        all three themes. `fundo` lets a panel match its own background instead
        of the window's.
        """
        theme = self.get_current_theme()
        trilho = (fundo or theme['main_bg']).name()
        polegar = self.mix(theme['main_fg'], theme['main_bg'], 0.62).name()
        polegar_hover = self.mix(theme['main_fg'], theme['main_bg'], 0.35).name()
        return f"""
            QScrollBar:vertical {{
                background: {trilho};
                width: 10px;
                margin: 0;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {polegar};
                border-radius: 5px;
                min-height: 28px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {polegar_hover};
            }}
            QScrollBar:horizontal {{
                background: {trilho};
                height: 10px;
                margin: 0;
                border: none;
            }}
            QScrollBar::handle:horizontal {{
                background: {polegar};
                border-radius: 5px;
                min-width: 28px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {polegar_hover};
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                height: 0; width: 0; border: none; background: none;
            }}
            QScrollBar::add-page, QScrollBar::sub-page {{
                background: none;
            }}
        """
    
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
        palette.setColor(
            QPalette.ColorRole.HighlightedText, self.contrast_on(theme['highlight'])
        )
        
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
