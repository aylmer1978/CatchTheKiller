# Catch the Killer

**Catch the Killer** es un juego de estrategia y deducción detectivesca desarrollado en Python. Tu misión como detective de la Unidad de Homicidios es identificar los crímenes cometidos por un asesino en serie analizando patrones, firmas y comportamientos sistemáticos.

![Imagen del juego](https://via.placeholder.com/800x450?text=Catch+the+Killer+GUI) *Nota: Añadir captura de pantalla real aquí.*

## 👁️ Descripción del Proyecto

El juego genera proceduralmente un asesino con una "firma" única compuesta por tres atributos específicos (víctima, arma, lugar, franja horaria o características especiales). El mapa se llena de crímenes reales del asesino y "señuelos" aleatorios. Mediante un sistema de gestión de cartas y avance de tiempo, deberás investigar los expedientes para encontrar el patrón común y detener al culpable antes de que la ciudad se sumerja en el caos.

## 🚀 Características Principales

- **Generación Procedural**: Cada partida es única. El asesino, su firma y los crímenes se generan de forma aleatoria siguiendo reglas lógicas de consistencia.
- **Sistema de Investigación por Cartas**: Utiliza cartas de "Investigar Expediente", "Investigar Caso" o atributos específicos para revelar datos de los crímenes.
- **Ciclo de Día/Noche**: Gestión de tiempo donde cada acción cuenta. Nuevos crímenes aparecen cada 3 días si no resuelves el caso.
- **Interfaz Gráfica Moderna**: Desarrollada con **PySide6 (Qt)**, con un estilo visual "noir" y técnico.
- **Niveles de Dificultad**: Fácil, Normal y Difícil, que ajustan el número de intentos de acusación disponibles.
- **Dossier Final**: Resumen detallado de la investigación tras ganar o perder.

## 🛠️ Requisitos e Instalación

### Requisitos previos
- **Python 3.10** o superior.
- **PySide6**: La biblioteca para la interfaz gráfica.

### Instalación
1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/CatchTheKiller.git
   cd CatchTheKiller
   ```
2. Instala las dependencias:
   ```bash
   pip install PySide6
   ```

## 🎮 Instrucciones de Uso

### Iniciar el Juego
Para comenzar la investigación, ejecuta el archivo principal:
```bash
python main.py
```

### Mecánica de Juego
1.  **Selección de Crimen**: Haz clic en cualquier icono de sobre en el mapa para abrir el expediente en el panel derecho.
2.  **Investigación**: Usa las cartas de tu mano (panel inferior) para revelar atributos ocultos del crimen seleccionado.
    - Solo puedes jugar **una carta por día**.
    - Puedes **descartar una carta gratis** por día para renovar tu mano.
3.  **Finalizar Día**: Cuando hayas agotado tus acciones, pulsa "Finalizar Día". Esto repondrá tu mano hasta 3 cartas y avanzará el calendario.
4.  **Identificar el Patrón**: El asesino siempre repite **exactamente 3 atributos** en todos sus crímenes (su "firma"). Si encuentras tres crímenes que comparten tres valores iguales, es muy probable que hayas encontrado al asesino.
5.  **Marcar Sospechosos**: Usa el botón "Marcar como sospechoso" en los expedientes que creas que pertenecen al asesino. Aparecerá una bandera sobre ellos en el mapa.
6.  **Acusación**: Cuando estés seguro, entra en la **Sala de Mando** y pulsa "Lanzar Acusación". Para ganar, debes haber marcado **todos** los crímenes del asesino y **ningún** señuelo.

## 📁 Estructura del Proyecto

```text
CatchTheKiller/
├── main.py                 # Punto de entrada de la aplicación
├── core/                   # Lógica de negocio y reglas del juego
│   ├── asesino.py          # Lógica de generación del asesino y su firma
│   ├── carta.py            # Modelos de cartas y tipos de investigación
│   ├── crimen.py           # Estructura de datos de los crímenes
│   ├── generador.py        # Generador procedural de la partida
│   ├── mazo.py             # Gestión del mazo, mano y descartes
│   └── partida.py          # Orquestador del estado global del juego
├── gui/                    # Interfaz de usuario (PySide6)
│   ├── main_window.py      # Ventana principal
│   ├── mapa_widget.py      # Visualización del mapa de la ciudad
│   ├── sala_mando.py       # Interfaz de acusación y estadísticas
│   └── ...                 # Otros paneles y componentes visuales
├── data/
│   └── elementos.json      # Base de datos de víctimas, armas y lugares
└── test_core.py            # Suite de pruebas para la lógica del juego
```

## 🧪 Pruebas (Testing)

El proyecto incluye una suite de pruebas para verificar la integridad de la lógica del juego (mazo, días, generación, etc.). Puedes ejecutarlos con:
```bash
python test_core.py
```

## ⚖️ Licencia
Este proyecto está bajo la Licencia [MIT/Personal/Comercial - Especificar]. 

---
*Desarrollado como parte del Modelo Modular de Validación para la producción de contenidos VOD.*
