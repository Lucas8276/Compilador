# Parce-Chamigo Compilador

**Parce-Chamigo** es un compilador educativo que transforma código fuente escrito con palabras clave inspiradas en el español latinoamericano a una máquina de pila simulada. Es ideal para aprender los conceptos fundamentales de compilación y para divertirse creando programas con sabor local.

---

## **¿Qué puedes hacer con Parce-Chamigo?**

- **Definir variables** con la palabra clave `Parce`.
  - Ejemplo: `Parce x = 5`

- **Imprimir valores y mensajes** con `Pilas`.
  - Ejemplo: `Pilas("El resultado es", x)`

- **Leer valores desde teclado** con `Guita`.
  - Ejemplo: `Parce nombre = Guita("¿Cómo te llamás?")`

- **Crear estructuras condicionales** usando:
  - `Pues` para **if**
  - `Orale pues` para **elif**
  - `Orale` para **else**

    > **Importante:**  
    > Por el diseño actual de la gramática, **los condicionales deben usarse siempre como grupo**  
    > (al menos un bloque `Pues` y un bloque `Orale`).  
    > No es posible usar un solo `Pues` o un solo `Orale` de forma aislada.

  - Ejemplo:
    ```plaintext
    Pues (x > 10) {
        Pilas("Mayor a 10")
    } Orale {
        Pilas("Menor o igual a 10")
    }
    ```

- **Usar valores booleanos** de forma nativa:
  - `Posta` representa `True`
  - `Niahi` representa `False`

    Ejemplo:
    ```plaintext
    Parce ok = Posta
    Parce fail = Niahi
    ```

---

## **Palabras clave disponibles**

| Palabra      | Significado        |
|--------------|-------------------|
| Parce        | Declarar variable |
| Pilas        | Imprimir          |
| Guita        | Leer variable     |
| Pues         | if                |
| Orale pues   | elif              |
| Orale        | else              |
| Posta        | True              |
| Niahi        | False             |

---

## **Ejemplo de programa**

```plaintext
Parce nombre = Guita("¿Cómo te llamás?")
Pilas("Hola", nombre)

Parce numero = Guita("Decime un número:")
Pues (numero > 0) {
    Pilas("Número positivo")
} Orale {
    Pilas("Número cero o negativo")
}

Parce ok = Posta
Parce fail = Niahi
Pilas("ok:", ok, "fail:", fail)
