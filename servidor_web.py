"""Servidor web local para la versión navegador del juego (build de pygbag)."""

import argparse
import http.server
import socket
import webbrowser

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Cache-Control": "no-cache",
}


class Manejador(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        for clave, valor in HEADERS.items():
            self.send_header(clave, valor)
        super().end_headers()


def ip_local():
    """Devuelve la IP local del equipo para acceder desde el celular."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def main():
    parser = argparse.ArgumentParser(description="Sirve el juego compilado con pygbag")
    parser.add_argument("directorio", nargs="?", default="build/web")
    parser.add_argument("--puerto", type=int, default=8000)
    args = parser.parse_args()

    manejador = lambda *a, **k: Manejador(*a, directory=args.directorio, **k)
    servidor = http.server.ThreadingHTTPServer(("0.0.0.0", args.puerto), manejador)
    ip = ip_local()
    print(f"Juego disponible en:  http://localhost:{args.puerto}/")
    print(f"Desde tu celular:     http://{ip}:{args.puerto}/")
    webbrowser.open(f"http://localhost:{args.puerto}/")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()