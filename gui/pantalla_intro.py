"""
gui/pantalla_intro.py — Introducción narrativa antes de empezar el caso.

Aparece tras elegir dificultad, antes del mapa.
El texto varía según la dificultad y el número real de víctimas iniciales.
El jugador solo conoce el número "comunicado", no el real.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal

from core.partida import Partida, Dificultad
from gui.estilos import *


# Textos de introducción según dificultad
# {n} se reemplaza por el número de víctimas comunicado
_INTRO_FACIL = """\
Llevas tres años en el Departamento de Homicidios.
Has visto muchas cosas. Pero esto es difer.

En los últimos meses se han producido múltiples asesinatos
en la ciudad. Casos aparentemente aislados, sin conexión visible.

Tus dos décadas de experiencia te dicen otra cosa.
El método. La elección de las víctimas. Los detalles.

Hay alguien ahí fuera que lo ha hecho antes.
Y lo volverá a hacer.

Tu instinto ya ha identificado {n} homicidio{s} que podrían
ser obra de la misma persona. Puede que haya más que aún
no han llegado a tu mesa.

El caso es tuyo. Empieza a trabajar.\
"""

_INTRO_NORMAL = """\
Una llamada anónima. Un expediente sin cerrar.
Un presentimiento que no puedes ignorar.

Has repasado los archivos durante semanas.
Demasiadas coincidencias para ser casualidad.

Crees que hay un asesino en serie suelto.
No tienes pruebas. Solo intuición y datos dispersos.

Hay al menos {n} homicidio{s} que encajan con tu teoría.
Puede que sean más. No puedes saberlo aún.

Nadie te ha pedido que investigues esto.
Lo haces porque alguien tiene que hacerlo.

El reloj corre.\
"""

_INTRO_DIFICIL = """\
No hay expediente oficial.
No hay caso abierto.
No hay nada.

Solo una sensación que te mantiene despierto por las noches:
alguien está matando de forma sistemática,
y nadie lo ha visto todavía.

Quizás llevas razón. Quizás estás persiguiendo sombras.

Lo que sí sabes: la ciudad tiene demasiados muertos sin resolver.
Y tú tienes una teoría.

Demuéstrala.\
"""

_TEXTOS = {
    Dificultad.FACIL:   _INTRO_FACIL,
    Dificultad.NORMAL:  _INTRO_NORMAL,
    Dificultad.DIFICIL: _INTRO_DIFICIL,
}


def _generar_texto(partida: Partida) -> str:
    plantilla = _TEXTOS[partida.dificultad]
    n = partida.victimas_comunicadas
    s = "s" if n != 1 else ""
    return plantilla.format(n=n, s=s)


class PantallaIntro(QWidget):
    """
    Pantalla de introducción narrativa.
    Emite partida_lista() cuando el jugador pulsa COMENZAR INVESTIGACIÓN.
    """
    partida_lista = Signal()

    def __init__(self, partida: Partida, parent=None):
        super().__init__(parent)
        self.partida = partida
        self._construir()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        caja = QWidget()
        caja.setFixedWidth(520)
        caja_lay = QVBoxLayout(caja)
        caja_lay.setSpacing(0)
        caja_lay.setContentsMargins(40, 48, 40, 48)

        # ── Cabecera ──────────────────────────────────────
        lbl_dept = QLabel("DEPARTAMENTO DE HOMICIDIOS")
        lbl_dept.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 8px;
            letter-spacing: 4px;
            font-family: {MONO};
        """)
        caja_lay.addWidget(lbl_dept)
        caja_lay.addSpacing(4)

        lbl_caso = QLabel("CASO NUEVO — CLASIFICADO")
        lbl_caso.setStyleSheet(f"""
            color: {AMBAR};
            font-size: 13px;
            letter-spacing: 4px;
            font-family: {MONO};
        """)
        caja_lay.addWidget(lbl_caso)
        caja_lay.addSpacing(20)

        sep = QFrame()
        sep.setStyleSheet(f"background: {AMBAR_OSCURO}; max-height: 1px; border: none;")
        caja_lay.addWidget(sep)
        caja_lay.addSpacing(28)

        # ── Texto narrativo ───────────────────────────────
        texto = _generar_texto(self.partida)
        lbl_texto = QLabel(texto)
        lbl_texto.setWordWrap(True)
        lbl_texto.setAlignment(Qt.AlignLeft)
        lbl_texto.setStyleSheet(f"""
            color: {BLANCO};
            font-size: 12px;
            font-family: {MONO};
        """)
        caja_lay.addWidget(lbl_texto)
        caja_lay.addSpacing(32)

        sep2 = QFrame()
        sep2.setStyleSheet(f"background: {GRIS_BORDE}; max-height: 1px; border: none;")
        caja_lay.addWidget(sep2)
        caja_lay.addSpacing(24)

        # ── Dificultad y botón ────────────────────────────
        fila_bot = QHBoxLayout()

        lbl_dif = QLabel(self.partida.dificultad.value.upper())
        lbl_dif.setStyleSheet(f"""
            color: {GRIS_TEXTO};
            font-size: 9px;
            letter-spacing: 3px;
            font-family: {MONO};
        """)
        fila_bot.addWidget(lbl_dif)
        fila_bot.addStretch()

        btn = QPushButton("COMENZAR INVESTIGACION  >>")
        btn.setFixedHeight(36)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {AMBAR_OSCURO};
                color: {BLANCO};
                border: 1px solid {AMBAR};
                border-radius: 2px;
                font-size: 10px;
                letter-spacing: 2px;
                font-family: {MONO};
                padding: 0 16px;
            }}
            QPushButton:hover {{ background: {AMBAR}; color: {NEGRO}; }}
        """)
        btn.clicked.connect(self.partida_lista.emit)
        fila_bot.addWidget(btn)

        caja_lay.addLayout(fila_bot)
        layout.addWidget(caja)
