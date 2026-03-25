"""
gui/sala_mando.py — Panel modal de la sala de mando.

El jugador ve sus sospechosos marcados, los intentos restantes
y puede formalizar la acusación.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt

from core.partida import Partida, ResultadoAcusacion
from gui.estilos import *


class SalaMando(QDialog):
    """
    Diálogo modal de la sala de mando.
    El resultado de la acusación se lee en self.resultado tras exec().
    """

    def __init__(self, partida: Partida, parent=None):
        super().__init__(parent)
        self.partida   = partida
        self.resultado = None
        self._construir()

    def _construir(self):
        self.setWindowTitle("SALA DE MANDO")
        self.setModal(True)
        self.setFixedWidth(420)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {GRIS_OSCURO};
                border: 1px solid {GRIS_BORDE};
                font-family: {MONO};
            }}
            QLabel {{ border: none; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        # ── Título ────────────────────────────────────────
        titulo = QLabel("SALA DE MANDO")
        titulo.setStyleSheet(f"""
            color: {AMBAR};
            font-size: 16px;
            letter-spacing: 6px;
            font-family: {MONO};
        """)
        layout.addWidget(titulo)

        sub = QLabel("FORMALIZACIÓN DE ACUSACIÓN")
        sub.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 9px; letter-spacing: 3px;")
        layout.addWidget(sub)

        sep = QFrame()
        sep.setStyleSheet(separador_h())
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # ── Intentos ──────────────────────────────────────
        intentos_layout = QHBoxLayout()
        lbl_int_key = QLabel("INTENTOS DISPONIBLES")
        lbl_int_key.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 10px; letter-spacing: 1px;")

        color_int = VERDE if self.partida.intentos > 1 else ROJO
        lbl_int_val = QLabel(f"{self.partida.intentos} / {self.partida.intentos_max}")
        lbl_int_val.setStyleSheet(f"""
            color: {color_int};
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 2px;
        """)
        lbl_int_val.setAlignment(Qt.AlignRight)

        intentos_layout.addWidget(lbl_int_key)
        intentos_layout.addStretch()
        intentos_layout.addWidget(lbl_int_val)
        layout.addLayout(intentos_layout)

        # Advertencia si es el último intento
        if self.partida.intentos == 1:
            aviso = QLabel("⚠  Este es tu último intento. Si fallas, el caso queda abierto.")
            aviso.setWordWrap(True)
            aviso.setStyleSheet(f"""
                color: {ROJO};
                font-size: 9px;
                line-height: 1.4;
            """)
            layout.addWidget(aviso)

        sep2 = QFrame()
        sep2.setStyleSheet(separador_h())
        sep2.setFixedHeight(1)
        layout.addWidget(sep2)

        # ── Sospechosos marcados ──────────────────────────
        lbl_sosp = QLabel("EXPEDIENTES ACUSADOS")
        lbl_sosp.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 9px; letter-spacing: 2px;")
        layout.addWidget(lbl_sosp)

        sospechosos = self.partida.sospechosos()

        if not sospechosos:
            lbl_ninguno = QLabel(
                "No has marcado ningún expediente como sospechoso.\n"
                "Vuelve al mapa y marca los crímenes del asesino."
            )
            lbl_ninguno.setWordWrap(True)
            lbl_ninguno.setStyleSheet(f"color: {ROJO}; font-size: 10px; line-height: 1.5;")
            layout.addWidget(lbl_ninguno)
            self._puede_acusar = False
        else:
            for idx, crimen in sospechosos:
                fila = _FilaSospechoso(idx, crimen)
                layout.addWidget(fila)
            self._puede_acusar = True

        sep3 = QFrame()
        sep3.setStyleSheet(separador_h())
        sep3.setFixedHeight(1)
        layout.addWidget(sep3)

        # ── Nota recordatorio ──────────────────────────────
        nota = QLabel(
            "El asesino comparte exactamente 3 rasgos en todos sus crímenes.\n"
            "Si tu acusación falla, aparecerá un nuevo crimen en el mapa."
        )
        nota.setWordWrap(True)
        nota.setStyleSheet(f"color: {GRIS_BORDE}; font-size: 9px; line-height: 1.5;")
        layout.addWidget(nota)

        # ── Botones ───────────────────────────────────────
        btns = QHBoxLayout()
        btns.setSpacing(10)

        btn_cancelar = QPushButton("VOLVER AL MAPA")
        btn_cancelar.setFixedHeight(34)
        btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {GRIS_TEXTO};
                border: 1px solid {GRIS_BORDE};
                border-radius: 2px;
                font-size: 10px;
                letter-spacing: 2px;
                font-family: {MONO};
            }}
            QPushButton:hover {{ color: {BLANCO}; border-color: {GRIS_MEDIO}; }}
        """)
        btn_cancelar.clicked.connect(self.reject)

        self.btn_acusar = QPushButton("⚑  FORMALIZAR ACUSACIÓN")
        self.btn_acusar.setFixedHeight(34)
        self.btn_acusar.setEnabled(self._puede_acusar)
        self.btn_acusar.setStyleSheet(f"""
            QPushButton {{
                background-color: {ROJO_OSCURO};
                color: {BLANCO};
                border: 1px solid {ROJO};
                border-radius: 2px;
                font-size: 10px;
                letter-spacing: 2px;
                font-family: {MONO};
            }}
            QPushButton:hover {{ background-color: {ROJO}; }}
            QPushButton:disabled {{
                background: {GRIS_PANEL};
                color: {GRIS_TEXTO};
                border-color: {GRIS_BORDE};
            }}
        """)
        self.btn_acusar.clicked.connect(self._on_acusar)

        btns.addWidget(btn_cancelar)
        btns.addWidget(self.btn_acusar)
        layout.addLayout(btns)

    def _on_acusar(self):
        self.resultado = self.partida.acusar()
        self.accept()


class _FilaSospechoso(QFrame):
    """Fila compacta mostrando un sospechoso en la sala de mando."""

    def __init__(self, idx: int, crimen, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {ROJO_OSCURO};
                border: 1px solid {ROJO};
                border-radius: 2px;
            }}
            QLabel {{ border: none; }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)

        lbl_num = QLabel(f"⚑  EXPEDIENTE #{idx + 1:02d}")
        lbl_num.setStyleSheet(f"color: {BLANCO}; font-size: 10px; letter-spacing: 1px;")

        # Mostrar primeros atributos conocidos
        vista = crimen.vista()
        conocidos = [v for v in vista.values() if v != "???"][:2]
        resumen = "  ·  ".join(conocidos) if conocidos else "Sin investigar"

        lbl_res = QLabel(resumen)
        lbl_res.setStyleSheet(f"color: {ROJO_CLARO}; font-size: 9px;")
        lbl_res.setAlignment(Qt.AlignRight)

        layout.addWidget(lbl_num)
        layout.addStretch()
        layout.addWidget(lbl_res)
