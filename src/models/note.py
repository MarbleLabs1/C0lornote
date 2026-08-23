# -*- coding: utf-8 -*-

"""Modelo de dados de uma nota."""

import datetime
import html
import re
import uuid

# Tags que separam blocos de texto: viram espaco, para "</p><p>" nao colar
# duas palavras uma na outra.
_QUEBRAS = re.compile(r"</?(?:br|p|div|li|ul|ol|h[1-6]|tr|td|th|table)\b[^>]*>", re.I)
_TAGS = re.compile(r"<[^>]+>")
_ESPACOS = re.compile(r"\s+")


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
    
    def plain_content(self):
        """Return the content as readable text.

        Rich text notes are stored as HTML. Showing that HTML raw in the note
        list is unreadable, so tags and entities are resolved here. Code notes
        are already plain text and are returned as they are.
        """
        if self.is_code:
            return self.content
        texto = _QUEBRAS.sub(" ", self.content)
        texto = _TAGS.sub("", texto)
        texto = html.unescape(texto)
        return _ESPACOS.sub(" ", texto).strip()

    def preview(self, tamanho=60):
        """Return a one-line summary for the note list."""
        texto = _ESPACOS.sub(" ", self.plain_content()).strip()
        if len(texto) <= tamanho:
            return texto
        # Corta na ultima palavra inteira, para nao truncar no meio dela.
        corte = texto[:tamanho]
        espaco = corte.rfind(" ")
        if espaco > tamanho // 2:
            corte = corte[:espaco]
        return corte.rstrip() + "..."

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
