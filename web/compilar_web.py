"""Compila el juego a WebAssembly con pygbag y completa los archivos del CDN.

El código se importa como paquete (`juego_lleva.*`), y pygbag exige que la
carpeta de la app contenga un `main.py` en su raíz. Por eso este script prepara
una carpeta temporal:

    app/main.py           -> ``from juego_lleva.main import main``
    app/juego_lleva/...   -> copia del paquete (sin build/tests)

compila esa carpeta con pygbag y publica el resultado en
``juego_lleva/build/web``.

pygbag 0.9.3 genera la web con dependencias externas que ya no están
disponibles en su CDN (browserfs.min.js) y Python deja el build "colgado"
tras escribir los artefactos. Este script:

1. Prepara la carpeta de staging con el paquete y un main.py de entrada.
2. Ejecuta la compilación de pygbag.
3. Espera a que aparezcan los artefactos (index.html, *.apk, *.tar.gz).
4. Publica el build en juego_lleva/build/web.
5. Sirve browserfs.min.js desde local (el CDN dio 404).
6. Coloca el wheel wasm de pygame-ce en build/web/cdn/cp312/.
7. Corrige index.html para usar los recursos locales.
"""

import pathlib
import shutil
import subprocess
import sys
import time

RAIZ = pathlib.Path(__file__).resolve().parent.parent
JUEGO = RAIZ / "juego_lleva"
STAGING = JUEGO / "build" / "app"
BUILD_PYGAG = STAGING / "build" / "web"
SALIDA = JUEGO / "build" / "web"
VENV_PY = RAIZ / ".venv" / "bin" / "python"
VENDOR = RAIZ / "web" / "vendor"
WHEEL_DIR = RAIZ / "web" / "cdn" / "cp312"

VISOR = "browserfs.min.js"
WHEEL_NOMBRE = "pygame_ce-2.5.7-cp312-cp312-wasm32_bi_emscripten.whl"

MAX_ESPERA_SEG = 900

ENTRADA = "from juego_lleva.main import main\n\nmain()\n"


def _preparar_staging():
    """Crea la carpeta de compilación con el paquete y un main.py de entrada."""
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)
    shutil.copytree(
        JUEGO,
        STAGING / "juego_lleva",
        ignore=shutil.ignore_patterns("build", "__pycache__", "tests", "*.pyc"),
    )
    (STAGING / "main.py").write_text(ENTRADA, encoding="utf-8")


def compilar():
    """Lanza pygbag y devuelve cuando los artefactos estén listos."""
    _preparar_staging()
    log = open(RAIZ / "web" / "build.log", "a", encoding="utf-8")
    log.write(f"\n--- compilacion {time.strftime('%H:%M:%S')} ---\n")
    proceso = subprocess.Popen(
        [str(VENV_PY), "-m", "pygbag", str(STAGING)],
        stdout=log,
        stderr=subprocess.STDOUT)
    inicio = time.time()
    inicio_ns = time.time_ns()
    while time.time() - inicio < MAX_ESPERA_SEG:
        if proceso.poll() is not None:
            log.flush()
            log.close()
            return
        try:
            index_nuevo = (BUILD_PYGAG / "index.html").stat().st_mtime_ns > inicio_ns
            apk_nuevo = any(p.stat().st_mtime_ns > inicio_ns for p in BUILD_PYGAG.glob("*.apk"))
            tar_nuevo = any(p.stat().st_mtime_ns > inicio_ns for p in BUILD_PYGAG.glob("*.tar.gz"))
        except FileNotFoundError:
            index_nuevo = apk_nuevo = tar_nuevo = False
        if index_nuevo and apk_nuevo and tar_nuevo:
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


def _publicar():
    """Copia el build de pygbag a juego_lleva/build/web."""
    if not BUILD_PYGAG.exists():
        sys.exit(f"No se genero el build de pygbag en {BUILD_PYGAG}")
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    shutil.copytree(BUILD_PYGAG, SALIDA)


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
    _publicar()
    completar_recursos()
    print("Listo. Servir con: .venv/bin/python servidor_web.py juego_lleva/build/web")


if __name__ == "__main__":
    main()
