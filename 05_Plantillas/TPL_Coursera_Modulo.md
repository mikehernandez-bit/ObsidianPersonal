<%*
const basePath = "02_Coursera";
const moduloNombre = tp.file.title.trim();
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

const targetFolder = [basePath, programa, cursoNombre, moduloNombre]
    .filter(Boolean)
    .join("/");
await ensureFolder(targetFolder);
await tp.file.move(`${targetFolder}/${moduloNombre}`);

const programaRow = programa ? `| **Programa** | ${programa} |` : null;
const programaFilter = programa ? ` AND programa = "${programa}"` : "";

const lines = [
    "---",
    "tipo: modulo_coursera",
    "plataforma: coursera",
    `programa: "${programa}"`,
    `curso: "${cursoNombre}"`,
    `modulo: "${moduloNombre}"`,
    `fecha: ${tp.date.now("YYYY-MM-DD")}`,
    "estado: en_curso",
    "tags:",
    "  - coursera",
    "  - modulo",
    "---",
    "",
    `# Modulo: ${moduloNombre}`,
    "",
    "| | |",
    "|---|---|",
    `| **Curso** | ${cursoNombre} |`,
    programaRow,
    "| **Estado** | `= this.estado` |",
    `| **Inicio** | ${tp.date.now("YYYY-MM-DD")} |`,
    "",
    "---",
    "",
    "## Objetivos del modulo",
    "",
    "1. ",
    "2. ",
    "3. ",
    "",
    "---",
    "",
    "## Lecciones",
    "",
    "```dataview",
    "TABLE",
    '  leccion AS "Leccion",',
    '  estado AS "Estado",',
    '  fecha AS "Fecha"',
    'FROM ""',
    `WHERE tipo = "leccion_coursera" AND modulo = "${moduloNombre}" AND curso = "${cursoNombre}"${programaFilter}`,
    "SORT file.name ASC",
    "```",
    "",
    "---",
    "",
    "## Resumen del modulo",
    "",
    "> Escribe aqui un resumen general despues de completar todas las lecciones.",
    "",
    "---",
    "",
    "## Conceptos principales del modulo",
    "",
    "| Concepto | Descripcion |",
    "|---|---|",
    "| | |",
    "| | |",
    "",
    "---",
    "",
    "## Cuestionarios del modulo",
    "",
    "```dataview",
    "LIST",
    'FROM ""',
    `WHERE tipo = "cuestionario" AND modulo = "${moduloNombre}" AND plataforma = "coursera"${programaFilter}`,
    "SORT file.name ASC",
    "```",
    "",
    "---",
    "",
    "## Audios explicativos",
    "",
    "```dataview",
    "LIST",
    'FROM ""',
    `WHERE tipo = "audio_script" AND modulo = "${moduloNombre}" AND plataforma = "coursera"${programaFilter}`,
    "SORT file.name ASC",
    "```",
    "",
    "---",
    "",
    "## Progreso",
    "",
    "- [ ] Leccion 1:",
    "- [ ] Leccion 2:",
    "- [ ] Leccion 3:",
    "- [ ] Leccion 4:",
    "- [ ] Quiz del modulo completado",
    "",
    "---",
    "",
    "## Reflexion del modulo",
    "",
    "> ",
];

tR += lines.filter((line) => line !== null).join("\n");
-%>
