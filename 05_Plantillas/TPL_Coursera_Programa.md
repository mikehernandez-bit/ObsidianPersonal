<%*
const basePath = "02_Coursera";
const programa = tp.file.title.trim();

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

const targetFolder = `${basePath}/${programa}`;
await ensureFolder(targetFolder);
await tp.file.move(`${targetFolder}/${programa}`);

const lines = [
    "---",
    "tipo: programa_coursera",
    "plataforma: coursera",
    `programa: "${programa}"`,
    `fecha_inicio: ${tp.date.now("YYYY-MM-DD")}`,
    "estado: en_curso",
    "tags:",
    "  - coursera",
    "  - programa",
    "---",
    "",
    `# Programa: ${programa}`,
    "",
    "| | |",
    "|---|---|",
    "| **Plataforma** | Coursera |",
    `| **Inicio** | ${tp.date.now("YYYY-MM-DD")} |`,
    "| **Estado** | `= this.estado` |",
    "",
    "---",
    "",
    "## Descripcion del programa",
    "",
    "> ",
    "",
    "---",
    "",
    "## Cursos del programa",
    "",
    "```dataview",
    "TABLE",
    '  estado AS "Estado",',
    '  fecha_inicio AS "Inicio"',
    'FROM ""',
    `WHERE tipo = "curso_coursera" AND programa = "${programa}"`,
    "SORT file.name ASC",
    "```",
    "",
    "---",
    "",
    "## Progreso general",
    "",
    "```dataview",
    "TABLE",
    '  curso AS "Curso",',
    '  modulo AS "Modulo",',
    '  leccion AS "Leccion",',
    '  estado AS "Estado"',
    'FROM ""',
    `WHERE tipo = "leccion_coursera" AND programa = "${programa}"`,
    "SORT curso ASC, modulo ASC, leccion ASC",
    "```",
    "",
    "---",
    "",
    "## Certificaciones",
    "",
    "| Curso | Certificado | Fecha |",
    "|---|---|---|",
    "| | ⬜ | |",
    "| | ⬜ | |",
    "| | ⬜ | |",
    "",
    "---",
    "",
    "## Progreso",
    "",
    "- [ ] Curso 1:",
    "- [ ] Curso 2:",
    "- [ ] Curso 3:",
    "- [ ] Certificacion del programa",
    "",
    "---",
    "",
    "## Notas generales",
    "",
    "> ",
];

tR += lines.join("\n");
-%>
