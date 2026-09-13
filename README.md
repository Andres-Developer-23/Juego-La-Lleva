# La Lleva - Juego Tradicional Colombiano

Juego multijugador local construido con Python y Pygame. Dos jugadores compiten por evitar ser "la lleva". Gana quien menos tiempo sea la lleva.

## Características

- Multijugador local (2 jugadores)
- Lleva inicial aleatoria
- Obstáculos: cajas (rebote) y zonas lentas
- Ranking de mejores tiempos con persistencia
- Interfaz animada con partículas

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

| Acción | Jugador 1 | Jugador 2 |
|--------|-----------|-----------|
| Moverse | W A S D | Flechas |
| Volver al menú | ESC | ESC |

## Cómo Jugar

1. Ingresar nombres de los jugadores
2. La lleva inicial se elige al azar
3. El jugador con la lleva (rojo) debe tocar al otro
4. Al ser tocado, ese jugador pasa a ser la lleva
5. Después de 60 segundos, gana quien menos tiempo fue la lleva
6. Los tiempos se registran en el ranking

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
└── assets/         # Sprites y fondos
```

## Requisitos

- Python 3.12+
- Pygame 2.6.1
