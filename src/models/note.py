# -*- coding: utf-8 -*-

"""Modelo de dados de uma nota."""

import datetime
import uuid


class Note:
    """Class representing a note"""
    
    @staticmethod
    def new_id():
        """Gera um identificador unico para uma nota."""
        return str(uuid.uuid4())

    def __init__(self, title="", content="", is_code=False, tags=None, category=None):
        self.id = Note.new_id()
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
            "id": self.id,
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
        note.id = data.get("id") or Note.new_id()
        note.created_date = datetime.datetime.fromisoformat(data.get("created_date", datetime.datetime.now().isoformat()))
        note.modified_date = datetime.datetime.fromisoformat(data.get("modified_date", datetime.datetime.now().isoformat()))
        return note
