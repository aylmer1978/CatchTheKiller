"""
gui/mapa_widget.py — Cuadrícula tipo distrito policial con puntos de crimen.

Cada crimen es un punto interactivo. El color y forma indica su estado:
  · Rojo pulsante  → sin investigar
  · Ámbar          → investigado parcialmente
  · Blanco         → completamente revelado
  · Rojo marcado   → sospechoso (para acusar)
  · Gris           → archivado (no visible en mapa)

El jugador hace clic en un punto para seleccionarlo.
"""

from PySide6.QtWidgets import QWidget, QSizePolicy, QToolTip
from PySide6.QtCore import Qt, Signal, QRect, QPoint, QTimer, QPointF
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont,
    QPainterPath, QRadialGradient, QLinearGradient
)

from core.partida import Partida
from core.crimen import Crimen
from gui.estilos import *

# Dimensiones de la cuadrícula
COLS  = 8
FILAS = 6

# Tamaño visual de cada celda (px)
CELDA_W = 90
CELDA_H = 70

# Radio del punto de crimen
R_NORMAL   = 10
R_HOVER    = 13
R_SELECTED = 12

# Colores de estado
COL_NUEVO      = QColor(ROJO)
COL_PARCIAL    = QColor(AMBAR)
COL_COMPLETO   = QColor(BLANCO)
COL_SOSPECHOSO = QColor(ROJO_CLARO)
COL_GRID       = QColor(GRIS_BORDE)
COL_GRID_BG    = QColor(NEGRO)
COL_FONDO      = QColor(GRIS_OSCURO)


def _color_crimen(crimen: Crimen) -> QColor:
    if crimen.sospechoso:
        return COL_SOSPECHOSO
    n = len(crimen.campos_revelados)
    if n == 0:
        return COL_NUEVO
    if n < 5:
        return COL_PARCIAL
    return COL_COMPLETO


class MapaWidget(QWidget):
    """
    Mapa de cuadrícula. Emite crimen_seleccionado(idx) al hacer clic.
    """
    crimen_seleccionado = Signal(int)   # idx en pool

    def __init__(self, partida: Partida, parent=None):
        super().__init__(parent)
        self.partida = partida
        self._hover_idx: int | None = None
        self._sel_idx:   int | None = None
        self._pulso: float = 0.0      # 0.0–1.0, para animación de puntos nuevos
        self._pulso_dir = 1

        # Timer de animación de pulso
        self._timer = QTimer(self)
        self._timer.setInterval(50)
        self._timer.timeout.connect(self._animar_pulso)
        self._timer.start()

        w = COLS  * CELDA_W + 1
        h = FILAS * CELDA_H + 1
        self.setFixedSize(w, h)
        self.setMouseTracking(True)
        self.setCursor(Qt.ArrowCursor)

    # ── Animación ─────────────────────────────────────────────────────── #

    def _animar_pulso(self):
        self._pulso += 0.07 * self._pulso_dir
        if self._pulso >= 1.0:
            self._pulso = 1.0
            self._pulso_dir = -1
        elif self._pulso <= 0.0:
            self._pulso = 0.0
            self._pulso_dir = 1
        self.update()

    # ── Coordenadas ───────────────────────────────────────────────────── #

    def _pos_a_pixel(self, col: int, fila: int) -> QPoint:
        x = col * CELDA_W + CELDA_W // 2
        y = fila * CELDA_H + CELDA_H // 2
        return QPoint(x, y)

    def _pixel_a_idx(self, px: int, py: int) -> int | None:
        """Devuelve el idx del crimen más cercano al punto (px,py), si está en rango."""
        mejor_idx  = None
        mejor_dist = R_HOVER + 4
        for idx, crimen in self.partida.crimenes_en_mapa():
            col, fila = self.partida.posicion(idx)
            centro = self._pos_a_pixel(col, fila)
            dx = px - centro.x()
            dy = py - centro.y()
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < mejor_dist:
                mejor_dist = dist
                mejor_idx  = idx
        return mejor_idx

    # ── Pintura ───────────────────────────────────────────────────────── #

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        self._dibujar_fondo(p)
        self._dibujar_grid(p)
        self._dibujar_crimenes(p)

        p.end()

    def _dibujar_fondo(self, p: QPainter):
        p.fillRect(self.rect(), COL_FONDO)

    def _dibujar_grid(self, p: QPainter):
        pen = QPen(COL_GRID, 1, Qt.SolidLine)
        p.setPen(pen)

        w = self.width()
        h = self.height()

        # Líneas verticales
        for col in range(COLS + 1):
            x = col * CELDA_W
            p.drawLine(x, 0, x, h)

        # Líneas horizontales
        for fila in range(FILAS + 1):
            y = fila * CELDA_H
            p.drawLine(0, y, w, y)

        # Etiquetas de columna (A-H) y fila (1-6) — estilo coordenada policial
        p.setFont(QFont("Courier New", 7))
        p.setPen(QPen(QColor(GRIS_BORDE)))
        for col in range(COLS):
            letra = chr(ord('A') + col)
            p.drawText(QRect(col * CELDA_W, 2, CELDA_W, 12),
                       Qt.AlignHCenter, letra)
        for fila in range(FILAS):
            p.drawText(QRect(2, fila * CELDA_H, 14, CELDA_H),
                       Qt.AlignVCenter, str(fila + 1))

    def _dibujar_crimenes(self, p: QPainter):
        for idx, crimen in self.partida.crimenes_en_mapa():
            col, fila = self.partida.posicion(idx)
            centro = self._pos_a_pixel(col, fila)
            self._dibujar_punto(p, idx, crimen, centro)

    def _dibujar_punto(self, p: QPainter, idx: int, crimen: Crimen, centro: QPoint):
        es_hover    = idx == self._hover_idx
        es_sel      = idx == self._sel_idx
        sin_inv     = len(crimen.campos_revelados) == 0
        color_base  = _color_crimen(crimen)

        # Radio con pulso si no está investigado
        if sin_inv and not crimen.sospechoso:
            radio = R_NORMAL + int(self._pulso * 3)
        elif es_hover:
            radio = R_HOVER
        elif es_sel:
            radio = R_SELECTED
        else:
            radio = R_NORMAL

        cx, cy = centro.x(), centro.y()

        # Halo exterior si está seleccionado
        if es_sel:
            halo = QColor(color_base)
            halo.setAlpha(60)
            p.setBrush(QBrush(halo))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(cx, cy), radio + 5, radio + 5)

        # Sombra suave
        sombra = QColor(0, 0, 0, 80)
        p.setBrush(QBrush(sombra))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(cx + 2, cy + 2), radio, radio)

        # Gradiente radial para el punto
        grad = QRadialGradient(QPointF(cx - radio*0.3, cy - radio*0.3), radio * 1.5)
        grad.setColorAt(0.0, color_base.lighter(140))
        grad.setColorAt(1.0, color_base.darker(130))
        p.setBrush(QBrush(grad))

        # Borde
        if es_sel:
            p.setPen(QPen(QColor(BLANCO), 1.5))
        elif es_hover:
            p.setPen(QPen(color_base.lighter(160), 1))
        else:
            p.setPen(QPen(color_base.darker(150), 1))

        p.drawEllipse(QPoint(cx, cy), radio, radio)

        # Número de expediente encima del punto
        p.setFont(QFont("Courier New", 7, QFont.Bold))
        p.setPen(QPen(QColor(NEGRO) if not sin_inv else QColor(BLANCO)))
        num = str(self.partida._pool.index(crimen) + 1)
        p.drawText(QRect(cx - 10, cy - 8, 20, 16), Qt.AlignCenter, num)

    # ── Eventos de ratón ─────────────────────────────────────────────── #

    def mouseMoveEvent(self, event):
        idx = self._pixel_a_idx(event.x(), event.y())
        if idx != self._hover_idx:
            self._hover_idx = idx
            if idx is not None:
                self.setCursor(Qt.PointingHandCursor)
                crimen = self.partida.crimen(idx)
                tip = f"Expediente #{idx+1}"
                n_rev = len(crimen.campos_revelados)
                if n_rev > 0:
                    tip += f" · {n_rev}/5 atributos"
                if crimen.sospechoso:
                    tip += " · SOSPECHOSO"
                QToolTip.showText(event.globalPosition().toPoint(), tip)
            else:
                self.setCursor(Qt.ArrowCursor)
                QToolTip.hideText()
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            idx = self._pixel_a_idx(event.x(), event.y())
            if idx is not None:
                self._sel_idx = idx
                self.crimen_seleccionado.emit(idx)
                self.update()

    def leaveEvent(self, event):
        self._hover_idx = None
        self.update()

    # ── API pública ───────────────────────────────────────────────────── #

    def actualizar(self):
        """Redibuja el mapa completo."""
        self.update()

    def seleccionar(self, idx: int | None):
        """Selecciona programáticamente un punto."""
        self._sel_idx = idx
        self.update()

    def deseleccionar(self):
        self._sel_idx = None
        self.update()
