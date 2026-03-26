"""
gui/panel_expediente.py — Panel central con el detalle del crimen seleccionado.

Muestra los 5 atributos (revelados o ???) y los botones de acción:
  · INVESTIGAR  → revela atributos (cuenta como acción)
  · SOSPECHOSO  → marca/desmarca para la acusación
  · ARCHIVAR    → envía a la reserva
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from core.crimen import Crimen, ATRIBUTOS, ETIQUETAS
from core.partida import Partida
from gui.estilos import *


class PanelExpediente(QWidget):
    """
    Panel que muestra el expediente del crimen seleccionado.
    La investigación se hace desde el panel de mano (cartas).
    """
    accion_sospechoso = Signal(int)   # idx
    accion_archivar   = Signal(int)   # idx

    def __init__(self, partida: Partida, parent=None):
        super().__init__(parent)
        self.partida   = partida
        self._idx_actual: int | None = None
        self._construir()
        self.mostrar_vacio()

    def _construir(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {GRIS_PANEL};
                border: 1px solid {GRIS_BORDE};
                border-radius: 2px;
            }}
        """)
        self.setFixedWidth(270)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # ── Cabecera ──────────────────────────────────────
        self.lbl_numero = QLabel("EXPEDIENTE")
        self.lbl_numero.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;
            letter-spacing: 3px;
            border: none;
        """)
        layout.addWidget(self.lbl_numero)

        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet(f"""
            color: {AMBAR};
            font-size: 10px;
            letter-spacing: 2px;
            border: none;
        """)
        layout.addWidget(self.lbl_estado)

        sep = QFrame()
        sep.setStyleSheet(separador_h())
        sep.setFixedHeight(1)
        layout.addWidget(sep)
        layout.addSpacing(4)

        # ── Atributos ─────────────────────────────────────
        self.filas_attr: dict[str, tuple[QLabel, QLabel]] = {}
        for attr in ATRIBUTOS:
            fila = QHBoxLayout()
            fila.setSpacing(8)

            lbl_key = QLabel(ETIQUETAS[attr])
            lbl_key.setFixedWidth(80)
            lbl_key.setStyleSheet(f"""
                color: {GRIS_TEXTO};
                font-size: 10px;
                border: none;
            """)

            lbl_val = QLabel("—")
            lbl_val.setWordWrap(True)
            lbl_val.setStyleSheet(f"""
                color: {GRIS_BORDE};
                font-size: 11px;
                font-weight: bold;
                border: none;
            """)

            fila.addWidget(lbl_key)
            fila.addWidget(lbl_val, stretch=1)
            layout.addLayout(fila)
            self.filas_attr[attr] = (lbl_key, lbl_val)

        layout.addSpacing(8)

        sep2 = QFrame()
        sep2.setStyleSheet(separador_h())
        sep2.setFixedHeight(1)
        layout.addWidget(sep2)
        layout.addSpacing(6)

        # ── Nota sobre cartas ──────────────────────────────
        lbl_nota = QLabel("Usa las cartas de la\nmano para investigar.")
        lbl_nota.setStyleSheet(f"""
            color: {GRIS_BORDE};
            font-size: 9px;

            border: none;
        """)
        layout.addWidget(lbl_nota)
        layout.addSpacing(6)

        self.btn_sospechoso = QPushButton("MARCAR SOSPECHOSO")
        self.btn_sospechoso.setFixedHeight(32)
        self.btn_sospechoso.setCheckable(True)
        self.btn_sospechoso.setStyleSheet(f"""
            QPushButton {{
                background: {GRIS_OSCURO};
                color: {GRIS_TEXTO};
                border: 1px solid {GRIS_BORDE};
                border-radius: 2px;
                font-size: 10px;
                letter-spacing: 2px;
                font-family: {MONO};
            }}
            QPushButton:checked {{
                background: {ROJO_OSCURO};
                color: {BLANCO};
                border-color: {ROJO};
            }}
            QPushButton:hover:!checked {{ border-color: {GRIS_MEDIO}; color: {BLANCO}; }}
            QPushButton:disabled {{ color: {GRIS_BORDE}; border-color: {GRIS_BORDE}; }}
        """)
        self.btn_sospechoso.clicked.connect(self._on_sospechoso)
        layout.addWidget(self.btn_sospechoso)

        self.btn_archivar = QPushButton("ARCHIVAR")
        self.btn_archivar.setFixedHeight(28)
        self.btn_archivar.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {GRIS_TEXTO};
                border: 1px solid {GRIS_BORDE};
                border-radius: 2px;
                font-size: 9px;
                letter-spacing: 2px;
                font-family: {MONO};
            }}
            QPushButton:hover {{ color: {BLANCO}; border-color: {GRIS_MEDIO}; }}
            QPushButton:disabled {{ color: {GRIS_BORDE}; border-color: {GRIS_BORDE}; }}
        """)
        self.btn_archivar.clicked.connect(self._on_archivar)
        layout.addWidget(self.btn_archivar)

        layout.addStretch()

    # ── API pública ───────────────────────────────────────────────────── #

    def mostrar_crimen(self, idx: int):
        """Carga y muestra el expediente del crimen idx."""
        self._idx_actual = idx
        crimen = self.partida.crimen(idx)

        # Cabecera
        self.lbl_numero.setText(f"EXPEDIENTE #{idx + 1:02d}")
        n_rev = len(crimen.campos_revelados)
        if crimen.sospechoso:
            self.lbl_estado.setText("⚑ SOSPECHOSO")
            self.lbl_estado.setStyleSheet(f"color: {ROJO}; font-size: 10px; letter-spacing: 2px; border: none;")
        elif n_rev == 0:
            self.lbl_estado.setText("● SIN INVESTIGAR")
            self.lbl_estado.setStyleSheet(f"color: {ROJO}; font-size: 10px; letter-spacing: 2px; border: none;")
        elif n_rev < 5:
            self.lbl_estado.setText(f"◑ PARCIAL  {n_rev}/5")
            self.lbl_estado.setStyleSheet(f"color: {AMBAR}; font-size: 10px; letter-spacing: 2px; border: none;")
        else:
            self.lbl_estado.setText("○ COMPLETO")
            self.lbl_estado.setStyleSheet(f"color: {VERDE}; font-size: 10px; letter-spacing: 2px; border: none;")

        # Atributos
        vista = crimen.vista()
        for attr, (lbl_k, lbl_v) in self.filas_attr.items():
            val = vista[attr]
            if val == "???":
                lbl_v.setText("???")
                lbl_v.setStyleSheet(f"""
                    color: {AMBAR};
                    font-size: 11px;
                    font-weight: bold;
                    letter-spacing: 3px;
                    border: none;
                """)
            else:
                lbl_v.setText(val)
                # Verde si recién revelado (en campos_revelados)
                if attr in crimen.campos_revelados:
                    color_val = VERDE if n_rev == len(ATRIBUTOS) else BLANCO
                else:
                    color_val = BLANCO
                lbl_v.setStyleSheet(f"""
                    color: {color_val};
                    font-size: 11px;
                    font-weight: bold;
                    border: none;
                """)

        # Botones

        self.btn_sospechoso.setChecked(crimen.sospechoso)
        self.btn_sospechoso.setText(
            "DESMARCAR SOSPECHOSO" if crimen.sospechoso else "MARCAR SOSPECHOSO"
        )
        self.btn_sospechoso.setEnabled(not self.partida.resuelta)

        self.btn_archivar.setEnabled(
            not crimen.sospechoso and not self.partida.resuelta
        )

        # Mostrar el widget
        self.setVisible(True)

    def mostrar_vacio(self):
        """Estado inicial: ningún crimen seleccionado."""
        self._idx_actual = None
        self.lbl_numero.setText("EXPEDIENTE")
        self.lbl_estado.setText("")
        for attr, (lbl_k, lbl_v) in self.filas_attr.items():
            lbl_v.setText("—")
            lbl_v.setStyleSheet(f"color: {GRIS_BORDE}; font-size: 11px; border: none;")
        self.btn_sospechoso.setEnabled(False)
        self.btn_archivar.setEnabled(False)
        self.btn_sospechoso.setText("MARCAR SOSPECHOSO")

    def refrescar(self):
        """Refresca sin cambiar el crimen seleccionado."""
        if self._idx_actual is not None:
            self.mostrar_crimen(self._idx_actual)

    # ── Handlers ─────────────────────────────────────────────────────── #

    def _on_sospechoso(self):
        if self._idx_actual is not None:
            self.accion_sospechoso.emit(self._idx_actual)

    def _on_archivar(self):
        if self._idx_actual is not None:
            self.accion_archivar.emit(self._idx_actual)