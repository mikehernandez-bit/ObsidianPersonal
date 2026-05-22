<%*
const basePath = "01_Universidad";
const notaNombre = tp.file.title.trim();
const tituloClase = notaNombre.replace(/^Teo\s*-\s*/i, "").trim() || notaNombre;
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

function escapeValue(value) {
    return String(value || "").replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

function formatCourseLabel(item) {
    return item.ciclo ? `${item.ciclo} / ${item.curso}` : item.curso;
}

const fileCaches = pages
    .map((path) => {
        const file = app.vault.getAbstractFileByPath(path);
        return file ? app.metadataCache.getFileCache(file) : null;
    })
    .filter((cache) => cache && cache.frontmatter);

const cursos = fileCaches
    .filter((cache) => cache.frontmatter.tipo === "curso")
    .map((cache) => ({
        curso: String(cache.frontmatter.curso_nombre || cache.frontmatter.curso || "").trim(),
        ciclo: String(cache.frontmatter.ciclo || "").trim(),
    }))
    .filter((item) => item.curso)
    .filter(
        (item, index, array) =>
            index === array.findIndex(
                (other) => other.curso === item.curso && other.ciclo === item.ciclo,
            ),
    )
    .sort((a, b) => formatCourseLabel(a).localeCompare(formatCourseLabel(b), "es"));

let cursoNombre = "";
let ciclo = "";

if (cursos.length > 0) {
    const etiquetasCurso = cursos.map((item) => formatCourseLabel(item));
    const seleccion = await tp.system.suggester(etiquetasCurso, etiquetasCurso);

    if (seleccion) {
        const cursoSeleccionado = cursos[etiquetasCurso.indexOf(seleccion)];
        cursoNombre = cursoSeleccionado.curso;
        ciclo = cursoSeleccionado.ciclo;
    }
}

if (!cursoNombre) {
    cursoNombre = await tp.system.prompt("Nombre del curso");
}

if (!ciclo) {
    const cycleOptions = Array.from(
        new Set(
            fileCaches
                .filter((cache) => cache.frontmatter.tipo === "curso")
                .map((cache) => String(cache.frontmatter.ciclo || "").trim())
                .filter(Boolean),
        ),
    );

    if (cycleOptions.length > 0) {
        ciclo = await tp.system.suggester(cycleOptions, cycleOptions);
    }
}

if (!ciclo) {
    ciclo = await tp.system.prompt("Ciclo del curso", "IX");
}

const semanas = Array.from(
    new Set(
        fileCaches
            .filter(
                (cache) =>
                    cache.frontmatter.tipo === "semana" &&
                    (cache.frontmatter.curso_nombre || cache.frontmatter.curso) === cursoNombre &&
                    String(cache.frontmatter.ciclo || "").trim() === String(ciclo || "").trim(),
            )
            .map((cache) => String(cache.frontmatter.semana || "").trim())
            .filter(Boolean),
    ),
).sort((a, b) => a.localeCompare(b, "es"));

let semanaNombre = "";
if (semanas.length > 0) {
    semanaNombre = await tp.system.suggester(semanas, semanas);
}

if (!semanaNombre) {
    semanaNombre = await tp.system.prompt("Nombre de la semana");
}

ciclo = String(ciclo || "").trim();

const cursoEsc = escapeValue(cursoNombre);
const cicloEsc = escapeValue(ciclo);
const semanaEsc = escapeValue(semanaNombre);
const tituloEsc = escapeValue(tituloClase);
const targetFolder = `${basePath}/${ciclo}/${cursoNombre}/${semanaNombre}`;

await ensureFolder(targetFolder);
await tp.file.move(`${targetFolder}/${notaNombre}`);

const lines = [
    "---",
    'tipo: "sesion"',
    `curso: "${cursoEsc}"`,
    `curso_nombre: "${cursoEsc}"`,
    `ciclo: "${cicloEsc}"`,
    `semana: "${semanaEsc}"`,
    'sesion: "Teoria"',
    `titulo: "${tituloEsc}"`,
    `fecha: ${tp.date.now("YYYY-MM-DD")}`,
    'estado: "en_proceso"',
    'transcript_status: "pendiente"',
    'summary_status: "pendiente"',
    'quiz_status: "pendiente"',
    'audio_status: "pendiente"',
    "tags:",
    "  - academia",
    "  - sesion",
    "  - teoria",
    "---",
    "",
    `# ${notaNombre}`,
    "",
    `> **Curso:** ${cursoNombre}  `,
    `> **Ciclo:** ${ciclo}  `,
    `> **Semana:** ${semanaNombre}`,
    "",
    "---",
    "",
    "## Objetivo de la clase",
    "",
    "> ",
    "",
    "---",
    "",
    "## Notas",
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
    "## Productos generados",
    "",
    "- Transcripcion: [[transcript.md]]",
    "- Resumen: [[resumen.md]]",
    "- Informe: [[informe.md]]",
    "- Puntos clave: [[puntos_clave.md]]",
    "- Cuestionario: [[cuestionario.md]]",
    "- Dudas: [[dudas.md]]",
    "- Proximas acciones: [[proximas_acciones.md]]",
    "- Guion de audio: [[audio_script.md]]",
    "- Audio explicativo: [[audio_explicativo.wav]]",
    "",
    "---",
    "",
    "## Observaciones",
    "",
    "> ",
];

tR += lines.join("\n");
-%>
