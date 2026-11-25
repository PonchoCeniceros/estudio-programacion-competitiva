# Guía del libro — *Rust · Cuaderno de campo*

Cómo se escribe, se dibuja y se verifica un capítulo. Leerla completa antes de
escribir uno. Los capítulos 3.2, 3.3 y 3.4 son la referencia: ante la duda, se hace
como en ellos.

## Qué es el libro

El cuaderno de Rust en formato de libro, para leerse en tablet (EPUB) e imprimirse
(PDF de 7 × 10 in). Sale de fusionar dos fuentes:

- **El curso «Aprende Rust»** (aprenderust.dev, midudev) aporta el hilo de la
  explicación: primero el problema, luego el código que falla, luego la causa y al
  final la regla. Sus lecciones están resumidas en `notas/curso-aprende-rust.md`.
- **El deck original** (`../notes/pages/`) aporta la profundidad técnica.

`../notes/FUSION-CURSO.md` cruza las dos: qué explicación del curso le falta a cada
página del deck, y en qué capítulo va cada uno de los 63 ejercicios del curso
(`~/Desktop/buffer/curso-rust-midudev/examples/`).

Las explicaciones del curso se reescriben con la voz de esta guía, nunca se copian.
Los ejercicios se usan como aplicación, con el crédito «ejercicio del curso
*Aprende Rust*».

## Archivos

```
libro.toml          manifiesto: portada, secciones y capítulos
build.py            verifica el código y genera build/libro.pdf y build/libro.epub
src/N-seccion/      un Markdown por capítulo: 3-memoria/3.2-ownership.md
src/figuras/        una figura por archivo, en HTML con SVG en línea
estilo/libro.css    tokens y componentes (PDF y EPUB)
estilo/impresion.css  página, portada, contenido, aperturas (solo PDF)
estilo/img/         cardumen de portada y contraportada, y su generador
notas/              material de trabajo; no entra al libro
```

Para agregar un capítulo: escribir el Markdown y ponerle `archivo = "..."` a su
entrada de `libro.toml`. Un capítulo sin `archivo` aparece en gris en el contenido.

## Estructura de un capítulo

Siempre en este orden, con estos títulos:

1. **`# N.M · Nombre`** y, sin subtítulo, **el problema** en dos párrafos cortos:
   qué duele o qué sorprende sin este concepto. Si el capítulo anterior dejó un
   problema abierto, se arranca de ahí.
2. **`## Definiciones y reglas`**: los términos nuevos como lista de definiciones,
   y las reglas numeradas en una caja `.reglas`. Dos o tres reglas, no más.
3. **`## De un vistazo`**: una tabla que compacte el capítulo. Si de ella sale un
   criterio de uso, se dice en una frase debajo.
4. **`## Las reglas, una por una`**: una subsección `###` por regla o por pieza.
   Cada una lleva su fragmento mínimo; lo que no compila se muestra con su error
   real. Aquí van las figuras. Las subsecciones que explican una regla llevan el
   prefijo `[Regla 1:]{.prefijo}`.
5. **`## Aplicación`**: uno o dos programas cortos que usan las reglas juntas. Si
   `FUSION-CURSO.md` asigna ejercicios del curso al capítulo, van aquí.
6. **`## A fondo`**: el detalle técnico del deck que se puede saltar en una primera
   lectura. Cada punto abre con una frase en negrita que termina en punto.
7. **`::: ver-tambien`** con tres a cinco referencias.

Largo: 1,000 a 1,700 palabras de prosa, 8 a 12 páginas en el PDF. Un capítulo
denso puede llegar a 15 o 16; más que eso, se recorta.

Como los bloques de código, las figuras y las cajas no se parten entre páginas, un
bloque que no cabe salta entero y deja un hueco. Para no inflar el paginado:

- La prosa que presenta un bloque va antes del bloque, no después.
- Cuando un ejemplo repite una declaración ya mostrada, la repetición puede ir en
  una línea (`struct Caja { valor: i32 }`, `enum Dir { Norte, Sur }`). La primera
  aparición va expandida, como la deja rustfmt.
- Un error secundario se cuenta en prosa, citando su código y su mensaje real, sin
  bloque propio. El bloque completo se reserva para el error que el apartado enseña.

## Orden topológico

Nada se usa antes de explicarse. El orden es el de `libro.toml`, igual al del deck
(ver «Learning line» en el `CLAUDE.md` de la raíz). Antes de usar algo en un
ejemplo, comprobar que su capítulo es anterior. Las dos excepciones permitidas en
todo el libro son los literales de texto y `String`.

Casos que ya salieron: en la sección 3 no hay `Option` (5.1), ni `Vec` (5.3), ni
adaptadores de iterador (5.6). Sí se puede recorrer con `for` y usar `matches!`
(2.4). Si un ejercicio del curso usa algo posterior, se reescribe con lo disponible
o se mueve a su capítulo.

## Vocabulario

Un término, una traducción, en todo el libro:

| Inglés | En el libro |
| :--- | :--- |
| *match* (verbo) | encajar: «la rama encaja» |
| *bind*, *binding* | ligar; el binding |
| *guard* | *guard*, en itálica |
| *borrow* | prestar, préstamo |
| *move* | mover; el move |
| *owner*, *ownership* | dueño; ownership |
| *scope* | scope |
| *slice* | slice |
| *trait*, *struct*, *enum* | sin traducir |
| *closure* | closure, en femenino: «una closure» |
| *array* | arreglo |
| *statement* / *expression* | enunciado / expresión |

## Tono

Manual técnico. Las reglas vienen de `../notes/GUIA-DE-TONO.md`; R9 y R11 de esa
guía eran para láminas y no aplican.

- **Tercera persona.** El sujeto es el lenguaje, el compilador o el código. Nunca
  «tú», «puedes», «vas a ver», «ya viste».
- **Frase corta**, de 12 a 15 palabras, una idea por frase.
- **Sin raya larga como bisagra.** Punto si son dos ideas; dos puntos si la segunda
  explica la primera.
- **Sin cierres que venden.** Un párrafo termina en dato, regla o ejemplo.
- **Sin superlativos** ni absolutos que no se puedan verificar.
- **Negrita solo** en la frase que abre cada punto de «A fondo». Los términos en
  inglés van en itálica la primera vez.
- **Referencias explícitas**: `[3.3 Borrowing]{.ref}`, no «como se vio antes».
- **Analogías**: las del curso (el libro prestado, la caja con candado) no se usan.
  El aterrizaje viene del orden de la explicación y de mostrar el error.
- Títulos en mayúscula inicial, no en Title Case.
- Español de México: «default», «arreglo», «acento».

## Sintaxis de los componentes

El Markdown es de Pandoc. `build.py` lo preprocesa.

**Título.** `# 3.2 · Ownership`, con ese separador. De ahí salen el número, el
nombre, la etiqueta de sección y la cornisa.

**Definiciones.**

```markdown
Dueño
:   *(owner)*: la variable responsable de liberar un valor.
```

**Caja de reglas.**

```markdown
::: {.reglas titulo="Las tres reglas del ownership"}
1. Cada valor tiene un dueño.
2. Solo puede haber un dueño a la vez.
:::
```

**Código.** Cuatro tipos de bloque:

| Cerca | Qué es | Qué verifica el build |
| :--- | :--- | :--- |
| ` ```rust ` | programa correcto | que compile |
| ` ```rust,compile_fail ` | no compila | que falle al compilar |
| ` ```rust,should_panic ` | compila y truena | que compile y falle al ejecutar |
| ` ```rust,ignore ` | archivo de un proyecto de Cargo | nada: se verifica a mano |
| ` ```salida ` | salida de `rustc`, de un panic o del programa | nada |

Un bloque `compile_fail` o `should_panic` seguido de un bloque `salida` se dibuja
como una sola pieza: cabecera roja, código y panel oscuro. Un bloque `salida`
después de un programa correcto se dibuja como panel oscuro suelto: sirve para un
aviso del compilador (el build compila con los avisos apagados, así que un programa
que solo avisa cuenta como correcto) o para lo que el programa imprime. Si la
salida cabe en un comentario al margen, se prefiere el comentario.

Todo bloque `rust` es un programa completo con `fn main()`. Un bloque en otro
lenguaje (` ```c `) sale como código plano, sin verificar.

`rust,ignore` es solo para código que `rustc` no puede compilar como archivo
suelto: un archivo de un proyecto con varios módulos, un test de integración, o
código que usa un crate externo. La primera línea es un comentario con la ruta
(`// src/lib.rs`). Quien lo escribe arma el proyecto real con `cargo` en una
carpeta temporal fuera del repo, lo compila y lo ejecuta, y lo dice en su reporte.
Si el ejemplo cabe en un solo archivo (módulos en línea con `mod x { ... }`, tests
junto a un `fn main()`), va como bloque `rust` normal. `Cargo.toml` va en un bloque
` ```toml `, y los comandos y su salida en ` ```salida `.
Si el archivo no compila, `rust,ignore,compile_fail` le pone la cabecera roja y lo
une a su `salida`, sin que el build intente compilarlo.

**Ancho: 62 columnas como máximo, en el código y en los bloques `salida`.** Más
ancho parte la línea en el PDF. Los comentarios al margen se acortan antes que
partir. La fuente dibuja con ligaduras `->`, `=>`, `>=`, `==` y `::`; es esperado.

**Comentarios de error.** Un comentario que contiene un código como `E0382` sale en
rojo. Se usa cuando el bloque no lleva `salida` aparte.

**Figura.** `::: {.figura src="figuras/3.3-regla1.html"}` y `:::` en la línea
siguiente.

**Advertencia.** `::: {.advertencia titulo="Lo que evita invalidar s1"}`, con un
párrafo dentro.

**Referencia cruzada.** `[3.3 Borrowing]{.ref}`. Se vuelve enlace cuando el
capítulo existe; mientras tanto solo va en color.

**Ver también.** `::: ver-tambien`, las referencias separadas por ` · `, y `:::`.

## Errores del compilador

Los mensajes son reales. Para cada bloque que no compila:

1. Compilar el fragmento con `rustc --edition 2024` y copiar la salida.
2. Recortarla a lo esencial: la línea `error[E...]`, las líneas de código señaladas
   y sus anotaciones. Se quitan la ruta del archivo, las notas de macros y el
   «aborting due to».
3. Partir a mano las líneas largas para que quepan en 62 columnas, alineando la
   continuación.

En la salida de un panic se quita el identificador del hilo (`thread 'main'
(12345)` queda `thread 'main'`), el archivo se escribe `src/main.rs` y se quita la
nota de `RUST_BACKTRACE`.

No se inventan ni se traducen mensajes. Si `rustc` cambia la redacción, se
actualiza.

## Figuras

Estilo intermedio entre el tema del libro y los diagramas de arquitectura de
`~/framework/artifacts/ft-layout-engine`: del tema, el marco, el título y la
tipografía; de los diagramas, las cajas con relleno por rol, los pasos numerados y
las flechas.

Cada figura es un archivo HTML con esta forma:

```html
<figure class="diagrama">
<figcaption><span class="titulo">Título</span><span class="pie">Una o dos frases.</span></figcaption>
<svg class="dg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 H" role="img" aria-label="...">
  ...
</svg>
</figure>
```

- **`viewBox` de 520 de ancho.** Es el ancho útil de la página, así que una unidad
  es casi un pixel y el texto de 12 sale del tamaño del código.
- **Roles**, como clase del grupo `<g>`: `r-dueno` (teal, quien posee o el valor
  principal), `r-heap` (café, memoria del heap), `r-ref` (azul, préstamos),
  `r-movido` (gris punteado y tachado: lo que dejó de valer), `r-err` (rojo, lo que
  no compila), `r-neutro` (blanco con borde gris: una definición, un molde, un
  valor de paso).
- Texto gris sin tachar, para lo que no se evalúa o no participa: `class="gris"`
  en el `<text>`. Un atributo `fill` no sirve en un `<text>`: la hoja de estilos
  le gana; se usa una clase o `style="fill: ..."`.
- **Piezas**: `caja` (rectángulo de un rol, `rx="6"`), `celda` (rectángulo blanco
  dentro de una caja, `rx="3"`), `tit` (rótulo de la caja, serif), `val` (texto
  centrado, mono), `cod` (línea de código de un paso), `col` (rótulo de columna en
  versalitas), `nota` (itálica gris), `idx` (índices pequeños), `num` (círculo con
  el número del paso).
- **Flechas**: un `<path class="fl-ROL">` para el trazo y un `<polygon
  class="pt-ROL">` para la punta (roles `dueno`, `ref`, `err`, `neutro`). **No usar `<marker>`**: Vivliostyle no los
  resuelve y la flecha sale sin punta.
- El `<svg>` va en línea, no como `<img>`: así usa las fuentes del libro.
- El `aria-label` describe la figura en una frase.
- Una idea por figura. Los mapas densos se reservan para una página de sección.

Las clases están en `estilo/libro.css`, bajo «Diagramas en SVG».

## Verificación

Un capítulo no está terminado hasta que:

1. `python3 build.py` termina con «código verificado».
2. **Se revisó cada página del capítulo renderizada.** Abrir `build/libro.pdf` y
   mirar: líneas de código partidas, texto de figuras cortado o encimado, cajas que
   se salen, tablas apretadas, un «Ver también» huérfano.
3. Ningún bloque de código pasa de 62 columnas.
4. Nada de lo que usa el capítulo se explica después.
5. El texto pasa la lista de tono: sin segunda persona, sin raya como bisagra, sin
   cierres que venden.

Los huecos al pie de página son esperados: el diseño no parte bloques de código,
figuras ni cajas entre páginas.

## Trabajo en paralelo

Cuando varios agentes escriben capítulos a la vez en esta carpeta:

- Cada uno crea y edita **solo** su capítulo y sus figuras
  (`src/figuras/N.M-*.html`). Nadie más toca `libro.toml`, `build.py`, `estilo/`,
  esta guía, ni capítulos o figuras ajenos. Si una figura necesita un estilo que no
  existe, va en línea dentro del propio SVG y se reporta.
- Archivos temporales, solo bajo `/tmp/libro-N.M/`.
- Se construye con `python3 build.py --solo src/.../N.M-nombre.md`, que deja
  `build-cap/N.M/libro.pdf`. **Nunca `python3 build.py` a secas**: reconstruye el
  libro entero.
- El PDF se revisa con la herramienta Read, página por página (con el parámetro
  `pages` si pasa de 10).
- Sin commits ni cambios de rama.
- El reporte final dice: qué cubre cada sección; cuántas páginas quedó; qué figuras
  se hicieron; qué se cambió en los ejercicios del autor; qué se verificó
  ejecutando código y qué no; qué estilos en línea se usaron; qué supone de otros
  capítulos aún no escritos; y las dudas que deba decidir el autor.

## Diseño

Tema 2a «Teal EDO» del handoff de diseño. Página de 7 × 10 in con márgenes de
0.8 in; Source Serif 4 para el texto, Yellowtail para los títulos de nivel 2 y
JetBrains Mono para el código. Los tokens de color están al inicio de
`estilo/libro.css`. El fondo de página es blanco, no el `#f7f6f2` del handoff, para
que se pueda imprimir.

## Pendientes conocidos

- El EPUB no tiene contenido ni aperturas de sección propias, y no se ha validado
  con `epubcheck` ni revisado en un lector.
- La contraportada no tiene texto: solo el título y el crédito al curso.
- El deck (`../notes`) sigue siendo la versión completa hasta que el libro lo cubra.
