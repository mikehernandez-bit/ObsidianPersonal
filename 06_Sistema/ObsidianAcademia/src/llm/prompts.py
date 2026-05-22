"""
ObsidianAcademia - Prompts para LLM
Prompts optimizados en español para Gemma 4 E4B.
Cada función recibe contexto y retorna el prompt formateado.
"""

# ============================================================
# PROMPT DE SISTEMA (compartido)
# ============================================================

SYSTEM_PROMPT = """Eres un asistente académico universitario experto. \
Tu rol es ayudar a estudiantes a comprender, organizar y estudiar contenido de clases universitarias. \
Responde siempre en español. Usa formato Markdown. Sé claro, estructurado y académico pero accesible."""


# ============================================================
# PROMPTS DE GENERACIÓN
# ============================================================

def prompt_resumen(contenido: str, curso: str = "", semana: str = "", tipo: str = "") -> str:
    """Genera el prompt para crear un resumen de sesión."""
    contexto = ""
    if curso:
        contexto += f"- **Curso:** {curso}\n"
    if semana:
        contexto += f"- **Semana:** {semana}\n"
    if tipo:
        contexto += f"- **Tipo de sesión:** {tipo}\n"

    return f"""Genera un resumen estructurado del siguiente contenido de clase universitaria.

{f"CONTEXTO:{chr(10)}{contexto}" if contexto else ""}
CONTENIDO:
{contenido}

INSTRUCCIONES:
1. Resume los conceptos principales en 3-5 párrafos organizados.
2. Usa encabezados Markdown (##) para cada sección temática.
3. Destaca términos clave en **negrita**.
4. Mantén un tono académico pero accesible.
5. Si hay fórmulas, procedimientos o definiciones, inclúyelos con claridad.
6. Al final, incluye una lista de los 3-5 conceptos más importantes.
7. NO incluyas frontmatter YAML. Solo el contenido del resumen."""


def prompt_cuestionario(
    contenido: str,
    num_preguntas: int = 8,
    curso: str = "",
) -> str:
    """Genera el prompt para crear un cuestionario de estudio."""
    return f"""Genera un cuestionario de estudio basado en el siguiente contenido académico{f" del curso {curso}" if curso else ""}.

CONTENIDO:
{contenido}

INSTRUCCIONES:
1. Genera exactamente {num_preguntas} preguntas variadas:
   - 3 de opción múltiple (con 4 opciones a-d, indica la correcta)
   - 2 de verdadero/falso (con justificación breve)
   - 2 de respuesta corta
   - 1 de desarrollo/análisis
2. Usa formato Markdown con numeración.
3. Las preguntas deben evaluar COMPRENSIÓN, no solo memorización.
4. Incluye preguntas de diferentes niveles de dificultad.
5. Coloca las respuestas en una sección separada al final titulada "## Respuestas".
6. NO incluyas frontmatter YAML."""


def prompt_descripcion_imagen(
    curso: str = "",
    tema: str = "",
    archivo: str = "",
) -> str:
    """Genera el prompt para describir una imagen academica con vision."""
    contexto = []
    if curso:
        contexto.append(f"- Curso: {curso}")
    if tema:
        contexto.append(f"- Tema o leccion: {tema}")
    if archivo:
        contexto.append(f"- Archivo: {archivo}")

    contexto_texto = "\n".join(contexto)

    return f"""Analiza esta imagen como material academico de estudio.

{f"CONTEXTO:{chr(10)}{contexto_texto}" if contexto_texto else ""}

INSTRUCCIONES:
1. Describe con precision lo que aparece visualmente.
2. Extrae y reescribe el texto visible importante, si lo hay.
3. Identifica diagramas, tablas, formulas, graficos, capturas o pizarras.
4. Explica que concepto o idea parece enseñar la imagen.
5. Senala detalles utiles para estudiar o entender mejor el tema.
6. Si la imagen no contiene informacion academica clara, dilo explicitamente.
7. Responde en espanol y en Markdown.
8. No incluyas frontmatter YAML."""


def prompt_informe(
    contenido: str,
    curso: str = "",
    semana: str = "",
    tipo: str = "",
    fecha: str = "",
) -> str:
    """Genera el prompt para crear un informe de sesión."""
    return f"""Genera un informe académico estructurado de la siguiente sesión de clase.

DATOS DE LA SESIÓN:
- Curso: {curso or "No especificado"}
- Semana: {semana or "No especificada"}
- Tipo: {tipo or "No especificado"}
- Fecha: {fecha or "No especificada"}

CONTENIDO DE LA SESIÓN:
{contenido}

INSTRUCCIONES:
Genera el informe con las siguientes secciones:

## Datos de la sesión
(Tabla con los datos proporcionados)

## Temas tratados
(Lista de temas principales abordados)

## Desarrollo de contenido
(Explicación de los temas desarrollados, 3-5 párrafos)

## Conceptos clave
(Lista con definiciones breves)

## Ejemplos y ejercicios
(Si los hay en el contenido, listarlos)

## Observaciones
(Notas relevantes, conexiones con temas previos)

NO incluyas frontmatter YAML."""


def prompt_puntos_clave(contenido: str, curso: str = "") -> str:
    """Genera el prompt para extraer puntos clave."""
    return f"""Extrae los puntos clave del siguiente contenido académico{f" del curso {curso}" if curso else ""}.

CONTENIDO:
{contenido}

INSTRUCCIONES:
1. Identifica los 5-10 puntos clave más importantes.
2. Para cada punto:
   - Escribe un título breve en **negrita**
   - Una explicación concisa de 1-2 oraciones
   - Si aplica, por qué es importante
3. Organízalos por orden de importancia o secuencia lógica.
4. Usa formato de lista Markdown.
5. Al final, incluye una sección "## Conexiones" que relacione los puntos entre sí.
6. NO incluyas frontmatter YAML."""


def prompt_guion_audio(contenido: str, curso: str = "", tema: str = "") -> str:
    """Genera el prompt para crear un guion de audio explicativo."""
    return f"""Genera un guion para un audio explicativo basado en el siguiente contenido académico.
{f"Curso: {curso}" if curso else ""}
{f"Tema: {tema}" if tema else ""}

CONTENIDO:
{contenido}

INSTRUCCIONES:
1. El guion es para ser leído en voz alta por un sintetizador de voz.
2. Escríbelo como un texto fluido y natural, como si estuvieras explicando a un compañero.
3. Duración objetivo: 3-5 minutos de audio (aprox. 500-800 palabras).
4. Estructura:
   - Breve introducción del tema
   - Desarrollo de los conceptos principales
   - Ejemplos o analogías cuando sea útil
   - Resumen final de lo más importante
5. NO uses bullets, tablas ni formato Markdown complejo (solo texto plano con párrafos).
6. NO uses abreviaturas ni símbolos — escribe todo en palabras.
7. Usa oraciones claras y pausadas.
8. NO incluyas frontmatter YAML ni encabezados.
9. NO incluyas indicaciones como "pausar aquí" ni marcas de escena."""


def prompt_dudas_pendientes(contenido: str) -> str:
    """Genera el prompt para identificar dudas y preguntas pendientes."""
    return f"""Analiza el siguiente contenido de clase universitaria e identifica posibles dudas, \
preguntas pendientes y aspectos que necesitan aclaración.

CONTENIDO:
{contenido}

INSTRUCCIONES:
1. Lista 3-5 preguntas que un estudiante podría tener después de esta sesión.
2. Identifica conceptos que parecen incompletos o requieren profundización.
3. Señala cualquier ambigüedad en el contenido.
4. Sugiere temas relacionados que sería útil investigar.
5. Formato: lista numerada en Markdown.
6. NO incluyas frontmatter YAML."""


def prompt_proximas_acciones(contenido: str, curso: str = "") -> str:
    """Genera el prompt para definir próximas acciones de estudio."""
    return f"""Basándote en el siguiente contenido de clase{f" del curso {curso}" if curso else ""}, \
genera una lista de próximas acciones y tareas de estudio.

CONTENIDO:
{contenido}

INSTRUCCIONES:
1. Define 3-7 acciones concretas que el estudiante debería tomar.
2. Prioriza las acciones por urgencia e importancia.
3. Incluye:
   - Tareas de repaso específicas
   - Material complementario a buscar
   - Ejercicios sugeridos
   - Preparación para la siguiente sesión
4. Usa formato de checklist Markdown: - [ ] tarea
5. Sé específico y actionable (no genérico).
6. NO incluyas frontmatter YAML."""
