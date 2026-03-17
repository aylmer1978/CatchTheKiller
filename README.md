# CatchTheKiller 🔪🔍

CatchTheKiller es un prototipo de juego de deducción lógica por consola escrito en Python. El jugador asume el papel de un investigador que debe identificar los crímenes cometidos por un asesino en serie analizando patrones y revelando pistas ocultas.

## 🚀 Estado Actual
El proyecto se encuentra en una fase de **prototipo funcional (CLI)**. El motor central de generación de crímenes, la lógica del asesino y la mecánica de investigación por fases están implementados.

## 🛠️ Características Principales
- **Firma del Asesino (2 Rasgos):** Cada partida genera un asesino con una firma de exactamente 2 rasgos idénticos (ej: misma arma y lugar), variando el resto en sus 3 crímenes.
- **Generación Dinámica (Min. 2 Diferencias):** Se generan múltiples crímenes. El sistema garantiza que ningún par de crímenes de toda la partida comparta más de 2 rasgos, creando un puzle lógico de deducción pura sin "ruido" confuso.
- **Mecánica de Investigación en 3 Fases:** El jugador puede elegir qué crimen investigar en cada ronda.
- **Minijuego Forense (Mastermind):** Para revelar una pista oculta (XXXXX), el jugador debe desencriptar el expediente acertando un código de 4 dígitos únicos en 6 intentos o perder la pista para siempre.

## 📂 Estructura del Proyecto
- `main.py`: Punto de entrada, textos introductorios y bucle principal del juego.
- `asesino.py`: Clase que define los rasgos persistentes del criminal.
- `crimen.py`: Clase que representa un incidente individual.
- `generador_crimenes.py`: Lógica algorítmica de generación que fuerza la regla de las 2 diferencias mínimas.
- `rutina_juego.py`: Controla la interfaz de usuario y la interacción de investigación.
- `minijuegos.py`: Contiene el minijuego lógico (Mastermind) para desbloquear las pistas de cada crimen.
- `test.py` / `check.py`: Herramientas para verificar la consistencia de la generación.

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
