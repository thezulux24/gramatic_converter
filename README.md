# 🔤 Conversor de Gramáticas 📘➡️🧠

Convierte cualquier gramática libre de contexto en **gramática bien formada**, **forma normal de Chomsky** y **forma normal de Greibach**, de manera visual, rápida y completamente interactiva gracias a **Streamlit**.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gramatica-conversor.streamlit.app/) 

---

## 🌟 Características Principales

* ✅ **Conversión Automática:**

  * Elimina epsilon-producciones `ε`, producciones unitarias `A → B` y símbolos inútiles.
* 🧮 **Forma Normal de Chomsky (CNF):**

  * Transforma producciones a la forma `A → BC` o `A → a`.
* 📗 **Forma Normal de Greibach (GNF):**

  * (En desarrollo) Convertirá a la forma `A → aα` para algoritmos de análisis más eficientes.
* 💡 **Visualización Clara:**

  * Cada etapa se despliega en un acordeón para seguir paso a paso la transformación.
* 💾 **Descarga de Resultados:**

  * Guarda la gramática bien formada, CNF y GNF como archivos `.txt`.
* 🎨 **Interfaz Moderna:**

  * Diseño limpio con instrucciones detalladas en la barra lateral.

---

## 🚀 Cómo Empezar

Sigue estos pasos para ejecutar la app en tu entorno local:

### 1. Prerrequisitos

* Python 3.8 o superior
* Git

### 2. Clonar el Repositorio

```bash
git clone https://github.com/thezulux24/gramatica-conversor.git
cd gramatica-conversor
```

### 3. Crear un Entorno Virtual (Recomendado)

```bash
python -m venv venv
# En Windows
venv\Scripts\activate
# En macOS/Linux
source venv/bin/activate
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecutar la Aplicación

```bash
streamlit run app.py
```

Abre tu navegador en `http://localhost:8501` (o la URL que indique Streamlit).

---

## 📝 Formato de Entrada

* Usa `->` para definir producciones.
* Separa alternativas con `|`.
* Usa `*` para representar `ε` (producción vacía).

**Ejemplo:**

```text
S -> bA | aB
A -> bAA | aS | a
B -> aBB | bS | b
```

---

## 📌 Estado Actual

* ✅ Gramática Bien Formada
* ✅ Forma Normal de Chomsky
* 🔧 Forma Normal de Greibach (en desarrollo)

---

## 🧠 ¿Para qué sirve?

Ideal para estudiantes y docentes de **Teoría de Lenguajes** y **Compiladores**, esta herramienta facilita preparar gramáticas para algoritmos de análisis sintáctico y validación de formalismos.

---

## 📬 Contribuciones

¡Las contribuciones son bienvenidas!

1. Haz un fork del proyecto.
2. Crea tu branch: `git checkout -b feature/tu-feature`.
3. Haz commit de los cambios: `git commit -m "Añade descripción de tu feature"`.
4. Envía tu branch: `git push origin feature/tu-feature`.
5. Abre un Pull Request.

---

## 👨‍💻 Autor

**Brayan Zuluaga**
💼 [Looplink](https://looplink.co) — Desarrollo web y consultoría.
