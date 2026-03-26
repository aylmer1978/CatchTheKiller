"""
gui/dossier_final.py — Pantalla de cierre estilo dossier policial.

Muestra:
  · Nombre de prensa del asesino
  · Firma (3 rasgos fijos)
  · Total de víctimas durante la investigación
  · Lista de víctimas con lugar y franja
  · Resultado (detenido / fugado)
  · Estadísticas de la partida
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from core.crimen import ETIQUETAS
from gui.estilos import *


class DossierFinal(QWidget):
    """
    Pantalla completa de fin de partida.
    Emite nueva_partida() cuando el jugador quiere reiniciar.
    """
    nueva_partida = Signal()

    def __init__(self, dossier: dict, parent=None):
        super().__init__(parent)
        self.dossier = dossier
        self._construir()

    def _construir(self):
        layout_outer = QVBoxLayout(self)
        layout_outer.setContentsMargins(0, 0, 0, 0)
        layout_outer.setAlignment(Qt.AlignCenter)

        # Scroll por si el contenido no cabe
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        contenido = QWidget()
        layout = QVBoxLayout(contenido)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignHCenter)

        victoria  = self.dossier["victoria"]
        nombre    = self.dossier["nombre_prensa"]
        firma     = self.dossier["firma"]
        victimas  = self.dossier["total_victimas"]
        historial = self.dossier["historial_victimas"]

        # ── Resultado ─────────────────────────────────────
        if victoria:
            res_texto = "CASO CERRADO"
            res_sub   = "EL SOSPECHOSO HA SIDO DETENIDO"
            res_color = VERDE
        else:
            res_texto = "CASO ABIERTO"
            res_sub   = "EL ASESINO SIGUE EN LIBERTAD"
            res_color = ROJO

        lbl_res = QLabel(res_texto)
        lbl_res.setAlignment(Qt.AlignCenter)
        lbl_res.setStyleSheet(f"""
            color: {res_color};
            font-size: 28px;
            font-weight: bold;
            letter-spacing: 10px;
            font-family: {MONO};
        """)
        layout.addWidget(lbl_res)

        lbl_sub = QLabel(res_sub)
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;
            letter-spacing: 4px;
            font-family: {MONO};
        """)
        layout.addWidget(lbl_sub)
        layout.addSpacing(28)

        # ── Separador decorativo ──────────────────────────
        layout.addWidget(self._sep())
        layout.addSpacing(24)

        # ── Nombre del asesino ────────────────────────────
        lbl_apodo_key = QLabel("CONOCIDO POR LA PRENSA COMO")
        lbl_apodo_key.setAlignment(Qt.AlignCenter)
        lbl_apodo_key.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;
            letter-spacing: 3px;
            font-family: {MONO};
        """)
        layout.addWidget(lbl_apodo_key)
        layout.addSpacing(8)

        lbl_nombre = QLabel(f'"{nombre}"')
        lbl_nombre.setAlignment(Qt.AlignCenter)
        lbl_nombre.setStyleSheet(f"""
            color: {AMBAR};
            font-size: 24px;
            font-style: italic;
            letter-spacing: 2px;
            font-family: {MONO};
        """)
        layout.addWidget(lbl_nombre)
        layout.addSpacing(24)

        # ── Firma ─────────────────────────────────────────
        layout.addWidget(self._sep())
        layout.addSpacing(20)

        lbl_firma_tit = QLabel("FIRMA DEL ASESINO  ·  3 RASGOS FIJOS")
        lbl_firma_tit.setAlignment(Qt.AlignCenter)
        lbl_firma_tit.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;
            letter-spacing: 3px;
            font-family: {MONO};
        """)
        layout.addWidget(lbl_firma_tit)
        layout.addSpacing(12)

        firma_widget = QWidget()
        firma_layout = QHBoxLayout(firma_widget)
        firma_layout.setSpacing(0)
        firma_layout.setContentsMargins(0, 0, 0, 0)
        firma_layout.setAlignment(Qt.AlignCenter)

        modus = self.dossier.get("modus_declarado") or {}
        for i, (attr, val) in enumerate(firma.items()):
            # ¿El jugador acertó este rasgo?
            acertado = modus.get(attr) == val
            bloque = self._bloque_firma(ETIQUETAS.get(attr, attr), val, acertado if modus else None)
            firma_layout.addWidget(bloque)
            if i < len(firma) - 1:
                sep_v = QLabel("·")
                sep_v.setStyleSheet(f"color: {GRIS_BORDE}; font-size: 18px; padding: 0 16px;")
                firma_layout.addWidget(sep_v)

        layout.addWidget(firma_widget)

        # Mostrar lo que declaró el jugador si fue incorrecto
        if modus and not victoria:
            layout.addSpacing(8)
            lbl_decl_tit = QLabel("TU DECLARACIÓN")
            lbl_decl_tit.setAlignment(Qt.AlignCenter)
            lbl_decl_tit.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 9px; letter-spacing: 3px;")
            layout.addWidget(lbl_decl_tit)
            decl_widget = QWidget()
            decl_layout = QHBoxLayout(decl_widget)
            decl_layout.setAlignment(Qt.AlignCenter)
            decl_layout.setSpacing(0)
            decl_layout.setContentsMargins(0, 0, 0, 0)
            for i, (attr, val) in enumerate(modus.items()):
                correcto = firma.get(attr) == val
                color_val = VERDE if correcto else ROJO
                bloque = self._bloque_firma(ETIQUETAS.get(attr, attr), val, correcto)
                decl_layout.addWidget(bloque)
                if i < len(modus) - 1:
                    sep_v = QLabel("·")
                    sep_v.setStyleSheet(f"color: {GRIS_BORDE}; font-size: 18px; padding: 0 16px;")
                    decl_layout.addWidget(sep_v)
            layout.addWidget(decl_widget)

        layout.addSpacing(24)

        # ── Víctimas ──────────────────────────────────────
        layout.addWidget(self._sep())
        layout.addSpacing(20)

        contador_widget = QHBoxLayout()
        contador_widget.setAlignment(Qt.AlignCenter)

        lbl_vict_key = QLabel("VÍCTIMAS DURANTE LA INVESTIGACIÓN")
        lbl_vict_key.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;
            letter-spacing: 3px;
            font-family: {MONO};
        """)

        lbl_vict_num = QLabel(str(victimas))
        lbl_vict_num.setStyleSheet(f"""
            color: {ROJO if victimas > 3 else AMBAR};
            font-size: 36px;
            font-weight: bold;
            font-family: {MONO};
            padding-left: 20px;
        """)

        contador_widget.addWidget(lbl_vict_key)
        contador_widget.addWidget(lbl_vict_num)

        layout.addLayout(contador_widget)
        layout.addSpacing(16)

        # Lista de víctimas
        if historial:
            for i, entrada in enumerate(historial):
                fila = self._fila_victima(i + 1, entrada)
                layout.addWidget(fila)
                layout.addSpacing(4)

        layout.addSpacing(24)

        # ── Estadísticas ──────────────────────────────────
        layout.addWidget(self._sep())
        layout.addSpacing(20)

        stats = [
            ("DIFICULTAD",         self.dossier["dificultad"]),
            ("DÍAS DE INVESTIGACIÓN", str(self.dossier["dias_totales"])),
            ("INTENTOS USADOS",    f"{self.dossier['intentos_usados']} / {self.dossier['intentos_max']}"),
            ("EXPEDIENTES VISTOS", f"{self.dossier['crimenes_vistos']} / {self.dossier['crimenes_pool']}"),
        ]

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setHorizontalSpacing(40)
        for i, (clave, valor) in enumerate(stats):
            fila = i // 2
            col_base = (i % 2) * 2

            lbl_k = QLabel(clave)
            lbl_k.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 9px; letter-spacing: 1px;")
            lbl_v = QLabel(valor)
            lbl_v.setStyleSheet(f"color: {BLANCO}; font-size: 12px; font-weight: bold; letter-spacing: 1px;")

            grid.addWidget(lbl_k, fila * 2,     col_base)
            grid.addWidget(lbl_v, fila * 2 + 1, col_base)

        stats_widget = QWidget()
        stats_widget.setLayout(grid)
        layout.addWidget(stats_widget, alignment=Qt.AlignHCenter)
        layout.addSpacing(32)

        # ── Botones finales ───────────────────────────────
        btns = QHBoxLayout()
        btns.setSpacing(12)
        btns.setAlignment(Qt.AlignCenter)

        btn_nueva = QPushButton("↺  NUEVA PARTIDA")
        btn_nueva.setFixedHeight(38)
        btn_nueva.setFixedWidth(200)
        btn_nueva.setStyleSheet(f"""
            QPushButton {{
                background: {GRIS_PANEL};
                color: {AMBAR};
                border: 1px solid {AMBAR_OSCURO};
                border-radius: 2px;
                font-size: 11px;
                letter-spacing: 3px;
                font-family: {MONO};
            }}
            QPushButton:hover {{ background: {AMBAR_OSCURO}; color: {BLANCO}; }}
        """)
        btn_nueva.clicked.connect(self.nueva_partida.emit)
        btns.addWidget(btn_nueva)

        layout.addLayout(btns)

        scroll.setWidget(contenido)
        layout_outer.addWidget(scroll)

    # ── Helpers de construcción ───────────────────────────────────────── #

    def _sep(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background: {GRIS_BORDE}; max-height: 1px; border: none;")
        return sep

    def _bloque_firma(self, etiqueta: str, valor: str, acertado: bool | None = None) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(4)
        lay.setAlignment(Qt.AlignCenter)

        lbl_e = QLabel(etiqueta)
        lbl_e.setAlignment(Qt.AlignCenter)
        lbl_e.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;
            letter-spacing: 2px;
            font-family: {MONO};
        """)

        # Color del valor según si el jugador acertó o no
        if acertado is True:
            color_val = VERDE
        elif acertado is False:
            color_val = ROJO
        else:
            color_val = AMBAR

        lbl_v = QLabel(valor)
        lbl_v.setAlignment(Qt.AlignCenter)
        lbl_v.setStyleSheet(f"""
            color: {color_val};
            font-size: 14px;
            font-weight: bold;
            font-family: {MONO};
        """)

        lay.addWidget(lbl_e)
        lay.addWidget(lbl_v)
        return w

    def _fila_victima(self, num: int, entrada: dict) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {GRIS_PANEL};
                border: 1px solid {GRIS_BORDE};
                border-left: 3px solid {ROJO};
                border-radius: 2px;
            }}
            QLabel {{ border: none; }}
        """)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(12, 6, 12, 6)

        lbl_num = QLabel(f"{num:02d}.")
        lbl_num.setFixedWidth(28)
        lbl_num.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 10px;")

        lbl_vic = QLabel(entrada["victima"])
        lbl_vic.setStyleSheet(f"color: {BLANCO}; font-size: 11px; font-weight: bold;")

        lbl_det = QLabel(f"{entrada['lugar']}  ·  {entrada['franja']}")
        lbl_det.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 10px;")
        lbl_det.setAlignment(Qt.AlignRight)

        lay.addWidget(lbl_num)
        lay.addWidget(lbl_vic)
        lay.addStretch()
        lay.addWidget(lbl_det)

        return frame
