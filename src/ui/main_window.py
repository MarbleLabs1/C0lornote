# -*- coding: utf-8 -*-

"""Janela principal e orquestracao da aplicacao."""

import datetime
from typing import List

from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QHBoxLayout, QLabel, QStatusBar, QFileDialog, QMessageBox
)
from PyQt6.QtGui import (
    QKeySequence, QAction, QShortcut
)
from PyQt6.QtCore import (
    Qt, QTimer
)

from src.models.note import Note
from src.models.storage import NoteStore
from src.ui.editor import NoteEditor
from src.ui.note_list import NoteListWidget
from src.ui.sidebar import SidebarWidget
from src.ui.theme import Theme, ThemeType

class MainWindow(QMainWindow):
    """Main window for the C0lorNote application"""

    # De quanto em quanto tempo o texto aberto vai para o disco.
    AUTOSAVE_INTERVAL_MS = 30_000

    def __init__(self):
        super().__init__()
        self.notes = []  # List of Note objects
        self.current_note_index = -1  # Index of the currently selected note
        self._editor_baseline = None  # texto do editor tal como foi salvo
        self.theme = Theme(ThemeType.MINIMALIST)  # Default theme
        self.store = NoteStore()  # Persistencia em SQLite
        
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

        # Start autosaving
        self.start_autosave()

    def start_autosave(self):
        """Save edits periodically.

        Without this the editor only reaches disk on Ctrl+S, on switching
        notes, or on a clean exit — so a crash or a power cut loses
        everything typed since the last one.
        """
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setInterval(self.AUTOSAVE_INTERVAL_MS)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start()

    def snapshot_editor(self):
        """Record what the editor holds right now, as the saved reference.

        Comparing against note.content does not work: QTextEdit.toHtml()
        returns a full normalised HTML document, never the fragment that was
        put in, so every rich text note would look modified the instant it
        was opened. Comparing the editor against itself avoids that entirely.
        """
        self._editor_baseline = self.note_editor.get_content()

    def has_unsaved_changes(self):
        """True when the editor holds text that has not been persisted."""
        if self.current_note_index < 0:
            return False
        if self.current_note_index >= len(self.note_list.filtered_notes):
            return False
        if self._editor_baseline is None:
            return False
        return self.note_editor.get_content() != self._editor_baseline

    def autosave(self):
        """Persist the open note, but only when it actually changed."""
        if not self.has_unsaved_changes():
            return
        note = self.note_list.filtered_notes[self.current_note_index]
        note.content = self.note_editor.get_content()
        note.modified_date = datetime.datetime.now()
        self.note_list.update_list()
        self.save_notes()
        self.snapshot_editor()
        self.status_message.setText(
            f"Autosaved at {note.modified_date.strftime('%H:%M:%S')}"
        )
    
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
        self.snapshot_editor()
        

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
        self.snapshot_editor()
    
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
        """Load notes from the database"""
        try:
            notes, categories, tags = self.store.load()
        except Exception as e:
            QMessageBox.warning(
                self,
                "Load Error",
                f"Failed to load notes: {str(e)}\nStarting with empty notebook."
            )
            self.create_sample_notes()
            return

        if not notes:
            # Primeira execucao: cria as notas de exemplo
            self.create_sample_notes()
            return

        self.notes = notes
        self.sidebar.categories = categories
        self.sidebar.tags = tags

        # Update the UI
        self.sidebar.update_categories_list()
        self.sidebar.update_tags_list()
        self.note_list.set_notes(self.notes)

        # Update status bar message
        self.status_message.setText(f"Loaded {len(self.notes)} notes")

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

        # Grava ja: sem isso as notas de exemplo so existem em memoria, e um
        # primeiro uso encerrado a forca comeca do zero na proxima abertura.
        self.save_notes()

    def save_notes(self):
        """Save all notes to the database"""
        try:
            self.store.save(self.notes, self.sidebar.categories, self.sidebar.tags)
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
