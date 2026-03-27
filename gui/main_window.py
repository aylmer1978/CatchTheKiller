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
from gui.pantalla_intro   import PantallaIntro
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
        self.setMinimumSize(1280, 920)
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
        self._partida_pendiente = Partida(asesino, self.elementos, dificultad)
        intro = PantallaIntro(self._partida_pendiente)
        intro.partida_lista.connect(self._mostrar_juego)
        self._stack.addWidget(intro)
        self._stack.setCurrentWidget(intro)

    def _mostrar_juego(self):
        pantalla = PantallaJuego(self._partida_pendiente)
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

        # ── Cuerpo central (con scroll horizontal de seguridad) ──────────
        from PySide6.QtWidgets import QScrollArea
        cuerpo_widget = QWidget()
        cuerpo = QHBoxLayout(cuerpo_widget)
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

        # Scroll horizontal de seguridad
        scroll_cuerpo = QScrollArea()
        scroll_cuerpo.setWidget(cuerpo_widget)
        scroll_cuerpo.setWidgetResizable(True)
        scroll_cuerpo.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_cuerpo.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(scroll_cuerpo, stretch=1)

        # ── Panel de mano (inferior) ──────────────────────
        self.panel_mano = PanelMano(self.partida)
        self.panel_mano.carta_jugada.connect(self._on_carta_jugada)
        self.panel_mano.carta_descartada.connect(self._on_carta_descartada)
        self.panel_mano.dia_finalizado.connect(self._on_finalizar_dia)
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
        self.lbl_acciones.setText(f"DÍA {self.partida.dias}")
        self.lbl_intentos.setText(
            f"INTENTOS: {self.partida.intentos}/{self.partida.intentos_max}"
        )

    # ── Selección de crimen ───────────────────────────────────────────── #

    def _on_crimen_seleccionado(self, idx: int):
        self._idx_crimen_sel = idx
        self.mapa.seleccionar(idx)
        self.panel_exp.mostrar_crimen(idx)
        self.panel_mano.set_crimen_seleccionado(idx)

    # ── Acciones de carta ─────────────────────────────────────────────── #

    def _on_carta_jugada(self, idx_carta: int):
        from core.carta import TIPOS_INV_PARALELA
        carta = self.partida.mazo.mano[idx_carta] if idx_carta < len(self.partida.mazo.mano) else None

        # Cartas paralelas no necesitan crimen seleccionado
        es_paralela = carta and carta.tipo in TIPOS_INV_PARALELA
        idx_crimen = None if es_paralela else self._idx_crimen_sel

        if not es_paralela and idx_crimen is None:
            return

        resultado = self.partida.jugar_carta(idx_carta, idx_crimen)

        if not resultado.exito:
            self._dialogo("CARTA NO JUGABLE", resultado.motivo_fallo, color=ROJO)
            return

        # Mostrar resultado de investigación paralela
        if resultado.texto_paralela:
            self._dialogo("INVESTIGACION PARALELA", resultado.texto_paralela, color=VERDE)

        if resultado.regenero_mazo:
            self._dialogo(
                "MAZO AGOTADO",
                "Se ha barajado el mazo de nuevo.\n"
                "Ha aparecido un nuevo crimen como penalizacion.",
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

    def _on_finalizar_dia(self):
        resultado = self.partida.finalizar_dia()
        if not resultado:
            return

        # Diálogo narrativo del paso del día
        self._dialogo_dia(resultado)
        self._actualizar_todo()

    def _dialogo_dia(self, resultado: dict):
        """Muestra el diálogo de fin de día con frase narrativa y evento."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        from core.evento import TipoEvento

        evento   = resultado.get("evento")
        dia_ant  = resultado["dia_nuevo"] - 1

        dlg = QDialog(self)
        dlg.setWindowTitle(f"DÍA {dia_ant} — FIN DE JORNADA")
        dlg.setFixedWidth(440)
        dlg.setStyleSheet(f"""
            QDialog {{ background: {GRIS_OSCURO}; font-family: {MONO}; }}
            QLabel  {{ border: none; }}
        """)

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(12)

        # Número de día
        lbl_dia = QLabel(f"— FIN DEL DÍA {dia_ant} —")
        lbl_dia.setAlignment(Qt.AlignCenter)
        lbl_dia.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 9px; letter-spacing: 4px;")
        lay.addWidget(lbl_dia)

        # Frase narrativa
        lbl_frase = QLabel(f'"{resultado["frase"]}"')
        lbl_frase.setWordWrap(True)
        lbl_frase.setAlignment(Qt.AlignCenter)
        lbl_frase.setStyleSheet(f"""
            color: {AMBAR};
            font-size: 12px;
            font-style: italic;

        """)
        lay.addWidget(lbl_frase)

        # Evento del día
        if evento:
            sep = QFrame()
            sep.setStyleSheet(f"background: {GRIS_BORDE}; max-height: 1px;")
            lay.addWidget(sep)

            # Color según tipo de evento
            color_ev = {
                TipoEvento.NUEVO_CRIMEN:         ROJO,
                TipoEvento.ERROR_POLICIAL:        ROJO,
                TipoEvento.CRIMEN_RESUELTO:       VERDE,
                TipoEvento.NARRATIVO:             GRIS_TEXTO,
                TipoEvento.COMUNICACION_ASESINO:  AMBAR,
                TipoEvento.BUROCRACIA:            ROJO,
                TipoEvento.FINANCIACION:          VERDE,
                TipoEvento.REFUERZOS:             VERDE,
            }.get(evento.tipo, GRIS_TEXTO)

            lbl_ev_tit = QLabel(f"{evento.icono}  {evento.titulo}")
            lbl_ev_tit.setStyleSheet(f"""
                color: {color_ev};
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 2px;
            """)
            lay.addWidget(lbl_ev_tit)

            lbl_ev_txt = QLabel(evento.texto)
            lbl_ev_txt.setWordWrap(True)
            lbl_ev_txt.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 10px;")
            lay.addWidget(lbl_ev_txt)

            # Modificadores mecánicos
            if evento.modifica_mano:
                n = evento.max_mano_override
                txt = f"Mañana recibirás {n} carta{'s' if n != 1 else ''}."
                lbl_mod = QLabel(f"→  {txt}")
                lbl_mod.setStyleSheet(f"color: {color_ev}; font-size: 10px; font-style: italic;")
                lay.addWidget(lbl_mod)
            if evento.da_refuerzos:
                lbl_ref = QLabel(f"→  Mañana podrás jugar {evento.cartas_jugables} cartas.")
                lbl_ref.setStyleSheet(f"color: {VERDE}; font-size: 10px; font-style: italic;")
                lay.addWidget(lbl_ref)

        # Penalización mazo
        if resultado.get("regenero_mazo"):
            lbl_pen = QLabel("⚠  El mazo se ha agotado. Ha aparecido un nuevo crimen.")
            lbl_pen.setWordWrap(True)
            lbl_pen.setStyleSheet(f"color: {ROJO}; font-size: 10px;")
            lay.addWidget(lbl_pen)

        # Separador y nuevo día
        sep2 = QFrame()
        sep2.setStyleSheet(f"background: {GRIS_BORDE}; max-height: 1px;")
        lay.addWidget(sep2)

        lbl_nuevo = QLabel(f"DÍA {resultado['dia_nuevo']} — SE REPONEN LAS CARTAS")
        lbl_nuevo.setAlignment(Qt.AlignCenter)
        lbl_nuevo.setStyleSheet(f"color: {VERDE}; font-size: 9px; letter-spacing: 3px;")
        lay.addWidget(lbl_nuevo)

        btn = QPushButton("CONTINUAR")
        btn.setFixedHeight(34)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {AMBAR_OSCURO}; color: {BLANCO};
                border: 1px solid {AMBAR}; border-radius: 2px;
                font-size: 10px; letter-spacing: 3px; font-family: {MONO};
            }}
            QPushButton:hover {{ background: {AMBAR}; color: {NEGRO}; }}
        """)
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)

        dlg.exec()

        # Si es comunicación del asesino, mostrar pantalla especial después
        if evento and evento.tipo == TipoEvento.COMUNICACION_ASESINO and evento.carta_asesino:
            self._mostrar_carta_asesino(evento.carta_asesino)

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
        ok = self.partida.recuperar(idx)
        if ok:
            self._actualizar_todo()

    # ── Sala de mando / acusación ─────────────────────────────────────── #

    def _abrir_sala_mando(self):
        if self.partida.resuelta:
            return
        dialogo = SalaMando(self.partida, self.partida.elementos, parent=self)
        if dialogo.exec() and dialogo.resultado:
            self._procesar_resultado(dialogo.resultado)

    def _procesar_resultado(self, resultado: dict):
        tipo = resultado["tipo"]
        if tipo in (ResultadoAcusacion.VICTORIA, ResultadoAcusacion.DERROTA_FINAL):
            self.partida_terminada.emit(self.partida.dossier())
        elif tipo == ResultadoAcusacion.FALLO_CON_INTENTO:
            aciertos = len(resultado["aciertos_rasgo"])
            fallos   = len(resultado["fallos_atributo"])
            self._dialogo(
                "MODUS OPERANDI INCORRECTO",
                f"Tu hipótesis no coincide con la firma del asesino.\n\n"
                f"Rasgos acertados: {aciertos} / 3\n"
                f"Rasgos fallados:  {fallos}\n\n"
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

    def _mostrar_carta_asesino(self, carta: tuple):
        """Pantalla especial con estética de carta manuscrita."""
        asunto, cuerpo = carta
        _dialogo_carta_asesino(self, asunto, cuerpo)


def _dialogo_carta_asesino(parent, asunto: str, cuerpo: str):
    """Diálogo de carta del asesino, usable desde cualquier widget."""
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
    dlg = QDialog(parent)
    dlg.setWindowTitle("COMUNICACIÓN ANÓNIMA — CLASIFICADO")
    dlg.setFixedWidth(480)
    dlg.setStyleSheet(f"""
        QDialog {{
            background-color: #1a1508;
            font-family: 'Courier New', monospace;
            border: 2px solid {AMBAR_OSCURO};
        }}
        QLabel {{ border: none; }}
    """)

    lay = QVBoxLayout(dlg)
    lay.setContentsMargins(32, 28, 32, 28)
    lay.setSpacing(16)

    lbl_clasificado = QLabel("— DOCUMENTO CLASIFICADO — USO INTERNO —")
    lbl_clasificado.setAlignment(Qt.AlignCenter)
    lbl_clasificado.setStyleSheet(f"color: {ROJO}; font-size: 8px; letter-spacing: 4px;")
    lay.addWidget(lbl_clasificado)

    sep_top = QFrame()
    sep_top.setStyleSheet(f"background: {AMBAR_OSCURO}; max-height: 1px;")
    lay.addWidget(sep_top)

    lbl_para = QLabel("PARA:  Departamento de Homicidios\nDE:    Remitente desconocido")
    lbl_para.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 9px;")
    lay.addWidget(lbl_para)

    lbl_asunto = QLabel(f"ASUNTO:  {asunto}")
    lbl_asunto.setStyleSheet(f"color: {AMBAR}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
    lay.addWidget(lbl_asunto)

    sep_mid = QFrame()
    sep_mid.setStyleSheet(f"background: {AMBAR_OSCURO}; max-height: 1px;")
    lay.addWidget(sep_mid)

    lbl_cuerpo = QLabel(cuerpo)
    lbl_cuerpo.setWordWrap(True)
    lbl_cuerpo.setStyleSheet(f"""
        color: #d4c9a0;
        font-size: 13px;
        font-style: italic;

        padding: 8px 0;
    """)
    lay.addWidget(lbl_cuerpo)

    sep_bot = QFrame()
    sep_bot.setStyleSheet(f"background: {AMBAR_OSCURO}; max-height: 1px;")
    lay.addWidget(sep_bot)

    lbl_nota = QLabel(
        "⚠  Sin huellas. Sin sello postal. Entregada en mano.\n"
        "El laboratorio forense no ha encontrado evidencias utilizables."
    )
    lbl_nota.setWordWrap(True)
    lbl_nota.setStyleSheet(f"color: {GRIS_TEXTO}; font-size: 9px;")
    lay.addWidget(lbl_nota)

    btn = QPushButton("ARCHIVAR COMUNICACIÓN")
    btn.setFixedHeight(34)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent; color: {AMBAR_OSCURO};
            border: 1px solid {AMBAR_OSCURO}; border-radius: 2px;
            font-size: 9px; letter-spacing: 3px; font-family: {MONO};
        }}
        QPushButton:hover {{ color: {AMBAR}; border-color: {AMBAR}; }}
    """)
    btn.clicked.connect(dlg.accept)
    lay.addWidget(btn)

    dlg.exec()
