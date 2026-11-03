# MathInvaders

Juego educativo de cálculo mental inspirado en Space Invaders, desarrollado en Python + Pygame.

Con amor para mis hijos.

![Captura original](images/Screenshot%202023-09-29%20123631.png)

## Reglas

1. Resuelve la operación que se muestra arriba a la izquierda.
2. Mueve la nave con **W A S D** y dispara con **ESPACIO** a la única estrella que contiene la respuesta correcta.
3. **Acierto:** ganas puntos y comienza inmediatamente una operación nueva. No hace falta destruir los distractores.
4. **Error:** se descuentan puntos y se conserva la operación hasta acertar.
5. Cada **5 respuestas correctas** aumenta el nivel. Desde el nivel **3** aparecen restas; a partir del **5** aparecen estrellas más rápidas.
6. El choque con una estrella quita una vida (con invulnerabilidad temporal). Dispones de 3 vidas.

Los aciertos suman como mínimo 1 punto multiplicado por el nivel actual. Un error descuenta el máximo entre 1 y la mitad entera del número incorrecto. La puntuación puede ser negativa.

## Instalación

Requiere Python 3.10 o superior.

    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python main.py

El programa busca los archivos multimedia en la carpeta del proyecto, incluso si se ejecuta desde otro directorio. **ENTER** o clic para comenzar, **R** para reiniciar y **ESC** para salir.

## Arquitectura

    main.py                      # Presentación, recursos, eventos, sonido y bucle
    mathinvaders/logic.py        # Preguntas, respuestas, puntuación, vidas y niveles (sin Pygame)
    mathinvaders/sprites.py      # Nave, disparos y estrellas; movimiento con delta time
    tests/test_logic.py          # Pruebas de la lógica educativa
    tests/test_game.py           # Integración con Pygame usando pantalla virtual
    .github/workflows/tests.yml  # Pruebas automáticas

Imágenes y fuentes se cargan una sola vez, las etiquetas numéricas se dibujan solo al crear cada estrella y el bucle se limita a 60 FPS. El movimiento usa tiempo por fotograma y coordenadas decimales.

## Pruebas

    python -m unittest discover -s tests -v

En entornos sin pantalla, establecer SDL_VIDEODRIVER=dummy y SDL_AUDIODRIVER=dummy. GitHub Actions ejecuta estas pruebas en las nuevas ramas y pull requests.

## Créditos

1. Iconos creados por Smashicons - Flaticon
   * [NUMERO 1](https://www.flaticon.es/iconos-gratis/numero-1)
   * [NUMERO 2](https://www.flaticon.es/iconos-gratis/numero-2)
   * [NUMERO 3](https://www.flaticon.es/iconos-gratis/numero-3)
   * [NUMERO 4](https://www.flaticon.es/iconos-gratis/numero-4)
   * [NUMERO 5](https://www.flaticon.es/iconos-gratis/numero-5)
   * [NUMERO 6](https://www.flaticon.es/iconos-gratis/numero-6)
   * [NUMERO 7](https://www.flaticon.es/iconos-gratis/numero-7)
   * [NUMERO 8](https://www.flaticon.es/iconos-gratis/numero-8)
   * [NUMERO 9](https://www.flaticon.es/iconos-gratis/numero-9)
   * [NUMERO 10](https://www.flaticon.es/iconos-gratis/numero-10)
     
2. Cuadrado iconos creados por Freepik - Flaticon
   * [CUADRADO NARANJA](https://www.flaticon.es/iconos-gratis/cuadrado)
   
4. Sustracción iconos creados por Flat Icons - Flaticon
   * [RESTA](https://www.flaticon.es/iconos-gratis/sustraccion)
     
5. Ui iconos creados por Flat Icons - Flaticon
   * [SUMA](https://www.flaticon.es/iconos-gratis/ui)
     
6. Igual iconos creados por Rohim - Flaticon
   * [IGUAL](https://www.flaticon.es/iconos-gratis/igual)

7. Corazón iconos creados por Kiranshastry - Flaticon
   * [CORAZÓN](https://www.flaticon.es/iconos-gratis/corazon)
