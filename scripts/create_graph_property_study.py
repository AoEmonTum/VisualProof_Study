#!/usr/bin/env python3
"""Shared generator for the counterbalanced graph-property studies."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import random
from shutil import copy2, rmtree
from typing import Callable

RESPONSE_TIME_MS = 6_000
# Set to True before generation to automatically continue when the timer ends.
AUTO_ADVANCE_ON_TIMEOUT = False
NUM_STUDY_VERSIONS = 10
GRAPHS_PER_SIZE = 6
VISUALIZATIONS = (
    "proof_property",
    "noproof_property",
    "proof_noproperty",
    "noproof_noproperty",
)
TRIAL_COMPONENT_PATH = "graph-property-study/assets/GraphTrial.tsx"

@dataclass(frozen=True)
class StudySettings:
    study_id: str
    stimulus_folder: str
    title: str
    property_name: str
    property_definition: str
    verification_prompt: str
    response_prefix: str
    yes_label: str
    no_label: str
    sidebar_explanation: str
    write_intro: Callable[[Path, str, dict[str, dict]], None]


def create_study(script_path: Path, settings: StudySettings) -> None:
    root = script_path.resolve().parents[1]
    public_dir = root / "public"
    study_dir = public_dir / settings.study_id
    assets_dir = study_dir / "assets"
    graphs_dir = assets_dir / "graphs"
    stimuli_dir = root.parents[1] / "graph_tests" / "stimuli" / settings.stimulus_folder
    tutorial_dir = root.parents[1] / "graph_tests" / "tutorial_stimuli" / settings.stimulus_folder

    def write_json(path: Path, data: dict) -> None:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def graph_size(vertices: int) -> str:
        if 10 <= vertices <= 33:
            return "small"
        if 34 <= vertices <= 66:
            return "medium"
        if 67 <= vertices <= 100:
            return "large"
        raise ValueError(f"Graph with {vertices} nodes is outside the configured size ranges")

    def graph_duration_ms(vertices: int) -> int:
        if 10 <= vertices <= 33:
            return 6_000
        if 34 <= vertices <= 66:
            return 8_000
        if 67 <= vertices <= 100:
            return 11_000
        raise ValueError(f"Graph with {vertices} nodes is outside the configured size ranges")

    def load_available_graphs() -> list[dict]:
        graphs = []
        for source_dir in sorted(path for path in stimuli_dir.glob("graph_*") if path.is_dir()):
            metadata = json.loads((source_dir / "metadata.json").read_text(encoding="utf-8"))
            graphs.append({
                "source": source_dir.name,
                "vertices": metadata["vertices"],
                "size": graph_size(metadata["vertices"]),
            })
        return graphs

    def create_versions(available_graphs: list[dict]) -> list[list[list[dict]]]:
        """Create ten 18-trial plans with balanced stimuli and size blocks."""
        graphs_by_size = {
            size: [graph for graph in available_graphs if graph["size"] == size]
            for size in ("small", "medium", "large")
        }
        for size, graphs in graphs_by_size.items():
            if len(graphs) < GRAPHS_PER_SIZE:
                raise ValueError(
                    f"Need at least {GRAPHS_PER_SIZE} {size} graphs, found {len(graphs)}"
                )

        def extra_visualizations() -> list[list[str]]:
            # Every size gets all four visualizations once. The two additional
            # visualizations per size yield a total distribution of 4, 4, 5, 5.
            repeated = random.sample(VISUALIZATIONS, 2)
            extras = [*VISUALIZATIONS, *repeated]
            while True:
                random.shuffle(extras)
                pairs = [extras[index:index + 2] for index in range(0, len(extras), 2)]
                if all(pair[0] != pair[1] for pair in pairs):
                    return pairs

        versions = []
        for version_index in range(1, NUM_STUDY_VERSIONS + 1):
            size_order = ["small", "medium", "large"]
            random.shuffle(size_order)
            trials_by_size = {}
            for size, extras in zip(size_order, extra_visualizations()):
                selected = random.sample(graphs_by_size[size], GRAPHS_PER_SIZE)
                conditions = [*VISUALIZATIONS, *extras]
                random.shuffle(conditions)
                trials = []
                for trial_index, (graph, condition) in enumerate(zip(selected, conditions), start=1):
                    trials.append({
                        **graph,
                        "condition": condition,
                        "image": f'{graph["source"]}_{condition}.png',
                        "id": f"version_{version_index:02d}_{size}_{trial_index:02d}",
                    })
                trials_by_size[size] = trials

            # Each size occurs in two of the three groups. Thus every group
            # contains exactly two sizes and six graphs (three of each size).
            for _ in range(10_000):
                groups = [[], [], []]
                for size, group_indices in (("small", (0, 1)), ("medium", (0, 2)), ("large", (1, 2))):
                    trials = list(trials_by_size[size])
                    random.shuffle(trials)
                    groups[group_indices[0]].extend(trials[:3])
                    groups[group_indices[1]].extend(trials[3:])
                if all({trial["condition"] for trial in group} == set(VISUALIZATIONS) for group in groups):
                    versions.append(groups)
                    break
            else:
                raise RuntimeError("Could not construct groups with all visualizations")
        return versions

    def copy_main_stimuli(versions: list[list[list[dict]]]) -> None:
        for version in versions:
            for group in version:
                for trial in group:
                    source = stimuli_dir / trial["source"] / f'{trial["condition"]}.png'
                    if not source.is_file():
                        raise FileNotFoundError(f"Missing stimulus image: {source}")
                    copy2(source, graphs_dir / trial["image"])

    def copy_reference_stimuli() -> dict[str, dict]:
        images = {}

        for condition in (
            "proof_property",
            "noproof_property",
            "proof_noproperty",
            "noproof_noproperty",
        ):
            tutorial_image = tutorial_dir / "graph_001" / f"{condition}.png"
            source = tutorial_image if tutorial_image.is_file() else stimuli_dir / "graph_001" / f"{condition}.png"

            if not source.is_file():
                raise FileNotFoundError(f"Missing reference image: {source}")

            target_name = f"tutorial_graph_001_{condition}.png"
            copy2(source, graphs_dir / target_name)
            images[condition] = target_name

        return {"graph_001": {"source": "graph_001", "images": images}}

    def write_intro(tutorial: dict[str, dict]) -> None:
        study_start_markdown = f"""
<style>
.study-shell {{
    max-width: 1120px;
    margin: 0 auto;
    padding: 8px 20px 36px;
    color: #1f2937;
}}

.study-hero {{
    padding: 28px 30px;
    border-radius: 24px;
    background: linear-gradient(135deg, #f7fbff 0%, #eef4ff 100%);
    border: 1px solid #dce7f5;
    box-shadow: 0 16px 36px rgba(15, 23, 42, 0.06);
}}

.study-kicker {{
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #3461d9;
}}

.study-title {{
    margin: 10px 0 10px;
    font-size: 34px;
    line-height: 1.1;
    font-weight: 750;
    color: #10213a;
}}

.study-lead {{
    margin: 0;
    font-size: 17px;
    line-height: 1.8;
    color: #354255;
    max-width: 72ch;
}}

.study-stack {{
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 12px;
    margin-top: 22px;
}}

.study-card {{
    padding: 14px 16px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid #dce7f5;
}}

.study-card h3 {{
    margin: 0 0 8px;
    font-size: 18px;
    line-height: 1.3;
    color: #10213a;
}}

.study-card p,
.study-card li {{
    margin: 0;
    font-size: 15px;
    line-height: 1.75;
    color: #445469;
}}

.study-card ul {{
    margin: 0;
    padding-left: 18px;
}}

.study-note {{
    margin-top: 18px;
    padding: 16px 18px;
    border-radius: 16px;
    background: #f5f8fc;
    border-left: 4px solid #3461d9;
    font-size: 15px;
    line-height: 1.7;
    color: #344457;
}}
</style>

<div class="study-shell">
  <div class="study-hero">
    <div class="study-kicker">Study Start</div>
    <div class="study-title">The {settings.property_name} part of the study begins now</div>
    <p class="study-lead">
      In this part, you will decide whether each graph has the {settings.property_name} property. Please answer as quickly as possible while trying to be as accurate as you can.
    </p>

<div class="study-stack">
      <div class="study-card">
        <h3>What will happen?</h3>
        <ul>
          <li>You will be shown <strong>18 graphs</strong>, one after another.</li>
          <li>For every graph, you will answer the same question by selecting <strong>Yes</strong> or <strong>No</strong>.</li>
          <li>Please answer as quickly as possible while trying to be as accurate as you can.</li>
        </ul>
      </div>

<div class="study-card">
        <h3>Time limit</h3>
        <ul>
          <li>Each graph will be displayed for <strong>6-11 seconds</strong> depending on its size.</li>
          <li>After the graph disappears, but you will still be able to answer the question.</li>
          <li>After answering, you will be asked how confident you are that your answer was correct.</li>
        </ul>
      </div>
    </div>

<div class="study-note">
      <strong>Ready?</strong><br>
      When you are ready, press <strong>Next</strong> to begin.
    </div>
  </div>
</div>
"""
        (assets_dir / "study_start.md").write_text(study_start_markdown, encoding="utf-8")
        settings.write_intro(assets_dir, settings.study_id, tutorial)

    def trial_component(trial: dict, tutorial: bool) -> dict:
        return {
            "type": "react-component",
            "path": TRIAL_COMPONENT_PATH,
            "response": [],
            "parameters": {
                "componentName": trial["id"],
                "trialId": trial["id"],
                "propertyName": settings.property_name,
                "propertyDefinition": settings.property_definition,
                "verificationPrompt": settings.verification_prompt,
                "yesLabel": settings.yes_label,
                "noLabel": settings.no_label,
                "graphPath": f'assets/graphs/{trial["image"]}',
                "graphLabel": f'{settings.title} graph {trial["source"]}',
                "durationMs": graph_duration_ms(trial["vertices"]),
                "nodeCount": trial["vertices"],
                "graphSize": trial["size"],
                "visualization": trial["condition"],
                "sourceGraph": trial["source"],
                "phase": "tutorial" if tutorial else "study",
            },
            "meta": {
                "condition": trial["condition"],
                "sourceGraph": trial["source"],
                "phase": "tutorial" if tutorial else "study",
            },
        }

    graphs_dir.mkdir(parents=True, exist_ok=True)
    for stale_dir in (assets_dir, graphs_dir):
        for stale_file in stale_dir.glob("trial_*.md"):
            stale_file.unlink(missing_ok=True)
        for stale_file in stale_dir.glob("version_*.md"):
            stale_file.unlink(missing_ok=True)
    for stale_file in (assets_dir / "property_explanation.md", assets_dir / "study_start.md"):
        stale_file.unlink(missing_ok=True)
    # Remove generated practice-only assets from earlier versions of the studies.
    for stale_file in (
        *assets_dir.glob("tutorial_graph_002_*.md"),
        *assets_dir.glob("tutorial_graph_003_*.md"),
        *graphs_dir.glob("tutorial_graph_002_*.png"),
        *graphs_dir.glob("tutorial_graph_003_*.png"),
        assets_dir / "tutorial_start.md",
    ):
        stale_file.unlink(missing_ok=True)
    available_graphs = load_available_graphs()
    versions = create_versions(available_graphs)
    copy_main_stimuli(versions)
    tutorial = copy_reference_stimuli()
    write_intro(tutorial)
    components: dict = {
        "property_explanation": {"type": "markdown", "path": f"{settings.study_id}/assets/property_explanation.md", "response": [], "nextButtonText": "Next", "nextButtonLocation": "belowStimulus"},
        "study_start": {"type": "markdown", "path": f"{settings.study_id}/assets/study_start.md", "response": [], "nextButtonText": "Next", "nextButtonLocation": "belowStimulus"},
    }
    version_blocks = []
    for version_index, groups in enumerate(versions, start=1):
        group_blocks = []
        for group_index, group in enumerate(groups, start=1):
            group_blocks.append({
                "id": f"version_{version_index:02d}_group_{group_index}",
                "order": "random",
                "components": [trial["id"] for trial in group],
            })
        version_blocks.append({
            "id": f"version_{version_index:02d}",
            "order": "random",
            "components": group_blocks,
        })
    for version in versions:
        for group in version:
            for trial in group:
                components[trial["id"]] = trial_component(trial, False)
    config = {
        "$schema": "https://raw.githubusercontent.com/revisit-studies/study/v2.4.3/src/parser/StudyConfigSchema.json",
        "studyMetadata": {"title": settings.title, "version": "0.2.0", "authors": ["Visual Proof Study Team"], "date": "2026-07-28", "description": f"Counterbalanced {settings.property_name} graph verification study.", "organizations": ["Technische Universitat Munchen"]},
        "uiConfig": {"contactEmail": "", "logoPath": "revisitAssets/revisitLogoSquare.svg", "withProgressBar": True, "autoDownloadStudy": False, "withSidebar": True, "nextButtonLocation": "belowStimulus"},
        "components": components,
        "sequence": {
            "order": "fixed",
            "components": [
                "property_explanation",
                "study_start",
                {"id": "study_version", "order": "random", "numSamples": 1, "components": version_blocks},
            ],
        },
    }
    write_json(
        assets_dir / "graphs.json",
        {
            "versions": versions,
        },
    )
    write_json(study_dir / "config.json", config)
    global_path = public_dir / "global.json"
    global_config = json.loads(global_path.read_text(encoding="utf-8"))
    if settings.study_id not in global_config.setdefault("configsList", []):
        global_config["configsList"].append(settings.study_id)
    global_config.setdefault("configs", {})[settings.study_id] = {"path": f"{settings.study_id}/config.json"}
    write_json(global_path, global_config)
    print(f"Created study '{settings.study_id}' at {study_dir}")
