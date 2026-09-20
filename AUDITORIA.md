# Auditoría del proyecto "La Lleva"

Fecha: 2026-09-20
Alcance: código (~7.500 líneas), assets, scripts web, tests y documentación.
Método: lectura completa del código, conteo de tests (113, verificado),
inspección de APIs reales de pygame-ce 2.5.7 y escaneo de imports/código muerto.

## 0. Resumen ejecutivo

El proyecto está bien estructurado por capas (core/models/views/ui/servicios/
controles/interfaces), con física por delta time y render procedural. La suite
de 113 tests es real y coherente. Los principales problemas son:

- 1 bug de crash (F11) y 1 bug de interacción (clic del menú en web).
- Varias pantallas sin limitador de FPS (CPU al 100% en escritorio).
- Código/assets muertos y datos personales versionados.
- Cachés de superficies sin límite (leak) y fuentes creadas por frame.
- Arquitectura de imports frágil (depende de `sys.path`).

Prioridad sugerida: Fase 1 (bugs) → Fase 2 (limpieza) → Fase 3 (docs) →
Fase 4 (rendimiento) → Fase 5 (arquitectura).

---

## 1. CRÍTICO — Bugs que rompen o degradan

| # | Problema | Ubicación | Detalle |
|---|----------|-----------|---------|
| 1 | F11 crashea el juego | `core/juego.py:157` | Llama `pygame.display.get_fullscreen()`, que no existe ni en pygame-ce 2.5.7 (el `.so` solo expone `is_fullscreen`). Al pulsar F11 → `AttributeError` sin capturar. Cambiar a `pygame.display.is_fullscreen()`. |
| 2 | Clics del menú desalineados en web | `ui/interfaz.py:385` vs `452-475` | Los botones se dibujan con `self._u(y)` (escalado) pero los hitboxes de `obtener_accion_menu` usan `y` crudo. En web (720p, escala 0.667) el clic no coincide. |
| 3 | CPU al 100% en varias pantallas | `core/juego.py` | `_menu_principal`, `_pantalla_nombres`, `_pantalla_ranking`, `_pantalla_opciones` y `_pantalla_fin_ronda` no llaman `self._ritmo()`. En escritorio el bucle queda sin límite de FPS. |
| 4 | `congelar` con rival `None` | `servicios/power_up_service.py:59` + `core/juego.py:509` | `efecto()` hace `rival.id` sin validar `None`. Con un solo jugador → `AttributeError`. |
| 5 | Datos corruptos tumban hilos de red | `red/protocolo.py:46` | `json.loads` puede lanzar `JSONDecodeError`, no capturado. Un cliente corrupto mata el hilo del servidor/cliente. |
| 6 | Botón "Volver" de ayuda fuera de pantalla en web | `ui/interfaz.py:619-620` | Dibujado en `y=680`, alto 50 → 730 > 720. En web queda cortado (solo funciona ESC). |

---

## 2. BORRAR (código/activos/datos muertos)

- `juego_lleva/assets/crear_placeholders.py` — script obsoleto; regenera
  `campo.png` a 1024×768 y **sobrescribe** el fondo bueno de `generar_assets.py`.
- Carga de sprites legacy en `views/jugador_view.py`: `cargar_sprites` (57),
  `_cargar_sprite` (71), `sprite_normal`/`sprite_lleva` (53-54). El render es
  procedural; nunca se dibujan. Con esto quedan sin uso los PNG en
  `assets/sprites/` (`jugador1.png`, `jugador2.png`, `lleva.png`) y su
  documentación en `assets/README.md`.
- `views/efecto_view.py`: `COLOR_PARTICULA` (14) y `COLORES_POWER_UP` (16)
  nunca se usan (hay copia en `PowerUpView`).
- `models/jugador.py:156`: `posicion_anterior` se asigna **después** de mover,
  por lo que nunca es la posición previa y nunca se lee.
- `servicios/colision.py`: `rebote_obstaculo` (150) y `detectar_colision` (17)
  solo los usan los tests; al borrarlos, borrar sus tests.
- Imports muertos: `views/power_up_view.py:4` (`random`),
  `tests/test_red.py:8` (`TIPO_CONEXION`).
- Duplicación: `core/juego.py:751-753` llama `set_volumen_musica` dos veces.
- Datos personales versionados: `assets/ranking.json` (289 líneas con partidas
  reales) y `assets/settings.json` (volumen en 0.0). Deben ir a `.gitignore` y
  dejar solo un `ranking.json` vacío/ejemplo.
- `__pycache__/` no debe versionarse (ya está en `.gitignore`).

---

## 3. CAMBIAR (correcciones y consistencia)

- README desactualizado/incorrecto:
  - Dice que el audio se sintetiza con **numpy** (línea 64): el código NO usa
    numpy (usa `array`/`math`).
  - Mezcla `.venv` (líneas 134-155) y `venv` (177-182).
  - No menciona que para la web hacen falta `pygbag` y `playwright`.
- `requirements.txt`: sin salto de línea final y sin dependencias de desarrollo.
  Añadir `pygbag`/`playwright` en un `requirements-dev.txt`.
- No hay `LICENSE` ni repositorio git (solo `.gitignore`), pero el README
  describe `git clone`. Definir licencia.
- `interfaces/movible.py:10`: la firma `mover(self, teclas=None)` no coincide
  con las implementaciones (`JugadorHumano.mover`, `JugadorIA.mover` con
  `delta_tiempo`, `obstaculos`). Contrato engañoso.
- `servicios/colision.py:15-70`: cooldown en **frames** (`COOLDOWN_FRAMES`) en
  vez de segundos; en web el framerate lo marca el navegador. Usar delta time.
- `views/power_up_view.py:85` y `views/efecto_view.py:38`: las cachés
  `_anillos`/`_halos` incluyen `radio`/`alpha` continuos y nunca se purgan →
  crecimiento sin límite en partidas largas.
- `PowerUpService.crear` (`servicios/power_up_service.py:36-43`): no evita
  obstáculos (solo jugadores); pueden aparecer sobre cajas.
- `Juego._registrar_en_ranking` (`core/juego.py:679-682`): indexa por nombre;
  nombres duplicados se pisan.
- `Entorno`/`Jugador`/`Interfaz`/etc. instancian `Config()` repetidamente
  (clase usada como singleton de constantes). Estandarizar.
- `models/__init__.py` y `views/__init__.py`: re-exportan pero nadie los usa
  por esa vía; simplificar o usarlos.

---

## 4. MEJORAR (arquitectura, rendimiento, calidad)

### Arquitectura
- El paquete no es importable como `juego_lleva`: imports absolutos
  (`from core.config import Config`) dependientes de `sys.path.insert`
  (`cliente.py:17`, `servidor.py:11`, `__main__.py:6`). Migrar a
  `from juego_lleva.core...` y ejecutar con `python -m juego_lleva`.
  **Resuelto en la Fase 5** (con staging en `web/compilar_web.py` para no
  romper el build de pygbag).
- Máquina de estados con strings (`"menu"`, `"jugando"`…). Usar `enum`/
  constantes.
- Mezcla de idiomas y nombres con acentos; definir convención.

### Rendimiento
- `views/jugador_view.py:499`: crea `pygame.font.SysFont` cada frame y por
  jugador. Cachear la fuente.
- `views/efecto_view.py:112` e `ui/interfaz.py:83`: crean una `Surface` nueva
  por partícula/frame. Reutilizar superficies.
- `views/obstaculo_view.py:34`: crea superficie de sombra cada frame.

### Tests / CI
- Los tests solo corren desde `juego_lleva/` por el `sys.path`; el refactor de
  paquete lo arregla. Añadir `pytest`, cobertura y `conftest.py`.
- Falta test de interacción del menú por mouse (bug #2) y de F11 (bug #1).

### Red
- Servidor sin límite de jugadores, sin validar rangos de posición y sin
  autenticación; `enviar_estado` a todos en cada movimiento no escala.

### Assets / docs
- `assets/README.md` recomienda sprites 32×32 que ya no se usan.
- `web/cdn/*.whl` y `web/vendor/browserfs.min.js` son binarios versionados;
  documentar por qué y cómo regenerarlos (`compilar_web.py`).

---

## 5. LO QUE ESTÁ BIEN (no tocar)

- Suite de 113 tests verificada y coherente con el README.
- Separación por capas clara y testeable.
- Física con delta time, diagonal normalizada y render procedural logrado.
- Manejo defensivo de audio/ranking en web (`activo`, `try/except`).

---

## 6. Plan de ejecución por fases

1. **Fase 1 – Bugs críticos**: F11 (`is_fullscreen`), hitboxes del menú
   escaladas, `_ritmo()` en todas las pantallas, guardas `None` en power-ups,
   `JSONDecodeError` en red, botón de ayuda.
2. **Fase 2 – Borrado**: `crear_placeholders.py`, sprites legacy + PNGs,
   constantes muertas, `posicion_anterior`, métodos solo-test, imports muertos,
   `.gitignore` para `ranking.json`/`settings.json`.
3. **Fase 3 – Docs/config**: corregir README (numpy, venv), `requirements`,
   `LICENSE`.
4. **Fase 4 – Rendimiento**: cachear fuentes/superficies, limitar cachés,
   cooldown por delta time.
5. **Fase 5 – Arquitectura**: imports de paquete + `python -m juego_lleva`,
   enum de estados, `Config` unificado.

## 7. Preguntas abiertas

- ¿Se pueden borrar `assets/ranking.json` y `assets/settings.json` con datos
  reales, o se conservan como ejemplo? (Pendiente; por ahora se conservan e
  ignoran en `.gitignore`.)
- ~~¿Se mantiene el soporte de sprites externos?~~ Resuelto: eliminado en la
  Fase 2 (render 100% procedural).
- ~~¿Preferencia de licencia?~~ Resuelto: MIT (`LICENSE`).

---

## 8. Estado de ejecución

- **Fase 1 (bugs críticos #1-#6): COMPLETADA.**
  - F11 usa `pygame.display.is_fullscreen()`.
  - Hitboxes del menú unificados con `BOTONES_MENU` y escalado `_u`.
  - `_ritmo()` añadido a los 9 estados (menú, nombres, fin de ronda, ranking,
    opciones).
  - Guarda `None` en el power-up "congelar".
  - `extraer_linea` captura `JSONDecodeError` y descarta mensajes no-`dict`.
  - Botón de ayuda reposicionado para que quepa en 720p.
- **Fase 2 (borrado de código/assets muertos): COMPLETADA.**
  - Eliminados: `assets/crear_placeholders.py`, `assets/sprites/` y la carga
    de sprites legacy (`cargar_sprites`, `_cargar_sprite`, `sprite_normal`,
    `sprite_lleva`, constantes `SPRITE_*`), `COLOR_PARTICULA`,
    `COLORES_POWER_UP`, `posicion_anterior`, `detectar_colision`,
    `rebote_obstaculo`, imports muertos y la llamada duplicada a
    `set_volumen_musica`.
  - `.gitignore`: se ignoran `assets/settings.json` y `assets/ranking.json`.
  - `assets/README.md` actualizado (render procedural, sin sprites externos).
  - Suite: **113 → 110 pruebas** (se eliminaron los tests de los métodos
    muertos); todas pasan.
- **Fase 3 (docs/config): COMPLETADA.**
  - README: corregida la mención a `numpy` (no se usa), entorno unificado a
    `.venv`, referencia a `requirements-dev.txt`, sección de Licencia y
    estructura del proyecto actualizada.
  - `requirements.txt` con salto de línea final; nuevo `requirements-dev.txt`
    (`pygbag`, `playwright`).
  - Añadido `LICENSE` (MIT).
- **Fase 4 (rendimiento): COMPLETADA.**
  - Fuente del nombre cacheada en `JugadorView` (antes se creaba por frame).
  - `EfectoView`: partículas cacheadas por color/radio y caché `_anillos`
    acotada (`_MAX_CACHE`).
  - Cachés `_halos` (power-ups), `_particulas_cache` (menú) y `_sombras`
    (obstáculos) acotadas/reutilizadas.
  - Cooldown de colisiones por **delta time** (`COOLDOWN_SEG`) en vez de
    frames; nuevo test de cooldown parcial.
  - Suite: **111 pruebas** (se añadió una); todas pasan.
- **Fase 5 (arquitectura): COMPLETADA.**
  - Añadido `core/estado.py` con `EstadoJuego(str, Enum)` y sustituidos todos
    los estados mágicos de `core/juego.py`.
  - Eliminado el único estado mutable guardado en `Config`: la dificultad de la
    IA ahora vive en `JugadorIA` (`velocidad_ia`, `variacion_ia`,
    `factor_ia_huyendo`), dejando `Config` como constantes de solo lectura.
  - **Migración a paquete `juego_lleva.*`**: todos los imports internos y de
    tests usan el prefijo `juego_lleva.`; se eliminaron los `sys.path.insert`
    de `cliente.py`, `servidor.py` y `__main__.py`. El juego se ejecuta con
    `python -m juego_lleva` y los tests con
    `python -m unittest discover -s juego_lleva/tests -t .`.
  - **Build web reestructurado**: `web/compilar_web.py` prepara una carpeta de
    staging (`juego_lleva/build/app`) con `main.py` + copia del paquete y
    apunta pygbag ahí, ya que pygbag exige `main.py` en la raíz de la app.
  - Suite: **111 pruebas**, todas pasan.

