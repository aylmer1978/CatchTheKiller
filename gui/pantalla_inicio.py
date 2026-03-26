"""
gui/pantalla_inicio.py — Pantalla de bienvenida y selección de dificultad.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal

from core.partida import Dificultad
from gui.estilos import *


class PantallaInicio(QWidget):
    """Emite señal partida_iniciada(dificultad) cuando el jugador elige."""

    partida_iniciada = Signal(object)   # Dificultad

    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        # Contenedor central
        caja = QWidget()
        caja.setFixedWidth(460)
        caja_layout = QVBoxLayout(caja)
        caja_layout.setSpacing(0)
        caja_layout.setContentsMargins(40, 40, 40, 40)

        # ── Título ────────────────────────────────────────
        titulo = QLabel("CATCH\nTHE KILLER")
        titulo.setAlignment(Qt.AlignLeft)
        titulo.setStyleSheet(f"""
            color: {AMBAR};
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 10px;

            font-family: {MONO};
        """)
        caja_layout.addWidget(titulo)
        caja_layout.addSpacing(6)

        subtitulo = QLabel("UNIDAD DE HOMICIDIOS · ANÁLISIS DE PATRONES")
        subtitulo.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;
            letter-spacing: 3px;
            font-family: {MONO};
        """)
        caja_layout.addWidget(subtitulo)
        caja_layout.addSpacing(32)

        sep = QFrame()
        sep.setStyleSheet(separador_h())
        sep.setFixedHeight(1)
        caja_layout.addWidget(sep)
        caja_layout.addSpacing(28)

        # ── Descripción ───────────────────────────────────
        desc = QLabel(
            "Se han producido múltiples homicidios en la ciudad.\n"
            "Uno de ellos es obra de un asesino en serie.\n\n"
            "Analiza los expedientes, identifica su patrón\n"
            "y deténlo antes de que actúe de nuevo.\n\n"
            "Cada acción que tomes puede costarle la vida\n"
            "a una nueva víctima."
        )
        desc.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 11px;

            font-family: {MONO};
        """)
        desc.setWordWrap(True)
        caja_layout.addWidget(desc)
        caja_layout.addSpacing(32)

        # ── Selección de dificultad ───────────────────────
        dif_label = QLabel("SELECCIONA DIFICULTAD")
        dif_label.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;
            letter-spacing: 3px;
            font-family: {MONO};
        """)
        caja_layout.addWidget(dif_label)
        caja_layout.addSpacing(12)

        dificultades = [
            (Dificultad.FACIL,   "FÁCIL",   "3 intentos de acusación"),
            (Dificultad.NORMAL,  "NORMAL",  "2 intentos de acusación"),
            (Dificultad.DIFICIL, "DIFÍCIL", "1 intento de acusación"),
        ]

        for dif, etiqueta, detalle in dificultades:
            btn = _BotonDificultad(etiqueta, detalle)
            btn.clicked.connect(lambda d=dif: self.partida_iniciada.emit(d))
            caja_layout.addWidget(btn)
            caja_layout.addSpacing(8)

        caja_layout.addSpacing(20)

        # ── Nota de pie ───────────────────────────────────
        nota = QLabel(
            "El asesino comparte exactamente 3 rasgos en todos sus crímenes.\n"
            "Cada 3 acciones, comete un nuevo homicidio."
        )
        nota.setStyleSheet(f"""
            color: {GRIS_BORDE};
            font-size: 9px;

            font-family: {MONO};
        """)
        nota.setWordWrap(True)
        caja_layout.addWidget(nota)

        layout.addWidget(caja)


class _BotonDificultad(QFrame):
    """Botón de dificultad con etiqueta y detalle."""

    clicked = Signal()

    def __init__(self, etiqueta: str, detalle: str, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{
                background: {GRIS_PANEL};
                border: 1px solid {GRIS_BORDE};
                border-radius: 2px;
            }}
            QFrame:hover {{
                border-color: {AMBAR_OSCURO};
                background: #1e1e22;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        lbl = QLabel(etiqueta)
        lbl.setStyleSheet(f"""
            color: {AMBAR};
            font-size: 12px;
            letter-spacing: 3px;
            font-family: {MONO};
            background: transparent;
            border: none;
        """)

        det = QLabel(detalle)
        det.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 10px;
            font-family: {MONO};
            background: transparent;
            border: none;
        """)
        det.setAlignment(Qt.AlignRight)

        layout.addWidget(lbl)
        layout.addStretch()
        layout.addWidget(det)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)
