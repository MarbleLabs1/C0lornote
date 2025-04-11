#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modern C0lorNote Application

A sleek, modern note-taking application built with PyQt6, inspired by Notion, Google Keep, and Apple Notes.
Features include rich text editing, code editing with syntax highlighting, and multiple themes.
"""

import sys
import os
import json
import subprocess
import datetime
from enum import Enum
from typing import Dict, List, Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QToolBar, QStatusBar, QMenu,
    QMenuBar, QDialog, QFileDialog, QMessageBox, QTabWidget, QComboBox,
    QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem, QCheckBox,
    QScrollArea, QFrame, QToolButton, QColorDialog
)
from PyQt6.QtGui import (
    QFont, QIcon, QColor, QPalette, QSyntaxHighlighter, QTextCharFormat,
    QKeySequence, QTextCursor, QKeyEvent, QTextDocument, QAction, QPixmap,
    QShortcut
)
from PyQt6.QtCore import (
    Qt, QSize, QRect, QPoint, QTimer, QRegularExpression, pyqtSignal, QObject
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


class NoteEditor(QWidget):
    """Rich text and code editor for notes"""
    
    def __init__(self, theme_instance):
        super().__init__()
        self.theme = theme_instance
        self.mode = "text"  # Either "text" or "code"
        
        # Set up the layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the editor toolbar
        self.create_toolbar()
        
        # Create the tab widget for different editor modes
        self.tab_widget = QTabWidget()
        self.text_editor = QTextEdit()
        self.code_editor = QTextEdit()
        
        # Add syntax highlighter to code editor
        self.highlighter = SyntaxHighlighter(self.code_editor.document(), self.theme)
        
        # Set monospace font for code editor
        code_font = QFont(self.theme.get_current_theme()['code_font_family'])
        code_font.setPointSize(12)
        self.code_editor.setFont(code_font)
        
        # Add the editors to the tab widget
        self.tab_widget.addTab(self.text_editor, "Rich Text")
        self.tab_widget.addTab(self.code_editor, "Code")
        
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.tab_changed)
        
        # Add the tab widget to the layout
        self.layout.addWidget(self.tab_widget)
        
        # Apply theme
        self.apply_theme()
    
    def create_toolbar(self):
        """Create the editor toolbar with formatting options"""
        self.toolbar = QWidget()
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        
        # Formatting buttons for text mode
        self.bold_btn = QPushButton("B")
        self.bold_btn.setToolTip("Bold")
        self.bold_btn.setCheckable(True)
        self.bold_btn.clicked.connect(self.format_bold)
        
        self.italic_btn = QPushButton("I")
        self.italic_btn.setToolTip("Italic")
        self.italic_btn.setCheckable(True)
        self.italic_btn.clicked.connect(self.format_italic)
        
        self.underline_btn = QPushButton("U")
        self.underline_btn.setToolTip("Underline")
        self.underline_btn.setCheckable(True)
        self.underline_btn.clicked.connect(self.format_underline)
        
        # Add text color button
        self.color_btn = QPushButton("Color")
        self.color_btn.setToolTip("Text Color")
        self.color_btn.clicked.connect(self.choose_text_color)
        
        # Add run code button (for code mode)
        self.run_btn = QPushButton("▶ Run")
        self.run_btn.setToolTip("Run Code (F5)")
        self.run_btn.clicked.connect(self.run_code)
        self.run_btn.setVisible(False)  # Hidden initially
        
        # Add buttons to toolbar
        toolbar_layout.addWidget(self.bold_btn)
        toolbar_layout.addWidget(self.italic_btn)
        toolbar_layout.addWidget(self.underline_btn)
        toolbar_layout.addWidget(self.color_btn)
        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(self.run_btn)
        
        # Add the toolbar to the main layout
        self.layout.addWidget(self.toolbar)
    
    def tab_changed(self, index):
        """Handle changing between editor tabs"""
        if index == 0:  # Text mode
            self.mode = "text"
            self.bold_btn.setVisible(True)
            self.italic_btn.setVisible(True)
            self.underline_btn.setVisible(True)
            self.color_btn.setVisible(True)
            self.run_btn.setVisible(False)
        else:  # Code mode
            self.mode = "code"
            self.italic_btn.setVisible(False)
            self.underline_btn.setVisible(False)
            self.color_btn.setVisible(False)
            self.run_btn.setVisible(True)
    
    def apply_theme(self):
        """Apply the current theme to all editor components"""
        theme = self.theme.get_current_theme()
        
        # Apply theme to toolbar
        self.toolbar.setStyleSheet(f"background-color: {theme['toolbar_bg'].name()};")
        
        # Apply theme to editors
        self.theme.apply_theme_to_widget(self.text_editor)
        self.theme.apply_theme_to_widget(self.code_editor)
        
        # Apply theme to buttons
        for btn in [self.bold_btn, self.italic_btn, self.underline_btn, self.color_btn, self.run_btn]:
            btn.setStyleSheet(
                f"background-color: {theme['button_bg'].name()}; "
                f"color: {theme['button_fg'].name()}; "
                f"border: 1px solid {theme['border'].name()}; "
                f"padding: 5px;"
            )
        
        # Re-create syntax highlighting rules for code editor
        self.highlighter.create_formatting_rules()
    
    def format_bold(self):
        """Apply bold formatting to selected text"""
        if self.mode == "text":
            cursor = self.text_editor.textCursor()
            if cursor.hasSelection():
                format = QTextCharFormat()
                if self.bold_btn.isChecked():
                    format.setFontWeight(QFont.Weight.Bold)
                else:
                    format.setFontWeight(QFont.Weight.Normal)
                cursor.mergeCharFormat(format)
                self.text_editor.setTextCursor(cursor)
    
    def format_italic(self):
        """Apply italic formatting to selected text"""
        if self.mode == "text":
            cursor = self.text_editor.textCursor()
            if cursor.hasSelection():
                format = QTextCharFormat()
                format.setFontItalic(self.italic_btn.isChecked())
                cursor.mergeCharFormat(format)
                self.text_editor.setTextCursor(cursor)
    
    def format_underline(self):
        """Apply underline formatting to selected text"""
        if self.mode == "text":
            cursor = self.text_editor.textCursor()
            if cursor.hasSelection():
                format = QTextCharFormat()
                format.setFontUnderline(self.underline_btn.isChecked())
                cursor.mergeCharFormat(format)
                self.text_editor.setTextCursor(cursor)
    
    def choose_text_color(self):
        """Choose text color for the selected text"""
        if self.mode == "text":
            cursor = self.text_editor.textCursor()
            if cursor.hasSelection():
                color = QColorDialog.getColor()
                if color.isValid():
                    format = QTextCharFormat()
                    format.setForeground(color)
                    cursor.mergeCharFormat(format)
                    self.text_editor.setTextCursor(cursor)
    
    def run_code(self):
        """Run the code in the code editor"""
        if self.mode == "code":
            code = self.code_editor.toPlainText()
            if code:
                try:
                    # Create a temporary file for the code
                    temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_code.py")
                    with open(temp_file, "w") as f:
                        f.write(code)
                    
                    # Execute the code and capture output
                    result = subprocess.run(
                        [sys.executable, temp_file], 
                        capture_output=True, 
                        text=True
                    )
                    
                    # Show the output in a dialog
                    output_dialog = QDialog(self)
                    output_dialog.setWindowTitle("Code Output")
                    output_dialog.setMinimumSize(600, 400)
                    
                    layout = QVBoxLayout(output_dialog)
                    
                    output_text = QTextEdit()
                    output_text.setReadOnly(True)
                    
                    # Format and display output
                    if result.stdout:
                        output_text.append("--- STDOUT ---\n")
                        output_text.append(result.stdout)
                    
                    if result.stderr:
                        output_text.append("\n--- STDERR ---\n")
                        output_text.append(result.stderr)
                    
                    close_btn = QPushButton("Close")
                    close_btn.clicked.connect(output_dialog.accept)
                    
                    layout.addWidget(output_text)
                    layout.addWidget(close_btn)
                    
                    output_dialog.exec()
                    
                    # Clean up the temp file
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to run code: {str(e)}")
    
    def get_content(self):
        """Get the content from the active editor"""
        if self.mode == "text":
            return self.text_editor.toHtml()
        else:
            return self.code_editor.toPlainText()
    
    def set_content(self, content, is_code=False):
        """Set the content in the appropriate editor"""
        if is_code:
            self.tab_widget.setCurrentIndex(1)
            self.code_editor.setPlainText(content)
        else:
            self.tab_widget.setCurrentIndex(0)
            try:
                self.text_editor.setHtml(content)
            except:
                self.text_editor.setPlainText(content)


class Note:
    """Class representing a note"""
    
    def __init__(self, title="", content="", is_code=False, tags=None, category=None):
        self.title = title
        self.content = content
        self.is_code = is_code
        self.tags = tags or []
        self.category = category
        self.created_date = datetime.datetime.now()
        self.modified_date = self.created_date
    
    def to_dict(self):
        """Convert note to dictionary for serialization"""
        return {
            "title": self.title,
            "content": self.content,
            "is_code": self.is_code,
            "tags": self.tags,
            "category": self.category,
            "created_date": self.created_date.isoformat(),
            "modified_date": self.modified_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create note from dictionary"""
        note = cls(
            title=data.get("title", ""),
            content=data.get("content", ""),
            is_code=data.get("is_code", False),
            tags=data.get("tags", []),
            category=data.get("category")
        )
        note.created_date = datetime.datetime.fromisoformat(data.get("created_date", datetime.datetime.now().isoformat()))
        note.modified_date = datetime.datetime.fromisoformat(data.get("modified_date", datetime.datetime.now().isoformat()))
        return note


class SidebarWidget(QWidget):
    """Sidebar with categories, tags, and smart views"""
    
    note_filter_changed = pyqtSignal(str, str)  # filter_type, filter_value
    
    def __init__(self, theme_instance):
        super().__init__()
        self.theme = theme_instance
        self.categories = []
        self.tags = []
        
        # Set up the layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header with app title
        self.header = QLabel("C0lorNote")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont(self.theme.get_current_theme()['font_family'])
        font.setPointSize(16)
        font.setBold(True)
        self.header.setFont(font)
        
        # Add the header to the layout
        self.layout.addWidget(self.header)
        
        # Add smart views
        self.create_smart_views()
        
        # Add categories section
        self.create_categories_section()
        
        # Add tags section
        self.create_tags_section()
        
        # Add stretcher to push settings to bottom
        self.layout.addStretch(1)
        
        # Add theme selector
        self.create_theme_selector()
        
        # Apply theme
        self.apply_theme()
    
    def create_smart_views(self):
        """Create the smart views section"""
        self.smart_views_label = QLabel("SMART VIEWS")
        self.smart_views_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        self.layout.addWidget(self.smart_views_label)
        
        # Add buttons for smart views
        self.all_notes_btn = QPushButton("All Notes")
        self.all_notes_btn.clicked.connect(lambda: self.note_filter_changed.emit("all", ""))
        
        self.recent_btn = QPushButton("Recent")
        self.recent_btn.clicked.connect(lambda: self.note_filter_changed.emit("recent", ""))
        
        self.code_notes_btn = QPushButton("Code Snippets")
        self.code_notes_btn.clicked.connect(lambda: self.note_filter_changed.emit("code", ""))
        
        # Add buttons to layout
        self.layout.addWidget(self.all_notes_btn)
        self.layout.addWidget(self.recent_btn)
        self.layout.addWidget(self.code_notes_btn)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(separator)
    
    def create_categories_section(self):
        """Create the categories section"""
        # Add header with controls
        categories_header = QWidget()
        header_layout = QHBoxLayout(categories_header)
        header_layout.setContentsMargins(0, 10, 0, 5)
        
        self.categories_label = QLabel("CATEGORIES")
        self.categories_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        
        self.add_category_btn = QPushButton("+")
        self.add_category_btn.setFixedSize(24, 24)
        self.add_category_btn.clicked.connect(self.add_category)
        
        header_layout.addWidget(self.categories_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.add_category_btn)
        
        self.layout.addWidget(categories_header)
        
        # Add categories list
        self.categories_list = QListWidget()
        self.categories_list.setMaximumHeight(150)
        self.categories_list.itemClicked.connect(self.category_clicked)
        self.layout.addWidget(self.categories_list)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(separator)
    
    def create_tags_section(self):
        """Create the tags section"""
        # Add header with controls
        tags_header = QWidget()
        header_layout = QHBoxLayout(tags_header)
        header_layout.setContentsMargins(0, 10, 0, 5)
        
        self.tags_label = QLabel("TAGS")
        self.tags_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        
        self.add_tag_btn = QPushButton("+")
        self.add_tag_btn.setFixedSize(24, 24)
        self.add_tag_btn.clicked.connect(self.add_tag)
        
        header_layout.addWidget(self.tags_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.add_tag_btn)
        
        self.layout.addWidget(tags_header)
        
        # Add tags list
        self.tags_list = QListWidget()
        self.tags_list.setMaximumHeight(150)
        self.tags_list.itemClicked.connect(self.tag_clicked)
        self.layout.addWidget(self.tags_list)
    
    def create_theme_selector(self):
        """Create the theme selector dropdown"""
        theme_layout = QHBoxLayout()
        
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Matrix")
        self.theme_combo.addItem("Dreamcore")
        self.theme_combo.addItem("Minimalist")
        
        # Set current theme
        self.theme_combo.setCurrentIndex(self.theme.theme_type.value)
        
        # Connect signal
        self.theme_combo.currentIndexChanged.connect(self.theme_changed)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        
        self.layout.addLayout(theme_layout)
    
    def apply_theme(self):
        """Apply the current theme to all sidebar components"""
        theme = self.theme.get_current_theme()
        
        # Apply theme to the whole sidebar
        self.setStyleSheet(f"background-color: {theme['sidebar_bg'].name()}; color: {theme['sidebar_fg'].name()};")
        
        # Apply theme to header
        self.header.setStyleSheet(f"color: {theme['accent'].name()}; font-weight: bold;")
        
        # Apply theme to buttons
        for btn in [self.all_notes_btn, self.recent_btn, self.code_notes_btn, self.add_category_btn, self.add_tag_btn]:
            btn.setStyleSheet(
                f"background-color: {theme['button_bg'].name()}; "
                f"color: {theme['button_fg'].name()}; "
                f"border: 1px solid {theme['border'].name()}; "
                f"padding: 5px;"
            )
    
    def theme_changed(self, index):
        """Handle theme change from the dropdown"""
        theme_type = ThemeType(index)
        self.theme.set_theme(theme_type)
        # Emit a signal that will be caught by the main window
        self.note_filter_changed.emit("theme_changed", "")
    
    def add_category(self):
        """Add a new category"""
        # Create a simple dialog to get category name
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Category")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel("Category Name:")
        layout.addWidget(label)
        
        name_input = QLineEdit()
        layout.addWidget(name_input)
        
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            category_name = name_input.text().strip()
            if category_name:
                if category_name not in self.categories:
                    self.categories.append(category_name)
                    self.update_categories_list()
    
    def add_tag(self):
        """Add a new tag"""
        # Create a simple dialog to get tag name
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Tag")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel("Tag Name:")
        layout.addWidget(label)
        
        name_input = QLineEdit()
        layout.addWidget(name_input)
        
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            tag_name = name_input.text().strip()
            if tag_name:
                if tag_name not in self.tags:
                    self.tags.append(tag_name)
                    self.update_tags_list()
    
    def update_categories_list(self):
        """Update the categories list widget"""
        self.categories_list.clear()
        for category in self.categories:
            self.categories_list.addItem(category)
    
    def update_tags_list(self):
        """Update the tags list widget"""
        self.tags_list.clear()
        for tag in self.tags:
            self.tags_list.addItem(tag)
    
    def category_clicked(self, item):
        """Handle category selection"""
        category = item.text()
        self.note_filter_changed.emit("category", category)
    
    def tag_clicked(self, item):
        """Handle tag selection"""
        tag = item.text()
        self.note_filter_changed.emit("tag", tag)


class NoteListWidget(QWidget):
    """Widget for displaying a list of notes"""
    
    note_selected = pyqtSignal(int)  # Emitted when a note is selected
    
    def __init__(self, theme_instance):
        super().__init__()
        self.theme = theme_instance
        self.notes = []  # List of Note objects
        self.filtered_notes = []  # Filtered list based on categories/tags
        
        # Set up the layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the search bar
        self.create_search_bar()
        
        # Create the notes list
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.note_clicked)
        self.layout.addWidget(self.list_widget)
        
        # Create new note button
        self.new_note_btn = QPushButton("+ New Note")
        self.new_note_btn.clicked.connect(self.create_new_note)
        self.layout.addWidget(self.new_note_btn)
        
        # Apply theme
        self.apply_theme()
    
    def create_search_bar(self):
        """Create the search bar"""
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notes...")
        self.search_input.textChanged.connect(self.search_notes)
        
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)
    
    def apply_theme(self):
        """Apply the current theme to the note list widget"""
        theme = self.theme.get_current_theme()
        
        # Apply theme to the widget
        self.theme.apply_theme_to_widget(self)
        
        # Apply theme to search input
        self.search_input.setStyleSheet(
            f"background-color: {theme['editor_bg'].name()}; "
            f"color: {theme['editor_fg'].name()}; "
            f"border: 1px solid {theme['border'].name()}; "
            f"padding: 5px;"
        )
        
        # Apply theme to new note button
        self.new_note_btn.setStyleSheet(
            f"background-color: {theme['accent'].name()}; "
            f"color: white; "
            f"border: none; "
            f"padding: 10px;"
        )
    
    def set_notes(self, notes):
        """Set the notes list"""
        self.notes = notes
        self.filtered_notes = notes
        self.update_list()
    
    def filter_notes(self, filter_type, filter_value):
        """Filter notes based on category or tag"""
        if filter_type == "all":
            self.filtered_notes = self.notes
        elif filter_type == "recent":
            # Filter notes from the last 7 days
            seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
            self.filtered_notes = [note for note in self.notes if note.modified_date >= seven_days_ago]
        elif filter_type == "code":
            # Filter code notes
            self.filtered_notes = [note for note in self.notes if note.is_code]
        elif filter_type == "category":
            # Filter by category
            self.filtered_notes = [note for note in self.notes if note.category == filter_value]
        elif filter_type == "tag":
            # Filter by tag
            self.filtered_notes = [note for note in self.notes if filter_value in note.tags]
        elif filter_type == "search":
            # Filter by search term
            term = filter_value.lower()
            self.filtered_notes = [
                note for note in self.notes 
                if term in note.title.lower() or 
                   term in (note.content.lower() if not note.is_code else note.content.lower())
            ]
        
        self.update_list()
    
    def search_notes(self, text):
        """Search notes by title and content"""
        if text:
            self.filter_notes("search", text)
        else:
            self.filter_notes("all", "")
    
    def update_list(self):
        """Update the list widget with current notes"""
        self.list_widget.clear()
        
        if not self.filtered_notes:
            # Add a "No notes" message
            no_notes_item = QListWidgetItem("No notes found")
            no_notes_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(no_notes_item)
            return
        
        # Add notes to the list
        for i, note in enumerate(self.filtered_notes):
            # Create a formatted list item
            item = QListWidgetItem()
            
            # Format item text with title and preview
            title = note.title or "Untitled"
            preview = note.content[:50].replace("\n", " ") + "..." if len(note.content) > 50 else note.content
            
            # Add note type indicator
            type_indicator = "[Code] " if note.is_code else ""
            
            # Format date
            date_str = note.modified_date.strftime("%Y-%m-%d %H:%M")
            
            item_text = f"{type_indicator}{title}\n{preview}\n{date_str}"
            item.setText(item_text)
            
            # Set item data to associate with note index
            item.setData(Qt.ItemDataRole.UserRole, i)
            
            self.list_widget.addItem(item)
    
    def note_clicked(self, item):
        """Handle note selection"""
        index = item.data(Qt.ItemDataRole.UserRole)
        if index is not None:
            self.note_selected.emit(index)
    
    def create_new_note(self):
        """Create a new note"""
        # Create a dialog to get note details
        dialog = QDialog(self)
        dialog.setWindowTitle("New Note")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        title_label = QLabel("Title:")
        layout.addWidget(title_label)
        
        title_input = QLineEdit()
        layout.addWidget(title_input)
        
        # Add category dropdown
        category_layout = QHBoxLayout()
        category_label = QLabel("Category:")
        category_combo = QComboBox()
        
        # Add all categories to the combo box
        category_combo.addItem("(None)")
        for category in self.parent().findChild(SidebarWidget).categories:
            category_combo.addItem(category)
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(category_combo)
        layout.addLayout(category_layout)
        
        # Add is_code checkbox
        is_code_check = QCheckBox("This is a code snippet")
        layout.addWidget(is_code_check)
        
        # Add tags input
        tags_label = QLabel("Tags (comma separated):")
        layout.addWidget(tags_label)
        
        tags_input = QLineEdit()
        layout.addWidget(tags_input)
        
        # Add buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
        
        # Show the dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = title_input.text().strip() or "Untitled"
            is_code = is_code_check.isChecked()
            category = category_combo.currentText()
            if category == "(None)":
                category = None
            
            # Parse tags
            tags = [tag.strip() for tag in tags_input.text().split(',') if tag.strip()]
            
            # Create the note
            note = Note(title=title, content="", is_code=is_code, tags=tags, category=category)
            self.notes.append(note)
            self.filtered_notes = self.notes
            self.update_list()
            
            # Select the new note
            self.note_selected.emit(len(self.notes) - 1)
            
            # Add any new tags to the sidebar
            sidebar = self.parent().findChild(SidebarWidget)
            for tag in tags:
                if tag not in sidebar.tags:
                    sidebar.tags.append(tag)
            sidebar.update_tags_list()


class MainWindow(QMainWindow):
    """Main window for the C0lorNote application"""
    
    def __init__(self):
        super().__init__()
        self.notes = []  # List of Note objects
        self.current_note_index = -1  # Index of the currently selected note
        self.theme = Theme(ThemeType.MINIMALIST)  # Default theme
        
        # Set up the main window
        self.setWindowTitle("C0lorNote")
        self.setMinimumSize(1000, 600)
        
        # Create the main layout with splitters
        self.create_layout()
        
        # Create the main menu
        self.create_menu()
        
        # Set up the status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Main status message label (aligned left)
        self.status_message = QLabel("Ready")
        self.status_bar.addWidget(self.status_message) # addWidget aligns left by default

        # Branding label (aligned right)
        self.branding_label = QLabel("@marbleceo")
        self.branding_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        # addPermanentWidget aligns right
        self.status_bar.addPermanentWidget(self.branding_label)
        
        # Connect signals
        self.sidebar.note_filter_changed.connect(self.handle_filter_change)
        self.note_list.note_selected.connect(self.handle_note_selection)
        
        # Add keyboard shortcuts
        self.create_shortcuts()
        
        # Load existing notes if available
        self.load_notes()
        
        # Apply the initial theme
        self.apply_theme()
    
    def create_layout(self):
        """Create the main window layout with splitters"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create and add sidebar
        self.sidebar = SidebarWidget(self.theme)
        self.sidebar.setMinimumWidth(200)
        self.sidebar.setMaximumWidth(300)
        self.main_splitter.addWidget(self.sidebar)
        
        # Create and add note list
        self.note_list = NoteListWidget(self.theme)
        self.note_list.setMinimumWidth(250)
        self.main_splitter.addWidget(self.note_list)
        
        # Create and add note editor
        self.note_editor = NoteEditor(self.theme)
        self.main_splitter.addWidget(self.note_editor)
        
        # Set initial splitter sizes
        self.main_splitter.setSizes([200, 300, 500])
        
        # Add splitter to main layout
        main_layout.addWidget(self.main_splitter)
    
    def create_menu(self):
        """Create the main menu"""
        # Create the menu bar
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        # New note action
        new_note_action = QAction("New Note", self)
        new_note_action.setShortcut(QKeySequence.StandardKey.New)
        new_note_action.triggered.connect(self.note_list.create_new_note)
        file_menu.addAction(new_note_action)
        
        # Save action
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_current_note)
        file_menu.addAction(save_action)
        
        # Save all action
        save_all_action = QAction("Save All", self)
        save_all_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_all_action.triggered.connect(self.save_notes)
        file_menu.addAction(save_all_action)
        
        # Export action
        export_action = QAction("Export Note", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_note)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        
        # Delete note action
        delete_action = QAction("Delete Note", self)
        delete_action.setShortcut(QKeySequence("Del"))
        delete_action.triggered.connect(self.delete_current_note)
        edit_menu.addAction(delete_action)
        
        # Run code action (for code editor)
        run_action = QAction("Run Code", self)
        run_action.setShortcut(QKeySequence("F5"))
        run_action.triggered.connect(self.note_editor.run_code)
        edit_menu.addAction(run_action)
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        
        # Theme submenu
        theme_menu = view_menu.addMenu("Theme")
        
        # Add theme actions
        matrix_action = QAction("Matrix", self)
        matrix_action.triggered.connect(lambda: self.change_theme(ThemeType.MATRIX))
        theme_menu.addAction(matrix_action)
        
        dreamcore_action = QAction("Dreamcore", self)
        dreamcore_action.triggered.connect(lambda: self.change_theme(ThemeType.DREAMCORE))
        theme_menu.addAction(dreamcore_action)
        
        minimalist_action = QAction("Minimalist", self)
        minimalist_action.triggered.connect(lambda: self.change_theme(ThemeType.MINIMALIST))
        theme_menu.addAction(minimalist_action)
    
    def create_shortcuts(self):
        """Create keyboard shortcuts"""
        # F5 to run code
        run_shortcut = QShortcut(QKeySequence("F5"), self)
        run_shortcut.activated.connect(self.note_editor.run_code)
        
        # Ctrl+S to save
        save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_shortcut.activated.connect(self.save_current_note)
    
    def apply_theme(self):
        """Apply the current theme to all components"""
        # Apply theme to components
        self.sidebar.apply_theme()
        self.note_list.apply_theme()
        self.note_editor.apply_theme()
        
        # Apply theme to main window
        theme = self.theme.get_current_theme()
        self.setStyleSheet(f"background-color: {theme['main_bg'].name()}; color: {theme['main_fg'].name()};")
        
        # Apply theme to status bar
        self.status_bar.setStyleSheet(
            f"background-color: {theme['toolbar_bg'].name()}; color: {theme['main_fg'].name()};"
        )
        # Ensure branding label color is also set
        self.branding_label.setStyleSheet(f"color: {theme['main_fg'].name()}; padding-right: 10px;") # Add some padding
    
    def handle_filter_change(self, filter_type, filter_value):
        """Handle changes to note filtering"""
        if filter_type == "theme_changed":
            # Theme has changed, update all components
            self.apply_theme()
        else:
            # Filter has changed, update the note list
            self.note_list.filter_notes(filter_type, filter_value)
    
    def handle_note_selection(self, index):
        """Handle note selection from the list"""
        if index < 0 or index >= len(self.note_list.filtered_notes):
            return
        
        # Save the current note if one is active
        if self.current_note_index >= 0:
            self.save_current_note()
        
        # Set the current note index
        self.current_note_index = index
        note = self.note_list.filtered_notes[index]
        
        # Update the editor with the note content
        self.note_editor.set_content(note.content, note.is_code)
        

        # Update status bar message
        self.status_message.setText(f"Editing: {note.title} | Last modified: {note.modified_date.strftime('%Y-%m-%d %H:%M')}")
    def save_current_note(self):
        """Save the current note"""
        if self.current_note_index < 0:
            return
        
        # Get the current note
        note = self.note_list.filtered_notes[self.current_note_index]
        
        # Update the note content from the editor
        note.content = self.note_editor.get_content()
        note.modified_date = datetime.datetime.now()
        
        # Update the note list
        self.note_list.update_list()
        

        # Update status bar message
        self.status_message.setText(f"Note '{note.title}' saved at {note.modified_date.strftime('%Y-%m-%d %H:%M')}")
        # Save all notes to disk
        self.save_notes()
    
    def delete_current_note(self):
        """Delete the current note"""
        if self.current_note_index < 0:
            return
        
        # Get the current note
        note = self.note_list.filtered_notes[self.current_note_index]
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Delete Note",
            f"Are you sure you want to delete the note '{note.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Find the note in the unfiltered list
            note_index = -1
            for i, n in enumerate(self.notes):
                if n is note:
                    note_index = i
                    break
            
            if note_index >= 0:
                # Remove the note
                self.notes.pop(note_index)
                
                # Reset the current note index
                self.current_note_index = -1
                
                # Update the filtered list
                self.note_list.set_notes(self.notes)
                
                # Save the notes
                self.save_notes()
                

                # Update status bar message
                self.status_message.setText(f"Note '{note.title}' deleted")
    def export_note(self):
        """Export the current note to a file"""
        if self.current_note_index < 0:
            return
        
        # Get the current note
        note = self.note_list.filtered_notes[self.current_note_index]
        
        # Determine the default file format based on note type
        default_extension = ".py" if note.is_code else ".html"
        default_filter = "Python Files (*.py)" if note.is_code else "HTML Files (*.html)"
        
        # Ask for the export file name
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Note",
            f"{note.title}{default_extension}",
            f"{default_filter};;Text Files (*.txt);;All Files (*)"
        )
        
        if not file_name:
            return
        
        try:
            # Save the note content to the file
            with open(file_name, "w", encoding="utf-8") as f:
                if note.is_code:
                    f.write(note.content)
                else:
                    # For rich text, consider if we need to export as plain text
                    if file_name.lower().endswith(".txt"):
                        # Export as plain text (strip HTML)
                        text_content = self.note_editor.text_editor.toPlainText()
                        f.write(text_content)
                    else:
                        # Export as HTML
                        f.write(note.content)
            

            # Update status bar message
            self.status_message.setText(f"Note exported to {file_name}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export note: {str(e)}"
            )
    
    def change_theme(self, theme_type):
        """Change the application theme"""
        self.theme.set_theme(theme_type)
        self.apply_theme()
        
        # Update theme selector in sidebar
        self.sidebar.theme_combo.setCurrentIndex(theme_type.value)
        

        # Update status bar message
        theme_name = self.theme.get_current_theme()['name']
        self.status_message.setText(f"Theme changed to {theme_name}")
    def load_notes(self):
        """Load notes from disk"""
        # Define the notes file path
        notes_dir = os.path.join(os.path.expanduser("~"), ".config", "c0lornote")
        os.makedirs(notes_dir, exist_ok=True)
        notes_file = os.path.join(notes_dir, "notes.json")
        
        # Check if the file exists
        if not os.path.exists(notes_file):
            # Create a sample note
            self.create_sample_notes()
            return
        
        try:
            # Load the notes from the file
            with open(notes_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Parse the notes
            self.notes = [Note.from_dict(note_data) for note_data in data.get("notes", [])]
            
            # Load categories and tags
            self.sidebar.categories = data.get("categories", [])
            self.sidebar.tags = data.get("tags", [])
            
            # Update the UI
            self.sidebar.update_categories_list()
            self.sidebar.update_tags_list()
            self.note_list.set_notes(self.notes)
            

            # Update status bar message
            self.status_message.setText(f"Loaded {len(self.notes)} notes")
        except Exception as e:
            QMessageBox.warning(
                self,
                "Load Error",
                f"Failed to load notes: {str(e)}\nStarting with empty notebook."
            )
            self.create_sample_notes()
    
    def create_sample_notes(self):
        """Create sample notes for a new user"""
        # Create a welcome note
        welcome_note = Note(
            title="Welcome to C0lorNote!",
            content="<h1>Welcome to C0lorNote</h1><p>This is a modern note-taking application with support for rich text and code snippets.</p><p>Features include:</p><ul><li>Rich text editing</li><li>Code editing with syntax highlighting</li><li>Multiple themes (try Matrix, Dreamcore, or Minimalist)</li><li>Organization with tags and categories</li><li>Smart views for recent notes and code snippets</li></ul><p>Get started by creating a new note!</p>",
            is_code=False,
            tags=["welcome", "tutorial"],
            category="Getting Started"
        )
        
        # Create a sample code note
        code_note = Note(
            title="Python Hello World Example",
            content="# A simple Python hello world example\n\ndef greet(name):\n    \"\"\"Return a greeting message\"\"\"\n    return f\"Hello, {name}!\"\n\n# Test the function\nif __name__ == \"__main__\":\n    print(greet(\"World\"))\n    # Press F5 to run this code!",
            is_code=True,
            tags=["python", "example"],
            category="Code Snippets"
        )
        
        # Add the notes
        self.notes = [welcome_note, code_note]
        
        # Add categories and tags
        self.sidebar.categories = ["Getting Started", "Code Snippets", "Personal", "Work"]
        self.sidebar.tags = ["welcome", "tutorial", "python", "example", "important"]
        
        # Update the UI
        self.sidebar.update_categories_list()
        self.sidebar.update_tags_list()
        self.note_list.set_notes(self.notes)
    
    def save_notes(self):
        """Save all notes to disk"""
        # Define the notes file path
        notes_dir = os.path.join(os.path.expanduser("~"), ".config", "c0lornote")
        os.makedirs(notes_dir, exist_ok=True)
        notes_file = os.path.join(notes_dir, "notes.json")
        
        try:
            # Prepare the data
            data = {
                "notes": [note.to_dict() for note in self.notes],
                "categories": self.sidebar.categories,
                "tags": self.sidebar.tags
            }
            
            # Save the data to the file
            with open(notes_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            

            # Update status bar message
            self.status_message.setText(f"Saved {len(self.notes)} notes")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save notes: {str(e)}"
            )
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Save the current note if one is active
        if self.current_note_index >= 0:
            self.save_current_note()
        
        # Save all notes
        self.save_notes()
        
        # Accept the close event
        event.accept()


def main():
    """Main application entry point"""
    # Create the application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Run the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
