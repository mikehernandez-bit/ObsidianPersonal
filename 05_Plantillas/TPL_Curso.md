<%*
const basePath = "01_Universidad";
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

function escapeValue(value) {
    return String(value || "").replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

const fileCaches = pages
    .map((path) => {
        const file = app.vault.getAbstractFileByPath(path);
        return file ? app.metadataCache.getFileCache(file) : null;
    })
    .filter((cache) => cache && cache.frontmatter);

const existingCycles = Array.from(
    new Set(
        fileCaches
            .filter((cache) => cache.frontmatter.tipo === "curso")
            .map((cache) => String(cache.frontmatter.ciclo || "").trim())
            .filter(Boolean),
    ),
).sort((a, b) => a.localeCompare(b, "es"));

let ciclo = "";
if (existingCycles.length > 0) {
    ciclo = await tp.system.suggester(existingCycles, existingCycles);
}

if (!ciclo) {
    ciclo = await tp.system.prompt("Ciclo del curso", existingCycles[0] || "IX");
}

ciclo = String(ciclo || "").trim();

const cursoEsc = escapeValue(cursoNombre);
const cicloEsc = escapeValue(ciclo);
const targetFolder = `${basePath}/${ciclo}/${cursoNombre}`;
const targetFolderEsc = escapeValue(targetFolder);

await ensureFolder(targetFolder);
await tp.file.move(`${targetFolder}/${cursoNombre}`);

const lines = [
    "---",
    'tipo: "curso"',
    `curso: "${cursoEsc}"`,
    `curso_nombre: "${cursoEsc}"`,
    `ciclo: "${cicloEsc}"`,
    `ruta_curso: "${targetFolderEsc}"`,
    "semanas_total: 16",
    'estado: "activo"',
    `fecha_inicio: ${tp.date.now("YYYY-MM-DD")}`,
    "tags:",
    "  - academia",
    "  - curso",
    "---",
    "",
    `# ${cursoNombre}`,
    "",
    "| Propiedad | Valor |",
    "|---|---|",
    "| **Ciclo** | `= this.ciclo` |",
    "| **Semanas** | `= this.semanas_total` |",
    "| **Estado** | `= this.estado` |",
    `| **Inicio** | ${tp.date.now("YYYY-MM-DD")} |`,
    "",
    "---",
    "",
    "## Descripcion del curso",
    "",
    "> ",
    "",
    "---",
    "",
    "## Semanas",
    "",
    "```dataview",
    "TABLE WITHOUT ID",
    '  link(file.link, semana) AS "Semana",',
    '  fecha_inicio AS "Inicio",',
    '  estado AS "Estado"',
    'FROM ""',
    `WHERE tipo = "semana" AND curso_nombre = "${cursoEsc}" AND ciclo = "${cicloEsc}"`,
    "SORT file.name ASC",
    "```",
    "",
    "---",
    "",
    "## Sesiones",
    "",
    "```dataview",
    "TABLE WITHOUT ID",
    '  link(file.link, file.name) AS "Sesion",',
    '  semana AS "Semana",',
    '  sesion AS "Tipo",',
    '  fecha AS "Fecha",',
    '  estado AS "Estado"',
    'FROM ""',
    `WHERE tipo = "sesion" AND curso_nombre = "${cursoEsc}" AND ciclo = "${cicloEsc}"`,
    "SORT fecha DESC",
    "```",
    "",
    "---",
    "",
    "## Tareas",
    "",
    "```dataview",
    "TABLE WITHOUT ID",
    '  link(file.link, titulo) AS "Tarea",',
    '  semana AS "Semana",',
    '  fecha_entrega AS "Entrega",',
    '  estado AS "Estado"',
    'FROM ""',
    `WHERE tipo = "tarea" AND curso_nombre = "${cursoEsc}" AND ciclo = "${cicloEsc}"`,
    "SORT fecha_asignacion DESC",
    "```",
    "",
    "---",
    "",
    "## Notas generales",
    "",
    "> ",
];

tR += lines.join("\n");
-%>
