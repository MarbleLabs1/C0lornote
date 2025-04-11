"""
C0lorNote Database Module

This module handles database connections, initialization, and migrations.
SQLAlchemy is used as the ORM to interact with the SQLite database.
"""

import os
import logging
import shutil
import datetime
from pathlib import Path
from contextlib import contextmanager

from sqlalchemy import create_engine, event, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

# Import settings to get the database path
from src.config import settings

# Create a base class for SQLAlchemy models
Base = declarative_base()

# Global variables for database connection
engine = None
Session = None
session_factory = None


def get_db_path():
    """
    Get the database path from settings
    
    Returns:
        str: The path to the database file
    """
    db_path = settings.get_setting("database_path")
    
    # Ensure the directory exists
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    return db_path


def initialize_db():
    """
    Initialize the database engine and session factory
    
    Returns:
        bool: True if successful, False otherwise
    """
    global engine, Session, session_factory
    
    try:
        db_path = get_db_path()
        logging.info(f"Initializing database at: {db_path}")
        
        # Create SQLite database engine with connection pooling
        sqlite_url = f"sqlite:///{db_path}"
        engine = create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False  # Set to True for SQL query logging
        )
        
        # Add pragma for foreign key support in SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        
        # Create session factory
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)
        
        # Create tables if they don't exist
        Base.metadata.create_all(engine)
        
        # Check if we need to run migrations
        current_version = get_db_version()
        run_migrations(current_version)
        
        return True
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        return False


def close_db():
    """
    Close the database connection
    
    Returns:
        bool: True if successful, False otherwise
    """
    global Session
    try:
        if Session:
            Session.remove()
        return True
    except Exception as e:
        logging.error(f"Error closing database: {e}")
        return False


@contextmanager
def db_session():
    """
    Context manager for database sessions to ensure proper cleanup
    
    Yields:
        Session: An SQLAlchemy session object
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def get_db_version():
    """
    Get the current database version
    
    Returns:
        int: The current database version
    """
    # Check if version table exists
    if not inspect(engine).has_table('db_version'):
        # Create version table and set initial version
        from sqlalchemy import Column, Integer, String, DateTime
        from sqlalchemy.sql import func
        
        class DBVersion(Base):
            __tablename__ = 'db_version'
            id = Column(Integer, primary_key=True)
            version = Column(Integer, nullable=False)
            description = Column(String, nullable=True)
            applied_at = Column(DateTime, default=func.now())
        
        Base.metadata.create_all(engine, tables=[DBVersion.__table__])
        
        with db_session() as session:
            version = DBVersion(version=1, description="Initial schema")
            session.add(version)
            session.commit()
        return 1
    
    # Get current version from the database
    with db_session() as session:
        # Dynamically define the model to avoid circular imports
        from sqlalchemy import Column, Integer, String, DateTime
        
        class DBVersion(Base):
            __tablename__ = 'db_version'
            id = Column(Integer, primary_key=True)
            version = Column(Integer, nullable=False)
            description = Column(String, nullable=True)
            applied_at = Column(DateTime)
        
        # Get the latest version
        latest_version = session.query(DBVersion).order_by(DBVersion.version.desc()).first()
        if latest_version:
            return latest_version.version
        return 0


def run_migrations(current_version):
    """
    Run necessary migrations to update the database schema
    
    Args:
        current_version (int): The current database version
    
    Returns:
        bool: True if migrations were applied, False otherwise
    """
    # Dictionary of migration functions keyed by version
    migrations = {
        # Example: 2: upgrade_to_v2,
        # 3: upgrade_to_v3,
    }
    
    latest_version = max(migrations.keys()) if migrations else current_version
    
    if current_version >= latest_version:
        logging.info(f"Database schema is up to date (version {current_version})")
        return False
    
    logging.info(f"Upgrading database from version {current_version} to {latest_version}")
    
    # Apply migrations in order
    with db_session() as session:
        for version in range(current_version + 1, latest_version + 1):
            if version in migrations:
                try:
                    # Run the migration function
                    migration_func = migrations[version]
                    description = migration_func()
                    
                    # Update the version in the database
                    from sqlalchemy import Column, Integer, String, DateTime
                    
                    class DBVersion(Base):
                        __tablename__ = 'db_version'
                        id = Column(Integer, primary_key=True)
                        version = Column(Integer, nullable=False)
                        description = Column(String, nullable=True)
                        applied_at = Column(DateTime)
                    
                    # Record the new version
                    new_version = DBVersion(
                        version=version,
                        description=description or f"Upgrade to version {version}"
                    )
                    session.add(new_version)
                    session.commit()
                    
                    logging.info(f"Applied migration to version {version}: {description}")
                except Exception as e:
                    logging.error(f"Migration to version {version} failed: {e}")
                    raise
    
    return True


def backup_database():
    """
    Create a backup of the database file
    
    Returns:
        str: Path to the backup file if successful, None otherwise
    """
    try:
        # Get paths
        db_path = get_db_path()
        backup_dir = settings.get_setting("backup_directory")
        max_backups = settings.get_setting("max_backups")
        
        # Ensure backup directory exists
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        db_filename = os.path.basename(db_path)
        backup_filename = f"{db_filename}_{timestamp}.bak"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy the database file
        shutil.copy2(db_path, backup_path)
        
        # Clean up old backups if necessary
        cleanup_old_backups(backup_dir, max_backups)
        
        logging.info(f"Database backup created at: {backup_path}")
        return backup_path
    except Exception as e:
        logging.error(f"Database backup failed: {e}")
        return None


def cleanup_old_backups(backup_dir, max_backups):
    """
    Remove old database backups to keep only the specified number
    
    Args:
        backup_dir (str): Directory containing backup files
        max_backups (int): Maximum number of backups to keep
    """
    try:
        # List all backup files
        backups = [f for f in os.listdir(backup_dir) if f.endswith('.bak')]
        
        # If we have more than max_backups, remove the oldest ones
        if len(backups) > max_backups:
            # Sort by modification time (oldest first)
            backups.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)))
            
            # Remove oldest backups
            for i in range(len(backups) - max_backups):
                os.remove(os.path.join(backup_dir, backups[i]))
                logging.info(f"Removed old backup: {backups[i]}")
    except Exception as e:
        logging.error(f"Cleanup of old backups failed: {e}")


def restore_database(backup_path):
    """
    Restore the database from a backup file
    
    Args:
        backup_path (str): Path to the backup file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Close current database connection
        close_db()
        
        # Get the current database path
        db_path = get_db_path()
        
        # Create a backup of the current database before restoring
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_restore_backup = f"{db_path}_pre_restore_{timestamp}.bak"
        shutil.copy2(db_path, pre_restore_backup)
        
        # Restore from backup
        shutil.copy2(backup_path, db_path)
        
        # Reinitialize the database connection
        initialize_db()
        
        logging.info(f"Database restored from: {backup_path}")
        return True
    except Exception as e:
        logging.error(f"Database restore failed: {e}")
        return False

