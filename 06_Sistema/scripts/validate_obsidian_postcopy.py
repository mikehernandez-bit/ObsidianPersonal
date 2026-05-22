from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SYSTEM_DIR = SCRIPT_DIR.parent
VAULT_DIR = SYSTEM_DIR.parent
BACKEND_DIR = SYSTEM_DIR / "ObsidianAcademia"
OBSIDIAN_DIR = VAULT_DIR / ".obsidian"
PLUGINS_DIR = OBSIDIAN_DIR / "plugins"

REQUIRED_COMMUNITY_PLUGINS = [
    "quickadd",
    "templater-obsidian",
    "buttons",
    "dataview",
]

REQUIRED_PLUGIN_FOLDERS = REQUIRED_COMMUNITY_PLUGINS + [
    "obsidian-excalidraw-plugin",
]

REQUIRED_FILES = [
    VAULT_DIR / "05_Plantillas" / "TPL_Coursera_Leccion.md",
    VAULT_DIR / "06_Sistema" / "scripts" / "coursera_lesson_actions.py",
    VAULT_DIR / "06_Sistema" / "scripts" / "quickadd_coursera_lesson_actions.js",
    BACKEND_DIR / "config.yaml",
    BACKEND_DIR / "main.py",
    BACKEND_DIR / "requirements.txt",
    BACKEND_DIR / "tools" / "ffmpeg-bin" / "ffmpeg.exe",
    BACKEND_DIR / "tools" / "ffmpeg-bin" / "ffprobe.exe",
    BACKEND_DIR / "tools" / "piper" / "piper.exe",
    BACKEND_DIR / "tools" / "voices" / "es_ES-mls_10246-low.onnx",
    BACKEND_DIR / "tools" / "voices" / "es_ES-mls_10246-low.onnx.json",
]

REQUIRED_QUICKADD_CHOICES = {
    "qa-coursera-process-lesson": "quickadd_coursera_lesson_actions.js::processLesson",
    "qa-coursera-generate-report": "quickadd_coursera_lesson_actions.js::generateReport",
    "qa-coursera-generate-audio": "quickadd_coursera_lesson_actions.js::generateAudio",
    "qa-coursera-generate-quiz": "quickadd_coursera_lesson_actions.js::generateQuiz",
}


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def add_result(results: list[CheckResult], name: str, ok: bool, detail: str) -> None:
    results.append(CheckResult(name=name, ok=ok, detail=detail))


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def check_required_files(results: list[CheckResult]) -> None:
    for path in REQUIRED_FILES:
        add_result(
            results,
            f"file:{path.relative_to(VAULT_DIR)}",
            path.exists(),
            str(path),
        )


def check_community_plugins(results: list[CheckResult]) -> None:
    plugins_path = OBSIDIAN_DIR / "community-plugins.json"
    if not plugins_path.exists():
        add_result(results, "community-plugins", False, "No existe community-plugins.json")
        return

    enabled = set(read_json(plugins_path))
    for plugin_id in REQUIRED_COMMUNITY_PLUGINS:
        add_result(
            results,
            f"community-plugin:{plugin_id}",
            plugin_id in enabled,
            f"enabled={plugin_id in enabled}",
        )


def check_plugin_folders(results: list[CheckResult]) -> None:
    for plugin_id in REQUIRED_PLUGIN_FOLDERS:
        plugin_dir = PLUGINS_DIR / plugin_id
        add_result(
            results,
            f"plugin-folder:{plugin_id}",
            plugin_dir.exists(),
            str(plugin_dir),
        )


def check_templater(results: list[CheckResult]) -> None:
    data_path = PLUGINS_DIR / "templater-obsidian" / "data.json"
    if not data_path.exists():
        add_result(results, "templater:data", False, "No existe data.json de Templater")
        return

    data = read_json(data_path)
    templates_folder = data.get("templates_folder")
    add_result(
        results,
        "templater:templates_folder",
        templates_folder == "05_Plantillas",
        f"templates_folder={templates_folder!r}",
    )


def _find_quickadd_choice(data: dict, choice_id: str) -> dict | None:
    for choice in data.get("choices", []):
        if choice.get("id") == choice_id:
            return choice
    return None


def check_quickadd(results: list[CheckResult]) -> None:
    data_path = PLUGINS_DIR / "quickadd" / "data.json"
    if not data_path.exists():
        add_result(results, "quickadd:data", False, "No existe data.json de QuickAdd")
        return

    data = read_json(data_path)
    add_result(
        results,
        "quickadd:template_folder",
        data.get("templateFolderPath") == "05_Plantillas",
        f"templateFolderPath={data.get('templateFolderPath')!r}",
    )
    add_result(
        results,
        "quickadd:use_selection_as_capture",
        data.get("useSelectionAsCaptureValue") is False,
        f"useSelectionAsCaptureValue={data.get('useSelectionAsCaptureValue')!r}",
    )

    for choice_id, user_script_name in REQUIRED_QUICKADD_CHOICES.items():
        choice = _find_quickadd_choice(data, choice_id)
        if not choice:
            add_result(results, f"quickadd:{choice_id}", False, "Choice no encontrado")
            continue

        macro = choice.get("macro") or {}
        commands = macro.get("commands") or []
        if not commands:
            add_result(results, f"quickadd:{choice_id}", False, "Macro sin commands")
            continue

        command = commands[0]
        script_path = command.get("path")
        script_name = command.get("name")
        ok = (
            command.get("type") == "UserScript"
            and script_path == "06_Sistema/scripts/quickadd_coursera_lesson_actions.js"
            and script_name == user_script_name
        )
        add_result(
            results,
            f"quickadd:{choice_id}",
            ok,
            f"type={command.get('type')!r}, path={script_path!r}, name={script_name!r}",
        )


def check_runtime_helpers(results: list[CheckResult]) -> None:
    js_path = VAULT_DIR / "06_Sistema" / "scripts" / "quickadd_coursera_lesson_actions.js"
    node_path = shutil.which("node")
    if not node_path:
        add_result(results, "runtime:node", False, "Node no esta disponible")
        return

    command = [
        node_path,
        "-e",
        (
            "const helper=require(process.argv[1]);"
            "const keys=Object.keys(helper).sort().join(',');"
            "console.log(keys);"
        ),
        str(js_path),
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=str(VAULT_DIR),
        timeout=30,
    )
    output = completed.stdout.strip()
    ok = completed.returncode == 0 and output == (
        "generateAudio,generateQuiz,generateReport,processLesson"
    )
    detail = output or completed.stderr.strip() or f"exit={completed.returncode}"
    add_result(results, "runtime:quickadd_helper", ok, detail)


def check_obsidian_cli(results: list[CheckResult]) -> None:
    obsidian_cli = shutil.which("obsidian")
    if not obsidian_cli:
        add_result(
            results,
            "runtime:obsidian_cli",
            True,
            "No instalado. Validacion dentro de la app omitida.",
        )
        return

    completed = subprocess.run(
        [obsidian_cli, "help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    add_result(
        results,
        "runtime:obsidian_cli",
        completed.returncode == 0,
        completed.stdout.splitlines()[0] if completed.stdout else completed.stderr.strip(),
    )


def print_report(results: list[CheckResult]) -> int:
    failures = [result for result in results if not result.ok]
    print("== Validacion post-copia de Obsidian ==", flush=True)
    for result in results:
        status = "OK" if result.ok else "FAIL"
        print(f"[{status}] {result.name} :: {result.detail}", flush=True)

    summary = {
        "ok": not failures,
        "checks": len(results),
        "failures": len(failures),
    }
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0 if not failures else 1


def main() -> int:
    results: list[CheckResult] = []
    check_required_files(results)
    check_community_plugins(results)
    check_plugin_folders(results)
    check_templater(results)
    check_quickadd(results)
    check_runtime_helpers(results)
    check_obsidian_cli(results)
    return print_report(results)


if __name__ == "__main__":
    raise SystemExit(main())
