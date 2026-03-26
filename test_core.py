"""test_core.py — Tests del core v5 (sistema de eventos)."""

import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.asesino import Asesino
from core.carta import Carta, TipoCarta
from core.mazo import Mazo, TAMANYO_MANO
from core.evento import (
    TipoEvento, generar_evento, Evento,
    DIAS_MIN_NUEVO_CRIMEN, DIAS_MAX_NUEVO_CRIMEN
)
from core.partida import Partida, Dificultad, ResultadoAcusacion, CRIMENES_INICIALES

def cargar():
    with open("data/elementos.json", encoding="utf-8") as f:
        return json.load(f)

def ok(msg):      print(f"  ✓ {msg}")
def seccion(msg): print(f"\n── {msg} ──")


def test_evento_nuevo_crimen_forzado(elementos):
    seccion("TEST 1: NUEVO_CRIMEN forzado al llegar al día límite")
    crimenes_inv = []
    senuelos     = [("mock", type("C", (), {"campos_revelados": set()})())]
    for _ in range(50):
        ev = generar_evento(
            dias_sin_crimen       = DIAS_MAX_NUEVO_CRIMEN,
            crimenes_investigados = crimenes_inv,
            senuelos_visibles     = senuelos,
            hay_crimenes_en_pool  = True,
        )
        assert ev.tipo == TipoEvento.NUEVO_CRIMEN, \
            f"Esperado NUEVO_CRIMEN, obtenido {ev.tipo}"
    ok(f"Con dias_sin_crimen={DIAS_MAX_NUEVO_CRIMEN} siempre es NUEVO_CRIMEN (50 iteraciones)")


def test_evento_sin_crimenes_investigados(elementos):
    seccion("TEST 2: ERROR_POLICIAL nunca aparece sin crímenes investigados")
    for _ in range(100):
        ev = generar_evento(
            dias_sin_crimen       = 0,
            crimenes_investigados = [],
            senuelos_visibles     = [],
            hay_crimenes_en_pool  = False,
        )
        assert ev.tipo != TipoEvento.ERROR_POLICIAL
        assert ev.tipo != TipoEvento.CRIMEN_RESUELTO
    ok("Sin crímenes investigados ni señuelos, esos eventos nunca aparecen")


def test_evento_error_policial_borra_atributos(elementos):
    seccion("TEST 3: ERROR_POLICIAL borra atributos del crimen")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)

    # Revelar atributos en el primer crimen
    idx = partida.crimenes_en_mapa()[0][0]
    partida.mazo.mano[0] = Carta(TipoCarta.INVESTIGAR_CASO)
    partida.jugar_carta(0, idx)
    assert partida.crimen(idx).todos_revelados()

    # Forzar evento ERROR_POLICIAL
    from core.evento import _crear_evento, TITULOS, ICONOS
    crimen_obj = partida.crimen(idx)
    mock_investigados = [(idx, crimen_obj)]
    ev = _crear_evento(TipoEvento.ERROR_POLICIAL, mock_investigados, [])

    assert ev.idx_crimen_afectado == idx
    assert len(ev.atributos_borrados) >= 1

    # Aplicar manualmente
    for attr in ev.atributos_borrados:
        crimen_obj.campos_revelados.discard(attr)

    assert not crimen_obj.todos_revelados()
    ok(f"ERROR_POLICIAL borró {len(ev.atributos_borrados)} atributos")


def test_evento_crimen_resuelto_archiva_senuelo(elementos):
    seccion("TEST 4: CRIMEN_RESUELTO archiva un señuelo")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)

    senuelos = [(i, c) for i, c in enumerate(partida._pool)
                if not c.marcado_asesino and c.visible_en_mapa]
    assert len(senuelos) > 0

    from core.evento import _crear_evento
    ev = _crear_evento(TipoEvento.CRIMEN_RESUELTO, [], senuelos)
    assert ev.idx_crimen_afectado is not None
    assert not partida._pool[ev.idx_crimen_afectado].marcado_asesino
    ok(f"CRIMEN_RESUELTO seleccionó señuelo #{ev.idx_crimen_afectado}")


def test_evento_burocracia_reduce_mano(elementos):
    seccion("TEST 5: BUROCRACIA reduce max_mano a 2")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)

    # Inyectar evento BUROCRACIA forzando finalizar_dia
    from core.evento import _crear_evento
    ev = _crear_evento(TipoEvento.BUROCRACIA, [], [])
    assert ev.max_mano_override == 2

    partida.mazo.finalizar_dia(max_mano_override=2)
    assert partida.mazo.max_mano == 2
    assert len(partida.mazo.mano) <= 2
    ok(f"Tras BUROCRACIA: max_mano={partida.mazo.max_mano}, mano={len(partida.mazo.mano)}")


def test_evento_financiacion_aumenta_mano(elementos):
    seccion("TEST 6: FINANCIACIÓN aumenta max_mano a 4")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)

    # Usar carta para tener <3 en mano
    idx = partida.crimenes_en_mapa()[0][0]
    partida.mazo.mano[0] = Carta(TipoCarta.INVESTIGAR_CASO)
    partida.jugar_carta(0, idx)

    partida.mazo.finalizar_dia(max_mano_override=4)
    assert partida.mazo.max_mano == 4
    assert len(partida.mazo.mano) == 4
    ok(f"Tras FINANCIACIÓN: max_mano={partida.mazo.max_mano}, mano={len(partida.mazo.mano)}")


def test_evento_refuerzos_permite_dos_cartas(elementos):
    seccion("TEST 7: REFUERZOS permite jugar 2 cartas")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)

    # Finalizar día con refuerzos
    partida.mazo.finalizar_dia(cartas_jugables=2)
    assert partida.mazo._max_jugadas_hoy == 2
    assert partida.mazo.jugadas_restantes() == 2

    # Jugar dos cartas
    ids = [i for i, _ in partida.crimenes_en_mapa()]
    partida.mazo.mano[0] = Carta(TipoCarta.ATRIBUTO_LUGAR)
    partida.jugar_carta(0, ids[0])
    assert partida.mazo.jugadas_restantes() == 1

    if len(partida.mazo.mano) > 0 and len(ids) > 1:
        partida.mazo.mano[0] = Carta(TipoCarta.ATRIBUTO_FRANJA)
        partida.jugar_carta(0, ids[1])
        assert partida.mazo.jugadas_restantes() == 0

    ok(f"REFUERZOS: se jugaron 2 cartas correctamente")


def test_dias_sin_crimen_se_resetea(elementos):
    seccion("TEST 8: dias_sin_crimen se resetea al aparecer crimen")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)
    assert partida.dias_sin_crimen == 0

    # Forzar varios días sin crimen (evento narrativo no añade crimen)
    partida.dias_sin_crimen = 4
    # Simular aparición de crimen
    if partida.hay_mas_crimenes():
        partida._hacer_visible(partida._siguiente_idx)
        partida._siguiente_idx += 1
    assert partida.dias_sin_crimen == 0
    ok("dias_sin_crimen se resetea a 0 al aparecer crimen")


def test_flujo_completo_con_eventos(elementos):
    seccion("TEST 9: Flujo completo - 5 días con eventos")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos, Dificultad.FACIL)

    for dia in range(5):
        resultado = partida.finalizar_dia()
        assert "evento" in resultado
        assert resultado["evento"] is not None
        assert resultado["dia_nuevo"] == dia + 2
        assert len(partida.mazo.mano) <= partida.mazo.max_mano

    ok(f"5 días completados, día actual: {partida.dias}")
    ok(f"Víctimas: {partida.victimas}, pool visibles: {len(partida.crimenes_en_mapa())}")


def test_dossier_con_eventos(elementos):
    seccion("TEST 10: Dossier final")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos, Dificultad.NORMAL)

    for _ in range(3):
        partida.finalizar_dia()

    for idx in partida.indices_asesino_visibles():
        partida.toggle_sospechoso(idx)
    partida.acusar()

    d = partida.dossier()
    assert "dias_totales" in d
    assert d["dias_totales"] == 4
    ok(f"Dossier: {d['dias_totales']} días, {d['total_victimas']} víctimas, victoria={d['victoria']}")


if __name__ == "__main__":
    print("=" * 55)
    print("  CATCH THE KILLER — Test del Core v5")
    print("=" * 55)

    elementos = cargar()
    test_evento_nuevo_crimen_forzado(elementos)
    test_evento_sin_crimenes_investigados(elementos)
    test_evento_error_policial_borra_atributos(elementos)
    test_evento_crimen_resuelto_archiva_senuelo(elementos)
    test_evento_burocracia_reduce_mano(elementos)
    test_evento_financiacion_aumenta_mano(elementos)
    test_evento_refuerzos_permite_dos_cartas(elementos)
    test_dias_sin_crimen_se_resetea(elementos)
    test_flujo_completo_con_eventos(elementos)
    test_dossier_con_eventos(elementos)

    print("\n" + "=" * 55)
    print("  Todos los tests pasaron ✓")
    print("=" * 55)

    print("\n--- Partida de ejemplo ---")
    asesino = Asesino(elementos)
    partida = Partida(asesino, elementos)
    partida.imprimir_estado()
    print("\nFinalizando 3 días...")
    for i in range(3):
        r = partida.finalizar_dia()
        ev = r["evento"]
        print(f"  Día {r['dia_nuevo']-1}→{r['dia_nuevo']}: {ev.icono} {ev.titulo}")
    partida.imprimir_estado()
