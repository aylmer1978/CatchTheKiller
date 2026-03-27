"""
partida.py — Estado completo de una partida en curso.

Modelo de día:
  - Dentro de un día: N cartas jugadas (default 1) + 0 o 1 descarte gratuito.
  - FINALIZAR DÍA: genera evento, aplica sus efectos, repone cartas.
  - Los eventos controlan cuándo aparecen crímenes nuevos (no hay ciclo fijo).
  - La garantía de nuevo crimen: a los 6 días sin crimen se fuerza el evento.
"""

import random
from enum import Enum
from core.crimen import Crimen, ATRIBUTOS
from core.asesino import Asesino
from core.generador import generar_crimenes_asesino, generar_crimenes_senuelo
from core.carta import Carta, TipoCarta, TIPOS_INV_PARALELA, PARALELA_A_ATRIBUTO
from core.mazo import Mazo
from core.evento import Evento, TipoEvento, generar_evento


# ── Dificultad ────────────────────────────────────────────────────────── #

class Dificultad(Enum):
    FACIL   = "Fácil"
    NORMAL  = "Normal"
    DIFICIL = "Difícil"

INTENTOS_POR_DIFICULTAD = {
    Dificultad.FACIL:   3,
    Dificultad.NORMAL:  2,
    Dificultad.DIFICIL: 1,
}

# Víctimas del asesino garantizadas entre los crímenes iniciales por dificultad
# (min, max) — el valor real se elige al azar dentro del rango
VICTIMAS_INICIALES = {
    Dificultad.FACIL:   (2, 2),   # siempre 2
    Dificultad.NORMAL:  (1, 2),   # 1 o 2, solo se comunica 1
    Dificultad.DIFICIL: (0, 2),   # 0, 1 o 2, no se comunica nada seguro
}

# Lo que se comunica al jugador en la intro (mínimo garantizado)
VICTIMAS_COMUNICADAS = {
    Dificultad.FACIL:   2,
    Dificultad.NORMAL:  1,
    Dificultad.DIFICIL: 0,
}

CRIMENES_INICIALES = {
    Dificultad.FACIL:   4,
    Dificultad.NORMAL:  5,
    Dificultad.DIFICIL: 6,
}
MIN_ATTRS_INICIALES = 3
MAX_ATTRS_INICIALES = 5
RANGO_ASESINO = (4, 7)
RANGO_SENUELO = (6, 10)

# Frases narrativas para el paso del día
FRASES_DIA = [
    "La ciudad duerme. Los archivos se acumulan sobre tu escritorio.",
    "Otro día termina sin respuestas. La lluvia golpea la ventana.",
    "Las luces de la comisaría se apagan una a una. Mañana seguirás.",
    "El café se ha enfriado hace horas. Cierras los expedientes por hoy.",
    "Las calles están vacías. En algún lugar ahí fuera, él también espera.",
    "Fin de jornada. Los datos siguen sin encajar del todo.",
    "Apagas el flexo. Las fotos del caso te siguen mirando desde el corcho.",
    "Otra noche sin detención. El reloj marca las 2 de la madrugada.",
    "Te frotas los ojos. El patrón está ahí, solo tienes que verlo.",
    "La ciudad nunca duerme del todo. Tú tampoco.",
    "Guardas los informes. Mañana los verás con ojos frescos.",
    "El turno ha terminado. El caso, no.",
]


class ResultadoAcusacion(Enum):
    VICTORIA          = "victoria"
    FALLO_CON_INTENTO = "fallo_con_intento"
    DERROTA_FINAL     = "derrota_final"


# Resultado de jugar una carta
class ResultadoCarta:
    def __init__(
        self,
        exito:          bool,
        carta:          Carta,
        atributos:      list[str],
        nuevo_crimen:   Crimen | None = None,
        regenero_mazo:  bool = False,
        motivo_fallo:   str = "",
        texto_paralela: str = "",
    ):
        self.exito          = exito
        self.carta          = carta
        self.atributos      = atributos
        self.nuevo_crimen   = nuevo_crimen
        self.regenero_mazo  = regenero_mazo
        self.motivo_fallo   = motivo_fallo
        self.texto_paralela = texto_paralela  # resultado de investigación paralela


class Partida:
    def __init__(self, asesino: Asesino, elementos: dict, dificultad: Dificultad = Dificultad.NORMAL):
        self.asesino    = asesino
        self.elementos  = elementos
        self.dificultad = dificultad

        self.intentos_max: int = INTENTOS_POR_DIFICULTAD[dificultad]
        self.intentos:     int = self.intentos_max

        # Generar pool completo
        n_asesino = random.randint(*RANGO_ASESINO)
        n_senuelo = random.randint(*RANGO_SENUELO)
        crimenes_asesino = generar_crimenes_asesino(asesino, n_asesino)
        crimenes_senuelo = generar_crimenes_senuelo(
            asesino, elementos, n_senuelo, crimenes_asesino
        )

        # Número de crímenes iniciales según dificultad
        n_iniciales = CRIMENES_INICIALES[dificultad]

        # Determinar cuántos crímenes del asesino aparecen entre los iniciales
        min_vic, max_vic = VICTIMAS_INICIALES[dificultad]
        max_vic = min(max_vic, len(crimenes_asesino))
        self.victimas_iniciales_reales: int = random.randint(min_vic, max_vic)
        self.victimas_comunicadas: int = VICTIMAS_COMUNICADAS[dificultad]

        # Construir los primeros n_iniciales con el número correcto del asesino
        random.shuffle(crimenes_asesino)
        random.shuffle(crimenes_senuelo)

        n_vic = self.victimas_iniciales_reales
        n_sen = n_iniciales - n_vic
        primeros = crimenes_asesino[:n_vic] + crimenes_senuelo[:n_sen]
        random.shuffle(primeros)

        resto = crimenes_asesino[n_vic:] + crimenes_senuelo[n_sen:]
        random.shuffle(resto)

        self._pool: list[Crimen] = primeros + resto

        self._posiciones: dict[int, tuple[int, int]] = self._asignar_posiciones()
        self._siguiente_idx: int = n_iniciales

        self.dias:           int = 1
        self.dias_sin_crimen: int = 0
        self.victimas:       int = 0
        self.historial_victimas: list[dict] = []

        # Cartas recibidas del asesino (para releer después)
        self.cartas_asesino: list[tuple[int, str, str]] = []
        # Cada entrada: (dia, asunto, cuerpo)

        self.resuelta: bool = False
        self.victoria: bool = False

        # Mazo de cartas
        self.mazo = Mazo()

        # Hacer visibles los primeros n_iniciales crímenes
        for i in range(min(n_iniciales, len(self._pool))):
            self._hacer_visible(i)

    # ── Setup ─────────────────────────────────────────────────────────── #

    def _asignar_posiciones(self) -> dict[int, tuple[int, int]]:
        cols, filas = 8, 6
        todas = [(c, f) for c in range(cols) for f in range(filas)]
        random.shuffle(todas)
        return {i: todas[i] for i in range(len(self._pool))}

    def _hacer_visible(self, idx: int) -> None:
        crimen = self._pool[idx]
        crimen.visible_en_mapa = True
        # Revelar 2 atributos aleatorios al aparecer el crimen
        attrs_a_revelar = random.sample(list(ATRIBUTOS), 2)
        for a in attrs_a_revelar:
            crimen.revelar(a)
        if crimen.marcado_asesino:
            self.victimas += 1
            self.historial_victimas.append({
                "victima": crimen.victima,
                "lugar":   crimen.lugar,
                "franja":  crimen.franja,
                "idx":     idx,
            })
        self.dias_sin_crimen = 0

    # ── Consultas ─────────────────────────────────────────────────────── #

    def crimenes_en_mapa(self) -> list[tuple[int, Crimen]]:
        return [(i, c) for i, c in enumerate(self._pool)
                if c.visible_en_mapa and not c.archivado]

    def crimenes_archivados(self) -> list[tuple[int, Crimen]]:
        return [(i, c) for i, c in enumerate(self._pool) if c.archivado]

    def posicion(self, idx: int) -> tuple[int, int]:
        return self._posiciones[idx]

    def crimen(self, idx: int) -> Crimen:
        return self._pool[idx]

    def hay_mas_crimenes(self) -> bool:
        return self._siguiente_idx < len(self._pool)

    def indices_asesino_visibles(self) -> set[int]:
        return {i for i, c in enumerate(self._pool)
                if c.marcado_asesino and c.visible_en_mapa}

    def sospechosos(self) -> list[tuple[int, Crimen]]:
        return [(i, c) for i, c in enumerate(self._pool) if c.sospechoso]

    def carta_usable_en(self, idx_carta: int, idx_crimen: int | None) -> tuple[bool, str]:
        """
        Comprueba si la carta idx_carta se puede jugar.
        Las cartas de investigación paralela no requieren crimen (idx_crimen=None).
        """
        if not (0 <= idx_carta < len(self.mazo.mano)):
            return False, "Índice de carta inválido."

        carta = self.mazo.mano[idx_carta]

        # Cartas de investigación paralela: siempre jugables (no necesitan crimen)
        if carta.es_inv_paralela():
            return True, ""

        # El resto requieren crimen seleccionado
        if idx_crimen is None:
            return False, "Selecciona un expediente primero."

        crimen = self._pool[idx_crimen]
        if not crimen.visible_en_mapa or crimen.archivado:
            return False, "El expediente no está disponible."
        if crimen.todos_revelados():
            return False, "Este expediente ya está completamente revelado."

        if carta.es_atributo_especifico():
            if carta.atributo in crimen.campos_revelados:
                return False, f"El atributo '{carta.atributo}' ya está revelado."

        return True, ""

    # ── Acciones de juego ─────────────────────────────────────────────── #

    def _aplicar_carta(self, carta: Carta, idx_crimen: int | None) -> tuple[list[str], str]:
        """
        Aplica el efecto de la carta.
        Devuelve (atributos_revelados, texto_resultado).
        texto_resultado es solo relevante para cartas paralelas.
        """
        # ── Investigación paralela: revela un valor que NO es la firma ──
        if carta.es_inv_paralela():
            attr = PARALELA_A_ATRIBUTO[carta.tipo]
            valor_firma = self.asesino.valores_firma.get(attr)
            clave_json = {
                "lugar":   "lugares",
                "franja":  "franjas",
                "arma":    "armas",
                "victima": "victimas",
                "otros":   "otros",
            }[attr]
            # Elegir un valor aleatorio que NO sea el de la firma para ese atributo
            candidatos = [v for v in self.elementos[clave_json] if v != valor_firma]
            if candidatos:
                valor_descartado = random.choice(candidatos)
                from core.crimen import ETIQUETAS
                attr_label = ETIQUETAS.get(attr, attr)
                texto = (
                    f"Investigación paralela — {attr_label}\n\n"
                    f"Las pruebas descartan:\n"
                    f"«{valor_descartado}»\n\n"
                    f"Este valor NO forma parte\n"
                    f"de la firma del asesino."
                )
            else:
                texto = "No se encontraron datos concluyentes."
            return [], texto

        # ── Cartas normales sobre un crimen ─────────────────────────────
        if idx_crimen is None:
            return [], ""

        crimen = self._pool[idx_crimen]
        a_revelar: list[str] = []

        if carta.tipo == TipoCarta.INVESTIGAR_EXPEDIENTE:
            ocultos = crimen.atributos_ocultos()
            n = random.randint(MIN_ATTRS_INICIALES,
                               min(MAX_ATTRS_INICIALES, len(ocultos)))
            a_revelar = random.sample(ocultos, min(n, len(ocultos)))
        elif carta.tipo == TipoCarta.INVESTIGAR_CASO:
            a_revelar = crimen.atributos_ocultos()
        elif carta.es_atributo_especifico():
            if carta.atributo not in crimen.campos_revelados:
                a_revelar = [carta.atributo]

        for a in a_revelar:
            crimen.revelar(a)
        return a_revelar, ""

    def jugar_carta(self, idx_carta: int, idx_crimen: int | None) -> ResultadoCarta:
        """
        Juega la carta idx_carta.
        Para cartas normales, idx_crimen debe apuntar al expediente objetivo.
        Para cartas de investigación paralela, idx_crimen puede ser None.
        """
        if self.resuelta:
            carta_ref = self.mazo.mano[idx_carta] if idx_carta < len(self.mazo.mano) else None
            return ResultadoCarta(False, carta_ref, [], motivo_fallo="La partida ya está resuelta.")

        if not self.mazo.puede_jugar():
            carta_ref = self.mazo.mano[idx_carta]
            return ResultadoCarta(False, carta_ref, [], motivo_fallo="Ya jugaste una carta hoy.")

        usable, motivo = self.carta_usable_en(idx_carta, idx_crimen)
        if not usable:
            carta_ref = self.mazo.mano[idx_carta]
            return ResultadoCarta(False, carta_ref, [], motivo_fallo=motivo)

        carta = self.mazo.mano[idx_carta]
        atributos, texto_paralela = self._aplicar_carta(carta, idx_crimen)
        self.mazo.jugar(idx_carta)

        return ResultadoCarta(
            exito=True,
            carta=carta,
            atributos=atributos,
            texto_paralela=texto_paralela,
        )

    def descartar_carta(self, idx_carta: int) -> tuple[bool, Carta | None, str]:
        """Descarte gratuito (una vez por día). No roba hasta finalizar el día."""
        if self.resuelta:
            return False, None, "La partida ya está resuelta."
        if not self.mazo.puede_descartar():
            return False, None, "Ya descartaste una carta hoy."
        try:
            carta = self.mazo.descartar(idx_carta)
            return True, carta, ""
        except (ValueError, IndexError) as e:
            return False, None, str(e)

    def finalizar_dia(self) -> dict:
        """
        Finaliza el día:
          1. Genera un evento aleatorio según el contexto.
          2. Aplica sus efectos sobre la partida.
          3. Repone cartas (con modificadores del evento).

        Devuelve un dict con:
          frase        — texto narrativo del paso del día
          dia_nuevo    — número del nuevo día
          evento       — objeto Evento con todos sus datos
          regenero_mazo— bool
        """
        if self.resuelta:
            return {}

        self.dias += 1
        self.dias_sin_crimen += 1

        # ── Contexto para el generador de eventos ─────────────────────
        crimenes_investigados = [
            (i, c) for i, c in enumerate(self._pool)
            if c.visible_en_mapa and not c.archivado and c.campos_revelados
        ]
        senuelos_visibles = [
            (i, c) for i, c in enumerate(self._pool)
            if c.visible_en_mapa and not c.archivado and not c.marcado_asesino
        ]

        # ── Generar evento ─────────────────────────────────────────────
        evento = generar_evento(
            dias_sin_crimen       = self.dias_sin_crimen,
            crimenes_investigados = crimenes_investigados,
            senuelos_visibles     = senuelos_visibles,
            hay_crimenes_en_pool  = self.hay_mas_crimenes(),
        )

        # ── Aplicar efectos del evento ─────────────────────────────────
        if evento.tipo == TipoEvento.NUEVO_CRIMEN:
            if self.hay_mas_crimenes():
                self._hacer_visible(self._siguiente_idx)
                self._siguiente_idx += 1

        elif evento.tipo == TipoEvento.ERROR_POLICIAL:
            if evento.idx_crimen_afectado is not None:
                crimen = self._pool[evento.idx_crimen_afectado]
                for attr in evento.atributos_borrados:
                    crimen.campos_revelados.discard(attr)

        elif evento.tipo == TipoEvento.CRIMEN_RESUELTO:
            if evento.idx_crimen_afectado is not None:
                self._pool[evento.idx_crimen_afectado].archivado = True

        # BUROCRACIA, FINANCIACION, REFUERZOS se aplican al reponer cartas

        # Guardar cartas del asesino para releer
        if evento.tipo == TipoEvento.COMUNICACION_ASESINO and evento.carta_asesino:
            asunto, cuerpo = evento.carta_asesino
            self.cartas_asesino.append((self.dias, asunto, cuerpo))

        # ── Reponer cartas con modificadores del evento ────────────────
        _, regenero = self.mazo.finalizar_dia(
            max_mano_override = evento.max_mano_override,
            cartas_jugables   = evento.cartas_jugables,
        )

        # Penalización por regeneración del mazo → crimen extra
        if regenero and self.hay_mas_crimenes():
            self._hacer_visible(self._siguiente_idx)
            self._siguiente_idx += 1

        return {
            "frase":         random.choice(FRASES_DIA),
            "dia_nuevo":     self.dias,
            "evento":        evento,
            "regenero_mazo": regenero,
        }

    def archivar(self, idx: int) -> bool:
        """Descarta un crimen al panel de archivados. Sin coste de acción."""
        crimen = self._pool[idx]
        if not crimen.visible_en_mapa or crimen.archivado or crimen.sospechoso:
            return False
        crimen.archivado = True
        return True

    def recuperar(self, idx: int) -> bool:
        """Recupera un crimen archivado al mapa. Sin coste adicional."""
        crimen = self._pool[idx]
        if not crimen.archivado:
            return False
        crimen.archivado = False
        return True

    def toggle_sospechoso(self, idx: int) -> bool:
        crimen = self._pool[idx]
        if crimen.archivado:
            return False
        crimen.sospechoso = not crimen.sospechoso
        return True

    # ── Acusación ─────────────────────────────────────────────────────── #

    def valores_investigados(self) -> dict[str, set[str]]:
        """
        Devuelve todos los valores únicos descubiertos por atributo
        en los crímenes visibles. Útil para poblar los desplegables
        de la sala de mando con pistas reales.
        Formato: {"lugar": {"Cementerio", "Bosque"}, "arma": {...}, ...}
        """
        encontrados: dict[str, set[str]] = {a: set() for a in ATRIBUTOS}
        for _, crimen in self.crimenes_en_mapa():
            for attr in crimen.campos_revelados:
                encontrados[attr].add(crimen.valor(attr))
        return encontrados

    def acusar(self, modus_operandi: dict[str, str]) -> dict:
        """
        El jugador declara su hipótesis del modus operandi del asesino.

        modus_operandi: exactamente 3 entradas {atributo: valor}
            Ejemplo: {"lugar": "Cementerio", "arma": "Cuchillo", "franja": "Noche"}

        Validaciones previas (devuelven "error"):
            - La partida ya está resuelta
            - Sin intentos disponibles
            - No se declaran exactamente 3 atributos distintos

        Evaluación:
            - Victoria si modus_operandi == asesino.valores_firma exactamente
            - Fallo si no coincide
        """
        if self.resuelta:
            return {"error": "La partida ya está resuelta."}
        if self.intentos <= 0:
            return {"error": "Sin intentos de acusación disponibles."}
        if len(modus_operandi) != 3:
            return {"error": f"Debes declarar exactamente 3 rasgos (declarados: {len(modus_operandi)})."}
        if len(set(modus_operandi.keys())) != 3:
            return {"error": "Los 3 rasgos deben ser atributos distintos."}
        for attr in modus_operandi:
            if attr not in ATRIBUTOS:
                return {"error": f"Atributo desconocido: '{attr}'."}

        firma_real = self.asesino.valores_firma   # {attr: valor}
        es_correcto = (modus_operandi == firma_real)

        # Desglose por rasgo para el feedback
        aciertos_rasgo  = {a: v for a, v in modus_operandi.items() if firma_real.get(a) == v}
        fallos_atributo = {a: v for a, v in modus_operandi.items() if firma_real.get(a) != v}
        no_declarados   = {a: v for a, v in firma_real.items() if a not in modus_operandi}

        self.intentos -= 1
        self._ultimo_modus = modus_operandi   # para el dossier
        nuevo_crimen = None

        if es_correcto:
            self.victoria = True
            self.resuelta = True
            tipo = ResultadoAcusacion.VICTORIA
        elif self.intentos <= 0:
            self.victoria = False
            self.resuelta = True
            tipo = ResultadoAcusacion.DERROTA_FINAL
        else:
            if self.hay_mas_crimenes():
                nuevo_idx = self._siguiente_idx
                self._hacer_visible(nuevo_idx)
                self._siguiente_idx += 1
                nuevo_crimen = self._pool[nuevo_idx]
            tipo = ResultadoAcusacion.FALLO_CON_INTENTO

        return {
            "tipo":               tipo,
            "victoria":           es_correcto,
            "intentos_restantes": self.intentos,
            "modus_declarado":    modus_operandi,
            "firma_real":         firma_real,
            "aciertos_rasgo":     aciertos_rasgo,
            "fallos_atributo":    fallos_atributo,
            "no_declarados":      no_declarados,
            "nuevo_crimen":       nuevo_crimen,
        }

    # ── Dossier final ─────────────────────────────────────────────────── #

    def dossier(self) -> dict:
        return {
            "nombre_prensa":          self.asesino.nombre_prensa(),
            "firma":                  self.asesino.resumen_firma(),
            "atributos_firma":        self.asesino.atributos_firma,
            "modus_declarado":        getattr(self, '_ultimo_modus', None),
            "dificultad":             self.dificultad.value,
            "victoria":               self.victoria,
            "total_victimas":         self.victimas,
            "victimas_iniciales":     self.victimas_iniciales_reales,
            "victimas_comunicadas":   self.victimas_comunicadas,
            "historial_victimas":     self.historial_victimas,
            "intentos_usados":        self.intentos_max - self.intentos,
            "intentos_max":           self.intentos_max,
            "dias_totales":           self.dias,
            "cartas_jugadas":         self.mazo.cartas_en_descarte(),
            "regeneraciones_mazo":    self.mazo.regeneraciones,
            "crimenes_vistos":        len([c for c in self._pool if c.visible_en_mapa]),
            "crimenes_pool":          len(self._pool),
        }

    # ── Debug ─────────────────────────────────────────────────────────── #

    def imprimir_estado(self, revelar_todo: bool = False) -> None:
        print(f"\n{'='*65}")
        print(f"  [{self.dificultad.value}]  pool:{len(self._pool)}"
              f"  visibles:{len(self.crimenes_en_mapa())}"
              f"  archivados:{len(self.crimenes_archivados())}")
        print(f"  Asesino: {self.asesino.nombre_prensa()!r}")
        print(f"  Firma: {self.asesino.resumen_firma()}")
        print(f"  Día:{self.dias}  Víctimas:{self.victimas}"
              f"  Intentos:{self.intentos}/{self.intentos_max}")
        print(f"  {self.mazo}")
        print(f"{'='*65}")
        for i, c in enumerate(self._pool):
            if not c.visible_en_mapa:
                continue
            marca = "★" if c.marcado_asesino else " "
            arch  = "A" if c.archivado       else " "
            sosp  = "⚑" if c.sospechoso      else " "
            rev   = f"{len(c.campos_revelados)}/5"
            datos = c.como_dict() if revelar_todo else c.vista()
            pos   = self._posiciones[i]
            print(f"  [{marca}{arch}{sosp}] #{i:02d} ({rev}) pos={pos} {datos}")
        print()
