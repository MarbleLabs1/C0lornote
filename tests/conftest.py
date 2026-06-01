"""
Shared pytest fixtures for C0lornote test suite.
"""

import sys
import os
from pathlib import Path
from contextlib import contextmanager
from unittest.mock import patch

# Ensure project root is on sys.path so `src.*` imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

import pytest


# ---------------------------------------------------------------------------
# Reentrant db_session replacement
# ---------------------------------------------------------------------------

@contextmanager
def _reentrant_db_session():
    """
    Drop-in replacement for src.models.db.db_session that handles the nested
    call pattern (Note.create → Tag.get_or_create both open a session).

    scoped_session returns the same underlying session for the same thread,
    so nested open/close calls on the plain context manager would close the
    session before the outer commit fires.  This wrapper tracks nesting depth
    and only commits/closes at the outermost level.
    """
    import src.models.db as db_module
    session = db_module.Session()
    nesting = getattr(session, '_test_nesting', 0)
    session._test_nesting = nesting + 1
    try:
        yield session
        if session._test_nesting == 1:
            session.commit()
    except Exception:
        if session._test_nesting == 1:
            session.rollback()
        raise
    finally:
        session._test_nesting -= 1
        if session._test_nesting == 0:
            session.close()


# ---------------------------------------------------------------------------
# config_dir — session-scoped, redirects settings module to a temp directory
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def config_dir(tmp_path_factory):
    """
    Redirects all settings file I/O to a temporary directory for the entire
    test session.  Uses unittest.mock.patch because monkeypatch is
    function-scoped and cannot span a session fixture.
    """
    import src.config.settings as s

    cfg = tmp_path_factory.mktemp("config")
    (cfg / "backups").mkdir()

    orig_backup_dir = s.DEFAULT_SETTINGS["backup_directory"]
    orig_db_path = s.DEFAULT_SETTINGS["database_path"]

    with patch.multiple(
        "src.config.settings",
        APP_CONFIG_DIR=str(cfg),
        CONFIG_FILE=str(cfg / "settings.yaml"),
        DEFAULT_DB_PATH=str(cfg / "notes.db"),
    ):
        s.DEFAULT_SETTINGS["backup_directory"] = str(cfg / "backups")
        s.DEFAULT_SETTINGS["database_path"] = str(cfg / "notes.db")
        yield cfg

    s.DEFAULT_SETTINGS["backup_directory"] = orig_backup_dir
    s.DEFAULT_SETTINGS["database_path"] = orig_db_path


# ---------------------------------------------------------------------------
# settings_dir — function-scoped, fresh config dir per test
# ---------------------------------------------------------------------------

@pytest.fixture()
def settings_dir(tmp_path, monkeypatch):
    """
    Provides a completely isolated settings environment per test function.
    Patches module-level constants and DEFAULT_SETTINGS dict entries.
    """
    import src.config.settings as s

    cfg = tmp_path / "config"
    cfg.mkdir()

    monkeypatch.setattr(s, "APP_CONFIG_DIR", str(cfg))
    monkeypatch.setattr(s, "CONFIG_FILE", str(cfg / "settings.yaml"))
    monkeypatch.setattr(s, "DEFAULT_DB_PATH", str(cfg / "notes.db"))
    monkeypatch.setitem(s.DEFAULT_SETTINGS, "backup_directory", str(cfg / "backups"))
    monkeypatch.setitem(s.DEFAULT_SETTINGS, "database_path", str(cfg / "notes.db"))

    return cfg


# ---------------------------------------------------------------------------
# db — function-scoped in-memory SQLite engine, patches module globals
# ---------------------------------------------------------------------------

@pytest.fixture()
def db(config_dir, monkeypatch):
    """
    Per-test in-memory SQLite engine.  Patches the three module-level
    globals in src.models.db and replaces db_session with a reentrant
    version that survives the nested Note.create → Tag.get_or_create
    call pattern.
    """
    import src.models.db as db_module
    from src.models.db import Base
    import src.models.note  # noqa: F401 — registers ORM tables on Base.metadata

    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_factory = sessionmaker(bind=test_engine, expire_on_commit=False)
    test_session = scoped_session(test_factory)

    monkeypatch.setattr(db_module, "engine", test_engine)
    monkeypatch.setattr(db_module, "Session", test_session)
    monkeypatch.setattr(db_module, "session_factory", test_factory)
    monkeypatch.setattr("src.models.db.db_session", _reentrant_db_session)
    monkeypatch.setattr("src.models.note.db_session", _reentrant_db_session)

    Base.metadata.create_all(test_engine)

    yield test_engine

    test_session.remove()
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


# ---------------------------------------------------------------------------
# Shared entity fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_category(db):
    from src.models.note import Category
    return Category.create(name="Work", color="#FF0000")


@pytest.fixture()
def sample_tag(db):
    from src.models.note import Tag
    return Tag.create(name="important", color="#00FF00")


@pytest.fixture()
def sample_note(db):
    from src.models.note import Note
    return Note.create(title="Hello", plain_content="World")
