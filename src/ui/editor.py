# -*- coding: utf-8 -*-

"""Editor de notas: texto rico + editor de codigo."""

import sys
import os
import subprocess

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QDialog, QMessageBox,
    QTabWidget, QColorDialog
)
from PyQt6.QtGui import (
    QFont, QTextCharFormat
)

from src.ui.highlighter import SyntaxHighlighter

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
