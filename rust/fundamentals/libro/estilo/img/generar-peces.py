#!/usr/bin/env python3
"""Genera los cardúmenes de la portada y la contraportada a partir de un solo pez.

    python3 estilo/img/generar-peces.py

Escribe portada-peces.svg (la página completa, 672 × 960) y peces.svg (la
contraportada). El pez mira a la derecha y mide 100 × 45 en su propio sistema.
"""
import pathlib

AQUI = pathlib.Path(__file__).resolve().parent
DEFS = """  <defs>
    <g id="pez" stroke-linecap="round" stroke-linejoin="round">
      <!-- relleno: cuerpo y sombra del vientre -->
      <path d="M22,26 C38,12 62,8 82,14 C90,17 95,21 97,24 C92,30 82,36 64,37 C46,38 32,34 22,26 Z" fill="#a33b2b"/>
      <path d="M30,30 C44,36 62,38 78,33 C86,30 92,27 97,24 C92,30 82,36 64,37 C46,38 34,35 30,30 Z" fill="#6e241b"/>
      <path d="M22,26 L7,15 C11,22 11,30 7,38 Z" fill="#a33b2b"/>
      <!-- rayas -->
      <g stroke="#ecc2b2" stroke-width="1.5" fill="none">
        <path d="M45,15 C43,22 43,30 45,36"/>
        <path d="M52,12 C50,20 50,30 52,37"/>
        <path d="M59,11 C57,19 57,30 59,37"/>
        <path d="M66,11 C64,19 64,29 66,36"/>
        <path d="M73,12 C71,19 71,28 73,35"/>
      </g>
      <!-- contorno crema, desfasado del relleno como en una serigrafía -->
      <g stroke="#ecdcc6" stroke-width="1.7" fill="none" transform="translate(-1.6 -1.8)">
        <path d="M22,26 C38,12 62,8 82,14 C90,17 95,21 97,24 C92,30 82,36 64,37 C46,38 32,34 22,26 Z"/>
        <path d="M22,26 L7,15 C11,22 11,30 7,38 Z"/>
        <path d="M46,11 C47,2 62,0 69,11"/>
        <path d="M56,37 C56,44 65,45 69,36"/>
        <path d="M81,15 C78,21 78,29 81,34"/>
      </g>
      <circle cx="88" cy="20" r="1.5" fill="#ecdcc6"/>
    </g>
  </defs>
"""


def pez(x, y, ancho, giro=0, espejo=False):
    """Un pez con su esquina superior izquierda en (x, y)."""
    e = ancho / 100
    voltea = " translate(100 0) scale(-1 1)" if espejo else ""
    return (f'  <use href="#pez" transform="translate({x:.1f} {y:.1f}) scale({e:.3f})'
            f'{voltea} rotate({giro} 50 25)"/>')


def svg(ancho, alto, peces, titulo):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" '
            f'width="{ancho}" height="{alto}">\n  <title>{titulo}</title>\n'
            + DEFS + "\n".join(peces) + "\n</svg>\n")


# ── Contraportada: el cardumen de peces-original.png ─────────────────────────
CAJAS = [(274, 25, 330, 50), (85, 35, 114, 48), (167, 69, 206, 85), (301, 109, 334, 126),
         (53, 120, 76, 129), (207, 156, 254, 175), (100, 189, 120, 197), (306, 207, 348, 224),
         (175, 241, 206, 257), (265, 284, 291, 295)]
GIROS = [-7, 3, -4, 5, -2, -6, 4, -3, 6, -5]


def contraportada():
    peces = [pez(x0, y0 - 2, x1 - x0, g) for (x0, y0, x1, _), g in zip(CAJAS, GIROS)]
    return svg(361, 308, peces, "Cardumen")


# ── Portada ─────────────────────────────────────────────────────────────────
# Coordenadas de la página de 7 × 10 in a 96 px/in. Es el cardumen de la
# contraportada sin espejear, ampliado sobre la página, más un pez grande. Los
# peces pueden cruzar el título: el texto de la portada va encima.
ORIGEN = (40, 200)                    # dónde cae la esquina del cardumen
ESCALA = 1.64                         # el cardumen mide 361 × 308 en su propio sistema
GRANDE = (110, 690, 170, -5)          # x, y, ancho, giro
OMITIR = {(207, 156, 254, 175)}       # el que quedaba detrás de «Cuaderno de campo»


def portada():
    ox, oy = ORIGEN
    peces = [pez(ox + x0 * ESCALA, oy + (y0 - 2) * ESCALA, (x1 - x0) * ESCALA, g)
             for (x0, y0, x1, y1), g in zip(CAJAS, GIROS) if (x0, y0, x1, y1) not in OMITIR]
    x, y, w, g = GRANDE
    peces.append(pez(x, y, w, g))
    return svg(672, 960, peces, "Cardumen de la portada")


if __name__ == "__main__":
    (AQUI / "portada-peces.svg").write_text(portada())
    (AQUI / "peces.svg").write_text(contraportada())
