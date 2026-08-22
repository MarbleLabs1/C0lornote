#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""C0lorNote - ponto de entrada da aplicacao.

Aplicacao de notas em PyQt6 com texto rico, editor de codigo com realce de
sintaxe e tres temas (Matrix, Dreamcore, Minimalist).
"""

import os
import sys

# Garante que o pacote src seja importavel quando executado direto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.utils.logger import setup_logger


def main():
    """Cria a aplicacao Qt, abre a janela principal e roda o loop de eventos."""
    logger = setup_logger()
    logger.info("Iniciando C0lorNote")

    app = QApplication(sys.argv)
    app.setApplicationName("C0lorNote")
    app.setOrganizationName("MarbleCeo")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
