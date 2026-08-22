# -*- coding: utf-8 -*-

"""Testes de fumaca do C0lorNote.

Sobem a aplicacao inteira sem abrir janela (plataforma Qt "offscreen") e
verificam o caminho critico: criar a janela, persistir no SQLite, reler,
trocar de tema e usar o editor de codigo.

Rodar:  pytest tests/  ou  python tests/test_smoke.py
"""

import os
import sys
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import src.models.storage as storage
from src.models.note import Note
from src.ui.theme import ThemeType


def _app_and_window():
    """Cria a aplicacao Qt sobre um diretorio de dados temporario."""
    from PyQt6.QtWidgets import QApplication
    from src.ui.main_window import MainWindow

    storage.APP_DIR = tempfile.mkdtemp(prefix="c0lornote_test_")
    app = QApplication.instance() or QApplication([])
    return app, MainWindow()


def test_janela_abre_com_notas_de_exemplo():
    _, window = _app_and_window()
    assert len(window.notes) == 2


def test_persistencia_sobrevive_ao_reload():
    _, window = _app_and_window()
    window.notes.append(
        Note(title="Teste persistencia", content="conteudo", tags=["t"], category="Work")
    )
    window.save_notes()

    notes, categories, tags = storage.NoteStore().load()
    assert len(notes) == 3
    assert any(n.title == "Teste persistencia" for n in notes)
    assert "Work" in categories
    assert "welcome" in tags


def test_todos_os_temas_aplicam():
    _, window = _app_and_window()
    for theme in (ThemeType.MATRIX, ThemeType.DREAMCORE, ThemeType.MINIMALIST):
        window.change_theme(theme)


def test_editor_de_codigo():
    _, window = _app_and_window()
    window.note_editor.set_content("def f():\n    return 42", is_code=True)
    assert "42" in window.note_editor.get_content()


def test_migracao_do_notes_json_antigo():
    """Um notes.json de versao anterior deve ser importado uma unica vez."""
    import json

    storage.APP_DIR = tempfile.mkdtemp(prefix="c0lornote_migr_")
    legacy = os.path.join(storage.APP_DIR, "notes.json")
    with open(legacy, "w", encoding="utf-8") as f:
        json.dump(
            {
                "notes": [Note(title="Antiga", content="do json").to_dict()],
                "categories": ["Legado"],
                "tags": ["antigo"],
            },
            f,
        )

    notes, categories, tags = storage.NoteStore().load()
    assert [n.title for n in notes] == ["Antiga"]
    assert categories == ["Legado"]
    assert tags == ["antigo"]
    assert not os.path.exists(legacy), "o notes.json deveria ter sido renomeado"
    assert os.path.exists(legacy + ".migrated")


if __name__ == "__main__":
    falhas = 0
    for nome, funcao in sorted(globals().items()):
        if nome.startswith("test_") and callable(funcao):
            try:
                funcao()
                print(f"OK   {nome}")
            except AssertionError as erro:
                falhas += 1
                print(f"FALHOU {nome}: {erro}")
    print("\ntodos passaram" if not falhas else f"\n{falhas} teste(s) falharam")
    sys.exit(1 if falhas else 0)
