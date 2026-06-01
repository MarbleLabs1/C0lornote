"""
Tests for src/utils/logger.py
"""

import logging
import os
from logging.handlers import RotatingFileHandler

import pytest


@pytest.fixture()
def logger_dir(tmp_path, monkeypatch):
    """Redirect APP_CONFIG_DIR for logger tests so log files go to tmp_path."""
    import src.config.settings as s
    monkeypatch.setattr(s, "APP_CONFIG_DIR", str(tmp_path))
    return tmp_path


def test_setup_logger_returns_logger_instance(logger_dir):
    from src.utils.logger import setup_logger
    result = setup_logger("test_app")
    assert isinstance(result, logging.Logger)
    assert result.name == "test_app"


def test_setup_logger_has_console_handler(logger_dir):
    from src.utils.logger import setup_logger
    logger = setup_logger("test_console")
    handler_types = [type(h) for h in logger.handlers]
    assert logging.StreamHandler in handler_types


def test_setup_logger_has_file_handler(logger_dir):
    from src.utils.logger import setup_logger
    logger = setup_logger("test_file")
    has_rotating = any(isinstance(h, RotatingFileHandler) for h in logger.handlers)
    assert has_rotating


def test_setup_logger_log_file_created(logger_dir):
    from src.utils.logger import setup_logger
    setup_logger("test_created")
    log_file = logger_dir / "logs" / "c0lornote.log"
    assert log_file.exists()


def test_setup_logger_respects_console_level(logger_dir):
    from src.utils.logger import setup_logger
    logger = setup_logger("test_level", console_level=logging.WARNING)
    stream_handlers = [h for h in logger.handlers if type(h) is logging.StreamHandler]
    assert stream_handlers[0].level == logging.WARNING


def test_setup_logger_removes_existing_handlers_on_recall(logger_dir):
    from src.utils.logger import setup_logger
    setup_logger("test_dup")
    logger = setup_logger("test_dup")
    # Should still have exactly 2 handlers (console + file), not 4
    assert len(logger.handlers) == 2


def test_get_module_logger_returns_child_logger(logger_dir):
    from src.utils.logger import get_module_logger
    logger = get_module_logger("mymodule")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "c0lornote.mymodule"


def test_get_log_path_creates_logs_directory(logger_dir):
    from src.utils.logger import get_log_path
    path = get_log_path()
    assert (logger_dir / "logs").is_dir()
    assert path.endswith("c0lornote.log")


def test_setup_logger_graceful_when_file_handler_fails(logger_dir, monkeypatch):
    import src.utils.logger as logger_mod
    monkeypatch.setattr(logger_mod, "get_log_path", lambda: (_ for _ in ()).throw(OSError("no disk")))
    from src.utils.logger import setup_logger
    logger = setup_logger("test_graceful")
    assert isinstance(logger, logging.Logger)
    # Console handler must still be present
    assert any(type(h) is logging.StreamHandler for h in logger.handlers)
