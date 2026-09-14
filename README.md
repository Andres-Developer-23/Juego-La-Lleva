# La Lleva - Juego Tradicional Colombiano

Juego construido con Python y **Pygame (pygame-ce)**. Los jugadores compiten por
evitar ser "la lleva": el objetivo es que el otro jugador sea quien más tiempo
permanezca como la lleva, y gana quien menos tiempo lo sea.

## Características

- Modo 1 jugador contra la computadora (IA con dificultad ajustable)
- Multijugador local (2 jugadores)
- Física realista: aceleración, inercia y diagonal normalizada (velocidad en píxeles por segundo)
- Muñecos procedimentales animados (cabeza, cuerpo, brazos y piernas con marcha y giro)
- Lleva inicial aleatoria
- Obstáculos: cajas (se deslizan y rebotan) y zonas lentas
- Power-ups: velocidad, escudo y congelar al rival
- Toque por alcance con tropiezo breve y flash de impacto
- Efectos visuales al tocar (anillo + partículas) y al recoger power-ups
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

## Cambios y mejoras realizadas

Desarrollo organizado en entregas sobre la rama `desarrollo`. Resumen de lo
implementado:

### Jugabilidad y contenido

- **Física realista**: el movimiento usa *delta time* (velocidad en píxeles por
  segundo) con aceleración, inercia, rozamiento y desaceleración al soltar las
  teclas. La diagonal se normaliza, de modo que moverse en diagonal no es más
  rápido que en línea recta. Cada jugador tiene velocidad (`vx`/`vy`), dirección
  de cara y conserva la inercia al rebotar.
- **Muñecos procedimentales**: los personajes se dibujan con pygame en tiempo
  real (cabeza, pelo, ojos, torso con brillo, brazos y piernas). Caminan con
  marcha animada según su velocidad, se voltean hacia donde corren, dejan
  sombra y rastro de partículas, y quien lleva "la lleva" luce pañuelo rojo
  ondeante y aura pulsante. Sin dependencia de sprites externos.
- **Balance de IA**: la IA persigue a "la lleva" y huye si no la lleva, evitando
  las cajas por repulsión, alejándose de las paredes y con un **tiempo de
  reacción** propio de cada dificultad (Rápida/Normal/Difícil).
- **Colisiones que deslizan**: al chocar con una caja el jugador se desliza
  alrededor de ella corrigiendo el eje de menor penetración; si entra a gran
  velocidad rebota perdiendo energía.
- **Toque por alcance**: el contacto se detecta por distancia entre centros
  (`ALCANCE_TOQUE`) antes de que los cuerpos se solapen, y al recibir la lleva el
  jugador **tropieza** brevemente con un destello de impacto en pantalla.
- **Power-ups**: velocidad (verde), escudo azul que bloquea un toque y
  congelación del rival (cian). Se generan con una frecuencia temporal, envejecen
  y expiran, con efectos y mensajes al recogerlos.
- **Entorno**: cajones de madera con sombra y charcos azules pulsantes que
  ralentizan al jugador.
- **Efectos al tocar**: anillo expansivo y partículas en el punto del contacto,
  audio de toque, pisadas al correr, y transferencia correcta del rol de "la
  lleva".
- **Sonido procedimental**: la música y los efectos se sintetizan con numpy en
  vez de usar archivos externos (no hay dependencia de sprites/audio descargado).

### Arquitectura y calidad de código

- **Separación en capas**: `core` (orquestación), `models` (estado), `views`
  (renderizado), `ui` (interfaz), `servicios` (lógica de negocio), `controles`
  (entrada) e `interfaces` (abstracciones). Las reglas de la ronda, el ranking,
  las colisiones, los power-ups y la síntesis de audio son **servicios
  independientes**, desacoplados de la interfaz.
- **Pruebas unitarias**: suite con **86 pruebas** usando `unittest`
  (puntajes, reglas de la ronda, ranking con persistencia, colisiones y
  deslizamiento, toque por alcance, física del jugador y de la IA, power-ups,
  configuración persistente, síntesis de audio y control táctil).

### Interfaz y experiencia de usuario

- **Navegación por teclado** en el menú (flechas + Enter y atajos 1/2/3) además
  del mouse.
- **Pantalla de nombres** para los jugadores (edición con teclado, TAB para
  cambiar de jugador).
- **Toasts**: notificaciones breves en pantalla durante la partida
  (quién es la lleva, bloqueos, power-ups).
- **Pantallas** de ayuda, countdown, pausa, fin de ronda (con revancha por medio
  de **R**) y ranking con normalización de nombres.
- **Opciones persistentes**: duración de ronda, dificultad, volumen y pantalla
  completa se guardan automáticamente en `assets/settings.json`.

### Versión web (compilación a WebAssembly)

- El juego se compila a WebAssembly con **pygbag** y funciona en el navegador
  del celular sin instalar nada.
- **Bucle asíncrono**: `main.py` detecta el navegador (`emscripten`) y corre un
  bucle cooperativo que cede el control al navegador cada frame
  (`await asyncio.sleep(0)`).
- **Controles táctiles**: `ControladorTactil` dibuja cruces de dirección para
  J1 (izquierda) y J2 (derecha) además de un botón de pausa; aparecen tras el
  primer toque y se fusionan con el teclado físico mediante un proxy de
  `pygame.key.get_pressed()` (`TeclasFusionadas`).
- **Robustez en navegador**: el audio se desactiva si la síntesis falla y el
  ranking tolera errores de escritura, sin romper la partida.
- **Recursos del CDN reparados**: la CDN de pygbag ya no sirve
  `browserfs.min.js` (404) y su cabecera de seguridad (COEP) bloqueaba el
  cargador. Se versionó el recurso en `web/vendor/`, el servidor ya no envía
  COEP y el wheel de pygame-ce para wasm se sirve localmente en `web/cdn/`.
- **Automatización**: `web/compilar_web.py` compila y completa los recursos
  faltantes; `web/probar_web.py` verifica la web compilada con un navegador
  headless (Playwright + Firefox).

### Rendimiento en navegador

- **Resolución reducida**: la web ahora renderiza a **1280×720** en lugar de
  1908×1080 (~2.2× menos píxeles por frame), con el canvas reescalado por el
  navegador a pantalla completa sin cambiar el layout (las posiciones de la UI
  usan constantes relativas).
- **Sin doble limitador de FPS**: el `pygame.time.Clock.tick()` se desactiva en
  el navegador (`_ritmo()`); es el `flip`/`requestAnimationFrame` el que marca
  el ritmo, eliminando tartamudeos del *sleep* emulado.

## Versión Web (navegador y móvil)

El juego se compila a WebAssembly con [pygbag](https://pygbag.github.io/) y se
puede jugar desde el navegador del celular sin instalar nada.

Compilar (genera `juego_lleva/build/web/`; pygbag 0.9.3 deja el build "colgado"
tras escribir los archivos, por eso el script espera a que aparezcan y completa
los recursos que su CDN ya no sirve):

```bash
.venv/bin/pip install pygbag playwright            # playwright solo para el test web
.venv/bin/python web/compilar_web.py
```

Servir y probar (desde la PC o el celular de la misma red):

```bash
.venv/bin/python servidor_web.py juego_lleva/build/web
```

Para exponerlo a internet y jugar desde el celular fuera de la red local
(usa Cloudflare Tunnel; muestra la URL pública al levantar):

```bash
bash web/servir_movil.sh
```

Verificar automáticamente la web compilada (abre Firefox headless, hace clic y
guarda una captura):

```bash
.venv/bin/python web/probar_web.py http://localhost:8000/ 30 /tmp/captura.png
```

El servidor muestra la IP local para abrir el juego desde el celular
(`http://<ip-pc>:8000/`). Notas:

- Si la web carga desde `localhost:8*`, pygbag descarga las librerías del propio
  servidor (se sirven ya en `build/web/cdn/`); desde una IP normal las baja de su
  CDN, así que el celular necesita internet.
- En pantalla táctil aparecen cruces de control para J1 (izquierda) y J2
  (derecha) más un botón de pausa. En el escritorio funcionan los controles
  normales.
- La primera vez un toque/clic suele ser necesario para activar el audio.

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

## Arquitectura

El proyecto sigue una separación en capas que facilita entenderlo y probarlo:

```
Eventos de entrada (teclado / mouse / táctil)
        │
        ▼
core/juego.py  ── orquesta estados (menú, nombres, jugando, pausa…)
        │
        ├── servicios/   → lógica de negocio (reglas de ronda, ranking,
        │                  colisiones, power-ups, puntaje, audio)
        ├── models/      → estado de jugadores y del entorno
        ├── interfaces/  → contratos (abstracciones) de los servicios
        ├── views/       → renderizado (jugadores, entorno, efectos, power-ups)
        ├── ui/          → menús, HUD, toasts
        └── controles/   → entrada (teclado y control táctil)
```

Las reglas del juego no dependen de la interfaz: se pueden probar de forma
automática con la suite de pruebas sin abrir la ventana.

## Estructura del Proyecto

```
Juego-La-Lleva/
├── juego_lleva/
│   ├── core/           # Configuración y orquestación
│   ├── models/         # Modelos de datos
│   ├── views/          # Renderizado
│   ├── ui/             # Interfaz de usuario
│   ├── servicios/      # Lógica de negocio
│   ├── controles/      # Manejo de entrada (teclado y táctil)
│   ├── interfaces/     # Abstracciones
│   ├── tests/          # 86 pruebas unitarias
│   └── assets/         # Sprites y fondos
├── web/                # Soporte para la versión navegador
│   ├── vendor/         # browserfs.min.js versionado (la CDN ya no lo sirve)
│   ├── cdn/            # Wheel wasm de pygame-ce servido localmente
│   ├── compilar_web.py # Compila con pygbag y completa recursos
│   └── probar_web.py   # Verificación con navegador headless
├── servidor_web.py     # Servidor de la versión compilada (sin COEP)
└── requirements.txt
```

## Pruebas

Ejecutar la suite de pruebas desde el directorio `juego_lleva/`:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Las **86 pruebas** cubren: puntajes, reglas de la ronda (regla clásica),
ranking con persistencia, colisiones y deslizamiento contra cajas, rebote a
alta velocidad, toque por alcance, física del jugador (inercia, diagonal
normalizada, tropiezo) y de la IA (persecución/huida, reacción), power-ups,
configuración persistente, síntesis de audio y control táctil para la versión
web.

## Requisitos

- Python 3.12+
- pygame-ce 2.5+