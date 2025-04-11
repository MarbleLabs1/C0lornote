"""
C0lorNote Main Window

This module implements the main window interface for the C0lorNote application,
including the sidebar, toolbar, note listing, and note editing areas.
"""

import os
import logging
import datetime
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinter import font as tkfont
import re
from typing import Dict, List, Optional, Callable, Any, Tuple
import threading

from src.config import settings
from src.models.note import Note, Tag, Category
from src.ui.theme_manager import ThemeManager


class MainWindow:
    """Main window for the C0lorNote application"""
    
    def __init__(self, root: tk.Tk, theme_manager: ThemeManager):
        """
        Initialize the main window
        
        Args:
            root (tk.Tk): The root tkinter window
            theme_manager (ThemeManager): Theme manager instance
        """
        self.root = root
        self.theme_manager = theme_manager
        self.colors = self.theme_manager.get_current_theme_colors()
        
        # Set application icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                   "assets", "icon.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
        except Exception as e:
            logging.warning(f"Could not load application icon: {e}")
        
        # State variables
        self.current_note = None
        self.notes = []
        self.categories = []
        self.tags = []
        self.autosave_timer = None
        self.search_active = False
        self.is_editing = False
        self.selected_note_index = -1
        
        # Create main layout
        self.create_layout()
        
        # Load initial data
        self.load_categories()
        self.load_tags()
        self.load_notes()
        
        # Set up autosave
        self.setup_autosave()
    
    def create_layout(self):
        """Create the main window layout"""
        # Configure root window
        self.root.title("C0lorNote")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Create paned window for sidebar and content
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create content area (notes list and editor)
        self.content_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.content_frame, weight=3)
        
        # Create notes list and editor with another paned window
        self.content_paned = ttk.PanedWindow(self.content_frame, orient=tk.HORIZONTAL)
        self.content_paned.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Create notes list
        self.create_notes_list()
        
        # Create note editor
        self.create_note_editor()
        
        # Configure pane sizes
        self.paned_window.sashpos(0, 200)  # Position first sash (sidebar)
        self.content_paned.sashpos(0, 300)  # Position second sash (notes list)
        
        # Bind events
        self.bind_events()
    
    def create_sidebar(self):
        """Create the sidebar with categories and tags"""
        # Create sidebar frame
        self.sidebar_frame = ttk.Frame(self.paned_window, style="Sidebar.TFrame")
        self.paned_window.add(self.sidebar_frame, weight=1)
        
        # Create header frame
        self.sidebar_header = ttk.Frame(self.sidebar_frame, style="Sidebar.TFrame")
        self.sidebar_header.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Add app title
        self.app_title = ttk.Label(
            self.sidebar_header, 
            text="C0lorNote", 
            font=self.theme_manager.heading_font,
            style="Sidebar.TLabel"
        )
        self.app_title.pack(side=tk.LEFT, pady=5)
        
        # Add new note button
        self.new_note_btn = ttk.Button(
            self.sidebar_header, 
            text="+", 
            width=3,
            command=self.create_new_note
        )
        self.new_note_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Create search box
        self.search_frame = ttk.Frame(self.sidebar_frame, style="Sidebar.TFrame")
        self.search_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_changed)
        
        self.search_entry = ttk.Entry(
            self.search_frame, 
            textvariable=self.search_var,
            font=self.theme_manager.sidebar_font
        )
        self.search_entry.pack(fill=tk.X, pady=5)
        self.search_entry.insert(0, "Search notes...")
        self.search_entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)
        self.search_entry.bind("<Return>", self.on_search_return)
        
        # Create section for smart views
        self.smart_views_frame = ttk.Frame(self.sidebar_frame, style="Sidebar.TFrame")
        self.smart_views_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.smart_label = ttk.Label(
            self.smart_views_frame, 
            text="SMART VIEWS",
            font=self.theme_manager.small_font, 
            style="Sidebar.TLabel"
        )
        self.smart_label.pack(anchor=tk.W, padx=5, pady=(0, 5))
        
        # Add smart view options
        self.all_notes_btn = ttk.Button(
            self.smart_views_frame, 
            text="All Notes", 
            command=lambda: self.show_smart_view("all"),
            style="Sidebar.TButton"
        )
        self.all_notes_btn.pack(fill=tk.X, padx=0, pady=1)
        
        self.recent_notes_btn = ttk.Button(
            self.smart_views_frame, 
            text="Recent", 
            command=lambda: self.show_smart_view("recent"),
            style="Sidebar.TButton"
        )
        self.recent_notes_btn.pack(fill=tk.X, padx=0, pady=1)
        
        self.pinned_notes_btn = ttk.Button(
            self.smart_views_frame, 
            text="Pinned", 
            command=lambda: self.show_smart_view("pinned"),
            style="Sidebar.TButton"
        )
        self.pinned_notes_btn.pack(fill=tk.X, padx=0, pady=1)
        
        # Create section for categories
        self.categories_frame = ttk.Frame(self.sidebar_frame, style="Sidebar.TFrame")
        self.categories_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.categories_header_frame = ttk.Frame(self.categories_frame, style="Sidebar.TFrame")
        self.categories_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.categories_label = ttk.Label(
            self.categories_header_frame, 
            text="CATEGORIES", 
            font=self.theme_manager.small_font,
            style="Sidebar.TLabel"
        )
        self.categories_label.pack(side=tk.LEFT, padx=5)
        
        self.add_category_btn = ttk.Button(
            self.categories_header_frame, 
            text="+", 
            width=2, 
            command=self.add_category
        )
        self.add_category_btn.pack(side=tk.RIGHT, padx=5)
        
        # Categories list container
        self.categories_list_frame = ttk.Frame(self.categories_frame, style="Sidebar.TFrame")
        self.categories_list_frame.pack(fill=tk.X, pady=0)
        
        # Create section for tags
        self.tags_frame = ttk.Frame(self.sidebar_frame, style="Sidebar.TFrame")
        self.tags_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.tags_header_frame = ttk.Frame(self.tags_frame, style="Sidebar.TFrame")
        self.tags_header_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.tags_label = ttk.Label(
            self.tags_header_frame, 
            text="TAGS", 
            font=self.theme_manager.small_font,
            style="Sidebar.TLabel"
        )
        self.tags_label.pack(side=tk.LEFT, padx=5)
        
        self.add_tag_btn = ttk.Button(
            self.tags_header_frame, 
            text="+", 
            width=2, 
            command=self.add_tag
        )
        self.add_tag_btn.pack(side=tk.RIGHT, padx=5)
        
        # Tags list container
        self.tags_list_frame = ttk.Frame(self.tags_frame, style="Sidebar.TFrame")
        self.tags_list_frame.pack(fill=tk.X, pady=0)
        
        # Settings section at the bottom
        self.settings_frame = ttk.Frame(self.sidebar_frame, style="Sidebar.TFrame")
        self.settings_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=10)
        
        self.theme_btn = ttk.Button(
            self.settings_frame, 
            text="Toggle Theme", 
            command=self.toggle_theme
        )
        self.theme_btn.pack(fill=tk.X, padx=5, pady=2)
        
        self.settings_btn = ttk.Button(
            self.settings_frame, 
            text="Settings", 
            command=self.show_settings
        )
        self.settings_btn.pack(fill=tk.X, padx=5, pady=2)
    
    def create_notes_list(self):
        """Create the notes list panel"""
        # Create the notes list frame
        self.notes_list_frame = ttk.Frame(self.content_paned)
        self.content_paned.add(self.notes_list_frame, weight=1)
        
        # Create header with sorting and view options
        self.notes_list_header = ttk.Frame(self.notes_list_frame)
        self.notes_list_header.pack(fill=tk.X, padx=5, pady=5)
        
        self.view_label = ttk.Label(
            self.notes_list_header, 
            text="All Notes", 
            font=self.theme_manager.bold_font
        )
        self.view_label.pack(side=tk.LEFT, padx=5)
        
        # Create the canvas and scrollbar for the notes list
        self.notes_list_canvas_frame = ttk.Frame(self.notes_list_frame)
        self.notes_list_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        self.notes_canvas = tk.Canvas(
            self.notes_list_canvas_frame,
            background=self.colors["bg"],
            highlightthickness=0,
            borderwidth=0
        )
        
        self.notes_scrollbar = ttk.Scrollbar(
            self.notes_list_canvas_frame, 
            orient=tk.VERTICAL, 
            command=self.notes_canvas.yview
        )
        self.notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.notes_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.notes_canvas.configure(yscrollcommand=self.notes_scrollbar.set)
        
        # Create the container for notes
        self.notes_container = ttk.Frame(self.notes_canvas)
        self.notes_canvas_window = self.notes_canvas.create_window(
            (0, 0), 
            window=self.notes_container, 
            anchor='nw',
            tags='notes_container'
        )
        
        # Bind events for scrolling and resizing
        self.notes_container.bind("<Configure>", self.on_notes_container_configure)
        self.notes_canvas.bind("<Configure>", self.on_notes_canvas_configure)
        
        # Create frame for note items
        self.note_items_frame = ttk.Frame(self.notes_container)
        self.note_items_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    def create_note_editor(self):
        """Create the note editor panel with formatting toolbar"""
        # Create the editor frame
        self.editor_frame = ttk.Frame(self.content_paned)
        self.content_paned.add(self.editor_frame, weight=2)
        
        # Create toolbar for formatting
        self.toolbar_frame = ttk.Frame(self.editor_frame, style="Toolbar.TFrame")
        self.toolbar_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Title field
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(
            self.toolbar_frame, 
            textvariable=self.title_var,
            font=self.theme_manager.heading_font,
            width=30
        )
        self.title_entry.pack(side=tk.LEFT, padx=10, pady=10)
        self.title_entry.bind("<KeyRelease>", self.on_title_changed)
        
        # Formatting buttons
        self.bold_btn = ttk.Button(
            self.toolbar_frame,
            text="B",
            width=3,
            command=self.format_bold,
            style="Toolbar.TButton"
        )
        self.bold_btn.pack(side=tk.LEFT, padx=2, pady=10)
        
        self.italic_btn = ttk.Button(
            self.toolbar_frame,
            text="I",
            width=3,
            command=self.format_italic,
            style="Toolbar.TButton"
        )
        self.italic_btn.pack(side=tk.LEFT, padx=2, pady=10)
        
        self.underline_btn = ttk.Button(
            self.toolbar_frame,
            text="U",
            width=3,
            command=self.format_underline,
            style="Toolbar.TButton"
        )
        self.underline_btn.pack(side=tk.LEFT, padx=2, pady=10)
        
        # Separator
        ttk.Separator(self.toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
        
        # List formatting
        self.bullet_btn = ttk.Button(
            self.toolbar_frame,
            text="•",
            width=3,
            command=self.format_bullet_list,
            style="Toolbar.TButton"
        )
        self.bullet_btn.pack(side=tk.LEFT, padx=2, pady=10)
        
        self.number_btn = ttk.Button(
            self.toolbar_frame,
            text="1.",
            width=3,
            command=self.format_number_list,
            style="Toolbar.TButton"
        )
        self.number_btn.pack(side=tk.LEFT, padx=2, pady=10)
        
        # Separator
        ttk.Separator(self.toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
        
        # Color selection
        self.color_label = ttk.Label(self.toolbar_frame, text="Color:")
        self.color_label.pack(side=tk.LEFT, padx=2, pady=10)
        
        self.color_var = tk.StringVar(value="default")
        self.color_combo = ttk.Combobox(
            self.toolbar_frame,
            textvariable=self.color_var,
            values=list(self.theme_manager.LIGHT_THEME["note_colors"].keys()),
            state="readonly",
            width=10
        )
        self.color_combo.pack(side=tk.LEFT, padx=2, pady=10)
        self.color_combo.bind("<<ComboboxSelected>>", self.on_color_changed)
        
        # Right side of toolbar
        self.toolbar_right = ttk.Frame(self.toolbar_frame, style="Toolbar.TFrame")
        self.toolbar_right.pack(side=tk.RIGHT, padx=10)
        
        # Pin button
        self.pin_var = tk.BooleanVar(value=False)
        self.pin_btn = ttk.Checkbutton(
            self.toolbar_right,
            text="Pin",
            variable=self.pin_var,
            command=self.toggle_pin,
            style="Toolbar.TButton"
        )
        self.pin_btn.pack(side=tk.LEFT, padx=2, pady=10)
        
        # Export button
        self.export_btn = ttk.Button(
            self.toolbar_right,
            text="Export",
            command=self.export_note,
            style="Toolbar.TButton"
        )
        self.export_btn.pack(side=tk.LEFT, padx=2, pady=10)
        
        # Delete button
        self.delete_btn = ttk.Button(
            self.toolbar_right,
            text="Delete",
            command=self.delete_note,
            style="Toolbar.TButton"
        )
        self.delete_btn.pack(side=tk.LEFT, padx=2, pady=10)
        
        # Create text editor with scrollbar
        self.editor_container = ttk.Frame(self.editor_frame)
        self.editor_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_editor = tk.Text(
            self.editor_container,
            wrap=tk.WORD,
            font=self.theme_manager.text_font,
            padx=10,
            pady=10,
            undo=True
        )
        
        self.editor_scrollbar = ttk.Scrollbar(
            self.editor_container,
            orient=tk.VERTICAL,
            command=self.text_editor.yview
        )
        self.editor_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_editor.configure(yscrollcommand=self.editor_scrollbar.set)
        
        # Configure tags for formatting
        self.text_editor.tag_configure("bold", font=self.theme_manager.bold_font)
        self.text_editor.tag_configure("italic", font=tkfont.Font(
            family=self.theme_manager.text_font.cget("family"),
            size=self.theme_manager.text_font.cget("size"),
            slant="italic"
        ))
        self.text_editor.tag_configure("underline", underline=1)
        self.text_editor.tag_configure("bullet", lmargin1=20, lmargin2=30)
        self.text_editor.tag_configure("number", lmargin1=20, lmargin2=30)
        
        # Bind events for text editor
        self.text_editor.bind("<KeyRelease>", self.on_text_changed)
        
        # Status bar
        self.status_bar = ttk.Frame(self.editor_frame)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        self.status_label = ttk.Label(
            self.status_bar,
            text="Ready",
            font=self.theme_manager.small_font
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.modified_label = ttk.Label(
            self.status_bar,
            text="",
            font=self.theme_manager.small_font
        )
        self.modified_label.pack(side=tk.RIGHT)
    
    def bind_events(self):
        """Bind keyboard shortcuts and events"""
        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.create_new_note())
        self.root.bind("<Control-s>", lambda e: self.save_current_note())
        self.root.bind("<Control-f>", lambda e: self.focus_search())
        self.root.bind("<Control-e>", lambda e: self.export_note())
        self.root.bind("<Control-d>", lambda e: self.delete_note())
        
        # Window resize
        self.root.bind("<Configure>", self.on_window_configure)
    
    def on_window_configure(self, event):
        """Handle window resize events"""
        # Only process if event is for the main window
        if event.widget == self.root:
            # Save window position and size in settings
            if not self.root.wm_state() == "zoomed":
                x, y = self.root.winfo_x(), self.root.winfo_y()
                w, h = self.root.winfo_width(), self.root.winfo_height()
                
                settings = settings.load_settings()
                settings["window_width"] = w
                settings["window_height"] = h
                settings["window_x"] = x
                settings["window_y"] = y
                settings.save_settings(settings)
    
    def on_notes_container_configure(self, event):
        """Handle notes container resize"""
        # Update the scrollregion when the size of the notes container changes
        self.notes_canvas.configure(scrollregion=self.notes_canvas.bbox("all"))
    
    def on_notes_canvas_configure(self, event):
        """Handle notes canvas resize"""
        # Resize the notes container to fill the canvas width
        self.notes_canvas.itemconfig(
            self.notes_canvas_window, 
            width=event.width
        )
    
    def load_categories(self):
        """Load categories from database"""
        self.categories = Category.get_all()
        self.update_categories_list()
    
    def load_tags(self):
        """Load tags from database"""
        self.tags = Tag.get_all()
        self.update_tags_list()
    def load_notes(self):
        """Load all notes from database"""
        self.notes = Note.get_all()
        self.render_notes()
    
    def render_notes(self, notes_to_display=None):
        """
        Render the notes list
        
        Args:
            notes_to_display: Optional list of notes to display. If None, displays all notes
        """
        # Clear existing notes
        for widget in self.note_items_frame.winfo_children():
            widget.destroy()
        
        # Determine which notes to render
        notes_to_render = notes_to_display if notes_to_display is not None else self.notes
        
        # Check if we have notes to display
        if not notes_to_render:
            # Show empty state
            empty_label = ttk.Label(
                self.note_items_frame,
                text="No notes found",
                font=self.theme_manager.text_font,
                padding=20
            )
            empty_label.pack(pady=20)
            
            # Disable editor
            self.disable_editor()
            return
        
        # Create note items
        for i, note in enumerate(notes_to_render):
            self.create_note_item(note, i)
        
        # Select the first note if none is selected
        if self.current_note is None and notes_to_render:
            self.select_note(0)
    
    def create_note_item(self, note, index):
        """Create a single note item in the notes list"""
        # Create frame for the note item
        item_frame = ttk.Frame(self.note_items_frame, style="NoteItem.TFrame")
        item_frame.pack(fill=tk.X, padx=5, pady=(0, 1))
        
        # Configure background color based on note color
        background = self.theme_manager.get_note_color(note.color or "default")
        
        # Create the note item canvas for custom styling
        item_canvas = tk.Canvas(
            item_frame,
            background=background,
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            height=80
        )
        item_canvas.pack(fill=tk.X, expand=True)
        
        # Add pin indicator if pinned
        if note.is_pinned:
            item_canvas.create_text(
                10, 10,
                text="📌",
                anchor=tk.NW,
                fill=self.colors["accent"]
            )
        
        # Add title
        title_text = note.title or "Untitled"
        item_canvas.create_text(
            20, 15,
            text=title_text,
            anchor=tk.NW,
            font=self.theme_manager.bold_font,
            fill=self.colors["fg"]
        )
        
        # Add preview of content
        preview_text = note.plain_content or ""
        if len(preview_text) > 100:
            preview_text = preview_text[:100] + "..."
        
        item_canvas.create_text(
            20, 40,
            text=preview_text,
            anchor=tk.NW,
            font=self.theme_manager.small_font,
            fill=self.colors["fg"],
            width=item_canvas.winfo_width() - 40
        )
        
        # Add date
        date_text = note.modified_date.strftime("%b %d, %Y %H:%M")
        item_canvas.create_text(
            item_canvas.winfo_width() - 10, 70,
            text=date_text,
            anchor=tk.SE,
            font=self.theme_manager.small_font,
            fill=self.colors["fg"]
        )
        
        # Bind click event
        item_canvas.bind("<Button-1>", lambda e, idx=index: self.select_note(idx))
        
        # Update note item when canvas is resized
        item_canvas.bind("<Configure>", lambda e, canvas=item_canvas, title=title_text, 
                                              preview=preview_text, date=date_text, 
                                              pinned=note.is_pinned: 
                                          self.update_note_item(canvas, title, preview, date, pinned))
    
    def update_note_item(self, canvas, title, preview, date, pinned):
        """Update note item canvas when resized"""
        # Clear canvas
        canvas.delete("all")
        
        # Redraw contents
        if pinned:
            canvas.create_text(
                10, 10,
                text="📌",
                anchor=tk.NW,
                fill=self.colors["accent"]
            )
        
        canvas.create_text(
            20, 15,
            text=title,
            anchor=tk.NW,
            font=self.theme_manager.bold_font,
            fill=self.colors["fg"]
        )
        
        canvas.create_text(
            20, 40,
            text=preview,
            anchor=tk.NW,
            font=self.theme_manager.small_font,
            fill=self.colors["fg"],
            width=canvas.winfo_width() - 40
        )
        
        canvas.create_text(
            canvas.winfo_width() - 10, 70,
            text=date,
            anchor=tk.SE,
            font=self.theme_manager.small_font,
            fill=self.colors["fg"]
        )
    
    def select_note(self, index):
        """Select a note from the list"""
        if index < 0 or index >= len(self.notes):
            return
        
        # Save current note if changed
        if self.is_editing and self.current_note:
            self.save_current_note()
        
        # Update selected note index
        self.selected_note_index = index
        self.current_note = self.notes[index]
        
        # Highlight selected note in the list
        for i, frame in enumerate(self.note_items_frame.winfo_children()):
            if i == index:
                for child in frame.winfo_children():
                    if isinstance(child, tk.Canvas):
                        child.configure(highlightbackground=self.colors["accent"], highlightthickness=2)
            else:
                for child in frame.winfo_children():
                    if isinstance(child, tk.Canvas):
                        child.configure(highlightbackground=self.colors["border"], highlightthickness=1)
        
        # Update editor with note content
        self.update_editor()
    
    def update_editor(self):
        """Update the editor with the current note content"""
        # Disable editing flag while loading content
        self.is_editing = False
        
        # Clear editor
        self.text_editor.delete("1.0", tk.END)
        self.title_var.set("")
        
        if not self.current_note:
            self.disable_editor()
            return
        
        # Enable editor
        self.enable_editor()
        
        # Set title
        if self.current_note.title:
            self.title_var.set(self.current_note.title)
        
        # Set content
        if self.current_note.content:
            self.text_editor.insert("1.0", self.current_note.content)
            
            # Apply stored formatting (would require parsing stored format)
            # This is a simple version without full formatting support
        
        # Set color
        self.color_var.set(self.current_note.color or "default")
        
        # Set pin status
        self.pin_var.set(self.current_note.is_pinned)
        
        # Update modified date
        if self.current_note.modified_date:
            date_text = f"Modified: {self.current_note.modified_date.strftime('%b %d, %Y %H:%M')}"
            self.modified_label.configure(text=date_text)
        
        # Reset editing flag
        self.is_editing = True
        
        # Update status
        self.status_label.configure(text="Ready")
    
    def enable_editor(self):
        """Enable the note editor"""
        self.text_editor.configure(state=tk.NORMAL)
        self.title_entry.configure(state=tk.NORMAL)
        self.color_combo.configure(state="readonly")
        self.pin_btn.configure(state=tk.NORMAL)
        self.export_btn.configure(state=tk.NORMAL)
        self.delete_btn.configure(state=tk.NORMAL)
        
        # Enable format buttons
        self.bold_btn.configure(state=tk.NORMAL)
        self.italic_btn.configure(state=tk.NORMAL)
        self.underline_btn.configure(state=tk.NORMAL)
        self.bullet_btn.configure(state=tk.NORMAL)
        self.number_btn.configure(state=tk.NORMAL)
    
    def disable_editor(self):
        """Disable the note editor"""
        self.text_editor.configure(state=tk.DISABLED)
        self.title_entry.configure(state=tk.DISABLED)
        self.color_combo.configure(state=tk.DISABLED)
        self.pin_btn.configure(state=tk.DISABLED)
        self.export_btn.configure(state=tk.DISABLED)
        self.delete_btn.configure(state=tk.DISABLED)
        
        # Disable format buttons
        self.bold_btn.configure(state=tk.DISABLED)
        self.italic_btn.configure(state=tk.DISABLED)
        self.underline_btn.configure(state=tk.DISABLED)
        self.bullet_btn.configure(state=tk.DISABLED)
        self.number_btn.configure(state=tk.DISABLED)
        
        # Clear modified date
        self.modified_label.configure(text="")
    
    def create_new_note(self):
        """Create a new note"""
        # Save current note if needed
        if self.is_editing and self.current_note:
            self.save_current_note()
        
        # Create a new note
        new_note = Note.create(
            title="Untitled",
            content="",
            plain_content="",
            color="default"
        )
        
        # Add to notes list
        self.notes.insert(0, new_note)
        
        # Refresh the notes list
        self.render_notes()
        
        # Select the new note
        self.select_note(0)
        
        # Focus the title field
        self.title_entry.focus_set()
    
    def save_current_note(self):
        """Save the current note"""
        if not self.current_note or not self.is_editing:
            return
        
        # Get content
        title = self.title_var.get()
        content = self.text_editor.get("1.0", tk.END).strip()
        plain_content = content  # In a full implementation, strip formatting for search
        color = self.color_var.get()
        is_pinned = self.pin_var.get()
        
        # Update note
        self.current_note.update(
            title=title,
            content=content,
            plain_content=plain_content,
            color=color,
            is_pinned=is_pinned
        )
        
        # Update note in list if needed (for title or pinned status changes)
        if self.selected_note_index >= 0:
            # Re-sort notes if pinned status changed
            if is_pinned != self.notes[self.selected_note_index].is_pinned:
                # Get the note ID
                note_id = self.current_note.id
                
                # Reload notes to get proper sorting
                self.notes = Note.get_all()
                
                # Find the note in the new list
                for i, note in enumerate(self.notes):
                    if note.id == note_id:
                        self.selected_note_index = i
                        self.current_note = note
                        break
                
                # Re-render the list
                self.render_notes()
            else:
                # Just update the current item
                self.create_note_item(self.current_note, self.selected_note_index)
        
        # Update status
        self.status_label.configure(text="Note saved")
        self.modified_label.configure(text=f"Modified: {datetime.datetime.now().strftime('%b %d, %Y %H:%M')}")
    
    def delete_note(self):
        """Delete the current note"""
        if not self.current_note:
            return
        
        # Confirm deletion
        if messagebox.askyesno("Delete Note", "Are you sure you want to delete this note?"):
            # Delete note
            note_id = self.current_note.id
            
            # Delete from database
            Note.delete(note_id)
            
            # Remove from list
            self.notes.pop(self.selected_note_index)
            
            # Reset current note
            self.current_note = None
            self.selected_note_index = -1
            
            # Refresh notes list
            self.render_notes()
    
    def on_search_changed(self, varname, index, mode):
        """
        Handle search input changes and filter notes list
        
        Args:
            varname: Variable name that changed (from trace_add)
            index: Index in the variable that changed
            mode: Type of change (write, read, etc.)
        """
        search_text = self.search_var.get().lower()
        
        # Skip filtering if the search box contains the placeholder text
        if search_text == "search notes...":
            return
        
        # If search is empty, show all notes
        if not search_text:
            self.render_notes()
            return
        
        # Filter notes based on search text
        filtered_notes = []
        for note in self.notes:
            # Search in title and content
            if (search_text in note.title.lower() or 
                (note.plain_content and search_text in note.plain_content.lower())):
                filtered_notes.append(note)
        
        # Update the notes list with filtered results
        self.render_notes(filtered_notes)
    
    def on_search_focus_in(self, event):
        """Handle focus entering the search box"""
        if self.search_var.get() == "Search notes...":
            self.search_var.set("")

    def on_search_focus_out(self, event):
        """Handle focus leaving the search box"""
        if not self.search_var.get():
            self.search_var.set("Search notes...")

    def on_search_return(self, event):
        """Handle Enter key in search box"""
        # Same as on_search_changed but forces update
        search_text = self.search_var.get().lower()
        
        if not search_text or search_text == "search notes...":
            self.render_notes()
            return
        
        filtered_notes = []
        for note in self.notes:
            if (search_text in note.title.lower() or 
                (note.plain_content and search_text in note.plain_content.lower())):
                filtered_notes.append(note)
        
        self.render_notes(filtered_notes)

    def update_categories_list(self):
        """Update the categories list in the sidebar"""
        # Clear existing categories
        for widget in self.categories_list_frame.winfo_children():
            widget.destroy()
        
        # Add each category
        for category in self.categories:
            cat_btn = ttk.Button(
                self.categories_list_frame,
                text=category.name,
                command=lambda c=category: self.filter_by_category(c),
                style="Sidebar.TButton"
            )
            cat_btn.pack(fill=tk.X, padx=0, pady=1)
    
    def update_tags_list(self):
        """Update the tags list in the sidebar"""
        # Clear existing tags
        for widget in self.tags_list_frame.winfo_children():
            widget.destroy()
        
        # Add each tag
        for tag in self.tags:
            tag_btn = ttk.Button(
                self.tags_list_frame,
                text=tag.name,
                command=lambda t=tag: self.filter_by_tag(t),
                style="Sidebar.TButton"
            )
            tag_btn.pack(fill=tk.X, padx=0, pady=1)
    
    def add_category(self):
        """Add a new category"""
        # Simple dialog to get category name
        category_name = simpledialog.askstring("New Category", "Enter category name:")
        if not category_name:
            return
        
        # Create new category
        new_category = Category.create(name=category_name)
        
        # Add to list and update display
        self.categories.append(new_category)
        self.update_categories_list()
    
    def add_tag(self):
        """Add a new tag"""
        # Simple dialog to get tag name
        tag_name = simpledialog.askstring("New Tag", "Enter tag name:")
        if not tag_name:
            return
        
        # Create new tag
        new_tag = Tag.create(name=tag_name)
        
        # Add to list and update display
        self.tags.append(new_tag)
        self.update_tags_list()
    
    def show_smart_view(self, view_type):
        """
        Show a smart view of notes
        
        Args:
            view_type (str): Type of view - "all", "recent", or "pinned"
        """
        if view_type == "all":
            self.view_label.configure(text="All Notes")
            self.render_notes()
        
        elif view_type == "recent":
            self.view_label.configure(text="Recent Notes")
            # Get notes from the last 7 days
            one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
            recent_notes = [n for n in self.notes if n.modified_date > one_week_ago]
            self.render_notes(recent_notes)
        
        elif view_type == "pinned":
            self.view_label.configure(text="Pinned Notes")
            pinned_notes = [n for n in self.notes if n.is_pinned]
            self.render_notes(pinned_notes)
    
    def filter_by_category(self, category):
        """Filter notes by category"""
        self.view_label.configure(text=f"Category: {category.name}")
        # Filter notes by category (assuming notes have a category attribute)
        filtered_notes = [n for n in self.notes if hasattr(n, 'category_id') and n.category_id == category.id]
        self.render_notes(filtered_notes)
    
    def filter_by_tag(self, tag):
        """Filter notes by tag"""
        self.view_label.configure(text=f"Tag: {tag.name}")
        # Filter notes by tag (assuming note-tag relationships)
        # This would need more logic to handle note-tag relationships
        # For simplicity, we'll just filter by tag name appearing in content
        filtered_notes = [n for n in self.notes if 
                          tag.name.lower() in (n.plain_content or "").lower()]
        self.render_notes(filtered_notes)
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.theme_manager.toggle_theme()
        
        # Update UI colors
        self.colors = self.theme_manager.get_current_theme_colors()
        
        # Refresh the UI
        self.render_notes()
    
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog would appear here")
        # In a full implementation, this would show a settings dialog

    def focus_search(self):
        """Set focus to the search box"""
        self.search_entry.focus_set()
        self.on_search_focus_in(None)

    def toggle_pin(self):
        """Toggle the pinned status of the current note"""
        if not self.current_note:
            return
            
        self.current_note.is_pinned = self.pin_var.get()
        self.save_current_note()
    
    def on_title_changed(self, event):
        """Handle title changes"""
        if self.is_editing and self.current_note:
            self.current_note.title = self.title_var.get()
            self.status_label.configure(text="Editing...")
            
            # Restart autosave timer if exists
            self.setup_autosave()
    
    def on_text_changed(self, event):
        """Handle text changes"""
        if self.is_editing and self.current_note:
            self.status_label.configure(text="Editing...")
            
            # Restart autosave timer
            self.setup_autosave()
    
    def on_color_changed(self, event):
        """Handle color changes"""
        if self.is_editing and self.current_note:
            self.current_note.color = self.color_var.get()
            self.save_current_note()
    
    def setup_autosave(self):
        """Set up autosave timer"""
        # Cancel existing timer if any
        if hasattr(self, 'autosave_timer') and self.autosave_timer:
            self.root.after_cancel(self.autosave_timer)
            
        # Set up new timer
        self.autosave_timer = self.root.after(30000, self.autosave)  # 30 seconds
    
    def autosave(self):
        """Automatically save current note"""
        if self.is_editing and self.current_note:
            self.save_current_note()
            self.status_label.configure(text="Autosaved")
            
        # Reset timer
        self.setup_autosave()
    
    def format_bold(self):
        """Apply bold formatting to selected text"""
        if not self.is_editing:
            return
            
        try:
            # Get selected text range
            if self.text_editor.tag_ranges("sel"):
                self.text_editor.tag_add("bold", "sel.first", "sel.last")
        except tk.TclError:
            pass
    
    def format_italic(self):
        """Apply italic formatting to selected text"""
        if not self.is_editing:
            return
            
        try:
            # Get selected text range
            if self.text_editor.tag_ranges("sel"):
                self.text_editor.tag_add("italic", "sel.first", "sel.last")
        except tk.TclError:
            pass
    
    def format_underline(self):
        """Apply underline formatting to selected text"""
        if not self.is_editing:
            return
            
        try:
            # Get selected text range
            if self.text_editor.tag_ranges("sel"):
                self.text_editor.tag_add("underline", "sel.first", "sel.last")
        except tk.TclError:
            pass
    
    def format_bullet_list(self):
        """Insert bullet list at cursor"""
        if not self.is_editing:
            return
            
        try:
            # Insert bullet at line start
            self.text_editor.insert("insert linestart", "• ")
            self.text_editor.tag_add("bullet", "insert linestart", "insert linestart+2c")
        except tk.TclError:
            pass
    
    def format_number_list(self):
        """Insert numbered list at cursor"""
        if not self.is_editing:
            return
            
        try:
            # Get current line number relative to visible lines
            line_count = int(self.text_editor.index("insert").split(".")[0])
            self.text_editor.insert("insert linestart", f"{line_count}. ")
            self.text_editor.tag_add("number", "insert linestart", f"insert linestart+{len(str(line_count))+2}c")
        except (tk.TclError, ValueError):
            pass
    
    def export_note(self):
        """Export the current note"""
        if not self.current_note:
            return
            
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"{self.current_note.title}.txt"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"{self.current_note.title}\n\n")
                f.write(self.text_editor.get("1.0", tk.END))
            
            self.status_label.configure(text=f"Exported to {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export note: {e}")
