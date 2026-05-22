<%*
const basePath = "02_Coursera";
const cursoNombre = tp.file.title.trim();
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

const programas = Array.from(
    new Set(
        fileCaches
            .filter((cache) => cache.frontmatter.tipo === "programa_coursera")
            .map((cache) => cache.frontmatter.programa)
            .filter(Boolean),
    ),
).sort((a, b) => a.localeCompare(b, "es"));

let programa = "";
if (programas.length > 0) {
    const opcionesPrograma = ["Sin programa (curso individual)"].concat(programas);
    const seleccionPrograma = await tp.system.suggester(
        opcionesPrograma,
        opcionesPrograma,
    );

    if (
        seleccionPrograma &&
        seleccionPrograma !== "Sin programa (curso individual)"
    ) {
        programa = seleccionPrograma;
    }
}

const targetFolder = [basePath, programa, cursoNombre].filter(Boolean).join("/");
await ensureFolder(targetFolder);
await tp.file.move(`${targetFolder}/${cursoNombre}`);

const programaRow = programa ? `| **Programa** | ${programa} |` : null;
const programaFilter = programa ? ` AND programa = "${programa}"` : "";

const lines = [
    "---",
    "tipo: curso_coursera",
    "plataforma: coursera",
    `programa: "${programa}"`,
    `curso: "${cursoNombre}"`,
    `fecha_inicio: ${tp.date.now("YYYY-MM-DD")}`,
    "estado: en_curso",
    "tags:",
    "  - coursera",
    "  - curso",
    "---",
    "",
    `# Curso: ${cursoNombre}`,
    "",
    "| | |",
    "|---|---|",
    "| **Plataforma** | Coursera |",
    programaRow,
    `| **Inicio** | ${tp.date.now("YYYY-MM-DD")} |`,
    "| **Estado** | `= this.estado` |",
    "",
    "---",
    "",
    "## Descripcion del curso",
    "",
    "> ",
    "",
    "---",
    "",
    "## Objetivos de aprendizaje",
    "",
    "1. ",
    "2. ",
    "3. ",
    "",
    "---",
    "",
    "## Modulos",
    "",
    "```dataview",
    "TABLE",
    '  estado AS "Estado"',
    'FROM ""',
    `WHERE tipo = "modulo_coursera" AND curso = "${cursoNombre}"${programaFilter}`,
    "SORT file.name ASC",
    "```",
    "",
    "---",
    "",
    "## Progreso general",
    "",
    "```dataview",
    "TABLE",
    '  modulo AS "Modulo",',
    '  leccion AS "Leccion",',
    '  estado AS "Estado",',
    '  fecha AS "Fecha"',
    'FROM ""',
    `WHERE tipo = "leccion_coursera" AND curso = "${cursoNombre}"${programaFilter}`,
    "SORT modulo ASC, leccion ASC",
    "```",
    "",
    "---",
    "",
    "## Resumenes por modulo",
    "",
    "```dataview",
    "LIST",
    'FROM ""',
    `WHERE tipo = "resumen" AND curso = "${cursoNombre}" AND plataforma = "coursera"${programaFilter}`,
    "SORT file.name ASC",
    "```",
    "",
    "---",
    "",
    "## Certificacion",
    "",
    "- [ ] Todos los modulos completados",
    "- [ ] Todos los quizzes aprobados",
    "- [ ] Proyecto final entregado (si aplica)",
    "- [ ] Certificado obtenido",
    "",
    "**Link al certificado:**",
    "",
    "---",
    "",
    "## Valoracion del curso",
    "",
    "**Calidad:** ⬜⬜⬜⬜⬜ (1-5)",
    "",
    "**Dificultad:** ⬜⬜⬜⬜⬜ (1-5)",
    "",
    "**Utilidad:** ⬜⬜⬜⬜⬜ (1-5)",
    "",
    "> Que me parecio el curso? Lo recomendaria?",
    "> ",
];

tR += lines.filter((line) => line !== null).join("\n");
-%>
