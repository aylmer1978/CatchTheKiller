"""
core/mazo.py — Mazo de cartas del juego.

Modelo de turno (día):
  - Dentro de un día el jugador puede hacer 0 o 1 de cada:
      · jugar una carta (la consume, NO roba hasta el día siguiente)
      · descartar una carta gratis (la pierde, NO roba hasta el día siguiente)
  - Al pulsar FINALIZAR DÍA: se reponen las cartas hasta 3 robando del mazo.
  - Si el mazo se agota al reponer: se baraja mazo + descarte (penalización).

Distribución (24 cartas total):
  Investigar Expediente : ×3  |  Investigar Caso : ×1
  Atributo Lugar/Franja/Arma/Víctima/Otros : ×4 cada uno
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
        self._mazo:    list[Carta] = _construir_mazo()
        self._descarte: list[Carta] = []
        self.mano:     list[Carta] = []

        # Flag: el jugador ya descartó gratis hoy
        self._descartado_hoy: bool = False

        # Flag: el jugador ya jugó una carta hoy
        self._jugado_hoy: bool = False

        # Contador de regeneraciones de mazo (cada una = penalización)
        self.regeneraciones: int = 0

        # Rellena la mano inicial
        self._reponer_hasta_tres()

    # ── Consultas ─────────────────────────────────────────────────────── #

    def cartas_en_mazo(self) -> int:
        return len(self._mazo)

    def cartas_en_descarte(self) -> int:
        return len(self._descarte)

    def puede_descartar(self) -> bool:
        return not self._descartado_hoy and len(self.mano) > 0

    def puede_jugar(self) -> bool:
        return not self._jugado_hoy and len(self.mano) > 0

    def cartas_totales(self) -> int:
        return len(self._mazo) + len(self._descarte) + len(self.mano)

    # ── Robo interno ──────────────────────────────────────────────────── #

    def _robar_una(self) -> bool:
        """
        Roba una carta del mazo a la mano.
        Si el mazo está vacío, regenera con la pila de descarte.
        Devuelve True si hubo regeneración.
        """
        if not self._mazo:
            if not self._descarte:
                return False
            self._mazo = self._descarte[:]
            self._descarte = []
            random.shuffle(self._mazo)
            self.regeneraciones += 1

        if self._mazo:
            self.mano.append(self._mazo.pop())
            return self.regeneraciones > 0  # True si acabamos de regenerar
        return False

    def _reponer_hasta_tres(self) -> tuple[int, bool]:
        """
        Roba cartas hasta tener TAMANYO_MANO en mano.
        Devuelve (cartas_robadas, hubo_regeneracion).
        """
        robadas = 0
        regenero = False
        while len(self.mano) < TAMANYO_MANO:
            antes = self.regeneraciones
            ok = self._robar_una()
            if self.regeneraciones > antes:
                regenero = True
            if not ok and len(self._mazo) == 0 and len(self._descarte) == 0:
                break  # No quedan cartas en ningún lado
            robadas += 1
        return robadas, regenero

    # ── Acciones del jugador ──────────────────────────────────────────── #

    def jugar(self, indice_mano: int) -> Carta:
        """
        Juega la carta en posición indice_mano.
        La carta va al descarte. NO se roba nueva hasta finalizar el día.
        Solo se puede jugar una carta por día.

        Lanza ValueError si ya se jugó hoy.
        """
        if self._jugado_hoy:
            raise ValueError("Ya jugaste una carta hoy.")
        if not (0 <= indice_mano < len(self.mano)):
            raise IndexError(f"Índice de mano inválido: {indice_mano}")

        carta = self.mano.pop(indice_mano)
        self._descarte.append(carta)
        self._jugado_hoy = True
        return carta

    def descartar(self, indice_mano: int) -> Carta:
        """
        Descarte gratuito (una vez por día).
        La carta va al descarte. NO se roba nueva hasta finalizar el día.

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

    def finalizar_dia(self) -> tuple[int, bool]:
        """
        Finaliza el día: repone cartas hasta 3 y resetea los flags.
        Devuelve (cartas_robadas, hubo_regeneracion_de_mazo).
        """
        robadas, regenero = _reponer_hasta_tres = self._reponer_hasta_tres()
        self._descartado_hoy = False
        self._jugado_hoy     = False
        return robadas, regenero

    # ── Debug ─────────────────────────────────────────────────────────── #

    def __repr__(self) -> str:
        mano_str = ", ".join(str(c) for c in self.mano)
        return (
            f"Mazo(mazo={len(self._mazo)}, descarte={len(self._descarte)}, "
            f"regen={self.regeneraciones})\n"
            f"  Mano [{len(self.mano)}]: [{mano_str}]\n"
            f"  jugado_hoy={self._jugado_hoy}  descartado_hoy={self._descartado_hoy}"
        )
