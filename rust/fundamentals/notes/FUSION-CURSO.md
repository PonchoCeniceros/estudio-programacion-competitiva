# Fusión con el curso «Aprende Rust» (aprenderust.dev, midudev)

Documento de trabajo. Cruza tres fuentes:

- **Curso**: las 26 lecciones de aprenderust.dev, leídas por resumen (no texto literal).
- **Ejercicios**: los 63 archivos de `~/Desktop/buffer/curso-rust-midudev/examples/`.
- **Cuaderno**: las páginas de `pages/` que incluye `slides.md`.

Límites de esta lectura:

- De cada lección solo se vio el enunciado del reto 1; los demás retos se conocen por
  los archivos de `examples/`.
- Los diagramas del curso se conocen por sus etiquetas de texto, no por la imagen.
- `examples/` empieza en la lección 8 (slices). No hay ejercicios guardados del
  módulo 1 ni de ownership y referencias, así que 1.x, 3.1, 3.2 y 3.3 no reciben
  ejemplos de aplicación: ahí el aporte del curso es solo de explicación.

Los enunciados y explicaciones son de midudev. Las explicaciones se reescriben con la
voz de `GUIA-DE-TONO.md`; los enunciados se resumen y el deck acredita el curso.

---

## A · Qué explicación del curso aporta algo a cada página

Solo aparecen las páginas donde el curso tiene algo que el cuaderno no. Prioridad:
**A** hueco real de contenido, **M** mejora de aterrizaje, **B** detalle.

### Sección 1 · Fundamentos

| Página | Lo que falta en el cuaderno y el curso sí tiene | Pri. |
| :--- | :--- | :---: |
| 1.2 Tipos escalares | Conversión con `as` y su pérdida silenciosa (`300 as u8` = 44, `3.99 as i32` = 3). No aparece en ninguna página. | A |
| 1.2 Tipos escalares | Rust no mezcla tipos numéricos: `5 + 2.5` es *E0277*. División entera frente a flotante (`7 / 2` = 3). | A |
| 1.2 Tipos escalares | Cómo se lee el nombre del tipo (`i`/`u` + bits), 2ⁿ valores, y `i8` frente a `u8`: mismos 256 valores, distinto inicio. Criterio de elección: `i32` por default, `usize` para posiciones. | M |
| 1.3 Variables | El `help:` del compilador que sugiere `let mut`. Advertencias de `mut` innecesario y de variable sin usar (prefijo `_`). | B |
| 1.5 Funciones | Por qué la firma exige tipos y el cuerpo no: la firma es el contrato que se lee sin abrir la función. | B |
| 1.6 Control de flujo | La página es solo plantillas, sin un ejemplo real. Faltan: rangos (`1..4`, `1..=4`, `.rev()`), `continue`, etiquetas de bucle (`'externo:` con `break 'externo`), la condición que debe ser `bool` (*E0308*, no hay *truthy*), y la tabla «qué bucle usar». | A |

### Sección 2 · Tipos compuestos

| Página | Lo que falta en el cuaderno y el curso sí tiene | Pri. |
| :--- | :--- | :---: |
| 2.1 Tuplas y arreglos | `[0; 5]`, `.len()`, impresión con `{:?}`. | B |
| 2.2 Structs | Sintaxis abreviada de campos, actualización `..otra` (y qué campos mueve), tuple structs, y que la mutabilidad es de la instancia entera. Hoy `..` aparece hasta 4.4 y las tuple structs se usan en 4.4, 4.5 y 6.3 sin haberse presentado. | A |
| 2.2 Structs | `#[derive(Debug)]`, `{:#?}` y `dbg!` como primer contacto (el *E0277* de imprimir un struct con `{}`). `dbg!` no aparece en el cuaderno. | M |
| 2.3 Enums | Las tres formas de variante en un mismo enum (sin datos, tupla, campos con nombre). Faltan las variantes con campos con nombre. Argumento de diseño: un enum y no cuatro structs, para poder recibir «un mensaje cualquiera». | M |
| 2.3 Enums | La exhaustividad como herramienta de mantenimiento: al agregar una variante, el compilador señala cada `match` (*E0004*). | M |

### Sección 3 · Memoria

| Página | Lo que falta en el cuaderno y el curso sí tiene | Pri. |
| :--- | :--- | :---: |
| 3.1 Stack y heap | Anatomía de `String` en el stack (`ptr`, `len`, `cap`). El cuaderno la da para `Vec` en 5.3, no aquí. | M |
| 3.2 Ownership | **`.clone()` no tiene lámina.** El curso lo presenta como copia profunda explícita y señal visible de costo. | A |
| 3.2 Ownership | La causa del move: si `s1` y `s2` fueran dueñas, habría doble liberación. El cuaderno enuncia la regla sin decir qué evita. | A |
| 3.2 Ownership | *E0382* leído línea por línea, y el caso del bucle (*value moved in previous iteration*). El catálogo de errores de 3.7 está retirado, así que hoy la sección no muestra ningún error de move. | M |
| 3.2 Ownership | Tabla resumen: `let b = a` / `f(a)` / `a.clone()` / fin de ámbito, por tipo `Copy` y tipo con heap. | M |
| 3.2 Ownership | Cierre con código: devolver `(String, usize)` para no perder el valor. Hoy «El costo del ownership estricto» es prosa. | M |
| 3.3 Borrowing | Un primer ejemplo de préstamo en función (`longitud(&s)`) antes de las reglas. Hoy se pasa de la definición a las reglas. | A |
| 3.3 Borrowing | NLL con ejemplo: `r1` y `r2` se usan, luego `&mut` compila. Hoy NLL es una viñeta en 3.6. | A |
| 3.3 Borrowing | La regla 2 con ejemplo: función que devuelve `&s` de una local. | A |
| 3.3 Borrowing | Los tres errores en orden: *E0596*, *E0499*, *E0502*. | M |
| 3.3 Borrowing | Criterio de firma: `&T` por default, `&mut T` si modifica, `T` solo si se queda con el valor. | M |
| 3.4 Strings | **Slices de texto (`&s[a..b]`) no aparecen.** Con ellos: el slice como par puntero/longitud sobre el mismo buffer, y el *panic* al cortar a media letra (`"ñandú"`). | A |
| 3.4 Strings | La motivación del slice: devolver un índice (`usize`) queda desincronizado tras `clear()`; devolver `&str` convierte ese bug en *E0502*. Es el mejor aterrizaje de 3.3 que tiene el curso. | A |
| 3.4 Strings | `+` toma posesión del operando izquierdo. Tabla de métodos con lo que devuelven: `trim` da `&str`, `to_uppercase` y `replace` dan `String`. `split` y `split_whitespace`. | M |
| 3.5 impl y métodos | Cuándo se consume `self`: cuando el valor original deja de tener sentido (carta enviada). Tabla «punto o dos puntos». `String::from` ya era una función asociada. | M |
| 3.6 Lifetimes | Entrada por el síntoma: `r = &x` con `x` en un bloque interior (*E0597*). Hoy esa lámina está en el catálogo retirado y la página arranca en abstracto. | A |
| 3.6 Lifetimes | Las tres reglas de elisión y la tabla «escribes / el compilador entiende». Hoy son una frase. | A |
| 3.6 Lifetimes | `'static` en literales, y el aviso: cuando el compilador lo sugiere, casi nunca es la solución. | M |

### Sección 4 · Abstracciones de costo cero

| Página | Lo que falta en el cuaderno y el curso sí tiene | Pri. |
| :--- | :--- | :---: |
| 4.1 Traits | `&impl Trait` frente a `<T: Trait>` con dos parámetros: el genérico obliga a que sean del mismo tipo. | B |
| 4.2 Generics | El error antes del bound (`mayor<T>` sin `PartialOrd`). `Punto<T>` con `5` y `4.0` no compila, y de ahí `Punto<T, U>`. `impl Punto<f64>`: métodos para un tipo concreto. | M |
| 4.3 Closures | La escalera de cuatro formas, de `fn` a `\|x\| x + 1`. Los tipos se fijan en el primer uso. | M |
| 4.3 Closures | **Devolver closures** (función fábrica con `move`). Hoy es una mención en una nota. | A |
| 4.3 Closures | Closures en la stdlib: `sort_by_key`, y `unwrap_or_else` frente a `unwrap_or` (perezoso frente a inmediato). Ninguno aparece en el cuaderno. | M |

### Sección 5 · Vocabulario stdlib

| Página | Lo que falta en el cuaderno y el curso sí tiene | Pri. |
| :--- | :--- | :---: |
| 5.1 Option | `Option<i32>` no es `i32`: `x + y` no compila. `?` sobre `Option`. Tabla de métodos con columna `Some` y columna `None`. | M |
| 5.2 Result | `panic!` frente a `Result`: irrecuperable o recuperable. Tabla de decisión `panic!` / `expect` / `match` / `unwrap_or` / `?`. `expect` como documentación de por qué no debería fallar. | A |
| 5.3 Vec | **`let primero = &v[0]; v.push(4);`** y por qué no compila: `push` puede realojar el buffer y dejar la referencia colgando. Es la regla de 3.3 con una causa física. | A |
| 5.3 Vec | `v[i]` o `get` según la intención: índice inválido como bug o como caso normal. Costo de `insert` y `remove`. | M |
| 5.4 HashMap | Ownership en `insert` (las llaves `String` se mueven). Sobrescribir frente a `entry`. La línea de `entry` leída en sus dos ramas. El orden cambia entre corridas. | M |
| 5.6 Iteradores | La pereza hecha visible: un `println!` dentro de `map` que no imprime hasta el `collect`. La misma tarea con `for` y con cadena, lado a lado. | M |
| 5.7 Iteradores a fondo | `any`, `all`, `find`, `position`. No aparecen. | M |

### Secciones 6 a 9

| Página | Lo que falta en el cuaderno y el curso sí tiene | Pri. |
| :--- | :--- | :---: |
| 6.1 Box | Los tres usos reales de `Box` (tipo recursivo, dato grande, trait object) dichos de entrada. | B |
| 6.2 Rc, RefCell | El contador subiendo y bajando al entrar y salir de un bloque. | B |
| 7.1 Módulos | **Campo privado + constructor = invariante**, y **`pub use`** para re-exportar. Ninguno aparece. `mod` no es un `import`: se declara una vez. En un enum `pub`, todas las variantes lo son. | A |
| 7.3 Tests | La salida literal de `cargo test` al pasar y al fallar (`left` / `right`). Filtros (`cargo test nombre`, `-- --nocapture`, `-- --ignored`), `#[ignore]`, tests que devuelven `Result`. | M |
| 8.1 Hilos | `thread::scope`: hilos que prestan sin `move` ni `Arc`. No aparece. | M |
| 8.x Canales | El curso los trata como fundamento. En el cuaderno están escritos y diferidos (`_8.4-canales.md`). Decisión pendiente, ver D. | — |

Sin aporte del curso: 1.1, 1.4, 2.4, 4.0, 4.4, 4.5, 5.5, 6.3, 6.4, 7.2, 7.4, 7.5, 7.6,
8.0, 8.2, 8.3 y toda la sección 9. En esas páginas el cuaderno ya es más profundo.

---

## B · Dónde va cada ejercicio

Ubicación por el **último concepto que usa**, según el orden del cuaderno. Destino:
**L** lámina de aplicación en la página, **E** a `ejercicios.md`, **—** no se usa
(el cuaderno ya tiene un ejemplo equivalente).

### Propuestos como lámina de aplicación (31 láminas, 32 ejercicios)

| # | Ejercicio | Página | Qué aterriza | Pulir antes |
| ---: | :--- | :--- | :--- | :--- |
| 07 | moneda_valor | 2.3 | `match` exhaustivo sin `_` | — |
| 09 | precio_entrada | 2.4 | rangos y guard con reglas de negocio | `x if x > 64` → `65..` |
| 03 | sin_extension | 3.4 | recibir `&str`, devolver un slice | depende del slice de texto (A) |
| 20 | saludo_ferris | 3.4 | `push_str`, `push`, `format!` | — |
| 22 | contar_vocales | 3.4 | `chars()` y no bytes («Murciélago») | la cadena de `\|\|` → `matches!` |
| 06 | borrador_publicacion | 3.5 | `&mut self`, `self` y `&self` en un solo tipo | `format!` → `push_str` |
| 08 | operacion_enum | 3.5 | métodos sobre un enum, `match self` | — |
| 41 | lifetimes_parciales | 3.6 | anotar solo la entrada de la que sale el retorno | devuelve `Option`, que llega en 5.1 |
| 42 | lifetimes_en_structs | 3.6 | `struct<'a>` con `impl<'a>` y un método | `palabras[0]` truena con texto vacío |
| 37 | animal_metodos_defecto | 4.1 | default que llama a otro método, y sobrescritura | — |
| 35 | punto_intercambiar | 4.2 | dos parámetros de tipo; `Punto<T, U>` → `Punto<U, T>` | `R` → `U` |
| 46 | closures_move | 4.3 | devolver un closure: fábrica de validadores | — |
| 13 | precio_final_option | 5.1 | `unwrap_or` | la resta desborda si el descuento supera al precio: `saturating_sub` (1.2) |
| 14 + 15 | dominio_bytes / dominio_find | 5.1 | antes y después de `?` sobre `Option` | — |
| 23 | sumar_linea | 5.2 | `if let Ok` para ignorar lo que no convierte | sobra el `collect` intermedio |
| 18 | notas_ordenar | 5.3 | `for x in &mut v`, `*x`, `sort` | `+= 1` |
| 19 | saldo_movimientos | 5.3 | un `Vec` de enum y un `match` por elemento | `+=`, `-=` |
| 34 | pila_generica | 5.3 | struct genérico sobre `Vec<T>` que devuelve `Option` | `cima` → `.last()` |
| 25 | inventario_fruteria | 5.4 | sobrescribir, `remove`, imprimir en orden | — |
| 27 | agrupar_por_inicial | 5.4 | agrupar con `entry(...).or_insert(vec![]).push(...)` | `or_default()` |
| 45 | closures_como_parametro | 5.6 | `map` escrito a mano, antes de presentar `map` | — |
| 50 | iteradores_consumidores | 5.7 | `any`, `all`, `position` | — |
| 21 | iniciales | 5.7 | `collect` hacia `String` | el doble `for` con `break` → cadena |
| 31 | sumar_todos | 5.7 | bucle con `?` junto a `collect` en `Result` | — |
| 52 | uso_de_box | 6.1 | la lista como enum recursivo, recorrida con `match` | — |
| 53 | reference_count | 6.2 | dos jugadores, un equipo; el contador baja con `drop` | — |
| 54 | reference_count_mutable | 6.2 | lista de tareas compartida; alias de tipo | — |
| 63 | modulos_3 | 7.1 | campo privado, constructor, `pub use` | — |
| 59 | testing_2 | 7.3 | año bisiesto con casos límite | pasar los `assert!` de `main` a `#[test]` |
| 32 | error_password | 7.4 | enum de error con `Display` y `validar` | `len()` cuenta bytes; el bucle con bandera → `any` |
| 57 | hilos_con_mutex | 8.3 | de `Rc<RefCell>` a `Arc<Mutex>`: la tabla de 8.0 en código | — |

### A `ejercicios.md` (16)

| # | Ejercicio | Sección | Motivo |
| ---: | :--- | :--- | :--- |
| 01 | frase_slices | 3 | la solución fija el índice 16 a mano; sirve como enunciado |
| 02 | maximo_slice | 5 | centinela `i32::MIN + 1`; mejor como ejercicio |
| 04 | cuenta_mut_self | 3 | `retirar` usa `>` y falla al retirar el saldo exacto; 06 cubre lo mismo |
| 05 | temperatura_conversion | 3 | funciones asociadas; el cuaderno ya tiene `Punto::origen` |
| 10 | recoger_monedas | 5 | `if let` sobre un slice de enum |
| 12 | primer_r_match | 5 | `find` + `match` |
| 17 | mayor_option | 5 | variante de 02 con `Option` |
| 26 | contar_palabras | 5 | el cuaderno ya cuenta letras de «banana» |
| 29 | leer_cantidad | 5 | `unwrap_or` sobre `Result` |
| 30 | parsear_edad | 5 | `map_err` |
| 33 | menor_generico | 5 | usa `&[T]` y `Option`: no cabe en 4.2 sin adelantar 5 |
| 36 | saludar_impl_trait | 4 | el cuaderno ya tiene `Descriptible` |
| 44 | closures_mutando | 4 | el cuaderno ya tiene `incrementar` |
| 58 | testing | 7 | las cuatro aserciones |
| 60 | testing_3 | 7 | `should_panic` |
| 62 | modulos_2 | 7 | `super::` con una constante privada |

### No se usan (15)

El cuaderno ya tiene un ejemplo equivalente o idéntico: 11 (`buscar` en 5.1),
16 (5.3), 24 (5.4, mismo dominio), 28 (5.2), 38 (`Display` de `Punto` en 4.4),
39 (`Figura` en 6.3), 40 (`foo` en 3.6), 43 (4.3), 47 y 48 (5.6), 49 (5.7),
51 (Fibonacci, idéntico en 5.7), 55 (8.1), 61 (7.1). El 56 es idéntico a la lámina
de `_8.4-canales.md` y entra solo si se reactiva esa página.

---

## C · Lo que apareció en el cuaderno al leerlo entero

No es parte de la fusión, pero afecta dónde caben los ejemplos.

- **Referencias hacia adelante ya existentes.** 2.4 usa `Option<&str>` en `largo`;
  5.1 usa `&[i32]`, `.iter().enumerate()`, `vec!` y `pop()` antes de 5.3 y 5.6.
  Si se toleran, 41 y 33 caben antes de lo que indica la tabla.
- **Referencias de sección desfasadas.** 2.2 dice que `impl` «llega en 3.4» (es 3.5)
  y tiene dos bloques «Ver también» seguidos. 2.3 remite a «Estructuras de control»
  en vez de 1.6. 5.3 dice «Tipos de Memoria» en vez de 3.1. 6.1 dice «la sección
  Borrowing y lifetimes». El catálogo retirado de 3.7 atribuye *E0597* a 3.5.
- **`foo` en 3.6.** El ejemplo central de lifetimes se llama `foo`. `mas_larga` o
  `mas_corta` (ejercicio 40) dice lo mismo con nombre.
- **Segunda persona.** 2.4 («si sabes construir un valor»), 3.4 («elegir por ti»),
  3.6 («no vas a encontrar», «un atajo tuyo») y 7.6 («vas a ver») rompen la R3 de
  la guía de tono.

---

## D · Decisiones que son tuyas

1. **Formato de la lámina de aplicación.** `ap2-aplicacion.md` ya tiene uno: código a
   la izquierda, tarjeta «Corrida mental» a la derecha, título
   `Aplicación · concepto — problema`. Propuesta: reusarlo al cierre de cada página,
   con el título `Aplicación · concepto — escenario`.
2. **Soluciones pulidas o tal como las escribiste.** La columna «Pulir antes» asume
   pulidas. Alternativa: mostrar tu versión y la idiomática lado a lado en los casos
   donde la diferencia enseña algo (13, 21, 32, 42).
3. **Canales.** Reactivar `_8.4-canales.md` (y con él el ejercicio 56) o dejarlo
   diferido.
4. **Catálogo de errores de 3.7.** Varias filas de prioridad A en la sección 3 piden
   mostrar *E0382*, *E0499*, *E0502* y *E0597* dentro de sus páginas. Eso usa el
   material del catálogo retirado, que estaba reservado para un capítulo futuro.
5. **Tamaño.** Las 17 filas A de la tabla A son unas 20 a 25 láminas nuevas; las de
   aplicación son otras 31. El deck pasaría de ~330 a ~385.

## Piloto propuesto: sección 3

Es donde más pesa la explicación y donde menos ejercicios hay, así que prueba las
dos mitades del trabajo:

- Explicación: `.clone()` y la causa del move en 3.2; primer préstamo, NLL y
  referencia colgante en 3.3; slices de texto en 3.4; entrada por *E0597* y reglas de
  elisión en 3.6.
- Aplicación: 03, 20 y 22 en 3.4; 06 y 08 en 3.5; 41 y 42 en 3.6.
