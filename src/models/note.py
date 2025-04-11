"""
C0lorNote Note Model

This module defines the Note, Tag, and Category models for the C0lorNote application.
"""

import uuid
import datetime
from typing import List, Optional, Dict, Any, Union
from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, 
    ForeignKey, Table, func, or_, and_, desc
)
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.sql import expression

from src.models.db import Base, db_session, Session


# Association table for many-to-many relationship between notes and tags
note_tag = Table(
    'note_tag',
    Base.metadata,
    Column('note_id', String(36), ForeignKey('notes.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', String(36), ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


class Category(Base):
    """Category model for organizing notes"""
    __tablename__ = 'categories'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(20), nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    
    # Relationship with notes
    notes = relationship("Note", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(id='{self.id}', name='{self.name}')>"
    
    @classmethod
    def create(cls, name: str, color: str = None) -> 'Category':
        """
        Create a new category
        
        Args:
            name (str): Category name
            color (str, optional): Color code for the category
            
        Returns:
            Category: The created category object
        """
        with db_session() as session:
            category = cls(name=name, color=color)
            session.add(category)
            session.commit()
            return category
    
    @classmethod
    def get_all(cls) -> List['Category']:
        """
        Get all categories
        
        Returns:
            List[Category]: List of all categories
        """
        with db_session() as session:
            return session.query(cls).order_by(cls.name).all()
    
    @classmethod
    def get_by_id(cls, category_id: str) -> Optional['Category']:
        """
        Get category by ID
        
        Args:
            category_id (str): Category ID
            
        Returns:
            Optional[Category]: The category if found, None otherwise
        """
        with db_session() as session:
            return session.query(cls).filter(cls.id == category_id).first()
    
    @classmethod
    def get_by_name(cls, name: str) -> Optional['Category']:
        """
        Get category by name
        
        Args:
            name (str): Category name
            
        Returns:
            Optional[Category]: The category if found, None otherwise
        """
        with db_session() as session:
            return session.query(cls).filter(cls.name == name).first()


class Tag(Base):
    """Tag model for tagging notes"""
    __tablename__ = 'tags'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(20), nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    
    # Relationship with notes
    notes = relationship("Note", secondary=note_tag, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(id='{self.id}', name='{self.name}')>"
    
    @classmethod
    def create(cls, name: str, color: str = None) -> 'Tag':
        """
        Create a new tag
        
        Args:
            name (str): Tag name
            color (str, optional): Color code for the tag
            
        Returns:
            Tag: The created tag object
        """
        with db_session() as session:
            tag = cls(name=name, color=color)
            session.add(tag)
            session.commit()
            return tag
    
    @classmethod
    def get_all(cls) -> List['Tag']:
        """
        Get all tags
        
        Returns:
            List[Tag]: List of all tags
        """
        with db_session() as session:
            return session.query(cls).order_by(cls.name).all()
    
    @classmethod
    def get_by_id(cls, tag_id: str) -> Optional['Tag']:
        """
        Get tag by ID
        
        Args:
            tag_id (str): Tag ID
            
        Returns:
            Optional[Tag]: The tag if found, None otherwise
        """
        with db_session() as session:
            return session.query(cls).filter(cls.id == tag_id).first()
    
    @classmethod
    def get_by_name(cls, name: str) -> Optional['Tag']:
        """
        Get tag by name
        
        Args:
            name (str): Tag name
            
        Returns:
            Optional[Tag]: The tag if found, None otherwise
        """
        with db_session() as session:
            return session.query(cls).filter(cls.name == name).first()
    
    @classmethod
    def get_or_create(cls, name: str, color: str = None) -> 'Tag':
        """
        Get an existing tag by name or create a new one
        
        Args:
            name (str): Tag name
            color (str, optional): Color code for the tag
            
        Returns:
            Tag: The existing or created tag
        """
        with db_session() as session:
            tag = session.query(cls).filter(cls.name == name).first()
            if not tag:
                tag = cls(name=name, color=color)
                session.add(tag)
                session.commit()
            return tag


class Note(Base):
    """Note model for storing note data"""
    __tablename__ = 'notes'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=True)  # Rich text content
    plain_content = Column(Text, nullable=True)  # Plain text for search
    created_date = Column(DateTime, default=datetime.datetime.now)
    modified_date = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    color = Column(String(20), nullable=True)
    is_pinned = Column(Boolean, default=False, server_default=expression.false())
    category_id = Column(String(36), ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    category = relationship("Category", back_populates="notes")
    tags = relationship("Tag", secondary=note_tag, back_populates="notes")
    
    def __repr__(self):
        return f"<Note(id='{self.id}', title='{self.title or 'Untitled'}')>"
    
    @classmethod
    def create(cls, title: str = None, content: str = None, 
               plain_content: str = None, color: str = None, 
               category_id: str = None, tags: List[str] = None) -> 'Note':
        """
        Create a new note
        
        Args:
            title (str, optional): Note title
            content (str, optional): Rich text content
            plain_content (str, optional): Plain text for search
            color (str, optional): Color code
            category_id (str, optional): Category ID
            tags (List[str], optional): List of tag names
            
        Returns:
            Note: The created note object
        """
        with db_session() as session:
            note = cls(
                title=title,
                content=content,
                plain_content=plain_content,
                color=color,
                category_id=category_id
            )
            
            # Add tags if provided
            if tags:
                for tag_name in tags:
                    tag = Tag.get_or_create(tag_name)
                    note.tags.append(tag)
            
            session.add(note)
            session.commit()
            return note
    
    @classmethod
    def get_all(cls, include_tags: bool = True, 
                include_category: bool = True) -> List['Note']:
        """
        Get all notes
        
        Args:
            include_tags (bool): Whether to include tags in the results
            include_category (bool): Whether to include category in the results
            
        Returns:
            List[Note]: List of all notes
        """
        with db_session() as session:
            query = session.query(cls)
            
            if include_tags:
                query = query.options(joinedload(cls.tags))
            
            if include_category:
                query = query.options(joinedload(cls.category))
            
            return query.order_by(cls.is_pinned.desc(), cls.modified_date.desc()).all()
    
    @classmethod
    def get_by_id(cls, note_id: str, include_tags: bool = True, 
                  include_category: bool = True) -> Optional['Note']:
        """
        Get note by ID
        
        Args:
            note_id (str): Note ID
            include_tags (bool): Whether to include tags in the results
            include_category (bool): Whether to include category in the results
            
        Returns:
            Optional[Note]: The note if found, None otherwise
        """
        with db_session() as session:
            query = session.query(cls).filter(cls.id == note_id)
            
            if include_tags:
                query = query.options(joinedload(cls.tags))
            
            if include_category:
                query = query.options(joinedload(cls.category))
            
            return query.first()
    
    @classmethod
    def search(cls, query_text: str, category_id: str = None, 
               tag_ids: List[str] = None, pinned_only: bool = False,
               include_tags: bool = True, include_category: bool = True) -> List['Note']:
        """
        Search notes based on query text and filters
        
        Args:
            query_text (str): Text to search for in title and content
            category_id (str, optional): Filter by category ID
            tag_ids (List[str], optional): Filter by tag IDs
            pinned_only (bool): Only include pinned notes
            include_tags (bool): Whether to include tags in the results
            include_category (bool): Whether to include category in the results
            
        Returns:
            List[Note]: List of matching notes
        """
        with db_session() as session:
            query = session.query(cls)
            
            # Add search condition if provided
            if query_text:
                search_terms = [f"%{term}%" for term in query_text.split()]
                search_conditions = []
                
                for term in search_terms:
                    search_conditions.append(or_(
                        cls.title.ilike(term),
                        cls.plain_content.ilike(term)
                    ))
                
                query = query.filter(and_(*search_conditions))
            
            # Filter by category if provided
            if category_id:
                query = query.filter(cls.category_id == category_id)
            
            # Filter by tags if provided
            if tag_ids and len(tag_ids) > 0:
                for tag_id in tag_ids:
                    query = query.filter(cls.tags.any(Tag.id == tag_id))
            
            # Filter by pinned status if requested
            if pinned_only:
                query = query.filter(cls.is_pinned == True)
            
            # Include relationships if requested
            if include_tags:
                query = query.options(joinedload(cls.tags))
            
            if include_category:
                query = query.options(joinedload(cls.category))
            
            # Order by pinned status and last modified date
            return query.order_by(cls.is_pinned.desc(), cls.modified_date.desc()).all()
    
    @classmethod
    def get_by_category(cls, category_id: str, include_tags: bool = True) -> List['Note']:
        """
        Get notes by category
        
        Args:
            category_id (str): Category ID
            include_tags (bool): Whether to include tags in the results
            
        Returns:
            List[Note]: List of notes in the category
        """
        with db_session() as session:
            query = session.query(cls).filter(cls.category_id == category_id)
            
            if include_tags:
                query = query.options(joinedload(cls.tags))
            
            return query.order_by(cls.is_pinned.desc(), cls.modified_date.desc()).all()
    
    @classmethod
    def get_by_tag(cls, tag_id: str, include_category: bool = True) -> List['Note']:
        """
        Get notes by tag
        
        Args:
            tag_id (str): Tag ID
            include_category (bool): Whether to include category in the results
            
        Returns:
            List[Note]: List of notes with the tag
        """
        with db_session() as session:
            query = session.query(cls).filter(cls.tags.any(Tag.id == tag_id))
            
            # Include tags since we're querying by tag
            query = query.options(joinedload(cls.tags))
            
            if include_category:
                query = query.options(joinedload(cls.category))
            
            return query.order_by(cls.is_pinned.desc(), cls.modified_date.desc()).all()
    
    @classmethod
    def get_recent(cls, limit: int = 10, include_tags: bool = True, 
                   include_category: bool = True) -> List['Note']:
        """
        Get recently modified notes
        
        Args:
            limit (int): Maximum number of notes to return
            include_tags (bool): Whether to include tags in the results
            include_category (bool): Whether to include category in the results
            
        Returns:
            List[Note]: List of recent notes
        """
        with db_session() as session:
            query = session.query(cls)
            
            if include_tags:
                query = query.options(joinedload(cls.tags))
            
            if include_category:
                query = query.options(joinedload(cls.category))
            
            return query.order_by(cls.modified_date.desc()).limit(limit).all()
    
    def update(self, title: str = None, content: str = None, 
               plain_content: str = None, color: str = None, 
               is_pinned: bool = None, category_id: str = None, 
               tag_names: List[str] = None) -> 'Note':
        """
        Update note properties
        
        Args:
            title (str, optional): New title
            content (str, optional): New rich text content
            plain_content (str, optional): New plain text for search
            color (str, optional): New color code
            is_pinned (bool, optional): New pinned status
            category_id (str, optional): New category ID
            tag_names (List[str], optional): New list of tag names
            
        Returns:
            Note: The updated note object
        """
        with db_session() as session:
            # Get the note from the database
            note = session.query(Note).filter(Note.id == self.id).first()
            if not note:
                raise ValueError(f"Note with ID {self.id} not found")
            
            # Update properties if provided
            if title is not None:
                note.title = title
            
            if content is not None:
                note.content = content
            
            if plain_content is not None:
                note.plain_content = plain_content
            
            if color is not None:
                note.color = color
            
            if is_pinned is not None:
                note.is_pinned = is_pinned
            
            if category_id is not None:
                note.category_id = category_id
            
            # Update tags if provided
            if tag_names is not None:
                # Clear existing tags
                note.tags = []
                
                # Add new tags
                for tag_name in tag_names:
                    tag = Tag.get_or_create(tag_name)
                    note.tags.append(tag)
            
            # Commit changes
            session.commit()
            
            return note
    
    def delete(self) -> bool:
        """
        Delete this note
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with db_session() as session:
                note = session.query(Note).filter(Note.id == self.id).first()
                if note:
                    session.delete(note)
                    session.commit()
                    return True
                return False
        except Exception as e:
            logging.error(f"Error deleting note: {e}")
            return False
    
    @classmethod
    def delete_by_id(cls, note_id: str) -> bool:
        """
        Delete a note by ID
        
        Args:
            note_id (str): Note ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with db_session() as session:
                note = session.query(cls).filter(cls.id == note_id).first()
                if note:
                    session.delete(note)
                    session.commit()
                    return True
                return False
        except Exception as e:
            logging.error(f"Error deleting note: {e}")
            return False
    
    def toggle_pin(self) -> bool:
        """
        Toggle the pinned status of this note
        
        Returns:
            bool: The new pinned status
        """
        with db_session() as session:
            note = session.query(Note).filter(Note.id == self.id).first()
            if note:
                note.is_pinned = not note.is_pinned
                session.commit()
                self.is_pinned = note.is_pinned
                return self.is_pinned
            return self.is_pinned
    
    def add_tag(self, tag_name: str) -> bool:
        """
        Add a tag to this note
        
        Args:
            tag_name (str): Name of the tag to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with db_session() as session:
                note = session.query(Note).options(joinedload(Note.tags)).filter(Note.id == self.id).first()
                if not note:
                    return False
                
                # Check if the tag already exists
                for tag in note.tags:
                    if tag.name.lower() == tag_name.lower():
                        return True  # Tag already exists
                
                # Get or create the tag
                tag = Tag.get_or_create(tag_name)
                
                # Add the tag to the note
                note.tags.append(tag)
                session.commit()
                return True
        except Exception as e:
            logging.error(f"Error adding tag: {e}")
            return False
    
    def remove_tag(self, tag_name: str) -> bool:
        """
        Remove a tag from this note
        
        Args:
            tag_name (str): Name of the tag to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with db_session() as session:
                note = session.query(Note).options(joinedload(Note.tags)).filter(Note.id == self.id).first()
                if not note:
                    return False
                
                # Find the tag to remove
                tag_to_remove = None
                for tag in note.tags:
                    if tag.name.lower() == tag_name.lower():
                        tag_to_remove = tag
                        break
                
                if not tag_to_remove:
                    return False  # Tag not found
                
                # Remove the tag from the note
                note.tags.remove(tag_to_remove)
                session.commit()
                return True
        except Exception as e:
            logging.error(f"Error removing tag: {e}")
            return False
    
    @classmethod
    def count_by_category(cls) -> Dict[str, int]:
        """
        Count notes by category
        
        Returns:
            Dict[str, int]: Dictionary mapping category IDs to note counts
        """
        with db_session() as session:
            # Query to count notes by category
            results = session.query(
                cls.category_id,
                func.count(cls.id).label('note_count')
            ).group_by(cls.category_id).all()
            
            # Convert to dictionary
            counts = {str(r[0] or 'uncategorized'): r[1] for r in results}
            return counts
    
    @classmethod
    def count_by_tag(cls) -> Dict[str, int]:
        """
        Count notes by tag
        
        Returns:
            Dict[str, int]: Dictionary mapping tag IDs to note counts
        """
        with db_session() as session:
            # Query to count notes by tag
            results = session.query(
                Tag.id,
                func.count(note_tag.c.note_id).label('note_count')
            ).join(note_tag, Tag.id == note_tag.c.tag_id)\
             .group_by(Tag.id).all()
            
            # Convert to dictionary
            counts = {str(r[0]): r[1] for r in results}
            return counts
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the note to a dictionary for JSON serialization
        
        Returns:
            Dict[str, Any]: Dictionary representation of the note
        """
        result = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'modified_date': self.modified_date.isoformat() if self.modified_date else None,
            'color': self.color,
            'is_pinned': self.is_pinned,
            'category_id': self.category_id,
        }
        
        # Add category if available
        if hasattr(self, 'category') and self.category:
            result['category'] = {
                'id': self.category.id,
                'name': self.category.name,
                'color': self.category.color
            }
        
        # Add tags if available
        if hasattr(self, 'tags'):
            result['tags'] = [{'id': tag.id, 'name': tag.name, 'color': tag.color} for tag in self.tags]
        
        return result
