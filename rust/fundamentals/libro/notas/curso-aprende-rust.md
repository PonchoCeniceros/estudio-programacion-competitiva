# Curso «Aprende Rust» (aprenderust.dev, midudev) — resumen por lección

Material de trabajo para escribir el libro. No entra al libro.

Es un resumen parafraseado de las 26 lecciones, tomado en noviembre de 2026. Sirve
para saber **cómo explica** cada tema el curso: en qué orden, con qué ejemplo y qué
error muestra. El texto del curso es de midudev: se toma el hilo, no las frases.

Límites: los diagramas se conocen solo por sus etiquetas de texto, y de cada
lección solo era visible el enunciado del reto 1. Los demás retos se conocen por
las soluciones en `~/Desktop/buffer/curso-rust-midudev/examples/`, que empiezan en
la lección 8.

**Rasgos comunes de todas las lecciones.** Abren con un diagrama animado de cuatro
pasos narrado por la mascota Ferris. Siguen el patrón: gancho que parte de una
necesidad, código mínimo, una variante que falla, la explicación causal, una regla
práctica en un recuadro y una tabla resumen. Segunda persona, español de España,
cuatro o cinco minutos de lectura. Difieren los temas avanzados a lecciones
posteriores de forma explícita. Casi no usan analogías largas ni comparan con otros
lenguajes más que de pasada.

---

## Módulo 1 · Primeros pasos

### 01 · Hola, Rust: tu primer programa
- **Secciones:** ¿Por qué Rust? · Instalar Rust · Tu primer programa · Compilar y
  ejecutar · Imprimir valores con `println!` · Comentarios.
- **Cómo explica:** abre con la promesa de la velocidad de C con seguridad moderna,
  y con usuarios reales (Firefox, Linux, Discord). Desglosa el hola mundo pieza por
  pieza; el `!` marca una macro, «código que genera código». Explica «compilado»
  con la cadena código fuente → `rustc` → binario que corre sin Rust instalado.
  Tabla de comandos de Cargo (`run`, `build`, `build --release`, `check`).
- **Deuda que abre:** qué pasa si se olvida el `;`. La paga en la lección 04.
- **Consejo:** leer los errores del compilador hasta el final; el `help:` suele
  traer el arreglo.
- **Reto 1:** imprimir `¡Hola, mundo!`.

### 02 · Variables y mutabilidad
- **Secciones:** `let` · Inmutables por defecto · `mut` · Constantes · Shadowing ·
  Ámbito de bloque.
- **Cómo explica:** una variable es una caja con nombre y candado; `mut` quita el
  candado; el shadowing es una caja nueva que tapa a la anterior. Da el porqué de
  la inmutabilidad antes del código: si un valor no cambia, nadie lo modifica a tus
  espaldas.
- **Errores:** *E0384* al reasignar, con el `help:` que sugiere `let mut`. *E0308*
  al cambiar de tipo con `mut`, en contraste con el shadowing que sí lo permite
  (`let espacios = "    "; let espacios = espacios.len();`). *E0425* al usar una
  variable fuera de su bloque.
- **Detalles:** `mut` cambia el valor, no el tipo. Advertencias de `mut`
  innecesario y de variable sin usar (prefijo `_`). Tabla `let` / `let mut` /
  `const`. Diagrama `mut` frente a shadowing.
- **Reto 1:** arreglar `vidas -= 1` sobre una variable inmutable.

### 03 · Tipos de datos
- **Secciones:** Inferencia y anotaciones · Enteros (y desbordamiento) · Decimales ·
  Booleanos · Caracteres · Tuplas · Arrays · Conversiones con `as`.
- **Cómo explica:** tipado estático como «detectar al compilar lo que descubrirías
  en producción». El nombre del tipo es un código: `i`/`u` más los bits. Con *n*
  bits caben 2ⁿ valores; `i8` y `u8` tienen los mismos 256, solo cambia dónde
  empieza el rango. Criterio: `i32` por default, `usize` para posiciones.
- **Desbordamiento por casos:** si el compilador lo ve, no compila (`let x: u8 =
  256`); en debug hace panic (`volumen: u8 = 250; volumen += 10`); en release da la
  vuelta; se pide explícito con `wrapping_add` o `saturating_add`.
- **Errores:** *E0277* al sumar `5 + 2.5`. Panic por índice fuera de rango, con el
  contraste con C.
- **`as`:** Rust nunca convierte números por su cuenta. `total as f64 / partes as
  f64`; `3.99 as i32` da 3; `300 as u8` da 44; `as` no avisa si pierde información.
- **También:** división entera (`7 / 2` es 3), `char` de 4 bytes, tupla con
  desestructuración, `()` como unit, `[0; 5]`, `{:?}`.
- **Reto 1:** cambiar anotaciones de tipo para que quepan los valores.

### 04 · Funciones y expresiones
- **Secciones:** Declarar · Parámetros · Devolver un valor · Sentencias y
  expresiones · El tipo unit · El error clásico: un punto y coma de más · `return`
  para salir antes · Devolver varios valores.
- **Cómo explica:** la función es una máquina: entra `21`, sale `42`. La firma
  exige tipos porque es un contrato que se lee sin abrir el cuerpo. Sentencia
  frente a expresión; un bloque vale su última expresión (`let y = { let x = 3; x +
  1 };`); con `;` vale `()`.
- **Error central:** *E0308* en `fn doble(n: i32) -> i32 { n * 2; }`, con el
  `help: remove this semicolon`. Cierra la deuda de la lección 01.
- **Aclaración:** `return 0;` sí lleva `;`. Devolver varios valores con una tupla
  (`rectangulo` → `(area, perimetro)`).
- **Reto 1:** arreglar `cuadrado` sin usar `return`.

### 05 · Control de flujo
- **Secciones:** `if`, `else if`, `else` · `if` como expresión · `loop` · `while` ·
  `for` (rangos y arrays) · Etiquetas de bucle · ¿Qué bucle elijo?
- **Cómo explica:** la condición debe ser `bool`: no hay *truthy* ni *falsy* como
  en JS o Python (*E0308*, `expected bool, found integer`). `if` como expresión
  hace innecesario el ternario; las dos ramas deben dar el mismo tipo (*E0308*).
  `loop` devuelve valor con `break valor`. Rangos `1..4`, `1..=4`, `(1..=3).rev()`.
  `for` sobre un array es más seguro que `while` con índice. Etiquetas
  `'externo:` con `break 'externo`.
- **Recurso:** la misma cuenta atrás escrita con `while` y con `for`. Tabla final
  de qué bucle elegir.
- **Reto 1:** `estado_bateria` con `if` / `else if` / `else`.

---

## Módulo 2 · Ownership y préstamos

### 06 · Ownership: quién es dueño de cada valor
- **Secciones:** ¿Por qué existe? · Stack y heap · Las tres reglas · Ámbito · El
  tipo `String` · Move · Clone · Tipos `Copy` · Ownership y funciones · Devolver la
  propiedad · Resumen.
- **Cómo explica:** tabla de tres estrategias (recolector, manual, ownership) con
  lo que cobra cada una. El stack como pila de platos. Anatomía de `String`: `ptr`,
  `len` y `cap` en el stack, los bytes en el heap. El move copia solo el stack, y
  `s1` se invalida porque dos dueñas harían una doble liberación.
- **Errores:** *E0382* leído línea por línea; aclara que dice *borrowed* porque
  `println!` toma prestado. *E0382* al llamar dos veces a una función, y el caso
  del bucle (`value moved here, in previous iteration of loop`).
- **Recursos:** `.clone()` como señal visible de que ahí se duplica memoria. Tabla
  final de cuatro filas (`let b = a`, `funcion(a)`, `a.clone()`, fin de ámbito) por
  tipo `Copy` y tipo con heap. Cierra devolviendo `(String, usize)` y lo llama
  «demasiada ceremonia», para dar paso a las referencias.
- **Reto 1:** copia profunda de un `String` sin quitar ningún `println!`.
- **Libro:** capítulo 3.2, ya escrito.

### 07 · Referencias y préstamos
- **Secciones:** Referencias con `&` · Inmutables por defecto · `&mut` · Las reglas
  del préstamo · El borrow checker · Un préstamo acaba en su último uso ·
  Referencias colgantes · Resumen.
- **Cómo explica:** retoma la «ceremonia» de la 06. `calcular_longitud(&s1)`; el
  `&` aparece en la llamada y en la firma. `mut` en tres lugares. `*puntos += 5`.
  Tres mini-diagramas: muchas `&`, una sola `&mut`, las dos a la vez.
- **Errores, en orden:** *E0596*, *E0499*, *E0502*, *E0106* (referencia colgante).
- **Recursos:** NLL con `r1`, `r2` y luego `r3 = &mut s`; muchas veces basta
  reordenar. Tabla `String` / `&String` / `&mut String`. Regla: `&T` por default,
  `&mut T` si modifica, `T` solo si se queda con el valor.
- **Reto 1:** cambiar `contar_letras` para que reciba `&String`.
- **Libro:** capítulo 3.3, ya escrito.

### 08 · Slices y el tipo `&str`
- **Secciones:** El problema: devolver un índice · Slices de `String` ·
  `primera_palabra` con slices · `&str` y `String` · Recibe `&str` en tus funciones
  · Slices de arrays · Cuidado con UTF-8.
- **Cómo explica:** motiva por dolor: devolver un `usize` queda desincronizado tras
  `clear()`; con `&str` es *E0502*. Diagrama del slice como `ptr` + `len` sobre el
  mismo buffer. Tabla de atajos `[..4]`, `[5..]`, `[..]`. Panic al cortar `"ñandú"`
  a media letra. `&[i32]` para arrays.
- **Ejercicios del usuario:** 01, 02, 03.
- **Libro:** capítulo 3.4, ya escrito. Los slices de arreglos quedan para 5.3.

---

## Módulo 3 · Structs, enums y patrones

### 09 · Structs: agrupa tus datos
- **Secciones:** Definir · Crear una instancia · Mutabilidad · Sintaxis abreviada ·
  Crear una instancia a partir de otra · Tuple structs · Unit structs · Imprimir
  con Debug · `dbg!` · Resumen.
- **Cómo explica:** gancho: en una tupla, «¿qué era `.1`?». La definición es un
  molde; la instancia, un valor. La mutabilidad es de la instancia entera. La
  sintaxis `..mario` mueve los campos que toma: con campos `Copy`, `mario` sigue
  usable; si tomara el `String`, no.
- **Errores:** *E0277* al imprimir con `{}`, puente a `#[derive(Debug)]`. Aviso
  `field is never read`.
- **Recursos:** `{:?}` frente a `{:#?}`. `dbg!` devuelve el valor y toma posesión,
  de ahí `dbg!(&rect)`. Tuple structs: `Color` y `Punto` son tipos distintos aunque
  tengan la misma forma.
- **Reto 1:** definir `Libro` e imprimirlo.
- **Libro:** 2.2.

### 10 · Métodos con `impl`
- **Secciones:** Tu primer método · `&self`, `&mut self` y `self` · Funciones
  asociadas · Punto o dos puntos · Métodos que reciben otra instancia · Varios
  bloques `impl`.
- **Cómo explica:** el primer parámetro decide qué hace el método con la instancia;
  tabla de tres filas. `Carta::enviar(self)` llamado dos veces da *E0382*: se
  consume cuando el valor original ya no tiene sentido. `String::from` ya era una
  función asociada. Regla: empezar por `&self`.
- **Ejercicios del usuario:** 04, 05, 06.
- **Libro:** 3.5.

### 11 · Enums y pattern matching
- **Secciones:** Definir · Variantes con datos · `match` (y exhaustividad) ·
  Patrones que extraen datos · Métodos en enums · Más patrones · `if let` · `let …
  else`.
- **Cómo explica:** un struct es «nombre Y email Y edad»; un enum es «una cosa U
  otra». Las tres formas de variante en un solo enum `Mensaje`. Argumento: con
  cuatro structs no se podría recibir «un mensaje cualquiera». Exhaustividad
  (*E0004*) como ayuda de mantenimiento. Diagrama que traza qué rama del `match`
  encaja.
- **Patrones:** `1 | 2 | 3`, `4..=9`, guardas, `_`, `..`; aviso `unreachable
  pattern` por el orden. Resumen de cuándo usar `match`, `if let` y `let … else`.
- **Ejercicios del usuario:** 07, 08, 09, 10.
- **Libro:** 2.3 y 2.4; el 08 va en 3.5 porque usa `impl`.

### 12 · `Option`: adiós a null
- **Secciones:** `Some` y `None` · Un `Option<i32>` no es un `i32` · Funciones que
  devuelven `Option` · `if let Some(x)` · Métodos útiles · `unwrap` y `expect` · El
  operador `?` con `Option`.
- **Cómo explica:** gancho histórico: Tony Hoare y su «error del billón de
  dólares». Comparación `edad: int` (31 o null) frente a `Option<u32>`. `x + y` con
  un `Option` no compila: hay que decidir qué hacer con `None`. Tabla de siete
  métodos con columna `Some` y columna `None`. Muchos `unwrap` indican que se
  esquiva al compilador.
- **Ejercicios del usuario:** 11, 12, 13, 14, 15.
- **Libro:** 5.1.

---

## Módulo 4 · Colecciones y errores

### 13 · Vectores: `Vec<T>`
- **Secciones:** Crear · `push` y `pop` · Índice o `get` · Recorrer · Vectores y
  préstamos · Otros métodos · Funciones que reciben vectores · Mezclar tipos con un
  enum.
- **Cómo explica:** la pieza fuerte es `let primero = &v[0]; v.push(4);`: no
  compila porque `push` puede realojar el buffer y dejar la referencia colgando.
  Diagrama de memoria en dos fases. Regla: `v[i]` si un índice inválido es un bug,
  `get` si es un caso normal. `for x in &v`, `&mut v`, `v`. `&[T]` en parámetros.
  Enum `Celda` para una hoja de cálculo.
- **Ejercicios del usuario:** 16, 17, 18, 19.
- **Libro:** 5.3.

### 14 · Strings en profundidad
- **Secciones:** Repaso `String` y `&str` · Crear · `push_str` y `push` · `+` y
  `format!` · UTF-8: por qué no `s[0]` · `chars` · Métodos más usados · `split` y
  `split_whitespace` · `parse`.
- **Cómo explica:** el texto es complicado, no Rust. `+` toma posesión del operando
  izquierdo. Escala de bytes: sin acento 1, `ñ` 2, `€` 3, emoji 4. Diagrama de
  «año». Tabla de métodos con lo que devuelven: `trim` da `&str`, `to_uppercase` y
  `replace` dan `String`. Turbofish en `parse::<i32>()`.
- **Ejercicios del usuario:** 20, 21, 22, 23.
- **Libro:** 3.4, ya escrito; `split` y `parse` quedan para 5.2 y 5.7.

### 15 · `HashMap`: pares clave-valor
- **Secciones:** Crear e insertar · `get` · Recorrer · `HashMap` y ownership ·
  Actualizar valores (y el contador de palabras) · `BTreeMap`.
- **Cómo explica:** un vector busca por posición; un mapa, por nombre. Invita a
  ejecutar varias veces para ver que el orden cambia. `insert` mueve los `String`.
  La línea `*conteo.entry(palabra).or_insert(0) += 1` leída en dos ramas, clave
  nueva y clave existente. Variante de agrupación con `or_insert(Vec::new())`.
- **Ejercicios del usuario:** 24, 25, 26, 27.
- **Libro:** 5.4.

### 16 · Manejo de errores: `Result` y `?`
- **Secciones:** `panic!` · `Result` · `unwrap` y `expect` · `map_err` · El
  operador `?` · `main` puede devolver `Result` · Tus propios errores · ¿panic o
  `Result`?
- **Cómo explica:** dos categorías que ordenan todo: irrecuperable (un bug,
  `panic!`) y recuperable (`Result`). Primero la versión larga con `match` y
  `return Err(e)`, luego `?` como atajo. Tabla de decisión: bug → `panic!`;
  prototipos → `expect`; error esperable → `match`; default razonable →
  `unwrap_or`; no sé gestionarlo aquí → `?`. Enum `ErrorRetirada` con `Display`.
- **Ejercicios del usuario:** 28, 29, 30, 31, 32.
- **Libro:** 5.2; los errores propios, en 7.4.

---

## Módulo 5 · Genéricos, traits y módulos

### 17 · Tipos genéricos
- **Secciones:** El problema: código duplicado · Funciones genéricas · Structs
  genéricos · Enums genéricos · Métodos en tipos genéricos · Monomorfización ·
  Resumen.
- **Cómo explica:** `mayor_i32` y `mayor_char` lado a lado. Primero `mayor<T>` sin
  bound, que falla (`binary operation > cannot be applied to type &T`), luego `T:
  PartialOrd`. `Punto<T>` con `5` y `4.0` no compila, y de ahí `Punto<T, U>`.
  `impl<T> Punto<T>` frente a `impl Punto<f64>`. Monomorfización: como haber escrito
  a mano cada versión; el precio se paga al compilar.
- **Ejercicios del usuario:** 33, 34, 35.
- **Libro:** 4.2.

### 18 · Traits: comportamiento compartido
- **Secciones:** Definir · Implementar · Métodos por defecto · Traits como
  parámetros (`+` y `where`) · Devolver `impl Trait` · `Display` · `derive` · Trait
  objects.
- **Cómo explica:** el trait es un contrato; se parece a las interfaces de Java,
  TypeScript o Go. `Noticia` y `Post` resumen cada uno a su manera. Un método por
  defecto puede llamar a otro sin cuerpo. Regla de coherencia con ejemplo. `&impl
  Resumen` frente a `<T: Resumen>` con dos parámetros del mismo tipo. `Vec<Box<dyn
  Forma>>`. Regla: genéricos por default, `dyn` para mezclar tipos.
- **Ejercicios del usuario:** 36, 37, 38, 39.
- **Libro:** 4.1, 4.4 y 6.3.

### 19 · Lifetimes
- **Secciones:** Referencias colgantes · El borrow checker compara ámbitos ·
  Lifetimes en funciones (qué significa realmente `'a`) · Reglas de elisión ·
  Structs que guardan referencias · El lifetime `'static`.
- **Cómo explica:** empieza por el síntoma: `r = &x` con `x` en un bloque interior
  (`x does not live long enough`), con barras de ámbito `'a` y `'b`. Una anotación
  no alarga la vida de nada: describe una relación. Caso que no compila aunque «a
  simple vista» el resultado sea `cadena1`. Anotar solo lo necesario. Las tres
  reglas de elisión con tabla «escribes / el compilador entiende». Cuando el
  compilador sugiere `'static`, casi nunca es la solución.
- **Ejercicios del usuario:** 40, 41, 42.
- **Libro:** 3.6.

### 20 · Módulos, crates y Cargo
- **Secciones:** Paquetes y crates · `Cargo.toml` y dependencias · `mod` ·
  Privacidad (y `pub` en structs y enums) · Rutas · `use` · Módulos en ficheros ·
  Re-exportar con `pub use`.
- **Cómo explica:** cuatro piezas de mayor a menor: paquete, crate, módulo, ruta.
  Privado por default, para poder cambiar lo interno sin romper a quien lo usa.
  `Usuario` con campo privado y constructor: el invariante `edad.min(150)`. En un
  enum `pub`, todas las variantes lo son. `mod` no es un `import`. `pub use` para
  una API sencilla sobre módulos internos.
- **Ejercicios del usuario:** 61, 62, 63.
- **Libro:** 7.1 y 7.2.

---

## Módulo 6 · Rust funcional

### 21 · Closures
- **Secciones:** Tu primera closure · Capturar el entorno · `move` · `Fn`, `FnMut`
  y `FnOnce` · Recibir closures · Devolver closures · Closures en la biblioteca
  estándar.
- **Cómo explica:** escalera de cuatro formas, de `fn` a `|x| x + 1`. Los tipos se
  fijan en el primer uso. Captura por la forma menos invasiva. Los tres traits como
  muñecas rusas. Fábrica `multiplicador(factor)` con `move`. `sort_by_key`, y
  `unwrap_or_else` frente a `unwrap_or` (perezoso frente a inmediato).
- **Ejercicios del usuario:** 43, 44, 45, 46.
- **Libro:** 4.3.

### 22 · Iteradores
- **Secciones:** El trait `Iterator` · `iter`, `iter_mut` e `into_iter` · Perezosos
  · Adaptadores · Consumidores (y `collect`) · Encadenar todo · Tu propio iterador.
- **Cómo explica:** «ya los has usado»: cada `for` usa uno. `next` a mano hasta
  `None`. La pereza hecha visible con un `println!` dentro de `map`. Tabla de siete
  adaptadores. `fold` convierte dígitos en 1984. La tienda: cadena de iteradores
  junto al `for` equivalente. Coste cero. `Contador` propio.
- **Ejercicios del usuario:** 47, 48, 49, 50, 51.
- **Libro:** 5.6 y 5.7.

### 23 · Smart pointers: `Box`, `Rc` y `RefCell`
- **Secciones:** `Box` (tipos recursivos, trait objects) · `Deref` y `Drop` · `Rc`
  · `RefCell` · `Rc` y `RefCell` juntos.
- **Cómo explica:** «ya conoces dos»: `String` y `Vec`. Admite que `Box<i32>` no
  tiene sentido y da los tres usos reales. `enum Lista` primero sin `Box`
  (`recursive type has infinite size`). `Drop` con mensajes para ver el orden.
  `Rc::strong_count` antes y después de clonar. `RefCell already borrowed` como
  panic. Saldo compartido con `Rc<RefCell<i32>>`. Tabla final de dueños, mutación y
  cuándo se comprueba. Ciclos y `Weak`.
- **Ejercicios del usuario:** 52, 53, 54.
- **Libro:** 6.1 y 6.2.

---

## Módulo 7 · Concurrencia y ecosistema

### 24 · Concurrencia sin miedo
- **Secciones:** `thread::spawn` · `join` · Closures `move` en hilos · Canales ·
  `Arc` y `Mutex` · ¿Por qué no `Rc`? `Send` y `Sync` · `thread::scope`.
- **Cómo explica:** las mismas reglas de ownership impiden las carreras de datos.
  Código que falla antes de la solución (`closure may outlive the current
  function`). `mpsc` con varios productores y el aviso del `drop(tx)` olvidado.
  `Mutex` primero sin hilos. Tabla `Rc` → `Arc`, `RefCell` → `Mutex`.
- **Ejercicios del usuario:** 55, 56, 57.
- **Libro:** sección 8. Los canales están diferidos en el deck.

### 25 · Tests en Rust
- **Secciones:** Tu primer test · `cargo test` · Macros de aserción · Tests que
  esperan un panic · Tests que devuelven `Result` · Ignorar tests lentos · Tests de
  integración · Doc tests.
- **Cómo explica:** el compilador no sabe si el código hace lo que debe. Muestra la
  salida literal de `cargo test` al pasar y al fallar (`left` / `right`). Se pueden
  probar funciones privadas. Tabla de filtros (`cargo test nombre`, `--
  --nocapture`, `-- --ignored`). Pirámide de unitarios, integración y doc tests.
- **Ejercicios del usuario:** 58, 59, 60.
- **Libro:** 7.3.

### 26 · El ecosistema de Rust (solo lectura)
- **Secciones:** crates.io · Crates imprescindibles · Las herramientas de Cargo ·
  async/await y Tokio · Dónde se usa Rust · `unsafe` · Versiones y ediciones ·
  Recursos.
- **Cómo explica:** criterios para elegir un crate. Tabla de crates (`serde`,
  `tokio`, `reqwest`, `clap`, `anyhow`/`thiserror`, `rayon`, `axum`). Aviso real de
  Clippy (`len() == 0` → `is_empty()`). `unsafe` no desactiva el borrow checker;
  comentario `// SAFETY:`. Versiones cada seis semanas y ediciones cada tres años.
- **Libro:** 7.2, y lo de async en la sección 9, donde el deck ya es más profundo.
