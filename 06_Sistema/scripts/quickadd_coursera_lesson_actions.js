const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

function getVaultPath(app) {
  return app.vault.adapter.basePath;
}

function getProjectDir(vaultPath) {
  const localProject = path.join(vaultPath, "06_Sistema", "ObsidianAcademia");
  if (fs.existsSync(path.join(localProject, "config.yaml"))) {
    return localProject;
  }

  const envProject = process.env.OBSIDIAN_ACADEMIA_PROJECT_DIR;
  if (envProject && fs.existsSync(path.join(envProject, "config.yaml"))) {
    return envProject;
  }

  const legacyProject = "C:\\Users\\jhoan\\ObsidianAcademia";
  return legacyProject;
}

function getPythonExecutable(vaultPath) {
  const projectDir = getProjectDir(vaultPath);
  const venvPython = path.join(projectDir, ".venv", "Scripts", "python.exe");
  return fs.existsSync(venvPython) ? venvPython : "python";
}

function getHelperScript(vaultPath) {
  return path.join(vaultPath, "06_Sistema", "scripts", "coursera_lesson_actions.py");
}

function stripQuotes(value) {
  if (typeof value !== "string") {
    return "";
  }
  return value.replace(/^["']|["']$/g, "").trim();
}

function getFrontmatter(cache) {
  return cache?.frontmatter || {};
}

function assertLessonContext(frontmatter) {
  if (frontmatter.tipo !== "leccion_coursera") {
    throw new Error("La nota activa no es una leccion Coursera.");
  }
  if (!frontmatter.curso || !frontmatter.modulo || !frontmatter.leccion) {
    throw new Error("La leccion activa no tiene curso, modulo o leccion en el frontmatter.");
  }
}

async function getActiveLessonContext(params) {
  const app = params.app;
  const activeFile = app.workspace.getActiveFile();

  if (!activeFile) {
    throw new Error("No hay una nota activa.");
  }

  const cache = app.metadataCache.getFileCache(activeFile);
  const frontmatter = getFrontmatter(cache);
  assertLessonContext(frontmatter);

  const vaultPath = getVaultPath(app);
  const absoluteNotePath = path.join(vaultPath, activeFile.path);

  return {
    app,
    file: activeFile,
    frontmatter,
    vaultPath,
    notePath: absoluteNotePath,
    lessonDir: path.dirname(absoluteNotePath),
  };
}

function buildArgs(action, context) {
  const args = [
    getHelperScript(context.vaultPath),
    action,
    "--vault",
    context.vaultPath,
    "--note",
    context.notePath,
    "--lesson-dir",
    context.lessonDir,
    "--course",
    stripQuotes(context.frontmatter.curso),
    "--module",
    stripQuotes(context.frontmatter.modulo),
    "--lesson",
    stripQuotes(context.frontmatter.leccion),
  ];

  const program = stripQuotes(context.frontmatter.programa || "");
  if (program) {
    args.push("--program", program);
  }

  return args;
}

function runPython(action, context) {
  const parseJsonOutput = (output) => {
    const lines = output
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean);

    if (!lines.length) {
      throw new Error("El helper no devolvio salida util.");
    }

    return JSON.parse(lines[lines.length - 1]);
  };

  return new Promise((resolve, reject) => {
    const child = spawn(getPythonExecutable(context.vaultPath), buildArgs(action, context), {
      cwd: getProjectDir(context.vaultPath),
      windowsHide: true,
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString("utf8");
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString("utf8");
    });

    child.on("error", (error) => {
      reject(error);
    });

    child.on("close", (code) => {
      if (code !== 0) {
        try {
          const parsed = parseJsonOutput(stdout);
          reject(new Error(parsed.message || "La accion Coursera termino con error."));
          return;
        } catch (error) {
          // El helper puede haber fallado antes de emitir JSON.
        }

        reject(
          new Error(
            stderr.trim() || stdout.trim() || `El proceso Python termino con codigo ${code}.`,
          ),
        );
        return;
      }

      try {
        resolve(parseJsonOutput(stdout));
      } catch (error) {
        reject(
          new Error(
            `No se pudo interpretar la salida del helper de Coursera. ${stdout.trim()}`,
          ),
        );
      }
    });
  });
}

async function updateLessonFrontmatter(context, statuses) {
  if (!statuses || typeof statuses !== "object") {
    return;
  }

  await context.app.fileManager.processFrontMatter(context.file, (frontmatter) => {
    Object.entries(statuses).forEach(([key, value]) => {
      frontmatter[key] = value;
    });
    frontmatter.fecha_ia = new Date().toISOString().slice(0, 10);
  });
}

async function openOutputFile(context, outputFile) {
  if (!outputFile) {
    return;
  }

  const relativePath = path.relative(context.vaultPath, outputFile).replace(/\\/g, "/");
  const file = context.app.vault.getAbstractFileByPath(relativePath);

  if (file) {
    await context.app.workspace.getLeaf(true).openFile(file);
  }
}

async function runAction(params, action, label) {
  const { Notice } = params.obsidian;
  const context = await getActiveLessonContext(params);
  const workingNotice = new Notice(`${label}...`, 0);

  try {
    const result = await runPython(action, context);

    if (!result.ok) {
      throw new Error(result.message || "La accion termino con error.");
    }

    await updateLessonFrontmatter(context, result.statuses);
    await openOutputFile(context, result.open_file);

    workingNotice.hide();
    new Notice(result.message || `${label} completado.`, 7000);
    return result.message || `${label} completado.`;
  } catch (error) {
    workingNotice.hide();
    new Notice(`Error: ${error.message}`, 10000);
    throw error;
  }
}

async function processLesson(params) {
  return runAction(params, "process-full", "Procesando leccion Coursera");
}

async function generateReport(params) {
  return runAction(params, "generate-report", "Generando informe");
}

async function generateAudio(params) {
  return runAction(params, "generate-audio", "Generando audio");
}

async function generateQuiz(params) {
  return runAction(params, "generate-quiz", "Generando cuestionario");
}

module.exports = {
  processLesson,
  generateReport,
  generateAudio,
  generateQuiz,
};
