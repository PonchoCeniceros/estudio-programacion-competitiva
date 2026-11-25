#!/usr/bin/env python3
"""Construye el libro: build/libro.pdf y build/libro.epub.

    python3 build.py              # verifica el código y genera PDF y EPUB
    python3 build.py --solo-pdf
    python3 build.py --sin-verificar
    python3 build.py --solo src/3-memoria/3.5-impl-metodos.md

`--solo` verifica y construye un único capítulo en build-cap/<número>/libro.pdf, sin
tocar build/ ni exigir que el capítulo esté dado de alta en libro.toml. Sirve para
escribir varios capítulos a la vez.

Pasos:
  1. Verifica los bloques ```rust de cada capítulo con rustc: los normales deben
     compilar, los ```rust,compile_fail deben fallar al compilar y los
     ```rust,should_panic deben compilar y fallar al ejecutar.
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
                if not m[1].startswith("rust"):
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
    print("código verificado" if ok else "hay bloques de código mal", file=sys.stderr)
    return ok


# ── PDF ───────────────────────────────────────────────────────────────────────

def html_portada() -> str:
    e = html.escape
    return f"""<div class="portada">
<img class="peces" src="estilo/img/portada-peces.svg" alt="">
<div class="arriba"><span class="etiqueta">{e(LIBRO['etiqueta'])}</span><span class="chip">{e(LIBRO['edicion'])}</span></div>
<div class="titulo">{e(LIBRO['titulo'])}</div>
<div class="subtitulo">{e(LIBRO['subtitulo'])}</div>
<div class="abajo"><div class="linea"></div>
<div class="autor">{e(LIBRO['autor'])}</div><div class="coautor">{e(LIBRO['coautor'])}</div></div>
</div>"""


def html_contraportada() -> str:
    e = html.escape
    return f"""<div class="contraportada">
<img class="peces" src="estilo/img/peces.svg" alt="">
<div class="abajo"><div class="linea"></div>
<div class="titulo-chico">{e(LIBRO['titulo'])} · <span>{e(LIBRO['subtitulo'])}</span></div>
<div class="creditos">{e(LIBRO['creditos'])}</div></div>
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
    for sec in LIBRO["secciones"]:
        href = f"#sec-{sec['numero']}"
        titulo = f'{sec["numero"]}. {html.escape(sec["nombre"])}'
        if any("archivo" in cap for cap in sec["capitulos"]):
            cabeza = f'<a href="{href}">{titulo}</a><a class="pag pag-ref" href="{href}"></a>'
        else:
            cabeza = f'<a class="pendiente">{titulo}</a>'
        partes.append(f'<div class="seccion"><div class="seccion-titulo">{cabeza}</div>'
                      f'<div class="temas">{lista_temas(sec)}</div></div>')
    partes.append("</div>")
    return "\n".join(partes)


def html_apertura(sec: dict) -> str:
    return f"""<div class="apertura" id="sec-{sec['numero']}">
<div class="banda"><div class="rotulo">SECCIÓN</div>
<div class="nombre"><span class="num">{sec['numero']}</span><span class="txt">{html.escape(sec['nombre'])}</span></div></div>
<div class="temas-titulo">TEMAS DE LA SECCIÓN</div>
<div class="temas">{lista_temas(sec)}</div>
</div>"""


def construir_pdf():
    cuerpo = [html_portada(), html_contenido()]
    for sec in LIBRO["secciones"]:
        if not any("archivo" in cap for cap in sec["capitulos"]):
            continue
        cuerpo.append(html_apertura(sec))
        for cap in sec["capitulos"]:
            if "archivo" in cap:
                cuerpo.append(pandoc(preprocesar(sec, cap), "--to", "html5", "--section-divs"))
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


def construir_epub():
    entradas = []
    for sec in LIBRO["secciones"]:
        for cap in sec["capitulos"]:
            if "archivo" in cap:
                entradas.append(preprocesar(sec, cap))
    md = BUILD / "tmp" / "libro.md"
    md.parent.mkdir(exist_ok=True)
    md.write_text("\n\n".join(entradas))
    args = ["pandoc", str(md), "--from", "markdown", "--to", "epub3",
            "--metadata", f"title={LIBRO['titulo']} · {LIBRO['subtitulo']}",
            "--metadata", f"author={LIBRO['autor']}",
            "--metadata", f"lang={LIBRO['idioma']}",
            "--metadata", f"rights={LIBRO['creditos']}",
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


def main():
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
