"""
partida.py — Estado completo de una partida en curso.

Modelo de día:
  - Dentro de un día: 0 o 1 carta jugada + 0 o 1 descarte gratuito.
  - FINALIZAR DÍA: avanza el tiempo, repone cartas hasta 3.
  - Cada 3 días → nuevo crimen aparece al inicio del nuevo día.
  - Al regenerar el mazo al reponer → penalización: crimen nuevo extra.
"""

import random
from enum import Enum
from core.crimen import Crimen, ATRIBUTOS
from core.asesino import Asesino
from core.generador import generar_crimenes_asesino, generar_crimenes_senuelo
from core.carta import Carta, TipoCarta
from core.mazo import Mazo


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

CRIMENES_INICIALES = 5
DIAS_POR_CRIMEN   = 3      # cada N días completos aparece un crimen nuevo
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
    ):
        self.exito         = exito
        self.carta         = carta
        self.atributos     = atributos        # atributos revelados
        self.nuevo_crimen  = nuevo_crimen     # crimen que apareció en el mapa, si hay
        self.regenero_mazo = regenero_mazo   # si el mazo se regeneró (penalización)
        self.motivo_fallo  = motivo_fallo


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
        self._pool: list[Crimen] = crimenes_asesino + crimenes_senuelo
        random.shuffle(self._pool)

        self._posiciones: dict[int, tuple[int, int]] = self._asignar_posiciones()
        self._siguiente_idx: int = CRIMENES_INICIALES

        self.dias:    int = 1       # día actual (empieza en 1)
        self.victimas: int = 0
        self.historial_victimas: list[dict] = []

        self.resuelta: bool = False
        self.victoria: bool = False

        # Mazo de cartas
        self.mazo = Mazo()

        # Hacer visibles los primeros N crímenes
        for i in range(min(CRIMENES_INICIALES, len(self._pool))):
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
        if crimen.marcado_asesino:
            self.victimas += 1
            self.historial_victimas.append({
                "victima": crimen.victima,
                "lugar":   crimen.lugar,
                "franja":  crimen.franja,
                "idx":     idx,
            })

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

    def proximos_dias_para_nuevo(self) -> int:
        """Días que faltan para que aparezca el próximo crimen."""
        return DIAS_POR_CRIMEN - ((self.dias - 1) % DIAS_POR_CRIMEN)

    def indices_asesino_visibles(self) -> set[int]:
        return {i for i, c in enumerate(self._pool)
                if c.marcado_asesino and c.visible_en_mapa}

    def sospechosos(self) -> list[tuple[int, Crimen]]:
        return [(i, c) for i, c in enumerate(self._pool) if c.sospechoso]

    def carta_usable_en(self, idx_carta: int, idx_crimen: int) -> tuple[bool, str]:
        """
        Comprueba si la carta idx_carta se puede jugar en el crimen idx_crimen.
        Devuelve (usable, motivo_si_no).
        """
        if not (0 <= idx_carta < len(self.mazo.mano)):
            return False, "Índice de carta inválido."

        crimen = self._pool[idx_crimen]
        if not crimen.visible_en_mapa or crimen.archivado:
            return False, "El expediente no está disponible."
        if crimen.todos_revelados():
            return False, "Este expediente ya está completamente revelado."

        carta = self.mazo.mano[idx_carta]

        # Para cartas de atributo específico: comprobar que ese atributo no esté ya revelado
        if carta.es_atributo_especifico():
            if carta.atributo in crimen.campos_revelados:
                return False, f"El atributo '{carta.atributo}' ya está revelado."

        return True, ""

    # ── Acciones de juego ─────────────────────────────────────────────── #

    def _aplicar_carta(self, carta: Carta, idx_crimen: int) -> list[str]:
        """Aplica el efecto de la carta. Devuelve atributos revelados."""
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
        return a_revelar

    def jugar_carta(self, idx_carta: int, idx_crimen: int) -> ResultadoCarta:
        """
        Juega la carta idx_carta sobre el crimen idx_crimen.
        La carta se consume. NO se roba nueva hasta finalizar el día.
        Solo se puede jugar una carta por día.
        """
        if self.resuelta:
            return ResultadoCarta(False, self.mazo.mano[idx_carta], [],
                                  motivo_fallo="La partida ya está resuelta.")
        if not self.mazo.puede_jugar():
            return ResultadoCarta(False, self.mazo.mano[idx_carta], [],
                                  motivo_fallo="Ya jugaste una carta hoy.")

        usable, motivo = self.carta_usable_en(idx_carta, idx_crimen)
        if not usable:
            return ResultadoCarta(False, self.mazo.mano[idx_carta], [],
                                  motivo_fallo=motivo)

        carta = self.mazo.mano[idx_carta]
        atributos = self._aplicar_carta(carta, idx_crimen)
        self.mazo.jugar(idx_carta)

        return ResultadoCarta(exito=True, carta=carta, atributos=atributos)

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
          1. Avanza el contador de días.
          2. Si toca (cada DIAS_POR_CRIMEN), hace aparecer un crimen nuevo.
          3. Repone cartas hasta 3 robando del mazo.
          4. Si el mazo se regenera al reponer → penalización: crimen extra.

        Devuelve:
          frase        — texto narrativo del paso del día
          dia_nuevo    — número del nuevo día
          nuevo_crimen — crimen que apareció por ciclo de días (o None)
          penalizacion — crimen extra por regeneración del mazo (o None)
          regenero_mazo — bool
        """
        if self.resuelta:
            return {}

        self.dias += 1

        # ¿Toca nuevo crimen por ciclo de días?
        nuevo_por_ciclo: Crimen | None = None
        if (self.dias - 1) % DIAS_POR_CRIMEN == 0 and self.hay_mas_crimenes():
            nuevo_idx = self._siguiente_idx
            self._hacer_visible(nuevo_idx)
            self._siguiente_idx += 1
            nuevo_por_ciclo = self._pool[nuevo_idx]

        # Reponer cartas (puede regenerar el mazo)
        _, regenero = self.mazo.finalizar_dia()

        # ¿Penalización por regeneración del mazo?
        nuevo_por_regen: Crimen | None = None
        if regenero and self.hay_mas_crimenes():
            nuevo_idx = self._siguiente_idx
            self._hacer_visible(nuevo_idx)
            self._siguiente_idx += 1
            nuevo_por_regen = self._pool[nuevo_idx]

        return {
            "frase":         random.choice(FRASES_DIA),
            "dia_nuevo":     self.dias,
            "nuevo_crimen":  nuevo_por_ciclo,
            "penalizacion":  nuevo_por_regen,
            "regenero_mazo": regenero,
        }

    def archivar(self, idx: int) -> bool:
        """Descarta un crimen al panel de archivados. Sin coste de acción."""
        crimen = self._pool[idx]
        if not crimen.visible_en_mapa or crimen.archivado or crimen.sospechoso:
            return False
        crimen.archivado = True
        return True

    def recuperar(self, idx: int) -> tuple[bool, Crimen | None]:
        """
        Recupera un crimen archivado al mapa. Cuenta como acción.
        """
        crimen = self._pool[idx]
        if not crimen.archivado:
            return False, None
        crimen.archivado = False
        nuevo = self._registrar_accion()
        return True, nuevo

    def toggle_sospechoso(self, idx: int) -> bool:
        crimen = self._pool[idx]
        if crimen.archivado:
            return False
        crimen.sospechoso = not crimen.sospechoso
        return True

    # ── Acusación ─────────────────────────────────────────────────────── #

    def acusar(self) -> dict:
        if self.resuelta:
            return {"error": "La partida ya está resuelta."}
        if self.intentos <= 0:
            return {"error": "Sin intentos de acusación disponibles."}

        reales   = self.indices_asesino_visibles()
        acusados = {i for i, c in enumerate(self._pool) if c.sospechoso}

        aciertos         = acusados & reales
        falsos_positivos = acusados - reales
        no_encontrados   = reales - acusados
        es_correcto      = (acusados == reales)

        self.intentos -= 1
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
            "acusados":           sorted(acusados),
            "reales":             sorted(reales),
            "aciertos":           sorted(aciertos),
            "falsos_positivos":   sorted(falsos_positivos),
            "no_encontrados":     sorted(no_encontrados),
            "nuevo_crimen":       nuevo_crimen,
        }

    # ── Dossier final ─────────────────────────────────────────────────── #

    def dossier(self) -> dict:
        return {
            "nombre_prensa":       self.asesino.nombre_prensa(),
            "firma":               self.asesino.resumen_firma(),
            "atributos_firma":     self.asesino.atributos_firma,
            "dificultad":          self.dificultad.value,
            "victoria":            self.victoria,
            "total_victimas":      self.victimas,
            "historial_victimas":  self.historial_victimas,
            "intentos_usados":     self.intentos_max - self.intentos,
            "intentos_max":        self.intentos_max,
            "dias_totales":        self.dias,
            "cartas_jugadas":      self.mazo.cartas_en_descarte(),
            "regeneraciones_mazo": self.mazo.regeneraciones,
            "crimenes_vistos":     len([c for c in self._pool if c.visible_en_mapa]),
            "crimenes_pool":       len(self._pool),
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
