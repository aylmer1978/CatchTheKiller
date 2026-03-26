"""
core/mazo.py — Mazo de cartas del juego.

Modelo de turno (día):
  - Dentro de un día el jugador puede:
      · jugar N cartas (N=1 por defecto, modificable por evento REFUERZOS)
      · descartar 1 carta gratis
  - Al FINALIZAR DÍA: repone cartas hasta max_mano, resetea flags.
  - max_mano es 3 por defecto, modificable por eventos (BUROCRACIA=2, FINANCIACION=4).
  - Si el mazo se agota al reponer: se regenera con el descarte (penalización).

Distribución (24 cartas total):
  Investigar Expediente×3 | Investigar Caso×1
  Atributo Lugar/Franja/Arma/Víctima/Otros ×4 cada uno
"""

import random
from core.carta import Carta, TipoCarta

TAMANYO_MANO = 3

DISTRIBUCION = [
    (TipoCarta.INVESTIGAR_EXPEDIENTE, 3),
    (TipoCarta.INVESTIGAR_CASO,       1),
    (TipoCarta.ATRIBUTO_LUGAR,        4),
    (TipoCarta.ATRIBUTO_FRANJA,       4),
    (TipoCarta.ATRIBUTO_ARMA,         4),
    (TipoCarta.ATRIBUTO_VICTIMA,      4),
    (TipoCarta.ATRIBUTO_OTROS,        4),
]


def _construir_mazo() -> list[Carta]:
    cartas = []
    for tipo, cantidad in DISTRIBUCION:
        cartas.extend(Carta(tipo) for _ in range(cantidad))
    random.shuffle(cartas)
    return cartas


class Mazo:
    def __init__(self):
        self._mazo:     list[Carta] = _construir_mazo()
        self._descarte: list[Carta] = []
        self.mano:      list[Carta] = []

        # Tamaño máximo de mano (modificable por eventos)
        self.max_mano: int = TAMANYO_MANO

        # Cartas jugadas hoy / máximo permitido hoy (modificable por REFUERZOS)
        self._jugadas_hoy:     int = 0
        self._max_jugadas_hoy: int = 1

        # Flag: el jugador ya descartó gratis hoy
        self._descartado_hoy: bool = False

        # Contador de regeneraciones (cada una = penalización)
        self.regeneraciones: int = 0

        # Rellena la mano inicial
        self._reponer_hasta_max()

    # ── Consultas ─────────────────────────────────────────────────────── #

    def cartas_en_mazo(self) -> int:
        return len(self._mazo)

    def cartas_en_descarte(self) -> int:
        return len(self._descarte)

    def puede_jugar(self) -> bool:
        return self._jugadas_hoy < self._max_jugadas_hoy and len(self.mano) > 0

    def puede_descartar(self) -> bool:
        return not self._descartado_hoy and len(self.mano) > 0

    def jugadas_restantes(self) -> int:
        return max(0, self._max_jugadas_hoy - self._jugadas_hoy)

    def cartas_totales(self) -> int:
        return len(self._mazo) + len(self._descarte) + len(self.mano)

    # ── Robo interno ──────────────────────────────────────────────────── #

    def _robar_una(self) -> bool:
        """Roba una carta. Regenera si el mazo está vacío. Devuelve True si ok."""
        if not self._mazo:
            if not self._descarte:
                return False
            self._mazo = self._descarte[:]
            self._descarte = []
            random.shuffle(self._mazo)
            self.regeneraciones += 1

        if self._mazo:
            self.mano.append(self._mazo.pop())
            return True
        return False

    def _reponer_hasta_max(self) -> tuple[int, bool]:
        """
        Roba cartas hasta alcanzar self.max_mano.
        Devuelve (cartas_robadas, hubo_regeneracion).
        """
        robadas  = 0
        regen_ant = self.regeneraciones
        while len(self.mano) < self.max_mano:
            if not self._robar_una():
                break
            robadas += 1
        return robadas, self.regeneraciones > regen_ant

    # ── Acciones del jugador ──────────────────────────────────────────── #

    def jugar(self, indice_mano: int) -> Carta:
        """
        Juega la carta. Va al descarte. NO roba hasta finalizar el día.
        Lanza ValueError si ya se alcanzó el límite de jugadas hoy.
        """
        if self._jugadas_hoy >= self._max_jugadas_hoy:
            raise ValueError(
                f"Ya jugaste {self._jugadas_hoy} carta(s) hoy "
                f"(máximo: {self._max_jugadas_hoy})."
            )
        if not (0 <= indice_mano < len(self.mano)):
            raise IndexError(f"Índice de mano inválido: {indice_mano}")

        carta = self.mano.pop(indice_mano)
        self._descarte.append(carta)
        self._jugadas_hoy += 1
        return carta

    def descartar(self, indice_mano: int) -> Carta:
        """
        Descarte gratuito (una vez por día). NO roba hasta finalizar el día.
        Lanza ValueError si ya se descartó hoy.
        """
        if self._descartado_hoy:
            raise ValueError("Ya descartaste una carta hoy.")
        if not (0 <= indice_mano < len(self.mano)):
            raise IndexError(f"Índice de mano inválido: {indice_mano}")

        carta = self.mano.pop(indice_mano)
        self._descarte.append(carta)
        self._descartado_hoy = True
        return carta

    def finalizar_dia(
        self,
        max_mano_override: int | None = None,
        cartas_jugables:   int | None = None,
    ) -> tuple[int, bool]:
        """
        Finaliza el día:
          - Aplica modificadores del evento para el día siguiente.
          - Repone cartas hasta el nuevo max_mano.
          - Resetea flags de jugadas y descarte.
        Devuelve (cartas_robadas, hubo_regeneracion).
        """
        self.max_mano         = max_mano_override if max_mano_override is not None else TAMANYO_MANO
        self._max_jugadas_hoy = cartas_jugables   if cartas_jugables   is not None else 1

        # Si el nuevo max es menor que la mano actual, descartar el exceso
        while len(self.mano) > self.max_mano:
            carta = self.mano.pop()
            self._descarte.append(carta)

        robadas, regenero = self._reponer_hasta_max()

        self._descartado_hoy = False
        self._jugadas_hoy    = 0

        return robadas, regenero

    # ── Debug ─────────────────────────────────────────────────────────── #

    def __repr__(self) -> str:
        mano_str = ", ".join(str(c) for c in self.mano)
        return (
            f"Mazo(mazo={len(self._mazo)}, descarte={len(self._descarte)}, "
            f"regen={self.regeneraciones})\n"
            f"  Mano [{len(self.mano)}/{self.max_mano}]: [{mano_str}]\n"
            f"  jugadas={self._jugadas_hoy}/{self._max_jugadas_hoy}"
            f"  descartado={self._descartado_hoy}"
        )
