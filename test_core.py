"""test_core.py — Tests del core v4 (modelo de días)."""

import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.asesino import Asesino, APODOS_PRENSA
from core.carta import Carta, TipoCarta
from core.mazo import Mazo, TAMANYO_MANO
from core.partida import (
    Partida, Dificultad, ResultadoAcusacion, ResultadoCarta,
    CRIMENES_INICIALES, DIAS_POR_CRIMEN, FRASES_DIA
)

def cargar():
    with open("data/elementos.json", encoding="utf-8") as f:
        return json.load(f)

def ok(msg):      print(f"  ✓ {msg}")
def seccion(msg): print(f"\n── {msg} ──")


def test_mazo_no_roba_al_jugar(elementos):
    seccion("TEST 1: Jugar carta NO roba nueva")
    mazo = Mazo()
    cartas_antes = len(mazo.mano)
    assert cartas_antes == TAMANYO_MANO

    mazo.jugar(0)
    assert len(mazo.mano) == TAMANYO_MANO - 1, \
        f"Mano debería tener {TAMANYO_MANO-1}, tiene {len(mazo.mano)}"
    ok(f"Tras jugar: mano={len(mazo.mano)} (bajó de {TAMANYO_MANO})")


def test_mazo_no_roba_al_descartar(elementos):
    seccion("TEST 2: Descartar NO roba nueva")
    mazo = Mazo()
    mazo.descartar(0)
    assert len(mazo.mano) == TAMANYO_MANO - 1
    ok(f"Tras descartar: mano={len(mazo.mano)}")


def test_mazo_una_carta_por_dia(elementos):
    seccion("TEST 3: Solo una carta jugada y un descarte por día")
    mazo = Mazo()
    mazo.jugar(0)
    assert not mazo.puede_jugar(), "No debería poder jugar dos veces"

    mazo.descartar(0)
    assert not mazo.puede_descartar(), "No debería poder descartar dos veces"

    try:
        mazo.jugar(0)
        assert False, "Debería lanzar ValueError"
    except ValueError:
        pass

    try:
        mazo.descartar(0)
        assert False, "Debería lanzar ValueError"
    except ValueError:
        pass
    ok("Bloques correctos tras jugar y descartar")


def test_mazo_finalizar_dia_repone(elementos):
    seccion("TEST 4: finalizar_dia() repone hasta 3")
    mazo = Mazo()
    mazo.jugar(0)
    mazo.descartar(0)
    assert len(mazo.mano) == 1

    robadas, _ = mazo.finalizar_dia()
    assert len(mazo.mano) == TAMANYO_MANO
    assert robadas == 2
    assert mazo.puede_jugar()
    assert mazo.puede_descartar()
    ok(f"Repuso {robadas} cartas, mano={len(mazo.mano)}, flags reseteados")


def test_mazo_finalizar_sin_accion(elementos):
    seccion("TEST 5: finalizar_dia() sin haber jugado ni descartado")
    mazo = Mazo()
    robadas, _ = mazo.finalizar_dia()
    assert robadas == 0
    assert len(mazo.mano) == TAMANYO_MANO
    ok("Sin acciones: no roba cartas, mano intacta")


def test_jugar_carta_partida(elementos):
    seccion("TEST 6: jugar_carta() en partida")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)
    idx_crimen = partida.crimenes_en_mapa()[0][0]

    partida.mazo.mano[0] = Carta(TipoCarta.INVESTIGAR_CASO)
    res = partida.jugar_carta(0, idx_crimen)

    assert res.exito
    assert len(res.atributos) == 5
    assert len(partida.mazo.mano) == TAMANYO_MANO - 1  # NO robó
    ok("INVESTIGAR_CASO revela 5 attrs, mano bajó a 2")

    # Segunda carta ese mismo día debe fallar
    res2 = partida.jugar_carta(0, idx_crimen)
    assert not res2.exito
    ok(f"Segunda carta bloqueada: '{res2.motivo_fallo}'")


def test_descartar_partida(elementos):
    seccion("TEST 7: descartar_carta() en partida")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)

    exito, carta, _ = partida.descartar_carta(0)
    assert exito
    assert len(partida.mazo.mano) == TAMANYO_MANO - 1
    ok("Descarte OK, mano bajó a 2")

    exito2, _, motivo = partida.descartar_carta(0)
    assert not exito2
    ok(f"Segundo descarte bloqueado: '{motivo}'")


def test_finalizar_dia_partida(elementos):
    seccion("TEST 8: finalizar_dia() en partida")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)

    # Jugar y descartar
    idx = partida.crimenes_en_mapa()[0][0]
    partida.mazo.mano[0] = Carta(TipoCarta.INVESTIGAR_CASO)
    partida.jugar_carta(0, idx)
    partida.descartar_carta(0)
    assert len(partida.mazo.mano) == 1

    resultado = partida.finalizar_dia()
    assert resultado["dia_nuevo"] == 2
    assert resultado["frase"] in FRASES_DIA
    assert len(partida.mazo.mano) == TAMANYO_MANO
    ok(f"Día finalizado: día={resultado['dia_nuevo']}, mano={len(partida.mazo.mano)}")


def test_nuevo_crimen_cada_3_dias(elementos):
    seccion("TEST 9: Nuevo crimen al inicio del día 4, 7, 10...")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)
    iniciales = len(partida.crimenes_en_mapa())

    # Finalizar 3 días → en el día 4 debe aparecer crimen
    nuevo_encontrado = None
    for _ in range(3):
        r = partida.finalizar_dia()
        if r.get("nuevo_crimen"):
            nuevo_encontrado = r["nuevo_crimen"]

    assert nuevo_encontrado is not None or not partida.hay_mas_crimenes(), \
        "Debería haber aparecido un crimen al llegar al día 4"
    ok(f"Crimen nuevo tras 3 días: {nuevo_encontrado is not None}")


def test_flujo_completo_dia(elementos):
    seccion("TEST 10: Flujo completo día a día")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos, Dificultad.FACIL)

    for dia in range(1, 4):
        # Jugar una carta
        if partida.mazo.mano and partida.crimenes_en_mapa():
            idx_c = partida.crimenes_en_mapa()[0][0]
            partida.mazo.mano[0] = Carta(TipoCarta.INVESTIGAR_CASO)
            partida.jugar_carta(0, idx_c)
        # Descartar una
        if partida.mazo.mano:
            partida.descartar_carta(0)
        # Finalizar día
        r = partida.finalizar_dia()
        assert r["dia_nuevo"] == dia + 1
        assert len(partida.mazo.mano) == TAMANYO_MANO

    ok(f"3 días completados, día actual: {partida.dias}, mano: {len(partida.mazo.mano)}")


def test_dossier_con_dias(elementos):
    seccion("TEST 11: Dossier incluye días")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos, Dificultad.NORMAL)

    partida.finalizar_dia()
    partida.finalizar_dia()

    for idx in partida.indices_asesino_visibles():
        partida.toggle_sospechoso(idx)
    partida.acusar()

    d = partida.dossier()
    assert "dias_totales" in d
    assert d["dias_totales"] == 3
    ok(f"Dossier: {d['dias_totales']} días, {d['total_victimas']} víctimas")


if __name__ == "__main__":
    print("=" * 55)
    print("  CATCH THE KILLER — Test del Core v4")
    print("=" * 55)

    elementos = cargar()
    test_mazo_no_roba_al_jugar(elementos)
    test_mazo_no_roba_al_descartar(elementos)
    test_mazo_una_carta_por_dia(elementos)
    test_mazo_finalizar_dia_repone(elementos)
    test_mazo_finalizar_sin_accion(elementos)
    test_jugar_carta_partida(elementos)
    test_descartar_partida(elementos)
    test_finalizar_dia_partida(elementos)
    test_nuevo_crimen_cada_3_dias(elementos)
    test_flujo_completo_dia(elementos)
    test_dossier_con_dias(elementos)

    print("\n" + "=" * 55)
    print("  Todos los tests pasaron ✓")
    print("=" * 55)

    print("\n--- Partida de ejemplo ---")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)
    partida.imprimir_estado(revelar_todo=False)
