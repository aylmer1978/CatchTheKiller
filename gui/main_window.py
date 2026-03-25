"""
gui/main_window.py — Ventana principal. Orquesta todas las pantallas.

Flujo de juego:
  1. Jugador hace clic en un crimen del mapa → se selecciona
  2. Panel de mano muestra qué cartas son jugables sobre ese crimen
  3. Jugador hace clic en una carta → se juega, se revelan atributos
  4. Jugador puede descartar una carta gratis por turno
  5. Jugador puede pasar turno si no hay jugables
  6. Jugador puede marcar sospechosos y abrir Sala de Mando para acusar
"""

import json, sys
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.asesino import Asesino
from core.partida import Partida, Dificultad, ResultadoAcusacion

from gui.estilos import (
    STYLESHEET, NEGRO, GRIS_OSCURO, GRIS_PANEL, GRIS_BORDE,
    GRIS_TEXTO, BLANCO, AMBAR, AMBAR_OSCURO, ROJO, ROJO_OSCURO,
    VERDE, MONO, separador_h
)
from gui.pantalla_inicio  import PantallaInicio
from gui.mapa_widget      import MapaWidget
from gui.panel_expediente import PanelExpediente
from gui.panel_archivados import PanelArchivados
from gui.panel_mano       import PanelMano
from gui.sala_mando       import SalaMando
from gui.dossier_final    import DossierFinal


class MainWindow(QMainWindow):
    def __init__(self, elementos: dict):
        super().__init__()
        self.elementos = elementos
        self.setWindowTitle("CATCH THE KILLER")
        self.setMinimumSize(1200, 780)
        self.setStyleSheet(STYLESHEET)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)
        self._mostrar_inicio()

    def _mostrar_inicio(self):
        pantalla = PantallaInicio()
        pantalla.partida_iniciada.connect(self._iniciar_partida)
        self._stack.addWidget(pantalla)
        self._stack.setCurrentWidget(pantalla)

    def _iniciar_partida(self, dificultad: Dificultad):
        asesino = Asesino(self.elementos)
        partida = Partida(asesino, self.elementos, dificultad)
        pantalla = PantallaJuego(partida)
        pantalla.partida_terminada.connect(self._mostrar_dossier)
        self._stack.addWidget(pantalla)
        self._stack.setCurrentWidget(pantalla)

    def _mostrar_dossier(self, dossier: dict):
        pantalla = DossierFinal(dossier)
        pantalla.nueva_partida.connect(self._reiniciar)
        self._stack.addWidget(pantalla)
        self._stack.setCurrentWidget(pantalla)

    def _reiniciar(self):
        while self._stack.count() > 0:
            w = self._stack.widget(0)
            self._stack.removeWidget(w)
            w.deleteLater()
        self._mostrar_inicio()


class PantallaJuego(QWidget):
    """
    Pantalla principal. Layout vertical:
      ┌─────────────────────────────────────────┐
      │  Barra superior (stats + sala de mando) │
      ├──────────────┬───────────┬──────────────┤
      │   Mapa       │ Expediente│  Archivados  │
      ├──────────────┴───────────┴──────────────┤
      │  Panel de mano (3 cartas)               │
      └─────────────────────────────────────────┘
    """
    partida_terminada = Signal(dict)

    def __init__(self, partida: Partida, parent=None):
        super().__init__(parent)
        self.partida = partida
        self._idx_crimen_sel: int | None = None
        self._construir()

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 0)
        layout.setSpacing(8)

        # ── Barra superior ────────────────────────────────
        layout.addWidget(self._crear_barra())

        sep = QFrame()
        sep.setStyleSheet(separador_h())
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # ── Cuerpo central ────────────────────────────────
        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(12)
        cuerpo.setContentsMargins(0, 8, 0, 0)

        # Columna izquierda: mapa
        col_izq = QVBoxLayout()
        col_izq.setSpacing(6)

        lbl_mapa = QLabel("MAPA DE LA CIUDAD")
        lbl_mapa.setStyleSheet(
            f"color: {GRIS_TEXTO}; font-size: 9px; letter-spacing: 3px;"
        )
        col_izq.addWidget(lbl_mapa)

        self.mapa = MapaWidget(self.partida)
        self.mapa.crimen_seleccionado.connect(self._on_crimen_seleccionado)
        col_izq.addWidget(self.mapa)
        col_izq.addStretch()
        cuerpo.addLayout(col_izq)

        # Columna central: expediente
        self.panel_exp = PanelExpediente(self.partida)
        self.panel_exp.accion_sospechoso.connect(self._on_sospechoso)
        self.panel_exp.accion_archivar.connect(self._on_archivar)
        cuerpo.addWidget(self.panel_exp)

        # Columna derecha: archivados
        self.panel_arch = PanelArchivados(self.partida)
        self.panel_arch.accion_recuperar.connect(self._on_recuperar)
        cuerpo.addWidget(self.panel_arch)

        layout.addLayout(cuerpo, stretch=1)

        # ── Panel de mano (inferior) ──────────────────────
        self.panel_mano = PanelMano(self.partida)
        self.panel_mano.carta_jugada.connect(self._on_carta_jugada)
        self.panel_mano.carta_descartada.connect(self._on_carta_descartada)
        self.panel_mano.turno_pasado.connect(self._on_pasar_turno)
        layout.addWidget(self.panel_mano)

    # ── Barra superior ────────────────────────────────────────────────── #

    def _crear_barra(self) -> QWidget:
        barra = QWidget()
        lay = QHBoxLayout(barra)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lbl_titulo = QLabel("CATCH THE KILLER")
        lbl_titulo.setStyleSheet(
            f"color: {AMBAR}; font-size: 16px; letter-spacing: 6px; font-family: {MONO};"
        )
        lay.addWidget(lbl_titulo)
        lay.addSpacing(16)

        sep_v = QFrame()
        sep_v.setFrameShape(QFrame.VLine)
        sep_v.setStyleSheet(f"background: {GRIS_BORDE}; max-width: 1px;")
        lay.addWidget(sep_v)
        lay.addSpacing(16)

        lbl_dif = QLabel(self.partida.dificultad.value.upper())
        lbl_dif.setStyleSheet(
            f"color: {GRIS_TEXTO}; font-size: 10px; letter-spacing: 2px;"
        )
        lay.addWidget(lbl_dif)
        lay.addStretch()

        self.lbl_acciones = QLabel()
        self.lbl_acciones.setStyleSheet(
            f"color: {GRIS_TEXTO}; font-size: 10px; letter-spacing: 1px;"
        )
        lay.addWidget(self.lbl_acciones)
        lay.addSpacing(20)

        self.lbl_intentos = QLabel()
        self.lbl_intentos.setStyleSheet(
            f"color: {AMBAR}; font-size: 10px; letter-spacing: 1px;"
        )
        lay.addWidget(self.lbl_intentos)
        lay.addSpacing(20)

        self.lbl_victimas = QLabel()
        lay.addWidget(self.lbl_victimas)
        lay.addSpacing(20)

        btn_sala = QPushButton("⚑  SALA DE MANDO")
        btn_sala.setFixedHeight(30)
        btn_sala.setStyleSheet(f"""
            QPushButton {{
                background: {ROJO_OSCURO}; color: {BLANCO};
                border: 1px solid {ROJO}; border-radius: 2px;
                font-size: 10px; letter-spacing: 2px;
                font-family: {MONO}; padding: 0 14px;
            }}
            QPushButton:hover {{ background: {ROJO}; }}
        """)
        btn_sala.clicked.connect(self._abrir_sala_mando)
        lay.addWidget(btn_sala)

        self._actualizar_barra()
        return barra

    def _actualizar_barra(self):
        prox    = self.partida.proximas_acciones_para_nuevo()
        hay_mas = self.partida.hay_mas_crimenes()
        self.lbl_acciones.setText(
            f"ACCIONES: {self.partida.acciones}"
            + (f"  ·  PRÓXIMO EN: {prox}" if hay_mas else "")
        )
        self.lbl_intentos.setText(
            f"INTENTOS: {self.partida.intentos}/{self.partida.intentos_max}"
        )
        vic = self.partida.victimas
        color_v = ROJO if vic > 3 else AMBAR
        self.lbl_victimas.setText(f"VÍCTIMAS: {vic}")
        self.lbl_victimas.setStyleSheet(
            f"color: {color_v}; font-size: 10px; letter-spacing: 1px;"
        )

    # ── Selección de crimen ───────────────────────────────────────────── #

    def _on_crimen_seleccionado(self, idx: int):
        self._idx_crimen_sel = idx
        self.mapa.seleccionar(idx)
        self.panel_exp.mostrar_crimen(idx)
        self.panel_mano.set_crimen_seleccionado(idx)

    # ── Acciones de carta ─────────────────────────────────────────────── #

    def _on_carta_jugada(self, idx_carta: int):
        if self._idx_crimen_sel is None:
            return

        resultado = self.partida.jugar_carta(idx_carta, self._idx_crimen_sel)

        if not resultado.exito:
            self._dialogo(
                "CARTA NO JUGABLE",
                resultado.motivo_fallo,
                color=ROJO
            )
            return

        # Aviso de regeneración de mazo (penalización)
        if resultado.regenero_mazo:
            self._dialogo(
                "MAZO AGOTADO",
                "Se ha barajado el mazo de nuevo.\n"
                "Ha aparecido un nuevo crimen como penalización.",
                color=ROJO
            )

        self._actualizar_todo()

        if resultado.nuevo_crimen:
            self._notificar_nuevo_crimen()

    def _on_carta_descartada(self, idx_carta: int):
        exito, carta, motivo = self.partida.descartar_carta(idx_carta)
        if not exito:
            self._dialogo("DESCARTE FALLIDO", motivo, color=ROJO)
            return
        self.panel_mano.actualizar()

    def _on_pasar_turno(self):
        nuevo = self.partida.pasar_turno()
        self._actualizar_todo()
        if nuevo:
            self._notificar_nuevo_crimen()

    # ── Acciones de expediente ────────────────────────────────────────── #

    def _on_sospechoso(self, idx: int):
        self.partida.toggle_sospechoso(idx)
        self._actualizar_todo()

    def _on_archivar(self, idx: int):
        if self.partida.archivar(idx):
            self._idx_crimen_sel = None
            self.panel_exp.mostrar_vacio()
            self.mapa.deseleccionar()
            self.panel_mano.set_crimen_seleccionado(None)
            self._actualizar_todo()

    def _on_recuperar(self, idx: int):
        ok, nuevo = self.partida.recuperar(idx)
        if ok:
            self._actualizar_todo()
            if nuevo:
                self._notificar_nuevo_crimen()

    # ── Sala de mando / acusación ─────────────────────────────────────── #

    def _abrir_sala_mando(self):
        if self.partida.resuelta:
            return
        dialogo = SalaMando(self.partida, parent=self)
        if dialogo.exec() and dialogo.resultado:
            self._procesar_resultado(dialogo.resultado)

    def _procesar_resultado(self, resultado: dict):
        tipo = resultado["tipo"]
        if tipo in (ResultadoAcusacion.VICTORIA, ResultadoAcusacion.DERROTA_FINAL):
            self.partida_terminada.emit(self.partida.dossier())
        elif tipo == ResultadoAcusacion.FALLO_CON_INTENTO:
            fp = len(resultado["falsos_positivos"])
            ne = len(resultado["no_encontrados"])
            self._dialogo(
                "ACUSACIÓN FALLIDA",
                f"Tu acusación es incorrecta.\n\n"
                f"Falsos positivos: {fp}\n"
                f"Crímenes del asesino no identificados: {ne}\n\n"
                f"Intentos restantes: {resultado['intentos_restantes']}\n"
                f"El asesino ha cometido un nuevo crimen.",
                color=ROJO
            )
            self._actualizar_todo()
            if resultado.get("nuevo_crimen"):
                self._notificar_nuevo_crimen()

    # ── Actualización de UI ───────────────────────────────────────────── #

    def _actualizar_todo(self):
        self.mapa.actualizar()
        self.panel_arch.actualizar()
        self.panel_mano.actualizar()
        self._actualizar_barra()
        if self._idx_crimen_sel is not None:
            self.panel_exp.mostrar_crimen(self._idx_crimen_sel)
        else:
            self.panel_exp.refrescar()

    # ── Diálogos ─────────────────────────────────────────────────────── #

    def _dialogo(self, titulo: str, texto: str, color: str = AMBAR):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(titulo)
        dlg.setText(texto)
        dlg.setStyleSheet(f"""
            QMessageBox {{ background: {GRIS_OSCURO}; font-family: {MONO}; }}
            QLabel {{ color: {color}; font-size: 11px; }}
            QPushButton {{
                background: {GRIS_PANEL}; color: {AMBAR};
                border: 1px solid {AMBAR_OSCURO}; padding: 6px 16px;
                font-family: {MONO};
            }}
        """)
        dlg.exec()

    def _notificar_nuevo_crimen(self):
        self._dialogo(
            "NUEVO CRIMEN",
            "¡Alerta! Se ha reportado un nuevo homicidio.\n"
            "Ha aparecido un nuevo expediente en el mapa.",
            color=AMBAR
        )
