"""
gui/panel_archivados.py — Panel lateral derecho.

Dos secciones en pestañas:
  · ARCHIVADOS  — expedientes descartados con botón RECUPERAR
  · CARTAS      — comunicaciones del asesino recibidas, releer al pulsar
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea,
    QSizePolicy, QDialog
)
from PySide6.QtCore import Qt, Signal

from core.partida import Partida
from core.crimen import Crimen
from gui.estilos import *


class PanelArchivados(QWidget):
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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Pestañas ──────────────────────────────────────
        self._tab_actual = "archivados"
        tabs = QWidget()
        tabs.setStyleSheet(f"background: {GRIS_OSCURO}; border: none;")
        tabs_lay = QHBoxLayout(tabs)
        tabs_lay.setContentsMargins(0, 0, 0, 0)
        tabs_lay.setSpacing(0)

        self._btn_tab_arch  = self._boton_tab("ARCHIVADOS", "archivados")
        self._btn_tab_carta = self._boton_tab("CARTAS ✉",  "cartas")
        tabs_lay.addWidget(self._btn_tab_arch)
        tabs_lay.addWidget(self._btn_tab_carta)
        layout.addWidget(tabs)

        sep = QFrame()
        sep.setStyleSheet(f"background: {GRIS_BORDE}; max-height: 1px; border: none;")
        layout.addWidget(sep)

        # ── Contenedor de contenido ───────────────────────
        self._contenido = QWidget()
        self._contenido.setStyleSheet("background: transparent; border: none;")
        self._contenido_layout = QVBoxLayout(self._contenido)
        self._contenido_layout.setContentsMargins(12, 10, 12, 12)
        self._contenido_layout.setSpacing(6)
        layout.addWidget(self._contenido, stretch=1)

        self._actualizar_tab()

    def _boton_tab(self, texto: str, nombre: str) -> QPushButton:
        btn = QPushButton(texto)
        btn.setFixedHeight(28)
        btn.setCheckable(True)
        btn.setChecked(nombre == self._tab_actual)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {GRIS_TEXTO};
                border: none;
                border-bottom: 2px solid transparent;
                font-size: 8px;
                letter-spacing: 2px;
                font-family: {MONO};
            }}
            QPushButton:checked {{
                color: {AMBAR};
                border-bottom: 2px solid {AMBAR};
            }}
            QPushButton:hover:!checked {{ color: {BLANCO}; }}
        """)
        btn.clicked.connect(lambda: self._cambiar_tab(nombre))
        return btn

    def _cambiar_tab(self, nombre: str):
        self._tab_actual = nombre
        self._btn_tab_arch.setChecked(nombre == "archivados")
        self._btn_tab_carta.setChecked(nombre == "cartas")
        self._actualizar_tab()

    def _actualizar_tab(self):
        # Limpiar contenido anterior
        while self._contenido_layout.count():
            item = self._contenido_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self._tab_actual == "archivados":
            self._construir_archivados()
        else:
            self._construir_cartas()

    # ── Pestaña archivados ────────────────────────────────────────────── #

    def _construir_archivados(self):
        lay = self._contenido_layout

        nota = QLabel("Recuperar cuenta\ncomo acción del día.")
        nota.setStyleSheet(f"color: {GRIS_BORDE}; font-size: 8px; border: none;")
        lay.addWidget(nota)

        archivados = self.partida.crimenes_archivados()

        if not archivados:
            lbl = QLabel("—  ninguno")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color: {GRIS_BORDE}; font-size: 10px; border: none;")
            lay.addWidget(lbl)
        else:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setStyleSheet("border: none; background: transparent;")
            cont = QWidget()
            cont.setStyleSheet("background: transparent; border: none;")
            cont_lay = QVBoxLayout(cont)
            cont_lay.setContentsMargins(0, 0, 0, 0)
            cont_lay.setSpacing(4)

            for idx, crimen in archivados:
                fila = _FilaArchivado(idx, crimen, self.partida.resuelta)
                fila.accion_recuperar.connect(self.accion_recuperar)
                cont_lay.addWidget(fila)
            cont_lay.addStretch()

            scroll.setWidget(cont)
            lay.addWidget(scroll)

        lay.addStretch()

    # ── Pestaña cartas ────────────────────────────────────────────────── #

    def _construir_cartas(self):
        lay = self._contenido_layout
        cartas = self.partida.cartas_asesino

        if not cartas:
            lbl_vacio = QLabel("Ninguna comunicación\nrecibida aún.")
            lbl_vacio.setAlignment(Qt.AlignCenter)
            lbl_vacio.setWordWrap(True)
            lbl_vacio.setStyleSheet(f"color: {GRIS_BORDE}; font-size: 10px; border: none;")
            lay.addWidget(lbl_vacio)
        else:
            nota = QLabel(f"{len(cartas)} comunicación{'es' if len(cartas)>1 else ''} recibida{'s' if len(cartas)>1 else ''}.")
            nota.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 8px; border: none;")
            lay.addWidget(nota)
            lay.addSpacing(4)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setStyleSheet("border: none; background: transparent;")
            cont = QWidget()
            cont.setStyleSheet("background: transparent; border: none;")
            cont_lay = QVBoxLayout(cont)
            cont_lay.setContentsMargins(0, 0, 0, 0)
            cont_lay.setSpacing(4)

            for dia, asunto, cuerpo in reversed(cartas):
                fila = _FilaCarta(dia, asunto, cuerpo)
                cont_lay.addWidget(fila)
            cont_lay.addStretch()

            scroll.setWidget(cont)
            lay.addWidget(scroll)

        lay.addStretch()

    # ── API pública ───────────────────────────────────────────────────── #

    def actualizar(self):
        self._actualizar_tab()
        # Actualizar badge de cartas en el botón
        n = len(self.partida.cartas_asesino)
        self._btn_tab_carta.setText(f"CARTAS ✉" if n == 0 else f"CARTAS ✉ ({n})")


# ── Widgets de fila ───────────────────────────────────────────────────── #

class _FilaArchivado(QFrame):
    accion_recuperar = Signal(int)

    def __init__(self, idx: int, crimen: Crimen, resuelta: bool, parent=None):
        super().__init__(parent)
        self.idx = idx
        self.setStyleSheet(f"""
            QFrame {{ background: {GRIS_OSCURO}; border: 1px solid {GRIS_BORDE}; border-radius: 2px; }}
            QLabel {{ border: none; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(3)

        lbl_num = QLabel(f"#{idx + 1:02d}")
        lbl_num.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 9px; letter-spacing: 1px;")
        layout.addWidget(lbl_num)

        n_rev = len(crimen.campos_revelados)
        if n_rev > 0:
            vista = crimen.vista()
            conocidos = [v for v in vista.values() if v != "???"][:2]
            resumen = " · ".join(conocidos) if conocidos else "—"
        else:
            resumen = "Sin investigar"

        lbl_res = QLabel(resumen)
        lbl_res.setWordWrap(True)
        lbl_res.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 9px;")
        layout.addWidget(lbl_res)

        if not resuelta:
            btn = QPushButton("↺ RECUPERAR")
            btn.setFixedHeight(22)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {AMBAR_OSCURO};
                    border: 1px solid {AMBAR_OSCURO}; border-radius: 2px;
                    font-size: 8px; letter-spacing: 1px; font-family: {MONO};
                }}
                QPushButton:hover {{ color: {AMBAR}; border-color: {AMBAR}; }}
            """)
            btn.clicked.connect(lambda: self.accion_recuperar.emit(self.idx))
            layout.addWidget(btn)


class _FilaCarta(QFrame):
    """Fila compacta de una carta del asesino con botón para releerla."""

    def __init__(self, dia: int, asunto: str, cuerpo: str, parent=None):
        super().__init__(parent)
        self.dia    = dia
        self.asunto = asunto
        self.cuerpo = cuerpo

        self.setStyleSheet(f"""
            QFrame {{
                background: #1a1508;
                border: 1px solid {AMBAR_OSCURO};
                border-radius: 2px;
            }}
            QLabel {{ border: none; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(3)

        lbl_dia = QLabel(f"DÍA {dia}")
        lbl_dia.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 8px; letter-spacing: 1px;")
        layout.addWidget(lbl_dia)

        lbl_asunto = QLabel(asunto)
        lbl_asunto.setWordWrap(True)
        lbl_asunto.setStyleSheet(f"color: {AMBAR}; font-size: 9px; font-style: italic;")
        layout.addWidget(lbl_asunto)

        btn = QPushButton("LEER")
        btn.setFixedHeight(20)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {AMBAR_OSCURO};
                border: 1px solid {AMBAR_OSCURO}; border-radius: 2px;
                font-size: 8px; letter-spacing: 2px; font-family: {MONO};
            }}
            QPushButton:hover {{ color: {AMBAR}; border-color: {AMBAR}; }}
        """)
        btn.clicked.connect(self._releer)
        layout.addWidget(btn)

    def _releer(self):
        """Abre la carta en un diálogo de lectura."""
        from gui.main_window import _dialogo_carta_asesino
        ventana = self.window()
        _dialogo_carta_asesino(ventana, self.asunto, self.cuerpo)
