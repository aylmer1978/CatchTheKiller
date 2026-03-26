"""
gui/sala_mando.py — Sala de mando: declaración del modus operandi.

El jugador declara los 3 rasgos que cree que definen al asesino:
  - Para cada rasgo: elige un atributo (lugar/franja/arma/víctima/otros)
                     y un valor de los disponibles en elementos.json

Los valores ya investigados aparecen destacados como pistas.
Los 3 atributos deben ser distintos.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QComboBox, QSizePolicy, QWidget
)
from PySide6.QtCore import Qt

from core.partida import Partida, ResultadoAcusacion
from core.crimen import ATRIBUTOS, ETIQUETAS
from gui.estilos import *

# Etiquetas limpias sin emoji para los desplegables
ETIQUETAS_CORTAS = {
    "lugar":   "Lugar",
    "franja":  "Franja horaria",
    "arma":    "Arma",
    "victima": "Víctima",
    "otros":   "Otros",
}


class SalaMando(QDialog):
    """
    Diálogo modal de la sala de mando.
    Tras exec(), el resultado de la acusación se lee en self.resultado.
    """

    def __init__(self, partida: Partida, elementos: dict, parent=None):
        super().__init__(parent)
        self.partida   = partida
        self.elementos = elementos
        self.resultado = None
        self._construir()

    # ── Construcción ──────────────────────────────────────────────────── #

    def _construir(self):
        self.setWindowTitle("SALA DE MANDO — MODUS OPERANDI")
        self.setModal(True)
        self.setFixedWidth(500)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {GRIS_OSCURO}; font-family: {MONO}; }}
            QLabel  {{ border: none; }}
            QComboBox {{
                background: {GRIS_PANEL};
                color: {BLANCO};
                border: 1px solid {GRIS_BORDE};
                border-radius: 2px;
                padding: 4px 8px;
                font-family: {MONO};
                font-size: 10px;
            }}
            QComboBox:focus {{ border-color: {AMBAR_OSCURO}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox QAbstractItemView {{
                background: {GRIS_PANEL};
                color: {BLANCO};
                selection-background-color: {AMBAR_OSCURO};
                border: 1px solid {GRIS_BORDE};
                font-family: {MONO};
                font-size: 10px;
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(14)

        # ── Título ────────────────────────────────────────
        lbl_titulo = QLabel("SALA DE MANDO")
        lbl_titulo.setStyleSheet(f"color: {AMBAR}; font-size: 16px; letter-spacing: 6px;")
        lay.addWidget(lbl_titulo)

        lbl_sub = QLabel("DECLARACIÓN DEL MODUS OPERANDI")
        lbl_sub.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 9px; letter-spacing: 3px;")
        lay.addWidget(lbl_sub)

        lay.addWidget(self._sep())

        # ── Intentos ──────────────────────────────────────
        fila_int = QHBoxLayout()
        lbl_int_k = QLabel("INTENTOS DISPONIBLES")
        lbl_int_k.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 10px;")
        color_int = VERDE if self.partida.intentos > 1 else ROJO
        lbl_int_v = QLabel(f"{self.partida.intentos} / {self.partida.intentos_max}")
        lbl_int_v.setStyleSheet(f"color: {color_int}; font-size: 14px; font-weight: bold;")
        lbl_int_v.setAlignment(Qt.AlignRight)
        fila_int.addWidget(lbl_int_k)
        fila_int.addStretch()
        fila_int.addWidget(lbl_int_v)
        lay.addLayout(fila_int)

        if self.partida.intentos == 1:
            lbl_aviso = QLabel("⚠  Último intento. Si fallas, el caso queda abierto.")
            lbl_aviso.setStyleSheet(f"color: {ROJO}; font-size: 9px;")
            lay.addWidget(lbl_aviso)

        lay.addWidget(self._sep())

        # ── Instrucción ───────────────────────────────────
        lbl_instr = QLabel(
            "Declara los 3 rasgos que definen al asesino en serie.\n"
            "Elige un atributo y su valor para cada rasgo."
        )
        lbl_instr.setWordWrap(True)
        lbl_instr.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 10px;")
        lay.addWidget(lbl_instr)

        # ── Filas de modus operandi ───────────────────────
        self._combos: list[tuple[QComboBox, QComboBox]] = []

        for i in range(3):
            fila_widget = self._crear_fila_rasgo(i)
            lay.addWidget(fila_widget)

        # Error de validación
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {ROJO}; font-size: 10px;")
        self.lbl_error.setWordWrap(True)
        lay.addWidget(self.lbl_error)

        lay.addWidget(self._sep())

        # ── Nota ──────────────────────────────────────────
        lbl_nota = QLabel(
            "Los crímenes marcados como sospechosos son solo una ayuda visual.\n"
            "Lo que se evalúa es el modus operandi que declares aquí."
        )
        lbl_nota.setWordWrap(True)
        lbl_nota.setStyleSheet(f"color: {GRIS_BORDE}; font-size: 9px;")
        lay.addWidget(lbl_nota)

        # ── Botones ───────────────────────────────────────
        btns = QHBoxLayout()
        btns.setSpacing(10)

        btn_cancelar = QPushButton("VOLVER AL MAPA")
        btn_cancelar.setFixedHeight(34)
        btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {GRIS_TEXTO};
                border: 1px solid {GRIS_BORDE}; border-radius: 2px;
                font-size: 10px; letter-spacing: 2px; font-family: {MONO};
            }}
            QPushButton:hover {{ color: {BLANCO}; border-color: {GRIS_MEDIO}; }}
        """)
        btn_cancelar.clicked.connect(self.reject)

        self.btn_acusar = QPushButton("⚑  FORMALIZAR ACUSACIÓN")
        self.btn_acusar.setFixedHeight(34)
        self.btn_acusar.setStyleSheet(f"""
            QPushButton {{
                background: {ROJO_OSCURO}; color: {BLANCO};
                border: 1px solid {ROJO}; border-radius: 2px;
                font-size: 10px; letter-spacing: 2px; font-family: {MONO};
            }}
            QPushButton:hover {{ background: {ROJO}; }}
            QPushButton:disabled {{
                background: {GRIS_PANEL}; color: {GRIS_TEXTO};
                border-color: {GRIS_BORDE};
            }}
        """)
        self.btn_acusar.clicked.connect(self._on_acusar)

        btns.addWidget(btn_cancelar)
        btns.addWidget(self.btn_acusar)
        lay.addLayout(btns)

    def _sep(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background: {GRIS_BORDE}; max-height: 1px;")
        return sep

    def _crear_fila_rasgo(self, num: int) -> QWidget:
        """Crea una fila con combo de atributo + combo de valor."""
        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background: {GRIS_PANEL};
                border: 1px solid {GRIS_BORDE};
                border-radius: 2px;
            }}
        """)
        lay = QHBoxLayout(widget)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(10)

        # Número de rasgo
        lbl_num = QLabel(f"{num + 1}.")
        lbl_num.setFixedWidth(16)
        lbl_num.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 11px; background: transparent; border: none;")
        lay.addWidget(lbl_num)

        # Combo de atributo
        combo_attr = QComboBox()
        combo_attr.setFixedWidth(140)
        combo_attr.addItem("— Atributo —", None)
        for attr in ATRIBUTOS:
            combo_attr.addItem(ETIQUETAS_CORTAS[attr], attr)

        # Combo de valor (se rellena al cambiar atributo)
        combo_val = QComboBox()
        combo_val.setFixedWidth(180)
        combo_val.addItem("— Valor —", None)
        combo_val.setEnabled(False)

        combo_attr.currentIndexChanged.connect(
            lambda _, ca=combo_attr, cv=combo_val: self._on_attr_cambiado(ca, cv)
        )

        lay.addWidget(combo_attr)
        lay.addWidget(combo_val)
        lay.addStretch()

        self._combos.append((combo_attr, combo_val))
        return widget

    def _on_attr_cambiado(self, combo_attr: QComboBox, combo_val: QComboBox):
        """Rellena el combo de valores al seleccionar un atributo."""
        combo_val.clear()
        attr = combo_attr.currentData()

        if attr is None:
            combo_val.addItem("— Valor —", None)
            combo_val.setEnabled(False)
            return

        combo_val.setEnabled(True)
        combo_val.addItem("— Valor —", None)

        # Mapa atributo → clave en elementos.json
        clave_json = {
            "lugar":   "lugares",
            "franja":  "franjas",
            "arma":    "armas",
            "victima": "victimas",
            "otros":   "otros",
        }[attr]

        for valor in sorted(self.elementos[clave_json]):
            combo_val.addItem(valor, valor)

        self.lbl_error.setText("")

    # ── Lógica de acusación ───────────────────────────────────────────── #

    def _leer_modus(self) -> tuple[dict | None, str]:
        """
        Lee los combos y construye el modus operandi.
        Devuelve (modus_dict, "") si es válido o (None, mensaje_error).
        """
        modus = {}
        for i, (ca, cv) in enumerate(self._combos):
            attr = ca.currentData()
            val  = cv.currentData()

            if attr is None:
                return None, f"Rasgo {i+1}: selecciona un atributo."
            if val is None:
                return None, f"Rasgo {i+1}: selecciona un valor."
            if attr in modus:
                return None, f"El atributo '{ETIQUETAS_CORTAS[attr]}' aparece más de una vez."

            modus[attr] = val

        return modus, ""

    def _on_acusar(self):
        modus, error = self._leer_modus()
        if modus is None:
            self.lbl_error.setText(f"⚠  {error}")
            return

        self.resultado = self.partida.acusar(modus)
        if "error" in self.resultado:
            self.lbl_error.setText(f"⚠  {self.resultado['error']}")
            self.resultado = None
            return

        self.accept()
