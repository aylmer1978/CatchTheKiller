"""
gui/estilos.py — Paleta de colores y stylesheet global.
Importar desde cualquier módulo GUI.
"""

# ── Paleta ────────────────────────────────────────────────
NEGRO        = "#0a0a0b"
GRIS_OSCURO  = "#111113"
GRIS_PANEL   = "#18181c"
GRIS_BORDE   = "#2a2a30"
GRIS_MEDIO   = "#3a3a45"
GRIS_TEXTO   = "#8888a0"
BLANCO       = "#e8e8f0"
AMBAR        = "#d4952a"
AMBAR_CLARO  = "#f0b945"
AMBAR_OSCURO = "#8a5e0f"
ROJO         = "#c0392b"
ROJO_CLARO   = "#e74c3c"
ROJO_OSCURO  = "#7a2020"
VERDE        = "#27ae60"
VERDE_OSCURO = "#1a6b3a"
AZUL         = "#2980b9"

MONO = "'Courier New', 'Courier', monospace"

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {NEGRO};
    color: {BLANCO};
    font-family: {MONO};
}}

QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background: {GRIS_OSCURO};
    width: 6px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {GRIS_BORDE};
    min-height: 20px;
    border-radius: 3px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QScrollBar:horizontal {{
    background: {GRIS_OSCURO};
    height: 6px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {GRIS_BORDE};
    min-width: 20px;
    border-radius: 3px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

QPushButton {{
    background-color: {GRIS_PANEL};
    color: {AMBAR};
    border: 1px solid {AMBAR_OSCURO};
    border-radius: 2px;
    padding: 6px 16px;
    font-family: {MONO};
    font-size: 11px;
    letter-spacing: 2px;
}}
QPushButton:hover  {{ background-color: {AMBAR_OSCURO}; color: {BLANCO}; }}
QPushButton:pressed {{ background-color: {AMBAR}; color: {NEGRO}; }}
QPushButton:disabled {{ color: {GRIS_BORDE}; border-color: {GRIS_BORDE}; background: {GRIS_OSCURO}; }}

QToolTip {{
    background-color: {GRIS_PANEL};
    color: {BLANCO};
    border: 1px solid {GRIS_BORDE};
    font-family: {MONO};
    font-size: 10px;
    padding: 4px;
}}
"""


def estilo_boton_rojo() -> str:
    return f"""
        QPushButton {{
            background-color: {ROJO_OSCURO};
            color: {BLANCO};
            border: 1px solid {ROJO};
            border-radius: 2px;
            font-family: {MONO};
            letter-spacing: 2px;
        }}
        QPushButton:hover {{ background-color: {ROJO}; }}
        QPushButton:disabled {{
            background-color: {GRIS_PANEL};
            color: {GRIS_TEXTO};
            border-color: {GRIS_BORDE};
        }}
    """


def estilo_boton_neutro() -> str:
    return f"""
        QPushButton {{
            background-color: {GRIS_OSCURO};
            color: {GRIS_TEXTO};
            border: 1px solid {GRIS_BORDE};
            border-radius: 2px;
            font-family: {MONO};
            letter-spacing: 1px;
        }}
        QPushButton:hover {{ color: {BLANCO}; border-color: {GRIS_MEDIO}; }}
    """


def separador_h() -> str:
    """Devuelve un stylesheet para un QFrame horizontal tipo línea."""
    return f"background: {GRIS_BORDE}; max-height: 1px; border: none;"
