"""
core/evento.py — Sistema de eventos al finalizar el día.

Tipos de evento:
  NUEVO_CRIMEN         — Aparece un nuevo expediente en el mapa
  ERROR_POLICIAL       — Se borran los atributos de un crimen investigado
  CRIMEN_RESUELTO      — Un señuelo se archiva como resuelto
  NARRATIVO            — Solo texto, sin efecto mecánico
  COMUNICACION_ASESINO — El asesino envía una carta anónima (rara)
  BUROCRACIA           — Próximo día: máximo de mano = 2
  FINANCIACION         — Próximo día: máximo de mano = 4
  REFUERZOS            — Próximo día: puede jugar 2 cartas

Garantía de nuevo crimen:
  Se lleva un contador de días sin crimen nuevo.
  A partir del día 3 sin crimen, el peso de NUEVO_CRIMEN sube linealmente
  hasta ser el único evento posible al llegar al día 6.
"""

import random
from dataclasses import dataclass, field
from enum import Enum, auto


class TipoEvento(Enum):
    NUEVO_CRIMEN         = auto()
    ERROR_POLICIAL       = auto()
    CRIMEN_RESUELTO      = auto()
    NARRATIVO            = auto()
    COMUNICACION_ASESINO = auto()
    BUROCRACIA           = auto()
    FINANCIACION         = auto()
    REFUERZOS            = auto()


# ── Contenido narrativo ───────────────────────────────────────────────── #

TITULOS = {
    TipoEvento.NUEVO_CRIMEN:         "NUEVO HOMICIDIO",
    TipoEvento.ERROR_POLICIAL:       "ERROR POLICIAL",
    TipoEvento.CRIMEN_RESUELTO:      "CASO CERRADO",
    TipoEvento.NARRATIVO:            "PARTE DIARIO",
    TipoEvento.COMUNICACION_ASESINO: "COMUNICACIÓN ANÓNIMA",
    TipoEvento.BUROCRACIA:           "PROBLEMAS BUROCRÁTICOS",
    TipoEvento.FINANCIACION:         "FINANCIACIÓN PRIVADA",
    TipoEvento.REFUERZOS:            "REFUERZOS",
}

ICONOS = {
    TipoEvento.NUEVO_CRIMEN:         "🔪",
    TipoEvento.ERROR_POLICIAL:       "⚠️",
    TipoEvento.CRIMEN_RESUELTO:      "✓",
    TipoEvento.NARRATIVO:            "📰",
    TipoEvento.COMUNICACION_ASESINO: "✉️",
    TipoEvento.BUROCRACIA:           "📋",
    TipoEvento.FINANCIACION:         "💰",
    TipoEvento.REFUERZOS:            "🔫",
}

TEXTOS_NARRATIVO = [
    "Los periódicos siguen cubriendo el caso. La presión mediática aumenta.",
    "Una reunión tensa con el comisario. Quiere resultados antes de fin de mes.",
    "El forense ha terminado los análisis. Nada nuevo que no supieras ya.",
    "Un confidente anónimo llamó, pero colgó antes de decir nada.",
    "Otro día sin avances visibles. La ciudad empieza a perder la fe.",
    "El departamento de comunicación pide prudencia. Nada de filtraciones.",
    "Revisas los archivos una vez más. El patrón sigue ahí, esquivo.",
    "Tu jefe te recuerda que el reloj corre. Tú ya lo sabes.",
    "Un reportero te sigue desde el aparcamiento. Le ignoras.",
    "Las redes sociales especulan con el caso. Nada útil.",
]

TEXTOS_ERROR = [
    "Un agente novato etiquetó mal las pruebas. Parte del expediente es ilegible.",
    "El sistema informático ha fallado. Algunos datos se han corrompido.",
    "Un testigo ha retractado su declaración. Hay que revisar el expediente.",
    "Una filtración interna ha comprometido parte de las pruebas.",
    "El laboratorio forense informa de una contaminación de muestras.",
]

TEXTOS_RESUELTO = [
    "El fiscal ha determinado que este caso no está relacionado con el asesino en serie.",
    "Nuevas pruebas apuntan a un sospechoso local ya detenido. Caso cerrado.",
    "El análisis forense descarta cualquier conexión con los otros crímenes.",
    "La investigación paralela ha concluido: este crimen tiene otro autor.",
    "Confesión del culpable. Este expediente queda oficialmente cerrado.",
]

TEXTOS_BUROCRACIA = [
    "Auditoría interna. La mitad del departamento está en reuniones todo el día.",
    "Presupuesto recortado hasta nuevo aviso. Recursos limitados.",
    "El juez ha paralizado parte de la investigación por un tecnicismo legal.",
    "Problemas con la cadena de custodia. Solo lo esencial hoy.",
    "La fiscalía requiere documentación adicional. Día improductivo.",
]

TEXTOS_FINANCIACION = [
    "Una fundación privada ha aportado fondos para la investigación.",
    "El ayuntamiento ha desbloqueado recursos extraordinarios para el caso.",
    "Un empresario anónimo ha financiado refuerzos temporales.",
    "Donación anónima al departamento. El comisario no hace preguntas.",
    "Subvención estatal aprobada con carácter urgente.",
]

TEXTOS_REFUERZOS = [
    "Dos inspectores de la unidad especial se incorporan temporalmente.",
    "El FBI ha cedido un analista para el caso. Mañana es tuyo.",
    "Refuerzos desde la capital. Un día de trabajo doble.",
    "El comisario ha llamado a todos los disponibles. Oportunidad.",
    "Interpol ha enviado un enlace. Aprovecha su experiencia mañana.",
]

CARTAS_ASESINO = [
    (
        "Ya sabes que soy yo",
        "Lo veo en tus ojos cuando revisas los expedientes.\n"
        "Sigues sin ver el hilo que los une.\n"
        "Quizás mañana."
    ),
    (
        "Un pequeño regalo",
        "He dejado algo para ti en el último caso.\n"
        "¿Lo has encontrado ya?\n"
        "Te ayuda, si sabes mirar."
    ),
    (
        "¿Cuánto tiempo más?",
        "Cada día que pasa es uno más para mí.\n"
        "Y uno menos para ti.\n"
        "El patrón siempre ha estado ahí."
    ),
    (
        "Sobre tus métodos",
        "He leído los periódicos.\n"
        "Tu departamento no me merece.\n"
        "Tú quizás sí."
    ),
    (
        "Una pista gratuita",
        "No te lo digo por bondad.\n"
        "Te lo digo porque el juego es más interesante así.\n"
        "Tres cosas siempre iguales. ¿Las ves?"
    ),
]


# ── Modelo de evento ──────────────────────────────────────────────────── #

@dataclass
class Evento:
    tipo:        TipoEvento
    titulo:      str
    icono:       str
    texto:       str

    # Datos específicos según el tipo (rellenados por el generador)
    idx_crimen_afectado: int | None      = None   # ERROR_POLICIAL, CRIMEN_RESUELTO
    atributos_borrados:  list[str]       = field(default_factory=list)  # ERROR_POLICIAL
    carta_asesino:       tuple | None    = None   # COMUNICACION_ASESINO (asunto, cuerpo)

    # Modificadores para el día siguiente
    max_mano_override:   int | None      = None   # BUROCRACIA(2) / FINANCIACION(4)
    cartas_jugables:     int | None      = None   # REFUERZOS(2)

    @property
    def tiene_efecto_mecanico(self) -> bool:
        return self.tipo not in (TipoEvento.NARRATIVO,)

    @property
    def modifica_mano(self) -> bool:
        return self.max_mano_override is not None

    @property
    def da_refuerzos(self) -> bool:
        return self.cartas_jugables is not None


# ── Generador de eventos ──────────────────────────────────────────────── #

# Pesos base (NUEVO_CRIMEN se gestiona por separado con el contador)
PESOS_BASE = {
    TipoEvento.ERROR_POLICIAL:       10,
    TipoEvento.CRIMEN_RESUELTO:      10,
    TipoEvento.NARRATIVO:            10,
    TipoEvento.COMUNICACION_ASESINO:  2,   # rara
    TipoEvento.BUROCRACIA:           10,
    TipoEvento.FINANCIACION:         10,
    TipoEvento.REFUERZOS:            10,
}

# El NUEVO_CRIMEN se fuerza entre el día 3 y 6 sin crimen
DIAS_MIN_NUEVO_CRIMEN = 3
DIAS_MAX_NUEVO_CRIMEN = 6


def generar_evento(
    dias_sin_crimen: int,
    crimenes_investigados: list[tuple[int, object]],  # (idx, Crimen) con atributos
    senuelos_visibles:    list[tuple[int, object]],   # (idx, Crimen) señuelos
    hay_crimenes_en_pool: bool,
) -> Evento:
    """
    Genera el evento del día según el contexto actual de la partida.

    dias_sin_crimen: días transcurridos desde el último crimen nuevo
    crimenes_investigados: crímenes con al menos 1 atributo revelado
    senuelos_visibles: señuelos visibles no archivados
    hay_crimenes_en_pool: si quedan crímenes por aparecer
    """

    # ── Calcular peso de NUEVO_CRIMEN ──────────────────────────────────
    peso_nuevo = 0
    if hay_crimenes_en_pool:
        if dias_sin_crimen >= DIAS_MAX_NUEVO_CRIMEN:
            # Forzado: es el único evento posible
            return _crear_evento_nuevo_crimen()
        elif dias_sin_crimen >= DIAS_MIN_NUEVO_CRIMEN:
            # Peso creciente desde el día 3
            t = (dias_sin_crimen - DIAS_MIN_NUEVO_CRIMEN) / (
                DIAS_MAX_NUEVO_CRIMEN - DIAS_MIN_NUEVO_CRIMEN
            )
            peso_nuevo = int(10 + t * 90)  # 10 en día 3, 100 en día 6

    # ── Filtrar eventos posibles ───────────────────────────────────────
    pesos = dict(PESOS_BASE)

    # ERROR_POLICIAL solo si hay crímenes investigados
    if not crimenes_investigados:
        pesos.pop(TipoEvento.ERROR_POLICIAL, None)

    # CRIMEN_RESUELTO solo si hay señuelos visibles
    if not senuelos_visibles:
        pesos.pop(TipoEvento.CRIMEN_RESUELTO, None)

    if peso_nuevo > 0:
        pesos[TipoEvento.NUEVO_CRIMEN] = peso_nuevo
    elif not hay_crimenes_en_pool:
        pesos.pop(TipoEvento.NUEVO_CRIMEN, None)

    # ── Selección ponderada ────────────────────────────────────────────
    tipos   = list(pesos.keys())
    weights = list(pesos.values())
    tipo = random.choices(tipos, weights=weights, k=1)[0]

    return _crear_evento(tipo, crimenes_investigados, senuelos_visibles)


def _crear_evento_nuevo_crimen() -> Evento:
    return Evento(
        tipo=TipoEvento.NUEVO_CRIMEN,
        titulo=TITULOS[TipoEvento.NUEVO_CRIMEN],
        icono=ICONOS[TipoEvento.NUEVO_CRIMEN],
        texto="Se ha reportado un nuevo homicidio en la ciudad.",
    )


def _crear_evento(
    tipo: TipoEvento,
    crimenes_investigados: list,
    senuelos_visibles: list,
) -> Evento:
    titulo = TITULOS[tipo]
    icono  = ICONOS[tipo]

    if tipo == TipoEvento.NUEVO_CRIMEN:
        return _crear_evento_nuevo_crimen()

    if tipo == TipoEvento.ERROR_POLICIAL:
        idx, crimen = random.choice(crimenes_investigados)
        # Borrar entre 1 y todos los atributos revelados
        revelados = list(crimen.campos_revelados)
        n_borrar  = random.randint(1, len(revelados))
        borrados  = random.sample(revelados, n_borrar)
        return Evento(
            tipo=tipo, titulo=titulo, icono=icono,
            texto=random.choice(TEXTOS_ERROR),
            idx_crimen_afectado=idx,
            atributos_borrados=borrados,
        )

    if tipo == TipoEvento.CRIMEN_RESUELTO:
        idx, _ = random.choice(senuelos_visibles)
        return Evento(
            tipo=tipo, titulo=titulo, icono=icono,
            texto=random.choice(TEXTOS_RESUELTO),
            idx_crimen_afectado=idx,
        )

    if tipo == TipoEvento.NARRATIVO:
        return Evento(
            tipo=tipo, titulo=titulo, icono=icono,
            texto=random.choice(TEXTOS_NARRATIVO),
        )

    if tipo == TipoEvento.COMUNICACION_ASESINO:
        carta = random.choice(CARTAS_ASESINO)
        return Evento(
            tipo=tipo, titulo=titulo, icono=icono,
            texto="Ha llegado una carta anónima al departamento.",
            carta_asesino=carta,
        )

    if tipo == TipoEvento.BUROCRACIA:
        return Evento(
            tipo=tipo, titulo=titulo, icono=icono,
            texto=random.choice(TEXTOS_BUROCRACIA),
            max_mano_override=2,
        )

    if tipo == TipoEvento.FINANCIACION:
        return Evento(
            tipo=tipo, titulo=titulo, icono=icono,
            texto=random.choice(TEXTOS_FINANCIACION),
            max_mano_override=4,
        )

    if tipo == TipoEvento.REFUERZOS:
        return Evento(
            tipo=tipo, titulo=titulo, icono=icono,
            texto=random.choice(TEXTOS_REFUERZOS),
            cartas_jugables=2,
        )

    # Fallback
    return Evento(tipo=tipo, titulo=titulo, icono=icono,
                  texto="Fin de jornada.")
