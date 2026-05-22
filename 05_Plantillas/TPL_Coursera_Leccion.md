<%*
const basePath = "02_Coursera";
const leccionNombre = tp.file.title.trim();
const pages = app.metadataCache.getCachedFiles();

async function ensureFolder(path) {
    const parts = path.split("/").filter(Boolean);
    let current = "";

    for (const part of parts) {
        current = current ? `${current}/${part}` : part;
        if (!app.vault.getAbstractFileByPath(current)) {
            await app.vault.createFolder(current);
        }
    }
}

const fileCaches = pages
    .map((path) => {
        const file = app.vault.getAbstractFileByPath(path);
        return file ? app.metadataCache.getFileCache(file) : null;
    })
    .filter((cache) => cache && cache.frontmatter);

const cursos = fileCaches
    .filter(
        (cache) =>
            cache.frontmatter.plataforma === "coursera" &&
            (
                cache.frontmatter.tipo === "curso" ||
                cache.frontmatter.tipo === "curso_coursera"
            ),
    )
    .map((cache) => ({
        curso: cache.frontmatter.curso_nombre || cache.frontmatter.curso || "",
        programa: cache.frontmatter.programa || "",
    }))
    .filter((item) => item.curso)
    .filter(
        (item, index, array) =>
            index === array.findIndex(
                (other) =>
                    other.curso === item.curso &&
                    other.programa === item.programa,
            ),
    )
    .sort((a, b) => {
        const left = `${a.programa}/${a.curso}`;
        const right = `${b.programa}/${b.curso}`;
        return left.localeCompare(right, "es");
    });

let cursoNombre = "";
let programa = "";

if (cursos.length > 0) {
    const etiquetasCurso = cursos.map((item) =>
        item.programa ? `${item.programa} / ${item.curso}` : item.curso,
    );
    const seleccion = await tp.system.suggester(etiquetasCurso, etiquetasCurso);

    if (seleccion) {
        const cursoSeleccionado = cursos[etiquetasCurso.indexOf(seleccion)];
        cursoNombre = cursoSeleccionado.curso;
        programa = cursoSeleccionado.programa;
    }
}

if (!cursoNombre) {
    cursoNombre = await tp.system.prompt("Nombre del curso en Coursera");
    programa = await tp.system.prompt(
        "Nombre del programa (vacio si es curso individual)",
        "",
    );
}

const modulos = fileCaches
    .filter(
        (cache) =>
            cache.frontmatter.tipo === "modulo_coursera" &&
            (cache.frontmatter.curso || "") === cursoNombre &&
            (cache.frontmatter.programa || "") === programa,
    )
    .map((cache) => cache.frontmatter.modulo || "")
    .filter(Boolean)
    .filter((item, index, array) => array.indexOf(item) === index)
    .sort((a, b) => a.localeCompare(b, "es"));

let moduloNombre = "";
if (modulos.length > 0) {
    moduloNombre = await tp.system.suggester(modulos, modulos);
}

if (!moduloNombre) {
    moduloNombre = await tp.system.prompt("Nombre del modulo");
}

const targetFolder = [basePath, programa, cursoNombre, moduloNombre, leccionNombre]
    .filter(Boolean)
    .join("/");
await ensureFolder(targetFolder);
await tp.file.move(`${targetFolder}/${leccionNombre}`);

const programaRow = programa ? `| **Programa** | ${programa} |` : null;

const lines = [
    "---",
    "tipo: leccion_coursera",
    "plataforma: coursera",
    `programa: "${programa}"`,
    `curso: "${cursoNombre}"`,
    `modulo: "${moduloNombre}"`,
    `leccion: "${leccionNombre}"`,
    `ruta_leccion: "${targetFolder}"`,
    `fecha: ${tp.date.now("YYYY-MM-DD")}`,
    "estado: en_curso",
    "transcript_status: pendiente",
    "summary_status: pendiente",
    "quiz_status: pendiente",
    "audio_status: pendiente",
    "report_status: pendiente",
    "tags:",
    "  - coursera",
    "  - leccion",
    "---",
    "",
    `# ${leccionNombre}`,
    "",
    "| | |",
    "|---|---|",
    "| **Plataforma** | Coursera |",
    programaRow,
    `| **Curso** | ${cursoNombre} |`,
    `| **Modulo** | ${moduloNombre} |`,
    `| **Fecha** | ${tp.date.now("YYYY-MM-DD")} |`,
    "| **Duracion** | min |",
    "",
    "---",
    "",
    "## Panel de IA",
    "",
    "> [!tip] Acciones de la leccion",
    "> Estos botones trabajan sobre la carpeta actual de esta leccion.",
    "> `Procesar leccion completa` toma audio, video, PDF y notas del mismo directorio.",
    "",
    "```button",
    "name 🤖 Procesar leccion completa",
    "type command",
    "action Procesar Leccion Coursera",
    "color blue",
    "```",
    "",
    "```button",
    "name 📄 Generar informe",
    "type command",
    "action Generar Informe Leccion Coursera",
    "color yellow",
    "```",
    "",
    "```button",
    "name 🔊 Generar audio",
    "type command",
    "action Generar Audio Leccion Coursera",
    "color green",
    "```",
    "",
    "```button",
    "name ❓ Generar cuestionario",
    "type command",
    "action Generar Cuestionario Leccion Coursera",
    "color red",
    "```",
    "",
    "---",
    "",
    "## Materiales de la leccion",
    "",
    "> Esta carpeta de leccion es el contenedor de PDF, audio, video e imagenes.",
    "> Deja aqui el material y luego usa los botones del panel de IA.",
    "",
    "### PDF",
    "",
    "- Sin PDF",
    "",
    "### Audio",
    "",
    "- Sin audio",
    "",
    "### Video",
    "",
    "- Sin video",
    "",
    "### Imagenes",
    "",
    "- Sin imagenes",
    "",
    "### Notas auxiliares",
    "",
    "- Sin notas auxiliares",
    "",
    "---",
    "",
    "## Notas de la leccion",
    "",
    "### Punto 1",
    "",
    "",
    "",
    "### Punto 2",
    "",
    "",
    "",
    "### Punto 3",
    "",
    "",
    "",
    "---",
    "",
    "## Conceptos clave",
    "",
    "| Concepto | Descripcion |",
    "|---|---|",
    "| | |",
    "| | |",
    "| | |",
    "",
    "---",
    "",
    "## Ideas importantes",
    "",
    "1. ",
    "2. ",
    "3. ",
    "",
    "---",
    "",
    "## Transcripciones",
    "",
    "### Fuentes detectadas",
    "",
    "- Audio: Sin audio fuente",
    "- Video: Sin video fuente",
    "",
    "### Transcript consolidado",
    "",
    "> No hay transcript generado todavia.",
    "",
    "---",
    "",
    "## Informe maestro",
    "",
    "> Este informe debe consolidar notas, transcripciones, imagenes y aclaraciones.",
    ">",
    "> Estado: pendiente.",
    "",
    "---",
    "",
    "## Productos generados",
    "",
    "> [!info] Estado actual",
    "> - Transcript: pendiente",
    "> - Resumen: pendiente",
    "> - Informe: pendiente",
    "> - Cuestionario: pendiente",
    "> - Audio: pendiente",
    "",
    "### Archivos disponibles",
    "",
    "- Transcripcion: pendiente",
    "- Resumen: pendiente",
    "- Informe: pendiente",
    "- Cuestionario: pendiente",
    "- Guion de audio: pendiente",
    "- Audio explicativo: pendiente",
    "",
    "---",
    "",
    "## Quiz de Coursera",
    "",
    "> El cuestionario se mostrara aqui cuando exista `cuestionario.md`.",
    "",
    "---",
    "",
    "## Links y recursos mencionados",
    "",
    "- ",
    "- ",
    "",
    "---",
    "",
    "## Dudas",
    "",
    "1. ",
    "2. ",
    "",
    "---",
    "",
    "## Reflexion",
    "",
    "> Que es lo mas valioso que aprendi en esta leccion?",
    "> ",
];

tR += lines.filter((line) => line !== null).join("\n");
-%>
