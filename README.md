# CatchTheKiller 🔪🔍

CatchTheKiller es un prototipo de juego de deducción lógica por consola escrito en Python. El jugador asume el papel de un investigador que debe identificar los crímenes cometidos por un asesino en serie analizando patrones y revelando pistas ocultas.

## 🚀 Estado Actual
El proyecto se encuentra en una fase de **prototipo funcional (CLI)**. El motor central de generación de crímenes, la lógica del asesino y la mecánica de investigación por fases están implementados.

## 🛠️ Características Principales
- **Sistema de Rasgos del Asesino:** Cada partida genera un asesino con rasgos específicos (víctima preferida, arma, ubicación, etc.).
- **Generación Dinámica de Crímenes:** Se generan múltiples crímenes, algunos cometidos por el asesino (que siguen su patrón) y otros que actúan como "ruido".
- **Mecánica de Investigación en 3 Fases:** El jugador puede elegir crímenes para investigar y desvelar información oculta (XXXXX).
- **Lógica de Deducción:** El objetivo es encontrar el patrón común que identifica al asesino.

## 📂 Estructura del Proyecto
- `main.py`: Punto de entrada y bucle principal del juego.
- `asesino.py`: Clase que define los rasgos persistentes del criminal.
- `crimen.py`: Clase que representa un incidente individual.
- `generador_crimenes.py`: Lógica para crear la mezcla de crímenes del asesino y crímenes aleatorios.
- `rutina_juego.py`: Controla la interfaz de usuario, la visualización de fases y la interacción de investigación.
- `test.py` / `check.py`: Herramientas para verificar la consistencia de la generación y conteo de repeticiones.

## 🎮 Cómo Jugar
1. Asegúrate de tener Python 3 instalado.
2. Ejecuta el juego desde la terminal:
   ```bash
   python main.py
   ```
3. Sigue las instrucciones en pantalla para elegir qué crímenes investigar en cada fase.
4. Al final de las tres fases, se mostrará un resumen de todos los crímenes para que puedas validar tus deducciones.

## 💡 Ideas para el Futuro
- **Subniveles de ubicación:** Mayor profundidad añadiendo sub-ubicaciones aleatorias (ej: Estación de Metro -> Estación de Hillyburg).
- **Interfaz Gráfica:** Transición de CLI a una interfaz visual.
- **Dificultad Variable:** Ajustar el número de crímenes "señuelo" y elementos ocultos.

---
*Este proyecto es parte de un desarrollo experimental de juegos de lógica.*
