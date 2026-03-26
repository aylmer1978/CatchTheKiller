"""
gui/panel_mano.py — Panel inferior con la mano de cartas del jugador.

Muestra las 3 cartas en mano como widgets visuales tipo carta.
El jugador primero selecciona un crimen en el mapa, luego hace
clic en una carta para jugarla sobre ese crimen.

Acciones disponibles:
  · Clic en carta    → jugar sobre el crimen seleccionado
  · Clic en ✕ carta  → descarte gratuito (una vez por turno)
  · PASAR TURNO      → acción sin carta si ninguna es jugable
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont

from core.carta import Carta, TipoCarta, TIPOS_ATRIBUTO
from core.partida import Partida
from gui.estilos import *

# Color de acento por tipo de carta
COLOR_TIPO = {
    TipoCarta.INVESTIGAR_EXPEDIENTE: AMBAR,
    TipoCarta.INVESTIGAR_CASO:       VERDE,
    TipoCarta.ATRIBUTO_LUGAR:        "#5b9bd5",
    TipoCarta.ATRIBUTO_FRANJA:       "#9b59b6",
    TipoCarta.ATRIBUTO_ARMA:         ROJO_CLARO,
    TipoCarta.ATRIBUTO_VICTIMA:      "#e67e22",
    TipoCarta.ATRIBUTO_OTROS:        "#c0392b",
}


class WidgetCarta(QFrame):
    """
    Widget visual de una carta individual.
    Emite:
      · jugada(idx_mano)     — clic principal para jugar
      · descartada(idx_mano) — clic en botón X
    """
    jugada     = Signal(int)
    descartada = Signal(int)

    def __init__(self, idx_mano: int, carta: Carta, jugable: bool,
                 puede_descartar: bool, parent=None):
        super().__init__(parent)
        self.idx_mano = idx_mano
        self.carta    = carta
        self._jugable = jugable
        self._seleccionada = False
        self._construir(puede_descartar)
        self._aplicar_estilo()

    def _construir(self, puede_descartar: bool):
        self.setFixedSize(160, 130)
        self.setCursor(Qt.PointingHandCursor if self._jugable else Qt.ArrowCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 8)
        layout.setSpacing(4)

        # ── Fila superior: icono + botón descarte ──────────
        fila_top = QHBoxLayout()
        fila_top.setContentsMargins(0, 0, 0, 0)

        lbl_icono = QLabel(self.carta.icono)
        lbl_icono.setStyleSheet("font-size: 18px; border: none; background: transparent;")
        fila_top.addWidget(lbl_icono)
        fila_top.addStretch()

        if puede_descartar:
            btn_x = QPushButton("✕")
            btn_x.setFixedSize(18, 18)
            btn_x.setToolTip("Descartar carta (gratis, una vez por turno)")
            btn_x.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {GRIS_TEXTO};
                    border: 1px solid {GRIS_BORDE};
                    border-radius: 9px;
                    font-size: 9px;
                    padding: 0;
                }}
                QPushButton:hover {{
                    color: {BLANCO};
                    border-color: {GRIS_MEDIO};
                }}
            """)
            btn_x.clicked.connect(lambda: self.descartada.emit(self.idx_mano))
            fila_top.addWidget(btn_x)

        layout.addLayout(fila_top)

        # ── Nombre ─────────────────────────────────────────
        color_acento = COLOR_TIPO.get(self.carta.tipo, AMBAR)
        lbl_nombre = QLabel(self.carta.nombre)
        lbl_nombre.setWordWrap(True)
        lbl_nombre.setStyleSheet(f"""
            color: {color_acento if self._jugable else GRIS_TEXTO};
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 0px;
            border: none;
            background: transparent;
        """)
        layout.addWidget(lbl_nombre)

        # ── Descripción ────────────────────────────────────
        lbl_desc = QLabel(self.carta.descripcion)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;

            border: none;
            background: transparent;
        """)
        layout.addWidget(lbl_desc)
        layout.addStretch()

        # ── Indicador de estado ────────────────────────────
        if not self._jugable:
            lbl_no = QLabel("NO JUGABLE")
            lbl_no.setStyleSheet(f"""
                color: {GRIS_BORDE};
                font-size: 8px;
                letter-spacing: 1px;
                border: none;
                background: transparent;
            """)
            layout.addWidget(lbl_no)

    def _aplicar_estilo(self):
        color_acento = COLOR_TIPO.get(self.carta.tipo, AMBAR)

        if self._seleccionada:
            borde = BLANCO
            fondo = f"#252530"
            borde_w = "2px"
        elif self._jugable:
            borde = color_acento
            fondo = GRIS_PANEL
            borde_w = "1px"
        else:
            borde = GRIS_BORDE
            fondo = GRIS_OSCURO
            borde_w = "1px"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {fondo};
                border: {borde_w} solid {borde};
                border-radius: 4px;
            }}
        """)

    def seleccionar(self, estado: bool):
        self._seleccionada = estado
        self._aplicar_estilo()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._jugable:
            self.jugada.emit(self.idx_mano)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        if self._jugable and not self._seleccionada:
            color_acento = COLOR_TIPO.get(self.carta.tipo, AMBAR)
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: #1e1e24;
                    border: 1px solid {color_acento};
                    border-radius: 4px;
                }}
            """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._aplicar_estilo()
        super().leaveEvent(event)


class PanelMano(QWidget):
    """
    Panel inferior con las 3 cartas en mano.
    Emite:
      · carta_jugada(idx_mano)     — el jugador quiere jugar esta carta
      · carta_descartada(idx_mano) — descarte gratuito
      · turno_pasado()             — pasar turno
    """
    carta_jugada     = Signal(int)
    carta_descartada = Signal(int)
    dia_finalizado   = Signal()

    def __init__(self, partida: Partida, parent=None):
        super().__init__(parent)
        self.partida = partida
        self._idx_crimen_sel: int | None = None
        self._idx_carta_sel:  int | None = None
        self._widgets_carta: list[WidgetCarta] = []
        self._construir()

    def _construir(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {GRIS_OSCURO};
                border-top: 1px solid {GRIS_BORDE};
            }}
        """)
        self.setFixedHeight(170)

        layout_outer = QHBoxLayout(self)
        layout_outer.setContentsMargins(16, 12, 16, 12)
        layout_outer.setSpacing(16)

        # ── Etiqueta lateral ──────────────────────────────
        col_label = QVBoxLayout()
        col_label.setAlignment(Qt.AlignVCenter)

        lbl_mano = QLabel("MANO")
        lbl_mano.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;
            letter-spacing: 3px;
            border: none;
        """)
        col_label.addWidget(lbl_mano)

        self.lbl_mazo = QLabel()
        self.lbl_mazo.setStyleSheet(f"""
            color: {GRIS_BORDE};
            font-size: 8px;
            letter-spacing: 1px;
            border: none;
        """)
        col_label.addWidget(self.lbl_mazo)
        layout_outer.addLayout(col_label)

        sep_v = QFrame()
        sep_v.setFrameShape(QFrame.VLine)
        sep_v.setStyleSheet(f"background: {GRIS_BORDE}; max-width: 1px; border: none;")
        layout_outer.addWidget(sep_v)

        # ── Cartas ────────────────────────────────────────
        self._contenedor_cartas = QHBoxLayout()
        self._contenedor_cartas.setSpacing(10)
        self._contenedor_cartas.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout_outer.addLayout(self._contenedor_cartas, stretch=1)

        # ── Instrucción + finalizar día ───────────────────
        col_accion = QVBoxLayout()
        col_accion.setAlignment(Qt.AlignVCenter)
        col_accion.setSpacing(8)

        self.lbl_instruccion = QLabel("Selecciona un\nexpediente en\nel mapa primero.")
        self.lbl_instruccion.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;

            border: none;
        """)
        col_accion.addWidget(self.lbl_instruccion)

        self.lbl_estado_dia = QLabel()
        self.lbl_estado_dia.setStyleSheet(f"""
            color: {GRIS_BORDE};
            font-size: 8px;
            letter-spacing: 1px;
            border: none;
        """)
        col_accion.addWidget(self.lbl_estado_dia)

        col_accion.addSpacing(4)

        self.btn_finalizar = QPushButton(">>  FINALIZAR DIA")
        self.btn_finalizar.setFixedSize(148, 36)
        self.btn_finalizar.setToolTip("Terminar el día y reponer cartas")
        self.btn_finalizar.setStyleSheet(f"""
            QPushButton {{
                background: {AMBAR_OSCURO};
                color: {BLANCO};
                border: 1px solid {AMBAR};
                border-radius: 2px;
                font-size: 10px;
                letter-spacing: 2px;
                font-family: {MONO};
            }}
            QPushButton:hover {{ background: {AMBAR}; color: {NEGRO}; }}
            QPushButton:disabled {{ background: {GRIS_OSCURO}; color: {GRIS_BORDE};
                                    border-color: {GRIS_BORDE}; }}
        """)
        self.btn_finalizar.clicked.connect(self._on_finalizar)
        col_accion.addWidget(self.btn_finalizar)

        layout_outer.addLayout(col_accion)

        self.actualizar()

    # ── API pública ───────────────────────────────────────────────────── #

    def set_crimen_seleccionado(self, idx: int | None):
        """Notifica al panel qué crimen está seleccionado en el mapa."""
        self._idx_crimen_sel = idx
        self._idx_carta_sel  = None
        self.actualizar()

    def actualizar(self):
        """Reconstruye los widgets de carta según el estado actual del mazo."""
        # Limpiar cartas anteriores
        for w in self._widgets_carta:
            self._contenedor_cartas.removeWidget(w)
            w.deleteLater()
        self._widgets_carta.clear()

        puede_desc = self.partida.mazo.puede_descartar() and not self.partida.resuelta

        for i, carta in enumerate(self.partida.mazo.mano):
            jugable = self._es_jugable(i)
            w = WidgetCarta(i, carta, jugable, puede_desc and not self.partida.resuelta)
            w.jugada.connect(self._on_carta_jugada)
            w.descartada.connect(self._on_carta_descartada)
            if i == self._idx_carta_sel:
                w.seleccionar(True)
            self._contenedor_cartas.addWidget(w)
            self._widgets_carta.append(w)

        # Actualizar etiquetas
        m = self.partida.mazo
        self.lbl_mazo.setText(
            f"Mazo: {m.cartas_en_mazo()}  Descarte: {m.cartas_en_descarte()}"
        )

        if self._idx_crimen_sel is not None:
            hay_jugable = any(self._es_jugable(i) for i in range(len(self.partida.mazo.mano)))
            if hay_jugable:
                self.lbl_instruccion.setText("Elige una carta\npara jugar sobre\nel expediente.")
            else:
                self.lbl_instruccion.setText("Ninguna carta\nes jugable.\nDescarta o finaliza.")
        else:
            self.lbl_instruccion.setText("Selecciona un\nexpediente en\nel mapa primero.")

        # Estado del día
        jugadas_rest = self.partida.mazo.jugadas_restantes()
        descartado   = self.partida.mazo._descartado_hoy
        max_jugadas  = self.partida.mazo._max_jugadas_hoy
        max_mano     = self.partida.mazo.max_mano

        partes = []
        if jugadas_rest < max_jugadas:
            jugadas_hechas = max_jugadas - jugadas_rest
            partes.append(f"✓ {jugadas_hechas}/{max_jugadas} carta{'s' if max_jugadas>1 else ''}")
        if descartado:
            partes.append("✓ descarte")
        if max_mano != 3:
            partes.append(f"mano máx: {max_mano}")
        self.lbl_estado_dia.setText("  ".join(partes) if partes else "")

        self.btn_finalizar.setEnabled(not self.partida.resuelta)

    def _es_jugable(self, idx_carta: int) -> bool:
        """True si la carta se puede jugar en el contexto actual."""
        if self.partida.resuelta:
            return False
        if not self.partida.mazo.puede_jugar():
            return False
        from core.carta import TIPOS_INV_PARALELA
        carta = self.partida.mazo.mano[idx_carta]
        # Cartas paralelas: jugables siempre (no necesitan crimen)
        if carta.tipo in TIPOS_INV_PARALELA:
            usable, _ = self.partida.carta_usable_en(idx_carta, None)
            return usable
        # Resto: necesitan crimen seleccionado
        if self._idx_crimen_sel is None:
            return False
        usable, _ = self.partida.carta_usable_en(idx_carta, self._idx_crimen_sel)
        return usable

    # ── Handlers ─────────────────────────────────────────────────────── #

    def _on_carta_jugada(self, idx_mano: int):
        self._idx_carta_sel = idx_mano
        self.carta_jugada.emit(idx_mano)

    def _on_carta_descartada(self, idx_mano: int):
        self.carta_descartada.emit(idx_mano)

    def _on_finalizar(self):
        self.dia_finalizado.emit()
