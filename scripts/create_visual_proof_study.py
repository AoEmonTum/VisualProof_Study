#!/usr/bin/env python3
"""Create the initial Visual Proof cut-vertex study."""

from __future__ import annotations

import json
from pathlib import Path

from cut_vertex_graph_generator import generate_cut_vertex_svgs


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
STUDY_ID = "visual-proof-cut-vertex"
OLD_STUDY_ID = "visual-proof-property-x"
NUM_TRIALS = 10
STUDY_DIR = PUBLIC_DIR / STUDY_ID
ASSETS_DIR = STUDY_DIR / "assets"
GRAPHS_DIR = ASSETS_DIR / "graphs"
CONFIG_PATH = STUDY_DIR / "config.json"
GLOBAL_CONFIG_PATH = PUBLIC_DIR / "global.json"


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def create_markdown_files(graph_metadata: list[dict]) -> None:
    for item in graph_metadata:
    index = item["index"]
    # Use the same image sizing style as the Hamiltonian study
    markdown = f'''<img src="{STUDY_ID}/assets/graphs/{item["filename"]}" alt="Cut vertex graph {index}" style="display: block; max-width: min(100%, 720px); max-height: 58vh; margin: 0 auto; object-fit: contain;" />
'''
    (ASSETS_DIR / f"visualization_{index:02d}.md").write_text(markdown, encoding="utf-8")


def verify_component(index: int) -> dict:
    return {
        "type": "markdown",
        "path": f"{STUDY_ID}/assets/visualization_{index:02d}.md",
        "response": [
            {
                "id": f"canVerifyCutVertex_{index:02d}",
                "prompt": "Based on this visualization, can you verify that the graph has a cut vertex?",
                "location": "aboveStimulus",
                "type": "radio",
                "options": [
                    {
                        "label": "Yes, I can verify",
                        "value": "yes",
                    },
                    {
                        "label": "No, I cannot verify",
                        "value": "no",
                    },
                ],
            }
        ],
    }


def confidence_component(index: int) -> dict:
    return {
        "type": "questionnaire",
        "response": [
            {
                "id": f"confidence_{index:02d}",
                "prompt": "Rate your confidence on a scale of 1 to 5. (1 being very low confidence and 5 being very high confidence)",
                "location": "aboveStimulus",
                "type": "likert",
                "numItems": 5,
                "start": 1,
                "spacing": 1,
                "leftLabel": "Very low confidence",
                "rightLabel": "Very high confidence",
                "labelLocation": "inline",
            }
        ],
    }


def study_config(graph_metadata: list[dict]) -> dict:
    components = {}
    trial_blocks = []

    for item in graph_metadata:
        index = item["index"]
        trial_id = f"trial_{index:02d}"
        verify_id = f"verifyCutVertex_{index:02d}"
        confidence_id = f"confidence_{index:02d}"
        next_trial_id = f"trial_{index + 1:02d}" if index < len(graph_metadata) else "end"

        components[verify_id] = verify_component(index)
        components[confidence_id] = confidence_component(index)
        trial_blocks.append(
            {
                "id": trial_id,
                "order": "fixed",
                "components": [verify_id, confidence_id],
                "skip": [
                    {
                        "name": verify_id,
                        "check": "response",
                        "responseId": f"canVerifyCutVertex_{index:02d}",
                        "value": "no",
                        "comparison": "equal",
                        "to": next_trial_id,
                    }
                ],
            }
        )

    return {
        "$schema": "https://raw.githubusercontent.com/revisit-studies/study/v2.4.3/src/parser/StudyConfigSchema.json",
        "studyMetadata": {
            "title": "Visual Proof Cut Vertex",
            "version": "0.1.0",
            "authors": ["Visual Proof Study Team"],
            "date": "2026-06-30",
            "description": "Initial scaffold for a cut-vertex verification study.",
            "organizations": ["Technische Universitat Munchen"],
        },
        "uiConfig": {
            "contactEmail": "",
            "logoPath": "revisitAssets/revisitLogoSquare.svg",
            "withProgressBar": True,
            "autoDownloadStudy": False,
            "withSidebar": True,
            "nextButtonLocation": "aboveStimulus",
        },
        "components": components,
        "sequence": {
            "order": "fixed",
            "components": trial_blocks,
        },
    }


def update_global_config() -> None:
    global_config = json.loads(GLOBAL_CONFIG_PATH.read_text(encoding="utf-8"))
    configs_list = global_config.setdefault("configsList", [])
    configs = global_config.setdefault("configs", {})

    if STUDY_ID not in configs_list:
        configs_list.append(STUDY_ID)

    configs[STUDY_ID] = {"path": f"{STUDY_ID}/config.json"}
    if OLD_STUDY_ID in configs_list:
        configs_list.remove(OLD_STUDY_ID)
    configs.pop(OLD_STUDY_ID, None)
    write_json(GLOBAL_CONFIG_PATH, global_config)


def main() -> None:
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    graph_metadata = generate_cut_vertex_svgs(GRAPHS_DIR, count=NUM_TRIALS)
    create_markdown_files(graph_metadata)
    write_json(ASSETS_DIR / "graphs.json", {"graphs": graph_metadata})
    write_json(CONFIG_PATH, study_config(graph_metadata))
    update_global_config()
    print(f"Created study '{STUDY_ID}' at {STUDY_DIR}")


if __name__ == "__main__":
    main()
