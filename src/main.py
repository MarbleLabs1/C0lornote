#!/usr/bin/env python3
"""
C0lorNote - A modern note-taking application inspired by macOS Notes and Google Keep
Main entry point for the application.
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk

# Add the parent directory to sys.path to ensure we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import application modules
from src.config import settings
from src.models.db import initialize_db, close_db
from src.models.note import Note
from src.ui.main_window import MainWindow
from src.ui.theme_manager import ThemeManager
from src.utils.logger import setup_logger

class C0lorNoteApp:
    """Main application class for C0lorNote"""
    
    def __init__(self):
        """Initialize the application"""
        # Set up logging
        self.logger = setup_logger()
        self.logger.info("Starting C0lorNote application")
        
        # Load settings
        self.settings = settings.load_settings()
        self.logger.info(f"Loaded settings: theme={self.settings.get('theme', 'default')}")
        
        # Initialize database
        self.db_initialized = initialize_db()
        if not self.db_initialized:
            self.logger.error("Failed to initialize database. Exiting application.")
            sys.exit(1)
        
        # Create the main application window
        self.root = ThemedTk(theme=self.settings.get("theme", "arc"))
        self.root.title("C0lorNote")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Set application icon (to be added in assets)
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     "assets", "icon.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
        except Exception as e:
            self.logger.warning(f"Could not load application icon: {e}")
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(self.root, self.settings)
        
        # Create the main window UI
        self.main_window = MainWindow(self.root, self.theme_manager)
        
        # Set up window close event handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Schedule periodic autosave
        self.schedule_autosave()
    
    def run(self):
        """Start the application main loop"""
        self.logger.info("Entering main application loop")
        self.root.mainloop()
    
    def schedule_autosave(self):
        """Schedule periodic autosave of notes"""
        self.root.after(300000, self.autosave)  # Autosave every 5 minutes (300000 ms)
    
    def autosave(self):
        """Automatically save all open notes"""
        try:
            if hasattr(self.main_window, 'save_all_notes'):
                self.main_window.save_all_notes()
                self.logger.info("Autosaved notes")
        except Exception as e:
            self.logger.error(f"Error during autosave: {e}")
        finally:
            # Reschedule the autosave
            self.schedule_autosave()
    
    def on_close(self):
        """Handle application close event"""
        try:
            # Save all notes before closing
            if hasattr(self.main_window, 'save_all_notes'):
                self.main_window.save_all_notes()
            
            # Close database connection
            close_db()
            
            # Save settings
            settings.save_settings(self.settings)
            
            self.logger.info("Application closing normally")
            
            # Destroy the root window and exit
            self.root.destroy()
        except Exception as e:
            self.logger.error(f"Error during application shutdown: {e}")
            self.root.destroy()


def main():
    """Main function to start the application"""
    app = C0lorNoteApp()
    app.run()


if __name__ == "__main__":
    main()

