"""
main.py — Punto de entrada de Catch the Killer.
Uso: python main.py
"""

import json, sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from gui.main_window import MainWindow


def main():
    ruta_json = Path(__file__).parent / "data" / "elementos.json"
    with open(ruta_json, encoding="utf-8") as f:
        elementos = json.load(f)

    app = QApplication(sys.argv)
    app.setApplicationName("Catch the Killer")

    ventana = MainWindow(elementos)
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
