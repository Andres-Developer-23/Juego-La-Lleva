# La Lleva - Juego Tradicional Colombiano

Juego construido con Python y Pygame. Los jugadores compiten por evitar ser "la lleva". Gana quien menos tiempo sea la lleva.

## Características

- Modo 1 jugador contra la computadora (IA equilibrada y dificultad ajustable)
- Multijugador local (2 jugadores)
- Movimiento por tiempo real (velocidad en píxeles por segundo)
- Lleva inicial aleatoria
- Obstáculos: cajas (rebote) y zonas lentas
- Power-ups: velocidad, escudo y congelar al rival
- Efectos visuales al tocar (anillo + partículas) y que se recogen power-ups
- Duración de ronda configurable (30 / 60 / 90 s)
- Ranking de mejores tiempos con persistencia
- Interfaz animada con partículas y transiciones de pantalla
- Notificaciones de eventos durante la partida (toasts)
- Menú navegable por teclado y mouse
- Sonido y música generados proceduralmente con volumen ajustable
- Pausa durante la partida
- Modo ventana / pantalla completa
- Preferencias guardadas en `assets/settings.json`
- Versión para navegador (móvil y escritorio) con controles táctiles

## Versión Web (navegador y móvil)

El juego se compila a WebAssembly con [pygbag](https://pygbag.github.io/) y se
puede jugar desde el navegador del celular sin instalar nada.

Compilar (genera `juego_lleva/build/web/`):

```bash
.venv/bin/pip install pygbag
.venv/bin/python -m pygbag juego_lleva
```

Servir y probar (desde la PC o el celular de la misma red):

```bash
.venv/bin/python servidor_web.py juego_lleva/build/web
```

El servidor muestra la IP local para abrir el juego desde el celular. En
pantalla táctil aparecen cruces de control para J1 (izquierda) y J2 (derecha)
más un botón de pausa. En el escritorio funcionan los controles normales.

## Instalación

1. Clonar el repositorio
   ```bash
   git clone https://github.com/Andres-Developer-23/Juego-La-Lleva.git
   cd Juego-La-Lleva
   ```

2. Crear entorno virtual
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instalar dependencias
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecutar el juego
   ```bash
   cd juego_lleva
   python main.py
   ```

## Controles

| Acción | Control |
|--------|---------|
| Menú | Flechas + Enter, o 1, 2, 3 (atajos) |
| Moverse (J1) | W A S D |
| Moverse (J2) | Flechas |
| Configurar | Flechas entre opciones, Izq/Der para cambiar |
| Pausar / continuar | P o ESC |
| Volver al menú desde pausa | Q |
| Revancha / menú | ENTER o R / ESC |
| Música | M |
| Pantalla completa | F11 |
| En móvil: moverse | Cruces táctiles (J1 izquierda, J2 derecha) |
| En móvil: pausar | Botón PAUSA (arriba a la derecha) |

## Cómo Jugar

1. Elegir modo (Un Jugador contra la IA o Multijugador local)
2. Ingresar nombres de los jugadores
3. La lleva inicial se elige al azar
4. El jugador con la lleva (rojo) debe tocar al otro
5. Al ser tocado, ese jugador pasa a ser la lleva
6. Recoge power-ups: velocidad (verde), escudo (azul, bloquea un toque) y congelar (cian, inmoviliza al rival)
7. Cuando expira el tiempo, gana quien menos tiempo fue la lleva
8. Los tiempos se registran en el ranking

## Opciones

La pantalla de Opciones (botón del menú o tecla 3) permite configurar:

- **Duración de la ronda**: 30, 60 o 90 segundos
- **Dificultad de la IA**: Fácil, Normal o Difícil
- **Volumen de la música y de los efectos**
- **Pantalla completa** (también con F11)

Las preferencias se guardan automáticamente en `assets/settings.json`.

## Estructura del Proyecto

```
juego_lleva/
├── core/           # Configuración y orquestación
├── models/         # Modelos de datos
├── views/          # Renderizado
├── ui/             # Interfaz de usuario
├── servicios/      # Lógica de negocio
├── controles/      # Manejo de entrada
├── interfaces/     # Abstracciones
├── tests/          # Pruebas unitarias e integración
└── assets/         # Sprites y fondos
```

## Pruebas

Ejecutar la suite de pruebas desde el directorio `juego_lleva/`:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Cubre puntajes, reglas de la ronda (regla clásica), ranking con persistencia,
colisiones, movimiento del jugador y de la IA (por tiempo real), power-ups,
configuración persistente y síntesis de audio.

## Requisitos

- Python 3.12+
- pygame-ce 2.5+
