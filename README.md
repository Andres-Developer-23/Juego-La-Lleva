# La Lleva - Juego Tradicional Colombiano

Juego construido con Python y Pygame. Los jugadores compiten por evitar ser "la lleva". Gana quien menos tiempo sea la lleva.

## Características

- Modo 1 jugador contra la computadora (IA)
- Multijugador local (2 jugadores)
- Lleva inicial aleatoria
- Obstáculos: cajas (rebote) y zonas lentas
- Ranking de mejores tiempos con persistencia
- Interfaz animada con partículas
- Sonido y música generados proceduralmente
- Pausa durante la partida
- Modo ventana / pantalla completa

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
| Menú | 1: Un Jugador, 2: Multijugador |
| Moverse (J1) | W A S D |
| Moverse (J2) | Flechas |
| Pausar / continuar | P o ESC |
| Volver al menú desde pausa | Q |
| Música | M |
| Pantalla completa | F11 |

## Cómo Jugar

1. Elegir modo (Un Jugador contra la IA o Multijugador local)
2. Ingresar nombres de los jugadores
3. La lleva inicial se elige al azar
4. El jugador con la lleva (rojo) debe tocar al otro
5. Al ser tocado, ese jugador pasa a ser la lleva
6. Después de 60 segundos, gana quien menos tiempo fue la lleva
7. Los tiempos se registran en el ranking

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
colisiones, movimiento de la IA y síntesis de audio.

## Requisitos

- Python 3.12+
- pygame-ce 2.5+
