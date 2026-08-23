# -*- coding: utf-8 -*-

"""Desenho de um item da lista de notas.

Cada item tem tres informacoes com pesos diferentes: o titulo, uma previa do
conteudo e a data. Com um QListWidgetItem comum as tres saem no mesmo tamanho e
na mesma cor, e o olho nao encontra o titulo. Aqui elas sao pintadas com
QPainter, cada uma com seu peso, alem do fundo arredondado de selecao e hover.
"""

from PyQt6.QtWidgets import QStyledItemDelegate, QStyle
from PyQt6.QtGui import QFont, QPen, QColor, QPainter, QPalette
from PyQt6.QtCore import Qt, QSize, QRect


class NoteItemDelegate(QStyledItemDelegate):
    """Pinta um item da lista de notas."""

    MARGEM_X = 12
    MARGEM_Y = 9
    ESPACO = 3
    RAIO = 8

    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme

    # ------------------------------------------------------------------ #

    def _fontes(self, base: QFont):
        titulo = QFont(base)
        titulo.setBold(True)
        titulo.setPointSizeF(base.pointSizeF() + 0.5)

        previa = QFont(base)

        data = QFont(base)
        data.setPointSizeF(max(6.5, base.pointSizeF() - 1.5))

        return titulo, previa, data

    def sizeHint(self, option, index):
        titulo, previa, data = self._fontes(option.font)
        altura = (
            self.MARGEM_Y * 2
            + option.fontMetrics.height()  # linha do titulo
            + self.ESPACO
            + option.fontMetrics.height()  # linha da previa
            + self.ESPACO
            + option.fontMetrics.height() - 3  # linha da data, menor
        )
        return QSize(option.rect.width(), altura)

    def paint(self, painter: QPainter, option, index):
        dados = index.data(Qt.ItemDataRole.UserRole + 1)
        if not isinstance(dados, dict):
            # Itens sem dados estruturados (ex.: "No notes found") seguem o
            # desenho padrao.
            super().paint(painter, option, index)
            return

        # As cores vem da palette que o estilo esta usando, nao de um
        # dicionario proprio: assim o item acompanha o tema do sistema quando
        # a aplicacao esta no estilo nativo.
        paleta = option.palette
        Role = QPalette.ColorRole
        fundo = paleta.color(Role.Base)
        texto = paleta.color(Role.Text)
        realce = paleta.color(Role.Highlight)

        selecionado = bool(option.state & QStyle.StateFlag.State_Selected)
        sob_o_mouse = bool(option.state & QStyle.StateFlag.State_MouseOver)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # --- fundo -----------------------------------------------------
        area = option.rect.adjusted(4, 2, -4, -2)
        if selecionado:
            painter.setBrush(realce)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(area, self.RAIO, self.RAIO)
            cor_titulo = paleta.color(Role.HighlightedText)
            cor_previa = cor_titulo
            cor_data = cor_titulo
        else:
            if sob_o_mouse:
                painter.setBrush(self.theme.mix(fundo, realce, 0.18))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(area, self.RAIO, self.RAIO)
            cor_titulo = texto
            cor_previa = self.theme.mix(texto, fundo, 0.42)
            cor_data = self.theme.mix(texto, fundo, 0.62)

        # --- texto -----------------------------------------------------
        titulo_fonte, previa_fonte, data_fonte = self._fontes(option.font)
        x = area.left() + self.MARGEM_X
        largura = area.width() - self.MARGEM_X * 2
        y = area.top() + self.MARGEM_Y

        def linha(texto, fonte, cor, altura_extra=0):
            nonlocal y
            painter.setFont(fonte)
            painter.setPen(QPen(cor))
            metrica = painter.fontMetrics()
            altura = metrica.height()
            elidido = metrica.elidedText(
                texto, Qt.TextElideMode.ElideRight, largura
            )
            painter.drawText(
                QRect(x, y, largura, altura),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                elidido,
            )
            y += altura + self.ESPACO + altura_extra

        linha(dados.get("titulo") or "Untitled", titulo_fonte, cor_titulo)
        linha(dados.get("previa", ""), previa_fonte, cor_previa)
        linha(dados.get("data", ""), data_fonte, cor_data)

        # --- marca de nota de codigo -----------------------------------
        # Uma barrinha no canto, no lugar do prefixo "[Code] " que roubava
        # espaco do titulo.
        if dados.get("is_code"):
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(cor_titulo if selecionado else realce)
            painter.drawRoundedRect(
                QRect(area.left() + 4, area.top() + self.MARGEM_Y, 3, 16), 1.5, 1.5
            )

        painter.restore()
