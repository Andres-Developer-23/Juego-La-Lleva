"""Compila el juego a WebAssembly con pygbag y completa los archivos del CDN.

pygbag 0.9.3 genera la web con dependencias externas que ya no están
disponibles en su CDN (browserfs.min.js) y Python deja el build "colgado"
tras escribir los artefactos. Este script:

1. Ejecuta la compilación de pygbag.
2. Espera a que aparezcan los artefactos (index.html, *.apk, *.tar.gz).
3. Sirve browserfs.min.js desde local (el CDN dio 404).
4. Coloca el wheel wasm de pygame-ce en build/web/cdn/cp312/.
5. Corrige index.html para usar los recursos locales.
"""

import pathlib
import shutil
import subprocess
import sys
import time

RAIZ = pathlib.Path(__file__).resolve().parent.parent
JUEGO = RAIZ / "juego_lleva"
SALIDA = JUEGO / "build" / "web"
VENV_PY = RAIZ / ".venv" / "bin" / "python"
VENDOR = RAIZ / "web" / "vendor"
WHEEL_DIR = RAIZ / "web" / "cdn" / "cp312"

VISOR = "browserfs.min.js"
WHEEL_NOMBRE = "pygame_ce-2.5.7-cp312-cp312-wasm32_bi_emscripten.whl"

MAX_ESPERA_SEG = 900


def compilar():
    """Lanza pygbag y devuelve cuando los artefactos estén listos."""
    log = open(RAIZ / "web" / "build.log", "a", encoding="utf-8")
    log.write(f"\n--- compilacion {time.strftime('%H:%M:%S')} ---\n")
    proceso = subprocess.Popen(
        [str(VENV_PY), "-m", "pygbag", str(JUEGO)],
        stdout=log,
        stderr=subprocess.STDOUT)
    inicio = time.time()
    while time.time() - inicio < MAX_ESPERA_SEG:
        if proceso.poll() is not None:
            log.flush()
            log.close()
            return
        listo = all((SALIDA / nombre).exists() for nombre in
                    ("index.html",) + tuple(p.name for p in SALIDA.glob("*.apk")) +
                    tuple(p.name for p in SALIDA.glob("*.tar.gz")))
        if listo and (SALIDA / "index.html").stat().st_size > 1000:
            log.flush()
            break
        time.sleep(5)
    if proceso.poll() is None:
        proceso.terminate()
        try:
            proceso.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proceso.kill()
    log.flush()
    log.close()


def completar_recursos():
    """Copia vendor y wheels a la salida y ajusta index.html."""
    shutil.copy2(VENDOR / VISOR, SALIDA / VISOR)

    destino_wheels = SALIDA / "cdn" / "cp312"
    destino_wheels.mkdir(parents=True, exist_ok=True)
    shutil.copy2(WHEEL_DIR / WHEEL_NOMBRE, destino_wheels / WHEEL_NOMBRE)

    indice = SALIDA / "index.html"
    html = indice.read_text(encoding="utf-8")
    salto = '<script src="%s"></script>' % VISOR
    if salto in html:
        pass
    elif "browserfs.min.js" in html:
        html = html.replace('https://pygame-web.github.io/cdn/0.9.3//browserfs.min.js', VISOR)
        html = html.replace('src="browserfs.min.js"', 'src="%s"' % VISOR)
    else:
        html = html.replace('<script src="https://pygame-web.github.io/cdn/0.9.3/pythons.js"',
                            salto + '\n<script src="https://pygame-web.github.io/cdn/0.9.3/pythons.js"')
    indice.write_text(html, encoding="utf-8")
    print("Recursos listos en", SALIDA)


def main():
    if not VENV_PY.exists():
        sys.exit("No existe el venv con pygbag: .venv/bin/python")
    compilar()
    completar_recursos()
    print("Listo. Servir con: .venv/bin/python servidor_web.py juego_lleva/build/web")


if __name__ == "__main__":
    main()