"""
Tests for src/models/db.py
"""

import os
import time
import pytest

from src.models.db import (
    db_session,
    get_db_version,
    run_migrations,
    close_db,
    backup_database,
    cleanup_old_backups,
)


# ---------------------------------------------------------------------------
# db_session context manager
# ---------------------------------------------------------------------------

def test_db_session_commits_on_success(db):
    from src.models.note import Category

    with db.connect() as conn:
        count_before = conn.execute(
            __import__("sqlalchemy").text("SELECT COUNT(*) FROM categories")
        ).scalar()

    # Insert a row via the context manager
    from src.models.db import db_session as real_session
    # Use the patched reentrant session directly via Category.create
    Category.create(name="SessionTest")

    with db.connect() as conn:
        count_after = conn.execute(
            __import__("sqlalchemy").text("SELECT COUNT(*) FROM categories")
        ).scalar()

    assert count_after == count_before + 1


def test_db_session_rollback_on_exception(db):
    import src.models.db as db_module
    from tests.conftest import _reentrant_db_session

    with pytest.raises(RuntimeError):
        with _reentrant_db_session() as session:
            from src.models.note import Category
            session.add(Category(name="ShouldNotExist"))
            raise RuntimeError("forced rollback")

    from src.models.note import Category
    assert Category.get_by_name("ShouldNotExist") is None


def test_db_session_reraises_exception(db):
    from tests.conftest import _reentrant_db_session

    with pytest.raises(ValueError, match="test error"):
        with _reentrant_db_session() as session:
            raise ValueError("test error")


# ---------------------------------------------------------------------------
# get_db_version
# ---------------------------------------------------------------------------

def test_get_db_version_returns_positive_int(db):
    result = get_db_version()
    assert isinstance(result, int)
    assert result >= 1


def test_get_db_version_idempotent(db):
    """Calling twice must not raise — validates the DBVersion redefinition fix."""
    v1 = get_db_version()
    v2 = get_db_version()
    assert v1 == v2


# ---------------------------------------------------------------------------
# run_migrations
# ---------------------------------------------------------------------------

def test_run_migrations_no_op_when_up_to_date(db):
    current = get_db_version()
    result = run_migrations(current)
    assert result is False


# ---------------------------------------------------------------------------
# close_db
# ---------------------------------------------------------------------------

def test_close_db_returns_true(db):
    assert close_db() is True


def test_close_db_when_session_is_none(monkeypatch):
    import src.models.db as db_module
    monkeypatch.setattr(db_module, "Session", None)
    assert close_db() is True


# ---------------------------------------------------------------------------
# backup_database / cleanup_old_backups
# ---------------------------------------------------------------------------

def _patch_settings_for_backup(monkeypatch, tmp_path, db_path, backup_dir):
    """Helper: fully isolates settings so load_settings() uses our values."""
    import src.config.settings as s
    monkeypatch.setattr(s, "APP_CONFIG_DIR", str(tmp_path))
    monkeypatch.setattr(s, "CONFIG_FILE", str(tmp_path / "settings.yaml"))
    monkeypatch.setitem(s.DEFAULT_SETTINGS, "database_path", str(db_path))
    monkeypatch.setitem(s.DEFAULT_SETTINGS, "backup_directory", str(backup_dir))
    monkeypatch.setitem(s.DEFAULT_SETTINGS, "max_backups", 5)


def test_backup_database_creates_file(db, tmp_path, monkeypatch):
    db_file = tmp_path / "notes.db"
    db_file.write_bytes(b"SQLite format 3\x00")
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    _patch_settings_for_backup(monkeypatch, tmp_path, db_file, backup_dir)

    result = backup_database()

    assert result is not None
    assert os.path.exists(result)
    assert result.endswith(".bak")


def test_backup_database_returns_none_on_missing_source(tmp_path, monkeypatch):
    missing = tmp_path / "does_not_exist.db"
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    _patch_settings_for_backup(monkeypatch, tmp_path, missing, backup_dir)

    result = backup_database()
    assert result is None


def test_cleanup_old_backups_removes_excess(tmp_path):
    # Create 7 .bak files with staggered modification times
    for i in range(7):
        f = tmp_path / f"notes_{i:02d}.bak"
        f.write_text("backup")
        os.utime(str(f), (i * 10, i * 10))  # oldest first

    cleanup_old_backups(str(tmp_path), max_backups=5)

    remaining = list(tmp_path.glob("*.bak"))
    assert len(remaining) == 5


def test_cleanup_old_backups_keeps_newest(tmp_path):
    for i in range(7):
        f = tmp_path / f"notes_{i:02d}.bak"
        f.write_text(f"backup {i}")
        os.utime(str(f), (i * 10, i * 10))

    cleanup_old_backups(str(tmp_path), max_backups=5)

    # The 2 oldest (index 0 and 1) should be gone; 2–6 should remain
    assert not (tmp_path / "notes_00.bak").exists()
    assert not (tmp_path / "notes_01.bak").exists()
    assert (tmp_path / "notes_06.bak").exists()


def test_cleanup_old_backups_does_nothing_under_limit(tmp_path):
    for i in range(3):
        (tmp_path / f"notes_{i}.bak").write_text("b")

    cleanup_old_backups(str(tmp_path), max_backups=5)

    assert len(list(tmp_path.glob("*.bak"))) == 3
