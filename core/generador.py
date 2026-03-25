"""
generador.py — Genera todos los crímenes de una partida.

Reglas de generación:
  1. Crímenes del asesino: comparten exactamente los 3 atributos de la firma.
     Los 2 atributos variables deben dar al menos 2 diferencias entre
     cualquier par de crímenes del asesino.

  2. Crímenes señuelo: completamente aleatorios, pero deben diferir en
     al menos 2 atributos de CUALQUIER otro crimen ya generado
     (asesino o señuelo). Esto evita confusión accidental con la firma.

  3. Número de crímenes del asesino: aleatorio entre min_asesino y max_asesino.
     Número de señuelos: aleatorio entre min_senuelo y max_senuelo.
"""

import random
from core.crimen import Crimen, ATRIBUTOS
from core.asesino import Asesino

# Límite de intentos para evitar bucles infinitos en casos de espacio agotado
MAX_INTENTOS = 10_000


def _diferencias(t1: tuple, t2: tuple) -> int:
    """Cuenta cuántos atributos difieren entre dos tuplas."""
    return sum(1 for a, b in zip(t1, t2) if a != b)


def _construir_crimen_asesino(asesino: Asesino) -> tuple:
    """Genera una tupla de valores para un crimen del asesino."""
    valores = {}
    for a in ATRIBUTOS:
        if a in asesino.atributos_firma:
            valores[a] = asesino.valores_firma[a]
        else:
            valores[a] = asesino.valor_aleatorio(a)
    return tuple(valores[a] for a in ATRIBUTOS)


def _construir_crimen_aleatorio(elementos: dict) -> tuple:
    """Genera una tupla de valores completamente aleatoria."""
    mapa = {
        "lugar":   "lugares",
        "franja":  "franjas",
        "arma":    "armas",
        "victima": "victimas",
        "otros":   "otros",
    }
    return tuple(random.choice(elementos[mapa[a]]) for a in ATRIBUTOS)


def _es_valido(candidato: tuple, existentes: list[tuple], min_difs: int) -> bool:
    """True si el candidato difiere en al menos min_difs de todos los existentes."""
    return all(_diferencias(candidato, e) >= min_difs for e in existentes)


# ------------------------------------------------------------------ #
#  Funciones públicas                                                  #
# ------------------------------------------------------------------ #

def generar_crimenes_asesino(
    asesino: Asesino,
    num: int,
    min_difs_entre_asesino: int = 1,
) -> list[Crimen]:
    """
    Genera 'num' crímenes del asesino.
    Entre ellos deben diferir al menos en min_difs_entre_asesino atributos
    (solo se aplica sobre los 2 atributos variables, así que 1 es suficiente).
    """
    generados: list[tuple] = []
    crimenes: list[Crimen] = []
    intentos = 0

    while len(generados) < num:
        if intentos > MAX_INTENTOS:
            raise RuntimeError(
                f"No se pudieron generar {num} crímenes del asesino "
                f"con {min_difs_entre_asesino} diferencias mínimas."
            )
        intentos += 1

        candidato = _construir_crimen_asesino(asesino)

        # Evitar duplicados exactos entre crímenes del asesino
        if candidato in generados:
            continue

        # Asegurarse de que difiere lo suficiente de los ya generados
        if not _es_valido(candidato, generados, min_difs_entre_asesino):
            continue

        generados.append(candidato)
        c = Crimen(*candidato)
        c.marcado_asesino = True
        crimenes.append(c)

    return crimenes


def generar_crimenes_senuelo(
    asesino: Asesino,
    elementos: dict,
    num: int,
    crimenes_existentes: list[Crimen],
    min_difs_global: int = 2,
) -> list[Crimen]:
    """
    Genera 'num' crímenes señuelo.
    Cada señuelo debe diferir en al menos min_difs_global atributos
    de CUALQUIER crimen ya en la partida (asesino + señuelos previos).
    """
    pool: list[tuple] = [c.como_tuple() for c in crimenes_existentes]
    crimenes: list[Crimen] = []
    intentos = 0

    while len(crimenes) < num:
        if intentos > MAX_INTENTOS:
            raise RuntimeError(
                f"No se pudieron generar {num} crímenes señuelo "
                f"con {min_difs_global} diferencias mínimas."
            )
        intentos += 1

        candidato = _construir_crimen_aleatorio(elementos)

        if not _es_valido(candidato, pool, min_difs_global):
            continue

        pool.append(candidato)
        c = Crimen(*candidato)
        c.marcado_asesino = False
        crimenes.append(c)

    return crimenes


def generar_partida(
    asesino: Asesino,
    elementos: dict,
    num_asesino: int | None = None,
    num_senuelo: int | None = None,
    rango_asesino: tuple[int, int] = (3, 5),
    rango_senuelo: tuple[int, int] = (4, 6),
) -> list[Crimen]:
    """
    Genera y mezcla todos los crímenes de una partida.

    Parámetros opcionales:
        num_asesino / num_senuelo: fija el número exacto (ignora rangos).
        rango_asesino / rango_senuelo: rango aleatorio si no se fija.

    Devuelve lista mezclada aleatoriamente.
    """
    n_asesino = num_asesino if num_asesino is not None else random.randint(*rango_asesino)
    n_senuelo = num_senuelo if num_senuelo is not None else random.randint(*rango_senuelo)

    crimenes_asesino = generar_crimenes_asesino(asesino, n_asesino)
    crimenes_senuelo = generar_crimenes_senuelo(asesino, elementos, n_senuelo, crimenes_asesino)

    todos = crimenes_asesino + crimenes_senuelo
    random.shuffle(todos)
    return todos
