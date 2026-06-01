"""
Tests for src/config/settings.py
"""

import os
import yaml
import pytest

import src.config.settings as s
from src.config.settings import (
    load_settings,
    save_settings,
    get_setting,
    update_setting,
    reset_to_defaults,
    ensure_config_dir,
    DEFAULT_SETTINGS,
)


def test_load_settings_returns_all_default_keys(settings_dir):
    result = load_settings()
    for key in DEFAULT_SETTINGS:
        assert key in result, f"Missing key: {key}"


def test_load_settings_creates_yaml_file_on_first_call(settings_dir):
    assert not os.path.exists(s.CONFIG_FILE)
    load_settings()
    assert os.path.exists(s.CONFIG_FILE)


def test_save_and_reload_round_trips(settings_dir):
    save_settings({"theme": "dark", "window_width": 1200})
    result = load_settings()
    assert result["theme"] == "dark"
    assert result["window_width"] == 1200
    # defaults fill in missing keys
    assert result["dark_mode"] == DEFAULT_SETTINGS["dark_mode"]


def test_load_settings_merges_missing_keys_from_defaults(settings_dir):
    os.makedirs(str(settings_dir), exist_ok=True)
    with open(s.CONFIG_FILE, "w") as f:
        yaml.dump({"theme": "clam"}, f)
    result = load_settings()
    assert result["theme"] == "clam"
    assert result["autosave_interval"] == DEFAULT_SETTINGS["autosave_interval"]


def test_load_settings_handles_corrupt_yaml_returns_defaults(settings_dir):
    os.makedirs(str(settings_dir), exist_ok=True)
    with open(s.CONFIG_FILE, "w") as f:
        f.write("NOT VALID YAML: {{{ :")
    result = load_settings()
    assert result["theme"] == DEFAULT_SETTINGS["theme"]
    assert result["window_width"] == DEFAULT_SETTINGS["window_width"]


def test_get_setting_known_key(settings_dir):
    assert get_setting("theme") == DEFAULT_SETTINGS["theme"]


def test_get_setting_unknown_key_returns_none(settings_dir):
    assert get_setting("definitely_not_a_real_key") is None


def test_get_setting_unknown_key_with_explicit_string_default(settings_dir):
    assert get_setting("definitely_not_a_real_key", default="fallback") == "fallback"


def test_get_setting_unknown_key_with_falsy_default(settings_dir):
    assert get_setting("definitely_not_a_real_key", default=False) is False
    assert get_setting("definitely_not_a_real_key", default=0) == 0


def test_get_setting_known_key_ignores_default(settings_dir):
    # The actual setting value should win over the default argument
    assert get_setting("dark_mode", default=True) == DEFAULT_SETTINGS["dark_mode"]


def test_update_setting_persists(settings_dir):
    update_setting("window_width", 1440)
    assert get_setting("window_width") == 1440


def test_reset_to_defaults_restores_all(settings_dir):
    update_setting("theme", "clam")
    reset_to_defaults()
    assert get_setting("theme") == DEFAULT_SETTINGS["theme"]


def test_ensure_config_dir_creates_directory(tmp_path, monkeypatch):
    new_dir = tmp_path / "newdir" / "c0lornote"
    monkeypatch.setattr(s, "APP_CONFIG_DIR", str(new_dir))
    monkeypatch.setitem(s.DEFAULT_SETTINGS, "backup_directory", str(new_dir / "backups"))
    assert not new_dir.exists()
    result = ensure_config_dir()
    assert result is True
    assert new_dir.exists()


def test_save_settings_returns_false_on_write_error(settings_dir, monkeypatch):
    import builtins
    original_open = builtins.open

    def broken_open(path, mode="r", **kwargs):
        if "w" in mode and str(s.CONFIG_FILE) in str(path):
            raise OSError("disk full")
        return original_open(path, mode, **kwargs)

    monkeypatch.setattr(builtins, "open", broken_open)
    result = save_settings({"theme": "x"})
    assert result is False
