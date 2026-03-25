"""
gui/panel_archivados.py — Panel lateral de crímenes archivados.

Muestra la lista de expedientes descartados por el jugador.
Cada uno tiene un botón RECUPERAR (cuenta como 1 acción).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from core.partida import Partida
from core.crimen import Crimen
from gui.estilos import *


class PanelArchivados(QWidget):
    """
    Panel lateral derecho con los expedientes archivados.
    Emite accion_recuperar(idx) al pulsar RECUPERAR.
    """
    accion_recuperar = Signal(int)

    def __init__(self, partida: Partida, parent=None):
        super().__init__(parent)
        self.partida = partida
        self._construir()

    def _construir(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {GRIS_PANEL};
                border: 1px solid {GRIS_BORDE};
                border-radius: 2px;
            }}
        """)
        self.setFixedWidth(200)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Cabecera
        cab = QLabel("ARCHIVADOS")
        cab.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;
            letter-spacing: 3px;
            border: none;
        """)
        layout.addWidget(cab)

        sep = QFrame()
        sep.setStyleSheet(separador_h())
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # Nota
        self.lbl_nota = QLabel("Recuperar cuenta\ncomo 1 acción.")
        self.lbl_nota.setStyleSheet(f"""
            color: {GRIS_BORDE};
            font-size: 8px;
            line-height: 1.4;
            border: none;
        """)
        layout.addWidget(self.lbl_nota)
        layout.addSpacing(4)

        # Área de scroll con las fichas
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll_area.setStyleSheet("border: none; background: transparent;")

        self._contenedor = QWidget()
        self._contenedor.setStyleSheet("background: transparent; border: none;")
        self._lista_layout = QVBoxLayout(self._contenedor)
        self._lista_layout.setContentsMargins(0, 0, 0, 0)
        self._lista_layout.setSpacing(6)
        self._lista_layout.addStretch()

        self._scroll_area.setWidget(self._contenedor)
        layout.addWidget(self._scroll_area)

        # Mensaje vacío
        self.lbl_vacio = QLabel("—  ninguno")
        self.lbl_vacio.setStyleSheet(f"""
            color: {GRIS_BORDE};
            font-size: 10px;
            font-style: italic;
            border: none;
        """)
        self.lbl_vacio.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_vacio)

    def actualizar(self):
        """Reconstruye la lista de archivados."""
        archivados = self.partida.crimenes_archivados()

        # Limpiar lista anterior
        while self._lista_layout.count() > 1:
            item = self._lista_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.lbl_vacio.setVisible(len(archivados) == 0)
        self._scroll_area.setVisible(len(archivados) > 0)

        for idx, crimen in archivados:
            fila = _FilaArchivado(idx, crimen, self.partida.resuelta)
            fila.accion_recuperar.connect(self.accion_recuperar)
            self._lista_layout.insertWidget(self._lista_layout.count() - 1, fila)


class _FilaArchivado(QFrame):
    """Una fila en el panel de archivados."""
    accion_recuperar = Signal(int)

    def __init__(self, idx: int, crimen: Crimen, resuelta: bool, parent=None):
        super().__init__(parent)
        self.idx = idx
        self.setStyleSheet(f"""
            QFrame {{
                background: {GRIS_OSCURO};
                border: 1px solid {GRIS_BORDE};
                border-radius: 2px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # Número
        lbl_num = QLabel(f"#{idx + 1:02d}")
        lbl_num.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;
            letter-spacing: 1px;
            border: none;
        """)
        layout.addWidget(lbl_num)

        # Resumen de atributos conocidos
        n_rev = len(crimen.campos_revelados)
        if n_rev > 0:
            vista = crimen.vista()
            resumen_partes = []
            for val in vista.values():
                if val != "???":
                    resumen_partes.append(val)
                    if len(resumen_partes) == 2:
                        break
            resumen = " · ".join(resumen_partes) if resumen_partes else "—"
        else:
            resumen = "Sin investigar"

        lbl_res = QLabel(resumen)
        lbl_res.setWordWrap(True)
        lbl_res.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;
            border: none;
        """)
        layout.addWidget(lbl_res)

        # Botón recuperar
        if not resuelta:
            btn = QPushButton("↺ RECUPERAR")
            btn.setFixedHeight(22)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {AMBAR_OSCURO};
                    border: 1px solid {AMBAR_OSCURO};
                    border-radius: 2px;
                    font-size: 8px;
                    letter-spacing: 1px;
                    font-family: {MONO};
                }}
                QPushButton:hover {{
                    color: {AMBAR};
                    border-color: {AMBAR};
                }}
            """)
            btn.clicked.connect(lambda: self.accion_recuperar.emit(self.idx))
            layout.addWidget(btn)
