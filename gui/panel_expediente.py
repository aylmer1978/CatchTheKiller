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
from PySide6.QtGui import QPixmap, QPainter

from core.crimen import Crimen, ATRIBUTOS, ETIQUETAS
from core.partida import Partida
from core.assets import (
    imagen_lugar, imagen_lugar_generica,
    imagen_arma,  imagen_arma_generica,
    imagen_cuerpo, imagen_cuerpo_generico,
)
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
        self.setFixedWidth(290)
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

        # ── Imagen compuesta (lugar + cuerpo + arma) ──────
        # El panel tiene 290px de ancho con 16px de margen a cada lado.
        # Ancho útil = 290 - 32 = 258px. Cuadrado 1:1.
        IMG_SIZE = 258
        self.img_widget = _ImagenCrimen()
        self.img_widget.setFixedSize(IMG_SIZE, IMG_SIZE)
        layout.addWidget(self.img_widget)

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

        # Imagen compuesta con rutas fijadas al aparecer el crimen
        lugar_revelado   = "lugar"   in crimen.campos_revelados
        arma_revelada    = "arma"    in crimen.campos_revelados
        victima_revelada = "victima" in crimen.campos_revelados
        self.img_widget.cargar(
            ruta_lugar   = crimen.img_lugar  if lugar_revelado   else None,
            ruta_cuerpo  = crimen.img_cuerpo if victima_revelada else None,
            ruta_arma    = crimen.img_arma   if arma_revelada    else None,
            hay_lugar_generico  = not lugar_revelado,
            hay_cuerpo_generico = not victima_revelada,
            hay_arma_generica   = not arma_revelada,
        )

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
        self.img_widget.cargar(
            hay_lugar_generico=True,
            hay_cuerpo_generico=True,
            hay_arma_generica=True,
        )

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

# ── Widget de imagen compuesta ────────────────────────────────────────── #

class _ImagenCrimen(QWidget):
    """
    Widget de imagen compuesta con tres capas:
      1. Lugar  (fondo opaco)
      2. Cuerpo (PNG transparente, centrado abajo)
      3. Arma   (PNG transparente, esquina inferior derecha)

    Las rutas se fijan al aparecer el crimen y nunca cambian.
    Cuando un atributo no está revelado se muestra la genérica (_generico.png).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._px_lugar:  QPixmap | None = None
        self._px_cuerpo: QPixmap | None = None
        self._px_arma:   QPixmap | None = None
        self._vacio = True
        self.setStyleSheet(f"background: {GRIS_OSCURO}; border: none;")

    def cargar(
        self,
        ruta_lugar:          object = None,
        ruta_cuerpo:         object = None,
        ruta_arma:           object = None,
        hay_lugar_generico:  bool   = False,
        hay_cuerpo_generico: bool   = False,
        hay_arma_generica:   bool   = False,
    ) -> None:
        from core.assets import imagen_lugar_generica, imagen_arma_generica, imagen_cuerpo_generico

        self._vacio = False

        def _pixmap(ruta, generico_fn, usar_generico):
            if ruta is not None:
                from pathlib import Path
                r = Path(ruta) if not hasattr(ruta, 'exists') else ruta
                if r.exists():
                    return QPixmap(str(r))
            if usar_generico:
                gen = generico_fn()
                if gen and gen.exists():
                    return QPixmap(str(gen))
            return None

        self._px_lugar  = _pixmap(ruta_lugar,  imagen_lugar_generica,  hay_lugar_generico)
        self._px_cuerpo = _pixmap(ruta_cuerpo, imagen_cuerpo_generico, hay_cuerpo_generico)
        self._px_arma   = _pixmap(ruta_arma,   imagen_arma_generica,   hay_arma_generica)

        self.update()

    def limpiar(self) -> None:
        self._px_lugar  = None
        self._px_cuerpo = None
        self._px_arma   = None
        self._vacio     = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        hay_algo = self._px_lugar or self._px_cuerpo or self._px_arma

        if self._vacio or not hay_algo:
            painter.fillRect(rect, Qt.transparent)
            if not self._vacio:
                from PySide6.QtGui import QColor, QFont
                painter.setPen(QColor(GRIS_BORDE))
                painter.setFont(QFont("Courier New", 8))
                painter.drawText(rect, Qt.AlignCenter, "[ sin ilustracion ]")
            painter.end()
            return

        # Capa 1: lugar (fondo)
        if self._px_lugar:
            px = self._px_lugar.scaled(
                rect.width(), rect.height(),
                Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (rect.width()  - px.width())  // 2
            y = (rect.height() - px.height()) // 2
            painter.drawPixmap(x, y, px)

        # Capa 2: cuerpo (centrado, alineado abajo)
        if self._px_cuerpo:
            max_w = int(rect.width() * 0.75)
            px_c = self._px_cuerpo.scaled(
                max_w, rect.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            cx = (rect.width()  - px_c.width())  // 2
            cy =  rect.height() - px_c.height()
            painter.drawPixmap(cx, cy, px_c)

        # Capa 3: arma (esquina inferior derecha)
        if self._px_arma:
            max_w = int(rect.width()  * 0.35)
            max_h = int(rect.height() * 0.45)
            px_a = self._px_arma.scaled(
                max_w, max_h,
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            ax = rect.width()  - px_a.width()  - 4
            ay = rect.height() - px_a.height() - 4
            painter.drawPixmap(ax, ay, px_a)

        painter.end()
