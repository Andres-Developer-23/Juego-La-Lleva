"""Launcher del servidor multijugador en red.

Arranca el servidor de sockets delega en ``juego_lleva.red.servidor``.
Uso:
    python servidor.py [--host 0.0.0.0] [--puerto 5555]
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "juego_lleva"))

from juego_lleva.red.servidor import main

if __name__ == "__main__":
    main()