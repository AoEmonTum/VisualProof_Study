#!/usr/bin/env python3
"""Shared generator for the counterbalanced graph-property studies."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import random
from shutil import copy2
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
        if 64 <= vertices <= 100:
            return "large"
        raise ValueError(f"Graph with {vertices} vertices is outside the configured size ranges")

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

    def create_intro(tutorial: dict[str, dict]) -> None:
        settings.write_intro(assets_dir, settings.study_id, tutorial)
        (assets_dir / "study_start.md").write_text(
    f"""

<style>
.info-title {{
    margin-top: 20px;
    font-size: 20px;
    font-weight: 650;
}}

.code-line {{
    display: inline;
    box-decoration-break: clone;
    -webkit-box-decoration-break: clone;
    padding: 3px 6px;
    line-height: 1.9;
    font-size: 16px;
}}
</style>
<b style="font-size: 22px; font-weight: 650;">The {settings.property_name} part of the study begins now</b>

<div style="max-width:1150px; margin-left: 20px;line-height:1.6;">

<div class="info-title">
What will happen?
</div>


<div class="code-line">
- You will be shown 18 graphs, one after another.<br>
- For every graph, you will answer the same question by selecting Yes or No.<br>
- Please answer as quickly as possible while trying to be as accurate as you can.
</div>


<div class="info-title">
Time limit
</div>

<div class="code-line">
- Each graph will be displayed for {RESPONSE_TIME_MS // 1000} seconds.<br>
- After the graph disappears, you will still have time to answer the question.<br>
- After answering, you will be asked how confident you are that your answer was correct.
</div>


<div class="info-title">
Ready?
</div>

<div class="code-line">
When you are ready, press Next to begin.
</div>

</div>
""",
    encoding="utf-8",
)

    sidebar_instruction = f'''## Reminder: {settings.property_name}

{settings.sidebar_explanation}
'''

    def write_markdown_files(versions: list[list[dict]]) -> None:
        for pattern in ("trial_*.md",):
            for stale_file in assets_dir.glob(pattern):
                stale_file.unlink()

        def write_stimulus(trial: dict, filename: str, timed: bool) -> None:
            timer = ""
            image_animation = ""

            if timed:
                timer = f'''<div aria-label="Six-second response timer"
        style="height: 8px; width: min(100%, 720px); margin: 12px auto 0;
                background: #e9ecef; border-radius: 4px; overflow: hidden;">
        <div style="height: 100%; width: 100%; background: #228be6;
                    transform-origin: left;
                    animation: visual-proof-countdown {RESPONSE_TIME_MS / 1000:g}s linear forwards;">
        </div>
    </div>

<style>
    @keyframes visual-proof-countdown {{
        from {{ transform: scaleX(1); }}
        to   {{ transform: scaleX(0); }}
    }}

    @keyframes visual-proof-hide-graph {{
        from {{ opacity: 1; }}
        to   {{ opacity: 0; }}
    }}
    </style>
    '''

                image_animation = (
                    f"animation: visual-proof-hide-graph 0s steps(1, end) "
                    f"{RESPONSE_TIME_MS / 1000:g}s forwards;"
                )

            (assets_dir / filename).write_text(
                f'''{timer}
<img src="{settings.study_id}/assets/graphs/{trial["image"]}" alt="{settings.title} graph {trial["source"]}"
    style="display: block;
            max-width: min(100%, 800px);
            max-height: 64vh;
            margin: 12px auto 0;
            object-fit: contain;
        {image_animation}" />
    ''',
                encoding="utf-8",
            )

        for version in versions:
            for group in version:
                for trial in group:
                    write_stimulus(trial, f'{trial["id"]}.md', timed=True)

    def timing_options() -> dict:
        return {"nextButtonAutoAdvanceTime": RESPONSE_TIME_MS, "nextButtonAutoAdvanceWarningTime": 0} if AUTO_ADVANCE_ON_TIMEOUT else {}

    def verify_component(trial: dict, tutorial: bool) -> dict:
        component = {
            "type": "markdown", "path": f'{settings.study_id}/assets/{trial["id"]}.md', "nextButtonLocation": "belowStimulus",
            "instruction": sidebar_instruction, "instructionLocation": "sidebar",
            "response": [{"id": f'{settings.response_prefix}_{trial["id"]}', "prompt": settings.verification_prompt, "location": "belowStimulus", "type": "radio", "options": [{"label": settings.yes_label, "value": "yes"}, {"label": settings.no_label, "value": "no"}]}],
            "meta": {
                "condition": trial["condition"],
                "sourceGraph": trial["source"],
                "phase": "tutorial" if tutorial else "study",
            },
        }
        if not tutorial:
            component.update(timing_options())
        return component

    def confidence_component(trial: dict, tutorial: bool) -> dict:
        return {"type": "questionnaire", "instruction": sidebar_instruction, "instructionLocation": "sidebar", "response": [{"id": f'confidence_{trial["id"]}', "prompt": "Rate your confidence on a scale of 1 to 5.", "location": "aboveStimulus", "type": "likert", "numItems": 5, "start": 1, "spacing": 1, "leftLabel": "Very low confidence", "rightLabel": "Very high confidence", "labelLocation": "inline"}], "meta": {
                    "condition": trial["condition"],
                    "sourceGraph": trial["source"],
                    "phase": "tutorial" if tutorial else "study",
                }}

    def trial_block(trial: dict, components: dict, tutorial: bool) -> dict:
        verify_id, confidence_id = f'verify_{trial["id"]}', f'confidence_{trial["id"]}'
        components[verify_id] = verify_component(trial, tutorial)
        components[confidence_id] = confidence_component(trial, tutorial)
        return {"id": trial["id"], "order": "fixed", "components": [verify_id, confidence_id]}

    graphs_dir.mkdir(parents=True, exist_ok=True)
    # Remove generated practice-only assets from earlier versions of the studies.
    for stale_file in (
        *assets_dir.glob("tutorial_graph_002_*.md"),
        *assets_dir.glob("tutorial_graph_003_*.md"),
        *graphs_dir.glob("tutorial_graph_002_*.png"),
        *graphs_dir.glob("tutorial_graph_003_*.png"),
        assets_dir / "tutorial_start.md",
        assets_dir / "study_start.md",
    ):
        stale_file.unlink(missing_ok=True)
    available_graphs = load_available_graphs()
    versions = create_versions(available_graphs)
    copy_main_stimuli(versions)
    tutorial = copy_reference_stimuli()
    create_intro(tutorial)
    write_markdown_files(versions)
    components: dict = {
        "intro": {"type": "markdown", "path": f"{settings.study_id}/assets/intro.md", "response": [], "nextButtonText": "Next", "nextButtonLocation": "belowStimulus"},
        "study_start": {"type": "markdown", "path": f"{settings.study_id}/assets/study_start.md", "response": [], "nextButtonText": "Next", "nextButtonLocation": "belowStimulus"},
    }
    version_blocks = []
    for version_index, groups in enumerate(versions, start=1):
        group_blocks = []
        for group_index, group in enumerate(groups, start=1):
            group_blocks.append({
                "id": f"version_{version_index:02d}_group_{group_index}",
                "order": "random",
                "components": [trial_block(trial, components, False) for trial in group],
            })
        version_blocks.append({
            "id": f"version_{version_index:02d}",
            "order": "random",
            "components": group_blocks,
        })
    config = {
        "$schema": "https://raw.githubusercontent.com/revisit-studies/study/v2.4.3/src/parser/StudyConfigSchema.json",
        "studyMetadata": {"title": settings.title, "version": "0.2.0", "authors": ["Visual Proof Study Team"], "date": "2026-07-28", "description": f"Counterbalanced {settings.property_name} graph verification study.", "organizations": ["Technische Universitat Munchen"]},
        "uiConfig": {"contactEmail": "", "logoPath": "revisitAssets/revisitLogoSquare.svg", "withProgressBar": True, "autoDownloadStudy": False, "withSidebar": True, "nextButtonLocation": "belowStimulus"},
        "components": components,
        "sequence": {
            "order": "fixed",
            "components": [
                "intro",
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
