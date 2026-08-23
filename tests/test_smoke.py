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


def test_preview_nao_mostra_html():
    """A lista de notas mostra texto legivel, nunca as tags."""
    nota = Note(
        title="Roadmap",
        content="<h1>Roadmap</h1><p>Metas do trimestre:</p><ul><li>Fechar a ponte</li></ul>",
    )
    preview = nota.preview(60)
    assert "<" not in preview and ">" not in preview
    assert preview.startswith("Roadmap Metas do trimestre")


def test_preview_resolve_entidades_e_nao_cola_palavras():
    nota = Note(title="t", content="<p>Caf&eacute;</p><p>azeite</p>")
    assert nota.plain_content() == "Café azeite"


def test_preview_corta_em_palavra_inteira():
    nota = Note(title="t", content="<p>" + "palavra " * 30 + "</p>")
    preview = nota.preview(60)
    assert preview.endswith("...")
    assert len(preview) <= 63
    assert not preview[:-3].endswith("palav")


def test_preview_de_codigo_fica_intacto():
    nota = Note(title="t", content="if a < b and b > c:\n    pass", is_code=True)
    assert "<" in nota.plain_content()


def test_busca_ignora_as_tags_html():
    """Procurar por 'li' ou 'div' nao pode casar com toda nota de texto rico."""
    _, window = _app_and_window()
    window.note_list.set_notes([
        Note(title="Compras", content="<ul><li>Cafe</li></ul>"),
        Note(title="Codigo", content="x = 1", is_code=True),
    ])

    window.note_list.search_notes("li")
    assert window.note_list.filtered_notes == [], "a busca casou com a tag <li>"

    window.note_list.search_notes("cafe")
    assert len(window.note_list.filtered_notes) == 1


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
