# -*- coding: utf-8 -*-

"""Barra lateral: visoes rapidas, categorias, tags e tema."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QDialog, QComboBox,
    QListWidget, QFrame
)
from PyQt6.QtGui import (
    QFont
)
from PyQt6.QtCore import (
    Qt, pyqtSignal
)

from src.ui.theme import Theme, ThemeType

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
