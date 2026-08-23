# -*- coding: utf-8 -*-

"""Lista de notas com busca e filtros."""

import datetime
from typing import List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QDialog, QComboBox,
    QListWidget, QListWidgetItem, QCheckBox
)
from PyQt6.QtCore import (
    Qt, pyqtSignal
)

from src.models.note import Note
from src.ui.note_item_delegate import NoteItemDelegate
from src.ui.sidebar import SidebarWidget

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
        self.list_widget.setItemDelegate(NoteItemDelegate(self.theme, self.list_widget))
        self.list_widget.setMouseTracking(True)  # necessario para o estado de hover
        self.list_widget.setUniformItemSizes(False)
        self.list_widget.setSpacing(1)
        self.list_widget.setVerticalScrollMode(
            QListWidget.ScrollMode.ScrollPerPixel
        )
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
        
        borda = theme['border'].name()
        acento = theme['accent']

        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme['editor_bg'].name()};
                color: {theme['editor_fg'].name()};
                border: 1px solid {borda};
                border-radius: 8px;
                padding: 7px 10px;
                selection-background-color: {theme['highlight'].name()};
            }}
            QLineEdit:focus {{
                border: 1px solid {acento.name()};
            }}
        """)

        # A lista nao tinha estilo proprio: herdava a moldura e a barra de
        # rolagem nativas do Windows, que destoam dos tres temas.
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {theme['main_bg'].name()};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                border: none;
            }}
        """ + self.theme.scrollbar_qss())

        # O texto do botao era branco fixo — ilegivel sobre o amarelo claro do
        # tema Minimalist. Agora o contraste vem da propria cor de fundo.
        texto_botao = self.theme.contrast_on(acento).name()
        self.new_note_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {acento.name()};
                color: {texto_botao};
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
                margin: 6px 4px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.mix(acento, theme['main_fg'], 0.18).name()};
            }}
            QPushButton:pressed {{
                background-color: {self.theme.mix(acento, theme['main_fg'], 0.32).name()};
            }}
        """)
    
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
            # Busca no texto legivel, nao no HTML: procurar "div" ou "li" nao
            # pode casar com as tags de toda nota de texto rico.
            self.filtered_notes = [
                note for note in self.notes
                if term in note.title.lower()
                or term in note.plain_content().lower()
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
            
            title = note.title or "Untitled"
            preview = note.preview(60)
            date_str = note.modified_date.strftime("%d %b %Y, %H:%M")

            # O desenho fica a cargo do NoteItemDelegate; aqui vao so os dados.
            # Antes o item era um texto unico com quebras de linha, e as tres
            # informacoes saiam com o mesmo peso.
            item.setData(Qt.ItemDataRole.UserRole + 1, {
                "titulo": title,
                "previa": preview,
                "data": date_str,
                "is_code": note.is_code,
            })

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
