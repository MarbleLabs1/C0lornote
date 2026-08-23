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
    SYSTEM = 3      # Follows the operating system's own colours


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
        if self.theme_type is ThemeType.SYSTEM:
            return self._system_theme()
        return self.themes[self.theme_type]

    def _system_theme(self):
        """Build a theme from the colours the operating system is using.

        Read fresh each time, so switching Windows between light and dark, or
        changing the accent colour, is picked up on the next theme apply.
        """
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        # A palette viva da aplicacao, nao style().standardPalette(): esta
        # ultima e uma paleta generica e clara, que nao segue o modo escuro do
        # sistema. Ler a errada fazia o titulo ser calculado sobre um fundo
        # claro enquanto os widgets desenhavam sobre um escuro.
        p = app.palette() if app else QPalette()

        Role = QPalette.ColorRole
        janela = p.color(Role.Window)
        texto = p.color(Role.WindowText)
        base = p.color(Role.Base)
        realce = p.color(Role.Highlight)
        escuro = self.contrast_on(janela).lightness() > 128  # texto claro => fundo escuro

        return {
            'name': 'System',
            'main_bg': janela,
            'main_fg': texto,
            'accent': realce,
            'sidebar_bg': self.mix(janela, texto, 0.04),
            'sidebar_fg': texto,
            'editor_bg': base,
            'editor_fg': p.color(Role.Text),
            'toolbar_bg': self.mix(janela, texto, 0.03),
            'button_bg': p.color(Role.Button),
            'button_fg': p.color(Role.ButtonText),
            'border': self.mix(janela, texto, 0.22),
            'highlight': realce,
            'code_bg': self.mix(base, texto, 0.05),
            'font_family': '',        # vazio: usa a fonte padrao do sistema
            'code_font_family': 'Consolas, "DejaVu Sans Mono", monospace',
            'is_dark': escuro,
        }

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

    @staticmethod
    def _luminancia_relativa(cor: QColor) -> float:
        """WCAG relative luminance of a colour."""
        def canal(v):
            v = v / 255.0
            return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

        return (
            0.2126 * canal(cor.red())
            + 0.7152 * canal(cor.green())
            + 0.0722 * canal(cor.blue())
        )

    @classmethod
    def contrast_ratio(cls, a: QColor, b: QColor) -> float:
        """WCAG contrast ratio between two colours, from 1.0 to 21.0."""
        la, lb = cls._luminancia_relativa(a), cls._luminancia_relativa(b)
        claro, escuro = max(la, lb), min(la, lb)
        return (claro + 0.05) / (escuro + 0.05)

    def heading_fg(self) -> QColor:
        """Colour for section headings, guaranteed to be readable.

        The app title used the accent colour directly. On the Minimalist theme
        that is pale yellow on a pale background; under the system theme in
        dark mode it is the Windows accent blue on near-black. Both are
        unreadable. The accent is only used when it clears 3:1 against the
        sidebar, the WCAG threshold for large text.
        """
        theme = self.get_current_theme()
        accent = theme['accent']
        fundo = theme['sidebar_bg']
        if self.contrast_ratio(accent, fundo) >= 3.0:
            return accent
        return theme['main_fg']

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
    
    def palette(self) -> QPalette:
        """Build a complete QPalette for the current theme.

        This is what makes the app native. Qt's own style draws every widget,
        reading its colours from the palette — no stylesheet involved. The
        previous approach set colours with setStyleSheet on each widget, which
        bypasses QStyle and is what makes a Qt app look like a web page.

        Every role is filled in, including the Disabled group: leaving a role
        unset means the widget falls back to the desktop's colour, which on a
        dark theme over a light desktop gives unreadable text.
        """
        t = self.get_current_theme()
        p = QPalette()

        janela, texto = t['main_bg'], t['main_fg']
        base, texto_base = t['editor_bg'], t['editor_fg']
        botao, texto_botao = t['button_bg'], self.contrast_on(t['button_bg'])
        realce = t['highlight']

        Role = QPalette.ColorRole
        Group = QPalette.ColorGroup

        cores = {
            Role.Window: janela,
            Role.WindowText: texto,
            Role.Base: base,
            Role.AlternateBase: self.mix(base, texto, 0.06),
            Role.Text: texto_base,
            Role.PlaceholderText: self.mix(texto_base, base, 0.55),
            Role.Button: botao,
            Role.ButtonText: texto_botao,
            Role.Highlight: realce,
            Role.HighlightedText: self.contrast_on(realce),
            Role.ToolTipBase: t['toolbar_bg'],
            Role.ToolTipText: texto,
            Role.Link: t['accent'],
            Role.LinkVisited: self.mix(t['accent'], janela, 0.35),
            Role.BrightText: self.contrast_on(janela),
            # Tons usados pelo Fusion para bordas, relevo e sombra.
            Role.Light: self.mix(janela, self.contrast_on(janela), 0.14),
            Role.Midlight: self.mix(janela, self.contrast_on(janela), 0.08),
            Role.Mid: t['border'],
            Role.Dark: self.mix(janela, QColor('#000000'), 0.35),
            Role.Shadow: self.mix(janela, QColor('#000000'), 0.6),
        }

        for grupo in (Group.Active, Group.Inactive):
            for role, cor in cores.items():
                p.setColor(grupo, role, cor)

        # Desabilitado: mesmo fundo, texto recuado — sem isso o Qt usa a cor do
        # desktop e o texto some.
        apagado = self.mix(texto, janela, 0.6)
        for role in (Role.WindowText, Role.Text, Role.ButtonText):
            p.setColor(Group.Disabled, role, apagado)
        for role, cor in cores.items():
            if role not in (Role.WindowText, Role.Text, Role.ButtonText):
                p.setColor(Group.Disabled, role, cor)

        return p

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
