# -*- coding: utf-8 -*-

"""Camada de persistencia das notas (SQLite via SQLAlchemy).

Substitui o antigo armazenamento em notes.json. Na primeira execucao, se
existir um notes.json de uma versao anterior, ele e importado automaticamente
e renomeado para notes.json.migrated, sem perda de dados.
"""

import os
import json
import datetime

from sqlalchemy import create_engine, Column, String, Text, Boolean, DateTime
from sqlalchemy.orm import sessionmaker

try:  # SQLAlchemy 2.x
    from sqlalchemy.orm import declarative_base
except ImportError:  # SQLAlchemy 1.4
    from sqlalchemy.ext.declarative import declarative_base

from src.models.note import Note

Base = declarative_base()

APP_DIR = os.path.join(os.path.expanduser("~"), ".config", "c0lornote")


class NoteRow(Base):
    """Uma nota persistida."""

    __tablename__ = "notes"

    id = Column(String(36), primary_key=True)
    title = Column(String(500), default="")
    content = Column(Text, default="")
    is_code = Column(Boolean, default=False)
    category = Column(String(200), nullable=True)
    tags = Column(Text, default="[]")  # lista JSON
    created_date = Column(DateTime, default=datetime.datetime.now)
    modified_date = Column(DateTime, default=datetime.datetime.now)

    def to_note(self):
        note = Note(
            title=self.title or "",
            content=self.content or "",
            is_code=bool(self.is_code),
            tags=json.loads(self.tags or "[]"),
            category=self.category,
        )
        note.id = self.id
        note.created_date = self.created_date or datetime.datetime.now()
        note.modified_date = self.modified_date or note.created_date
        return note


class MetaRow(Base):
    """Pares chave/valor para categorias e tags globais."""

    __tablename__ = "meta"

    key = Column(String(50), primary_key=True)
    value = Column(Text, default="[]")


class NoteStore:
    """Le e grava notas, categorias e tags."""

    def __init__(self, db_path=None):
        os.makedirs(APP_DIR, exist_ok=True)
        self.db_path = db_path or os.path.join(APP_DIR, "notes.db")
        self.engine = create_engine(f"sqlite:///{self.db_path}", future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, future=True)

    # ------------------------------------------------------------------ #

    def is_empty(self):
        with self.Session() as s:
            return s.query(NoteRow).count() == 0

    def load(self):
        """Devolve (notas, categorias, tags)."""
        self._migrate_legacy_json()
        with self.Session() as s:
            notes = [r.to_note() for r in s.query(NoteRow).order_by(NoteRow.modified_date.desc())]
            meta = {m.key: json.loads(m.value or "[]") for m in s.query(MetaRow)}
        return notes, meta.get("categories", []), meta.get("tags", [])

    def save(self, notes, categories, tags):
        """Grava o estado completo (substitui o conteudo anterior)."""
        with self.Session() as s:
            s.query(NoteRow).delete()
            for note in notes:
                s.add(
                    NoteRow(
                        id=getattr(note, "id", None) or Note.new_id(),
                        title=note.title,
                        content=note.content,
                        is_code=note.is_code,
                        category=note.category,
                        tags=json.dumps(note.tags or []),
                        created_date=note.created_date,
                        modified_date=note.modified_date,
                    )
                )
            for key, value in (("categories", categories), ("tags", tags)):
                row = s.get(MetaRow, key)
                if row is None:
                    s.add(MetaRow(key=key, value=json.dumps(value or [])))
                else:
                    row.value = json.dumps(value or [])
            s.commit()

    # ------------------------------------------------------------------ #

    def _migrate_legacy_json(self):
        """Importa um notes.json antigo, uma unica vez."""
        legacy = os.path.join(APP_DIR, "notes.json")
        if not os.path.exists(legacy) or not self.is_empty():
            return
        try:
            with open(legacy, "r", encoding="utf-8") as f:
                data = json.load(f)
            notes = [Note.from_dict(d) for d in data.get("notes", [])]
            self.save(notes, data.get("categories", []), data.get("tags", []))
            os.replace(legacy, legacy + ".migrated")
        except Exception:
            # Um json corrompido nao pode impedir a aplicacao de abrir.
            pass
