#!/usr/bin/env python3
"""Generate the single Visual Proof study containing all three properties.

The generated study is self-contained: it copies the assets from the three
property studies, so it can still run even when those studies are no longer
listed in ``public/global.json``.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from shutil import copytree


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
STUDY_ID = "visual-proof-studies"
STUDY_DIR = PUBLIC_DIR / STUDY_ID
ASSETS_DIR = STUDY_DIR / "assets"
GLOBAL_CONFIG_PATH = PUBLIC_DIR / "global.json"
PROPERTY_STUDIES = (
    ("bipartite", "bipartite-study"),
    ("hamiltonian", "hamiltonian-cycle-study"),
    ("cut_vertex", "cut-vertex-study"),
)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def prefix_block(block: dict, prefix: str) -> dict:
    """Namespace component and block identifiers in a sequence block."""
    result = copy.deepcopy(block)
    if "id" in result:
        result["id"] = f"{prefix}{result['id']}"
    result["components"] = [
        f"{prefix}{component}" if isinstance(component, str) else prefix_block(component, prefix)
        for component in result["components"]
    ]
    for skip in result.get("skip", []):
        for key in ("name", "responseId", "to"):
            if key in skip and skip[key] != "end":
                skip[key] = f"{prefix}{skip[key]}"
    return result


def rewrite_asset_paths(value: object, source_study_id: str, section: str) -> object:
    """Point copied source-study assets at this combined study's assets."""
    if isinstance(value, str):
        return value.replace(
            f"{source_study_id}/assets/", f"{STUDY_ID}/assets/{section}/"
        )
    if isinstance(value, list):
        return [rewrite_asset_paths(item, source_study_id, section) for item in value]
    if isinstance(value, dict):
        return {
            key: rewrite_asset_paths(item, source_study_id, section)
            for key, item in value.items()
        }
    return value


def load_section(section: str, source_study_id: str) -> tuple[dict, list]:
    source_dir = PUBLIC_DIR / source_study_id
    source_config_path = source_dir / "config.json"
    source_assets_dir = source_dir / "assets"
    if not source_config_path.is_file() or not source_assets_dir.is_dir():
        raise FileNotFoundError(
            f"Generate '{source_study_id}' before generating the combined study."
        )

    target_assets_dir = ASSETS_DIR / section
    copytree(source_assets_dir, target_assets_dir, dirs_exist_ok=True)
    for markdown_path in target_assets_dir.rglob("*.md"):
        markdown_path.write_text(
            markdown_path.read_text(encoding="utf-8").replace(
                f"{source_study_id}/assets/", f"{STUDY_ID}/assets/{section}/"
            ),
            encoding="utf-8",
        )
    source = json.loads(source_config_path.read_text(encoding="utf-8"))
    prefix = f"{section}_"
    components = {
        f"{prefix}{name}": prefix_component(
            rewrite_asset_paths(component, source_study_id, section), prefix
        )
        for name, component in source["components"].items()
    }
    sequence = rewrite_asset_paths(source["sequence"]["components"], source_study_id, section)
    return components, [
        f"{prefix}{component}" if isinstance(component, str) else prefix_block(component, prefix)
        for component in sequence
    ]


def prefix_component(component: object, prefix: str) -> dict:
    result = copy.deepcopy(component)
    for response in result.get("response", []):
        if "id" in response:
            response["id"] = f"{prefix}{response['id']}"
    return result


def write_intro_and_outro() -> None:
    (ASSETS_DIR / "intro.md").write_text(
        """# Visual Proof Certificates for Graph Properties

Welcome! In this study, you will complete three short parts about graph
properties: bipartiteness, Hamiltonian cycles, and cut vertices.

Each part begins with its own explanation and is followed by graph trials.

Press **Next** to begin.
""",
        encoding="utf-8",
    )
    (ASSETS_DIR / "outro.md").write_text(
        """# Thank you!

Thank you for completing the study. Your contribution is greatly appreciated.
""",
        encoding="utf-8",
    )


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    write_intro_and_outro()

    components = {
        "intro": {
            "type": "markdown",
            "path": f"{STUDY_ID}/assets/intro.md",
            "response": [],
            "nextButtonText": "Next",
            "nextButtonLocation": "belowStimulus",
        },
        "outro": {
            "type": "markdown",
            "path": f"{STUDY_ID}/assets/outro.md",
            "response": [],
            "nextButtonText": "Finish",
            "nextButtonLocation": "belowStimulus",
        },
    }
    sections = []
    for section, source_study_id in PROPERTY_STUDIES:
        source_components, source_sequence = load_section(section, source_study_id)
        components.update(source_components)
        sections.append({
            "id": f"{section}_section",
            "order": "fixed",
            "components": source_sequence,
        })

    config = {
        "$schema": "https://raw.githubusercontent.com/revisit-studies/study/v2.4.3/src/parser/StudyConfigSchema.json",
        "studyMetadata": {
            "title": "Visual Proof Certificates for Graph Properties",
            "version": "1.0.0",
            "authors": ["Visual Proof Study Team"],
            "date": "2026-08-10",
            "description": "Combined study of bipartiteness, Hamiltonian cycles, and cut vertices.",
            "organizations": ["Technische Universitat Munchen"],
        },
        "uiConfig": {
            "contactEmail": "",
            "logoPath": "revisitAssets/revisitLogoSquare.svg",
            "withProgressBar": True,
            "autoDownloadStudy": False,
            "withSidebar": True,
            "nextButtonLocation": "belowStimulus",
        },
        "components": components,
        "sequence": {
            "order": "fixed",
            "components": [
                "intro",
                {
                    "id": "property_order",
                    "order": "latinSquare",
                    "numSamples": 3,
                    "components": sections,
                },
                "outro",
            ],
        },
    }
    write_json(STUDY_DIR / "components_config.json", config)

    global_config = json.loads(GLOBAL_CONFIG_PATH.read_text(encoding="utf-8"))
    if STUDY_ID not in global_config.setdefault("configsList", []):
        global_config["configsList"].append(STUDY_ID)
    global_config.setdefault("configs", {})[STUDY_ID] = {
        "path": f"{STUDY_ID}/components_config.json",
    }
    write_json(GLOBAL_CONFIG_PATH, global_config)
    print(f"Created study '{STUDY_ID}' at {STUDY_DIR}")


if __name__ == "__main__":
    main()
