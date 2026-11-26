#!/usr/bin/env python3
"""Construye el libro: build/libro.pdf y build/libro.epub.

    python3 build.py              # verifica el código y genera PDF y EPUB
    python3 build.py --solo-pdf
    python3 build.py --sin-verificar
    python3 build.py --solo src/3-memoria/3.5-impl-metodos.md
    python3 build.py --gris       # build/libro-gris.pdf, a partir del último build

`--solo` verifica y construye un único capítulo en build-cap/<número>/libro.pdf, sin
tocar build/ ni exigir que el capítulo esté dado de alta en libro.toml. Sirve para
escribir varios capítulos a la vez.

Pasos:
  1. Verifica los bloques ```rust de cada capítulo con rustc: los normales deben
     compilar, los ```rust,compile_fail deben fallar al compilar y los
     ```rust,should_panic deben compilar y fallar al ejecutar. Un ```rust,ignore
     se resalta y no se verifica (archivos de un proyecto de Cargo).
  2. Preprocesa el Markdown: resalta el código con los colores del tema, agrupa
     cada bloque que no compila con su ```salida, inserta las figuras y resuelve
     las referencias [3.3 Borrowing]{.ref}.
  3. PDF: Pandoc convierte cada capítulo a HTML; se ensamblan portada, contenido y
     aperturas de sección; Vivliostyle pagina.
  4. EPUB: Pandoc, con las fuentes incrustadas y la portada del PDF como imagen.

Requiere pandoc, rustc y @vivliostyle/cli (pnpm install en esta carpeta).
"""
import html
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

RAIZ = pathlib.Path(__file__).resolve().parent
BUILD = RAIZ / "build"
LIBRO = tomllib.loads((RAIZ / "libro.toml").read_text())


# ── Resaltado de Rust ─────────────────────────────────────────────────────────

PALABRAS_CLAVE = set("""
as async await break const continue crate dyn else enum extern fn for if impl in
let loop match mod move mut pub ref return self static struct super trait type
unsafe use where while
""".split())
PRIMITIVOS = set("i8 i16 i32 i64 i128 isize u8 u16 u32 u64 u128 usize f32 f64 bool char str".split())

TOKEN = re.compile(r"""
    (?P<comentario>//[^\n]*)
  | (?P<cadena>b?"(?:\\.|[^"\\])*")
  | (?P<caracter>b?'(?:\\.|[^'\\])')
  | (?P<vida>'[a-z_]\w*)
  | (?P<numero>\b\d[\d_]*(?:\.\d[\d_]*)?(?:[iu](?:8|16|32|64|128|size)|f32|f64)?\b)
  | (?P<ident>[A-Za-z_]\w*!?)
""", re.VERBOSE)


def resaltar_rust(codigo: str) -> str:
    """HTML con <span> por token, con las clases de libro.css."""
    salida, pos = [], 0
    for m in TOKEN.finditer(codigo):
        salida.append(html.escape(codigo[pos:m.start()]))
        texto, tipo = m.group(), m.lastgroup
        clase = None
        if tipo == "comentario":
            clase = "ce" if re.search(r"\bE0\d{3}\b", texto) else "c"
        elif tipo in ("cadena", "caracter"):
            clase = "s"
        elif tipo == "numero":
            clase = "n"
        elif tipo == "ident":
            resto = codigo[m.end():]
            if texto in ("true", "false"):
                clase = "n"
            elif texto in PALABRAS_CLAVE:
                clase = "k"
            elif texto.endswith("!"):
                clase = "f"
            elif texto in PRIMITIVOS or texto[0].isupper():
                clase = "t"
            elif re.match(r"\s*(::<[^>]*>)?\(", resto):
                clase = "f"
        esc = html.escape(texto)
        salida.append(f'<span class="{clase}">{esc}</span>' if clase else esc)
        pos = m.end()
    salida.append(html.escape(codigo[pos:]))
    return "".join(salida)


def resaltar_salida(texto: str) -> str:
    """Colorea la salida de rustc: código de error, gutter y marcas ^^."""
    lineas = []
    for linea in texto.split("\n"):
        esc = html.escape(linea)
        m = re.match(r"(error\[E\d+\]|error|warning)(:.*)", linea)
        if m:
            lineas.append(f'<span class="e">{html.escape(m[1])}</span>'
                          f'<span class="em">{html.escape(m[2])}</span>')
            continue
        m = re.match(r"(\s*\d+ \|)(.*)", linea)
        if m:
            lineas.append(f'<span class="g">{html.escape(m[1])}</span>{html.escape(m[2])}')
            continue
        m = re.match(r"(\s*\|)(.*)", linea)
        if m:
            cuerpo = m[2]
            i = cuerpo.find("^")
            if i >= 0:
                lineas.append(f'<span class="g">{html.escape(m[1] + cuerpo[:i])}</span>'
                              f'<span class="x">{html.escape(cuerpo[i:])}</span>')
            else:
                lineas.append(f'<span class="g">{esc}</span>')
            continue
        lineas.append(esc)
    return "\n".join(lineas)


# ── Preprocesado del Markdown ─────────────────────────────────────────────────

BLOQUE = re.compile(r"^```([^\n`]*)\n(.*?)^```\n", re.M | re.S)


def capitulos():
    for sec in LIBRO["secciones"]:
        for cap in sec["capitulos"]:
            yield sec, cap


def ancla(numero: str) -> str:
    return "cap-" + numero.replace(".", "-")


def preprocesar(sec: dict, cap: dict) -> str:
    texto = (RAIZ / cap["archivo"]).read_text()
    disponibles = {c["numero"] for _, c in capitulos() if "archivo" in c}

    # Título: «# 3.2 · Ownership» → número y nombre con sus clases, más los datos
    # para la etiqueta de sección y la cornisa.
    texto = re.sub(
        r"\A# (\S+) · (.+)\n",
        lambda m: (f'# [{m[1]}]{{.num}} [{m[2]}]{{.nombre}} '
                   f'{{#{ancla(m[1])} seccion="Sección {sec["numero"]} · {sec["nombre"]}" '
                   f'cornisa="{m[1]} · {m[2]}"}}\n'),
        texto)

    # Código: cada bloque pasa a HTML ya resaltado. Un bloque que no compila se
    # agrupa con la salida del compilador que lo sigue, si la hay.
    def bloque_html(m_codigo, m_salida=None):
        info, codigo = m_codigo[1], m_codigo[2].rstrip("\n")
        if info.startswith("{"):          # ```{=html} y similares: pasan tal cual a Pandoc
            return m_codigo[0]
        if info.startswith("rust"):
            cuerpo = resaltar_rust(codigo)
        else:
            cuerpo = html.escape(codigo)
        if "compile_fail" in info or "should_panic" in info:
            rotulo = "✗ NO COMPILA" if "compile_fail" in info else "✗ COMPILA, PERO FALLA AL EJECUTAR"
            partes = ['<div class="no-compila">',
                      f'<div class="cabecera">{rotulo}</div>',
                      f'<pre class="fuente"><code>{cuerpo}</code></pre>']
            if m_salida is not None:
                partes.append(f'<pre class="salida"><code>{resaltar_salida(m_salida[2].rstrip())}</code></pre>')
            partes.append("</div>")
            html_bloque = "\n".join(partes)
        elif info == "salida":
            html_bloque = f'<pre class="salida"><code>{resaltar_salida(codigo)}</code></pre>'
        else:
            html_bloque = f'<div class="codigo"><pre><code>{cuerpo}</code></pre></div>'
        return "```{=html}\n" + html_bloque + "\n```\n"

    piezas, pos = [], 0
    bloques = list(BLOQUE.finditer(texto))
    i = 0
    while i < len(bloques):
        m = bloques[i]
        piezas.append(texto[pos:m.start()])
        siguiente = bloques[i + 1] if i + 1 < len(bloques) else None
        falla = "compile_fail" in m[1] or "should_panic" in m[1]
        if (falla and siguiente is not None and siguiente[1] == "salida"
                and texto[m.end():siguiente.start()].strip() == ""):
            piezas.append(bloque_html(m, siguiente))
            pos = siguiente.end()
            i += 2
        else:
            piezas.append(bloque_html(m))
            pos = m.end()
            i += 1
    piezas.append(texto[pos:])
    texto = "".join(piezas)

    # Figuras: ::: {.figura src="figuras/x.html"} ::: → el HTML del archivo.
    texto = re.sub(
        r'^::: \{\.figura src="([^"]+)"\}\n:::\n',
        lambda m: "```{=html}\n" + (RAIZ / "src" / m[1]).read_text().strip() + "\n```\n",
        texto, flags=re.M)

    # Referencias: enlace si el capítulo existe, texto en color si está pendiente.
    def ref(m):
        numero = m[1]
        if numero in disponibles:
            return f"[{numero} {m[2]}](#{ancla(numero)})"
        return f"[{numero} {m[2]}]{{.ref}}"
    texto = re.sub(r"\[(\d+\.\d+) ([^\]]+)\]\{\.ref\}", ref, texto)
    return texto


def pandoc(entrada: str, *args) -> str:
    r = subprocess.run(["pandoc", "--from", "markdown", "--wrap=none", *args],
                       input=entrada, capture_output=True, text=True, check=True)
    if r.stderr.strip():
        print(r.stderr.strip(), file=sys.stderr)
    return r.stdout


# ── Verificación del código ───────────────────────────────────────────────────

def verificar(archivos=None) -> bool:
    ok = True
    if archivos is None:
        archivos = [cap["archivo"] for _, cap in capitulos() if "archivo" in cap]
    with tempfile.TemporaryDirectory() as tmp:
        for archivo in archivos:
            cap = {"archivo": archivo}
            texto = (RAIZ / archivo).read_text()
            for n, m in enumerate(BLOQUE.finditer(texto), 1):
                if not m[1].startswith("rust") or "ignore" in m[1]:
                    continue
                debe_fallar = "compile_fail" in m[1]
                fuente = pathlib.Path(tmp) / f"b{n}.rs"
                fuente.write_text(m[2])
                r = subprocess.run(
                    ["rustc", "--edition", "2024", "--crate-type", "bin", "-A", "warnings",
                     "-o", str(fuente.with_suffix("")), str(fuente)],
                    capture_output=True, text=True)
                compilo = r.returncode == 0
                linea = texto[:m.start()].count("\n") + 1
                if "should_panic" in m[1] and compilo:
                    corrida = subprocess.run([str(fuente.with_suffix(""))], capture_output=True)
                    if corrida.returncode == 0:
                        ok = False
                        print(f"✗ {cap['archivo']}:{linea}: debía fallar al ejecutar", file=sys.stderr)
                if compilo == debe_fallar:
                    ok = False
                    esperado = "fallar" if debe_fallar else "compilar"
                    print(f"✗ {cap['archivo']}:{linea}: debía {esperado}", file=sys.stderr)
                    if not compilo:
                        print(r.stderr, file=sys.stderr)
                # rustc deja fuera lo que está bajo #[cfg(test)]: se compila aparte.
                if compilo and not debe_fallar and "#[test]" in m[2]:
                    rt = subprocess.run(
                        ["rustc", "--edition", "2024", "--test", "-A", "warnings",
                         "-o", str(fuente.with_suffix(".t")), str(fuente)],
                        capture_output=True, text=True)
                    if rt.returncode != 0:
                        ok = False
                        print(f"✗ {cap['archivo']}:{linea}: los tests no compilan", file=sys.stderr)
                        print(rt.stderr, file=sys.stderr)
    print("código verificado" if ok else "hay bloques de código mal", file=sys.stderr)
    return ok


# ── PDF ───────────────────────────────────────────────────────────────────────

def html_portada() -> str:
    e = html.escape
    return f"""<div class="portada">
<img class="peces" src="estilo/img/portada-peces.svg" alt="">
<div class="arriba"><span></span><span class="chip">{e(LIBRO['edicion'])}</span></div>
<div class="titulo">{e(LIBRO['titulo'])}</div>
<div class="subtitulo">{e(LIBRO['subtitulo'])}</div>
<div class="abajo"><div class="linea"></div>
<div class="autor">{e(LIBRO['autor'])}</div></div>
</div>"""


def html_contraportada() -> str:
    e = html.escape
    return f"""<div class="contraportada">
<img class="peces" src="estilo/img/peces.svg" alt="">
<div class="descripcion"><p>{e(LIBRO['descripcion'].strip())}</p>
<p>{e(LIBRO['descripcion2'].strip())}</p></div>
</div>"""


def lista_temas(sec: dict) -> str:
    filas = []
    for cap in sec["capitulos"]:
        n, t = html.escape(cap["numero"]), html.escape(cap["titulo"])
        if "archivo" in cap:
            href = "#" + ancla(cap["numero"])
            filas.append(f'<span class="n">{n}</span><a href="{href}">{t}</a>'
                         f'<a class="pag-ref" href="{href}"></a>')
        else:
            filas.append(f'<span class="n pendiente">{n}</span><span class="pendiente">{t}</span><span></span>')
    return "\n".join(filas)


def html_contenido() -> str:
    partes = ['<div class="contenido">', '<div class="encabezado">Contenido</div>']
    suelto = ('<div class="seccion suelto"><div class="seccion-titulo"><a href="#{0}">{1}</a>'
              '<a class="pag pag-ref" href="#{0}"></a></div></div>')
    partes.append(suelto.format("prefacio", "Prefacio"))
    partes.append(suelto.format("agradecimientos", "Agradecimientos"))
    partes.append(suelto.format("mapa", "Mapa del lenguaje"))
    for sec in LIBRO["secciones"]:
        href = f"#sec-{sec['numero']}"
        titulo = f'{sec["numero"]}. {html.escape(sec["nombre"])}'
        if any("archivo" in cap for cap in sec["capitulos"]):
            cabeza = f'<a href="{href}">{titulo}</a><a class="pag pag-ref" href="{href}"></a>'
        else:
            cabeza = f'<a class="pendiente">{titulo}</a>'
        partes.append(f'<div class="seccion"><div class="seccion-titulo">{cabeza}</div>'
                      f'<div class="temas">{lista_temas(sec)}</div></div>')
    partes.append(suelto.format("referencias", "Referencias"))
    partes.append("</div>")
    return "\n".join(partes)


def preliminar(clave: str) -> str:
    """Prefacio y referencias: Markdown sin código, directo a Pandoc."""
    return (RAIZ / LIBRO[clave]).read_text()


def mapa_md() -> str:
    """El mapa del lenguaje: las secciones en una columna central y sus capítulos a
    los lados. Se dibuja desde libro.toml, así que siempre coincide con el contenido."""
    e = html.escape
    ancho, cx, nodo_w = 600, 300, 178
    fila, sep = 18, 11
    partes, y = [], 8
    bloques = []
    for sec in LIBRO["secciones"]:
        caps = sec["capitulos"]
        mitad = (len(caps) + 1) // 2
        filas = max(mitad, 2)
        alto = filas * fila
        bloques.append((sec, caps[:mitad], caps[mitad:], y, alto))
        y += alto + sep
    total = y - sep + 8
    partes.append(f'<path class="mapa-eje" d="M{cx} 0 L{cx} {total}"/>')

    def chip(cap, x, yc, derecha):
        n, t = cap["numero"], cap["titulo"]
        w = 34 + len(t) * 5.3 + (5 if len(n) > 3 else 0)
        x0 = x if derecha else x - w
        tx = x0 + (27 if len(n) <= 3 else 32)
        clase = "mapa-chip" if "archivo" in cap else "mapa-chip pendiente"
        cuerpo = (f'<rect class="{clase}" x="{x0:.1f}" y="{yc - 7.5}" width="{w:.1f}" height="15" rx="3"/>'
                  f'<text class="mapa-n" x="{x0 + 5:.1f}" y="{yc + 3}">{e(n)}</text>'
                  f'<text class="mapa-t" x="{tx:.1f}" y="{yc + 3.2}">{e(t)}</text>')
        if "archivo" in cap:
            return f'<a href="#{ancla(n)}">{cuerpo}</a>'
        return cuerpo

    for sec, izq, der, y0, alto in bloques:
        yc = y0 + alto / 2
        for lado, caps in ((False, izq), (True, der)):
            if not caps:
                continue
            xb = cx + (nodo_w / 2 + 14) * (1 if lado else -1)
            xn = cx + (nodo_w / 2) * (1 if lado else -1)
            ys = [yc + (i - (len(caps) - 1) / 2) * fila for i in range(len(caps))]
            partes.append(f'<path class="mapa-rama" d="M{xn} {yc} L{xb} {yc} M{xb} {ys[0]} L{xb} {ys[-1]}"/>')
            for cap, yy in zip(caps, ys):
                xc = xb + (6 if lado else -6)
                partes.append(f'<path class="mapa-rama" d="M{xb} {yy} L{xc} {yy}"/>')
                partes.append(chip(cap, xc, yy, lado))
        partes.append(
            f'<a href="#sec-{sec["numero"]}"><rect class="mapa-nodo" x="{cx - nodo_w / 2}" y="{yc - 15}" '
            f'width="{nodo_w}" height="30" rx="5"/>'
            f'<text class="mapa-sec" x="{cx}" y="{yc - 2}">{sec["numero"]} · {e(sec["nombre"])}</text>'
            f'<text class="mapa-idea" x="{cx}" y="{yc + 10}">{e(sec.get("idea", ""))}</text></a>')
    svg = (f'<svg class="dg mapa" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {total}" '
           f'role="img" aria-label="Mapa del lenguaje: las secciones del libro en orden, '
           f'cada una con sus capítulos.">' + "".join(partes) + "</svg>")
    return ('# [Mapa del lenguaje]{.nombre} {#mapa cornisa="Mapa del lenguaje"}\n\n'
            "Las secciones, de arriba abajo, en el orden en que se leen: cada una usa "
            "solo lo que explican las anteriores. A los lados, sus capítulos.\n\n"
            "```{=html}\n" + svg + "\n```\n")


def html_apertura(sec: dict) -> str:
    return f"""<div class="apertura" id="sec-{sec['numero']}">
<div class="banda"><div class="rotulo">SECCIÓN</div>
<div class="nombre"><span class="num">{sec['numero']}</span><span class="txt">{html.escape(sec['nombre'])}</span></div></div>
<div class="temas-titulo">TEMAS DE LA SECCIÓN</div>
<div class="temas">{lista_temas(sec)}</div>
</div>"""


def construir_pdf():
    cuerpo = [html_portada(), html_contenido(),
              pandoc(preliminar("prefacio"), "--to", "html5", "--section-divs"),
              pandoc(preliminar("agradecimientos"), "--to", "html5", "--section-divs"),
              pandoc(mapa_md(), "--to", "html5", "--section-divs")]
    for sec in LIBRO["secciones"]:
        if not any("archivo" in cap for cap in sec["capitulos"]):
            continue
        cuerpo.append(html_apertura(sec))
        for cap in sec["capitulos"]:
            if "archivo" in cap:
                cuerpo.append(pandoc(preprocesar(sec, cap), "--to", "html5", "--section-divs"))
    cuerpo.append(pandoc(preliminar("referencias"), "--to", "html5", "--section-divs"))
    cuerpo.append(html_contraportada())
    documento = f"""<!DOCTYPE html>
<html lang="{LIBRO['idioma']}"><head><meta charset="utf-8">
<title>{html.escape(LIBRO['titulo'])} · {html.escape(LIBRO['subtitulo'])}</title>
<link rel="stylesheet" href="estilo/libro.css">
<link rel="stylesheet" href="estilo/impresion.css">
</head><body>
{chr(10).join(cuerpo)}
</body></html>"""
    (BUILD / "libro.html").write_text(documento)
    subprocess.run(["pnpm", "exec", "vivliostyle", "build", "build/libro.html",
                    "-o", "build/libro.pdf"], cwd=RAIZ, check=True,
                   stdout=subprocess.DEVNULL)
    print("build/libro.pdf", file=sys.stderr)


# ── PDF en escala de grises ───────────────────────────────────────────────────

def a_gris(texto: str) -> str:
    """Cambia cada color #rgb / #rrggbb por su gris de igual luminancia."""
    def gris(m):
        h = m[1]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        y = round(0.299 * r + 0.587 * g + 0.114 * b)
        return f"#{y:02x}{y:02x}{y:02x}"
    return re.sub(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", gris, texto)


def construir_pdf_gris():
    """build/libro-gris.pdf: el interior en escala de grises, para ver cómo saldría
    impreso en blanco y negro; portada y contraportada siguen a color. Parte de
    build/libro.html."""
    destino = BUILD / "gris"
    if destino.exists():
        shutil.rmtree(destino)
    copiar_estilo(destino)
    # Portada y contraportada se quedan a color: sus reglas y los peces no se tocan.
    def regla(m):
        selector = m[0].split("{")[0]
        return m[0] if "portada" in selector else a_gris(m[0])
    for archivo in (destino / "estilo").glob("*.css"):
        css = archivo.read_text()
        archivo.write_text(re.sub(r"[^{}]+\{(?:[^{}]|\{[^{}]*\})*\}", regla, css))
    (destino / "libro.html").write_text(a_gris((BUILD / "libro.html").read_text()))
    subprocess.run(["pnpm", "exec", "vivliostyle", "build", "build/gris/libro.html",
                    "-o", "build/libro-gris.pdf"], cwd=RAIZ, check=True,
                   stdout=subprocess.DEVNULL)
    print("build/libro-gris.pdf", file=sys.stderr)


# ── EPUB ──────────────────────────────────────────────────────────────────────

def portada_png() -> pathlib.Path | None:
    """La primera página del PDF como imagen, para la portada del EPUB (macOS)."""
    if not shutil.which("qlmanage") or not (BUILD / "libro.pdf").exists():
        return None
    subprocess.run(["qlmanage", "-t", "-s", "1600", "-o", str(BUILD), str(BUILD / "libro.pdf")],
                   capture_output=True)
    png = BUILD / "libro.pdf.png"
    if png.exists():
        destino = BUILD / "portada.png"
        png.rename(destino)
        return destino
    return None


def estilo_diagramas() -> str:
    """Las reglas `.dg` de libro.css, con las variables resueltas: un SVG suelto no
    hereda ni las variables ni la hoja del libro."""
    css = (RAIZ / "estilo" / "libro.css").read_text()
    variables = dict(re.findall(r"(--[\w-]+):\s*([^;]+);", css))
    reglas = [r.strip() for r in re.findall(r"[^{}]+\{[^{}]*\}", css)
              if ".dg" in r.split("{")[0]]
    texto = "\n".join(reglas)
    return re.sub(r"var\((--[\w-]+)\)", lambda m: variables[m[1]].strip(), texto)


def diagramas_como_imagen(texto: str, contador: list) -> str:
    """En el EPUB cada diagrama va como imagen SVG con fondo blanco. Un lector en modo
    oscuro aclara el texto del documento, también el de un SVG en línea, pero no toca
    una imagen: así el diagrama se ve igual con cualquier tema."""
    estilo = estilo_diagramas()

    def a_imagen(m):
        contador[0] += 1
        svg = m[0]
        apertura = re.match(r"<svg[^>]*>", svg)[0]
        alto = re.search(r'viewBox="[\d.]+ [\d.]+ ([\d.]+) ([\d.]+)"', apertura)
        fondo = (f'<rect x="-8" y="-8" width="{float(alto[1]) + 16}" '
                 f'height="{float(alto[2]) + 16}" rx="6" fill="#ffffff"/>')
        vb = re.sub(r'viewBox="([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)"',
                    lambda v: f'viewBox="-8 -8 {float(v[3]) + 16} {float(v[4]) + 16}"', apertura)
        cuerpo = svg[len(apertura):]
        archivo = BUILD / "tmp" / f"figura-{contador[0]:02d}.svg"
        archivo.write_text(f"{vb}<style>{estilo}</style>{fondo}{cuerpo}")
        etiqueta = re.search(r'aria-label="([^"]*)"', apertura)
        alt = etiqueta[1] if etiqueta else ""
        return f'<img class="dg-img" src="{archivo}" alt="{alt}" />'

    return re.sub(r'<svg class="dg"[\s\S]*?</svg>', a_imagen, texto)


def construir_epub():
    (BUILD / "tmp").mkdir(exist_ok=True)
    contador = [0]
    entradas = [preliminar("prefacio"), preliminar("agradecimientos"),
                diagramas_como_imagen(mapa_md(), contador)]
    for sec in LIBRO["secciones"]:
        for cap in sec["capitulos"]:
            if "archivo" in cap:
                entradas.append(diagramas_como_imagen(preprocesar(sec, cap), contador))
    entradas.append(preliminar("referencias"))
    md = BUILD / "tmp" / "libro.md"
    md.parent.mkdir(exist_ok=True)
    md.write_text("\n\n".join(entradas))
    args = ["pandoc", str(md), "--from", "markdown", "--to", "epub3",
            "--metadata", f"title={LIBRO['titulo']} · {LIBRO['subtitulo']}",
            "--metadata", f"author={LIBRO['autor']}",
            "--metadata", f"lang={LIBRO['idioma']}",
            "--metadata", f"rights={LIBRO['autor']}",
            "--css", str(RAIZ / "estilo" / "libro.css"),
            "--split-level=1", "--toc-depth=1",
            "-o", str(BUILD / "libro.epub")]
    for fuente in sorted((RAIZ / "estilo" / "fuentes").glob("*.ttf")):
        args.append(f"--epub-embed-font={fuente}")
    portada = portada_png()
    if portada:
        args += [f"--epub-cover-image={portada}", "--epub-title-page=false"]
    subprocess.run(args, check=True)
    print("build/libro.epub", file=sys.stderr)


def copiar_estilo(destino: pathlib.Path):
    (destino / "estilo" / "img").mkdir(parents=True)
    for css in (RAIZ / "estilo").glob("*.css"):
        shutil.copy(css, destino / "estilo")
    for svg in (RAIZ / "estilo" / "img").glob("*.svg"):
        shutil.copy(svg, destino / "estilo" / "img")
    shutil.copytree(RAIZ / "estilo" / "fuentes", destino / "fonts")


def construir_solo(archivo: str):
    """Un capítulo suelto, en build-cap/<número>/, para trabajar varios a la vez."""
    ruta = (RAIZ / archivo) if not pathlib.Path(archivo).is_absolute() else pathlib.Path(archivo)
    archivo = str(ruta.relative_to(RAIZ))
    m = re.match(r"# (\d+)\.(\d+) · (.+)", ruta.read_text())
    if not m:
        sys.exit(f"{archivo}: la primera línea debe ser «# N.M · Título»")
    numero = f"{m[1]}.{m[2]}"
    sec = next((s for s in LIBRO["secciones"] if str(s["numero"]) == m[1]), None)
    if sec is None:
        sys.exit(f"{archivo}: la sección {m[1]} no está en libro.toml")
    if not verificar([archivo]):
        sys.exit(1)
    destino = RAIZ / "build-cap" / numero
    if destino.exists():
        shutil.rmtree(destino)
    copiar_estilo(destino)
    cap = {"numero": numero, "titulo": m[3], "archivo": archivo}
    cuerpo = pandoc(preprocesar(sec, cap), "--to", "html5", "--section-divs")
    (destino / "libro.html").write_text(f"""<!DOCTYPE html>
<html lang="{LIBRO['idioma']}"><head><meta charset="utf-8"><title>{numero}</title>
<link rel="stylesheet" href="estilo/libro.css">
<link rel="stylesheet" href="estilo/impresion.css">
</head><body>
{cuerpo}
</body></html>""")
    relativo = destino.relative_to(RAIZ)
    subprocess.run(["pnpm", "exec", "vivliostyle", "build", str(relativo / "libro.html"),
                    "-o", str(relativo / "libro.pdf")], cwd=RAIZ, check=True,
                   stdout=subprocess.DEVNULL)
    print(relativo / "libro.pdf", file=sys.stderr)


OPCIONES = {"--solo", "--solo-pdf", "--sin-verificar", "--gris"}


def main():
    desconocidas = [a for a in sys.argv[1:] if a.startswith("-") and a not in OPCIONES]
    if desconocidas:
        sys.exit(__doc__)
    if "--gris" in sys.argv:
        construir_pdf_gris()
        return
    if "--solo" in sys.argv:
        construir_solo(sys.argv[sys.argv.index("--solo") + 1])
        return
    opciones = set(sys.argv[1:])
    if "--sin-verificar" not in opciones and not verificar():
        sys.exit(1)
    if BUILD.exists():
        shutil.rmtree(BUILD)
    copiar_estilo(BUILD)
    construir_pdf()
    if "--solo-pdf" not in opciones:
        construir_epub()


if __name__ == "__main__":
    main()
