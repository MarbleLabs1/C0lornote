# -*- coding: utf-8 -*-

"""Realce de sintaxe Python para o editor de codigo."""

from PyQt6.QtGui import (
    QFont, QColor, QSyntaxHighlighter, QTextCharFormat
)
from PyQt6.QtCore import (
    QRegularExpression
)

from src.ui.theme import ThemeType

class SyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for code editing"""
    
    def __init__(self, document, theme_instance):
        super().__init__(document)
        self.theme = theme_instance
        
        # Set up the formatting for different syntax elements
        self.create_formatting_rules()
    
    def create_formatting_rules(self):
        """Define the syntax highlighting rules for programming languages"""
        self.highlighting_rules = []
        theme_colors = self.theme.get_current_theme()
        
        # Keywords format (if, else, for, while, etc.)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6" if self.theme.theme_type == ThemeType.MATRIX else "#0000FF"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "\\bdef\\b", "\\bclass\\b", "\\bif\\b", "\\belse\\b", "\\belif\\b", 
            "\\bfor\\b", "\\bwhile\\b", "\\btry\\b", "\\bexcept\\b", "\\breturn\\b",
            "\\bimport\\b", "\\bfrom\\b", "\\bas\\b", "\\bpass\\b", "\\bbreak\\b",
            "\\bcontinue\\b", "\\bTrue\\b", "\\bFalse\\b", "\\bNone\\b"
        ]
        for pattern in keywords:
            expression = QRegularExpression(pattern)
            self.highlighting_rules.append((expression, keyword_format))
        
        # String format (for string literals)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178" if self.theme.theme_type == ThemeType.MATRIX else "#A31515"))
        self.highlighting_rules.append((
            QRegularExpression("\".*\""), 
            string_format
        ))
        self.highlighting_rules.append((
            QRegularExpression("'.*'"), 
            string_format
        ))
        
        # Comment format (for code comments)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955" if self.theme.theme_type == ThemeType.MATRIX else "#008000"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            QRegularExpression("#[^\n]*"), 
            comment_format
        ))
        
        # Function format (for function names)
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA" if self.theme.theme_type == ThemeType.MATRIX else "#795E26"))
        function_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((
            QRegularExpression("\\b[A-Za-z0-9_]+(?=\\()"), 
            function_format
        ))
        
        # Class format (for class names)
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0" if self.theme.theme_type == ThemeType.MATRIX else "#267F99"))
        class_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((
            QRegularExpression("\\bclass\\s+\\w+"), 
            class_format
        ))
    
    def highlightBlock(self, text):
        """Highlight a block of text based on the syntax rules"""
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
