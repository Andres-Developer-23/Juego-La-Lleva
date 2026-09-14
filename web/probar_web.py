"""Verifica la versión web compilada con un navegador headless.

Uso:
    .venv/bin/python web/probar_web.py [url] [segundos] [png_salida]

Se imprime la consola del navegador, los errores de página y se guarda una
captura. Útil después de cada web/compilar_web.py.
"""

import pathlib
import sys
import time

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/"
ESPERA = int(sys.argv[2]) if len(sys.argv) > 2 else 30
SALIDA = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else \
    pathlib.Path("/tmp/opencode/web_probar.png")

consola = []
errores = []

with sync_playwright() as p:
    navegador = p.firefox.launch(headless=True)
    pagina = navegador.new_page()
    pagina.on("console", lambda m: consola.append(f"{m.type}: {m.text}"))
    pagina.on("pageerror", lambda e: errores.append(str(e)))
    pagina.goto(URL, wait_until="load", timeout=60000)
    time.sleep(ESPERA)
    pagina.mouse.click(640, 360)
    time.sleep(5)
    pagina.screenshot(path=str(SALIDA))
    navegador.close()

print("== Errores de página ==")
print("\n".join(errores) or "(ninguno)")
print("== Consola (últimas 25) ==")
print("\n".join(consola[-25:]))
print("== Captura:", SALIDA)
sys.exit(1 if errores else 0)