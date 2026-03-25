"""
core/mazo.py — Mazo de cartas del juego.

Distribución (24 cartas total):
  - Investigar Expediente : ×3  (poco frecuente)
  - Investigar Caso       : ×1  (rara)
  - Atributo: Lugar       : ×4  )
  - Atributo: Franja      : ×4  )
  - Atributo: Arma        : ×4  ) frecuentes
  - Atributo: Víctima     : ×4  )
  - Atributo: Otros       : ×4  )

Reglas:
  - Mano de 3 cartas. Al jugar una se roba otra del mazo.
  - Descarte gratis una vez por turno: la carta va a pila de descarte.
  - Pasar turno: válido si no hay cartas jugables (cuenta como acción).
  - Al agotar el mazo: se baraja mazo + descarte de nuevo
    y aparece un crimen nuevo como penalización.
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

        # Estado de descarte por turno
        self._descartado_este_turno: bool = False

        # Contador de regeneraciones (cada una = penalización)
        self.regeneraciones: int = 0

        # Rellena la mano inicial
        for _ in range(TAMANYO_MANO):
            self._robar_a_mano()

    # ── Consultas ─────────────────────────────────────────────────────── #

    def cartas_en_mazo(self) -> int:
        return len(self._mazo)

    def cartas_en_descarte(self) -> int:
        return len(self._descarte)

    def puede_descartar(self) -> bool:
        return not self._descartado_este_turno and len(self.mano) > 0

    def cartas_totales(self) -> int:
        return len(self._mazo) + len(self._descarte) + len(self.mano)

    # ── Robo interno ──────────────────────────────────────────────────── #

    def _robar_a_mano(self) -> bool:
        """
        Roba una carta del mazo a la mano.
        Si el mazo está vacío, regenera (mazo + descarte) y registra penalización.
        Devuelve True si hubo regeneración.
        """
        regenero = False
        if not self._mazo:
            if not self._descarte:
                return False   # No hay cartas en ningún lado
            self._mazo = self._descarte[:]
            self._descarte = []
            random.shuffle(self._mazo)
            self.regeneraciones += 1
            regenero = True

        self.mano.append(self._mazo.pop())
        return regenero

    # ── Acciones del jugador ──────────────────────────────────────────── #

    def jugar(self, indice_mano: int) -> tuple[Carta, bool]:
        """
        Juega la carta en posición indice_mano de la mano.
        La envía al descarte y roba una nueva.
        Resetea el flag de descarte del turno.

        Devuelve (carta_jugada, hubo_regeneracion).
        """
        if not (0 <= indice_mano < len(self.mano)):
            raise IndexError(f"Índice de mano inválido: {indice_mano}")

        carta = self.mano.pop(indice_mano)
        self._descarte.append(carta)
        regenero = self._robar_a_mano()
        self._descartado_este_turno = False   # Nuevo turno, reset
        return carta, regenero

    def descartar(self, indice_mano: int) -> Carta:
        """
        Descarte gratuito (una vez por turno).
        La carta va a la pila de descarte y se roba una nueva.
        No resetea el flag de turno (solo se puede hacer una vez).

        Lanza ValueError si ya se descartó este turno.
        """
        if self._descartado_este_turno:
            raise ValueError("Ya se descartó una carta este turno.")
        if not (0 <= indice_mano < len(self.mano)):
            raise IndexError(f"Índice de mano inválido: {indice_mano}")

        carta = self.mano.pop(indice_mano)
        self._descarte.append(carta)
        self._robar_a_mano()
        self._descartado_este_turno = True
        return carta

    def pasar_turno(self) -> None:
        """
        Pasa el turno sin jugar carta.
        Resetea el flag de descarte para el siguiente turno.
        """
        self._descartado_este_turno = False

    def iniciar_turno(self) -> None:
        """
        Llamar al inicio de cada turno para resetear el estado de descarte.
        (Alternativa a hacerlo automáticamente en jugar/pasar.)
        """
        self._descartado_este_turno = False

    # ── Debug ─────────────────────────────────────────────────────────── #

    def __repr__(self) -> str:
        mano_str = ", ".join(str(c) for c in self.mano)
        return (
            f"Mazo(mazo={len(self._mazo)}, "
            f"descarte={len(self._descarte)}, "
            f"regeneraciones={self.regeneraciones})\n"
            f"  Mano: [{mano_str}]"
        )
