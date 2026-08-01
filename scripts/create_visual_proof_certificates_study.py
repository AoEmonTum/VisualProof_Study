#!/usr/bin/env python3
"""Create one study that combines the three Visual Proof property studies."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
STUDY_ID = "visual-proof-certificates-for-graph-properties"
STUDY_DIR = PUBLIC_DIR / STUDY_ID
ASSETS_DIR = STUDY_DIR / "assets"
CONFIG_PATH = STUDY_DIR / "config.json"
GLOBAL_CONFIG_PATH = PUBLIC_DIR / "global.json"
PROPERTY_STUDIES = (
    ("bipartite", "visual-proof-bipartite"),
    ("hamiltonian", "visual-proof-hamiltonian-cycle"),
    ("cut_vertex", "visual-proof-cut-vertex"),
)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def prefix_component(component: dict, prefix: str) -> dict:
    """Namespace response IDs so all source-study components can coexist."""
    result = copy.deepcopy(component)
    for response in result.get("response", []):
        if "id" in response:
            response["id"] = f"{prefix}{response['id']}"
    return result


def prefix_block(block: dict, prefix: str) -> dict:
    """Namespace a reVISit sequence block recursively."""
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


def load_property_section(prefix: str, source_study_id: str) -> tuple[dict, list]:
    source_path = PUBLIC_DIR / source_study_id / "config.json"
    if not source_path.is_file():
        raise FileNotFoundError(f"Generate '{source_study_id}' before creating the combined study.")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    components = {
        f"{prefix}{name}": prefix_component(component, prefix)
        for name, component in source["components"].items()
    }
    sequence_components = [
        f"{prefix}{component}" if isinstance(component, str) else prefix_block(component, prefix)
        for component in source["sequence"]["components"]
    ]
    return components, sequence_components


def write_markdown() -> None:
    (ASSETS_DIR / "intro.md").write_text(
        """# Visual Proof Certificates for Graph Properties

A **graph** is a collection of vertices (or nodes) connected by edges. Graphs can represent many systems, such as social networks, transport routes, or links between web pages.

In this study, you will work through three graph properties:

- bipartiteness,
- Hamiltonian cycles, and
- cut vertices.

Each section explains its property before presenting the graph trials. The order of graph trials within every section is counterbalanced with a Latin-square design.

Press **Next** to begin.
""",
        encoding="utf-8",
    )
    (ASSETS_DIR / "outro.md").write_text(
        """# Thank you!

Thank you for completing the Visual Proof Certificates for Graph Properties study and for taking the time to participate.

Your contribution is greatly appreciated.
""",
        encoding="utf-8",
    )


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    write_markdown()

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
    for prefix, source_study_id in PROPERTY_STUDIES:
        namespace = f"{prefix}_"
        source_components, source_sequence = load_property_section(namespace, source_study_id)
        components.update(source_components)
        sections.append({
            "id": f"{prefix}_section",
            "order": "fixed",
            "components": source_sequence,
        })

    config = {
        "$schema": "https://raw.githubusercontent.com/revisit-studies/study/v2.4.3/src/parser/StudyConfigSchema.json",
        "studyMetadata": {
            "title": "Visual Proof Certificates for Graph Properties",
            "version": "0.1.0",
            "authors": ["Visual Proof Study Team"],
            "date": "2026-07-31",
            "description": "Combined counterbalanced study of bipartiteness, Hamiltonian cycles, and cut vertices.",
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
            "components": ["intro", *sections, "outro"],
        },
    }
    write_json(CONFIG_PATH, config)

    global_config = json.loads(GLOBAL_CONFIG_PATH.read_text(encoding="utf-8"))
    if STUDY_ID not in global_config.setdefault("configsList", []):
        global_config["configsList"].append(STUDY_ID)
    global_config.setdefault("configs", {})[STUDY_ID] = {"path": f"{STUDY_ID}/config.json"}
    write_json(GLOBAL_CONFIG_PATH, global_config)
    print(f"Created study '{STUDY_ID}' at {STUDY_DIR}")


if __name__ == "__main__":
    main()
