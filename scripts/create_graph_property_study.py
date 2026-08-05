#!/usr/bin/env python3
"""Shared generator for the counterbalanced graph-property studies."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import random
from shutil import copy2
from typing import Callable


CONDITIONS = ("proof_property", "noproof_property", "proof_noproperty", "noproof_noproperty")
SIZES = ("small", "medium", "large")
GRAPHS_PER_SIZE = 6
MAIN_TRIALS = 18
PARTICIPANT_LISTS = 4
RESPONSE_TIME_MS = 6_000
# Set to True before generation to automatically continue when the timer ends.
AUTO_ADVANCE_ON_TIMEOUT = False


def select_graphs(graphs: list[dict], rng: random.Random) -> list[dict]:
    """Select six unique graphs from each size group.

    Keeping this policy separate makes it straightforward to substitute a
    different graph-selection strategy later.
    """
    selected = []
    for size in SIZES:
        size_graphs = [graph for graph in graphs if graph["size"] == size]
        if len(size_graphs) < GRAPHS_PER_SIZE:
            raise ValueError(f"Expected at least {GRAPHS_PER_SIZE} {size} graphs, found {len(size_graphs)}")
        selected.extend(rng.sample(size_graphs, GRAPHS_PER_SIZE))
    return selected


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

    def copy_images(source_dir: Path, target_prefix: str) -> dict[str, str]:
        images = {}
        for condition in CONDITIONS:
            source = source_dir / f"{condition}.png"
            if not source.is_file():
                raise FileNotFoundError(f"Missing stimulus image: {source}")
            target_name = f"{target_prefix}_{condition}.png"
            copy2(source, graphs_dir / target_name)
            images[condition] = target_name
        return images

    def copy_main_stimuli() -> list[dict]:
        graphs = []
        for source_dir in sorted(path for path in stimuli_dir.glob("graph_*") if path.is_dir()):
            metadata = json.loads((source_dir / "metadata.json").read_text(encoding="utf-8"))
            graphs.append({
                "source": source_dir.name,
                "vertices": metadata["vertices"],
                "size": graph_size(metadata["vertices"]),
                "images": copy_images(source_dir, source_dir.name),
            })
        return graphs

    def copy_reference_stimuli() -> dict[str, dict]:
        """Copy intro/sidebar examples, falling back to the main stimulus set if needed."""
        images = {}
        for condition in CONDITIONS:
            tutorial_image = tutorial_dir / "graph_001" / f"{condition}.png"
            source = tutorial_image if tutorial_image.is_file() else stimuli_dir / "graph_001" / f"{condition}.png"
            if not source.is_file():
                raise FileNotFoundError(f"Missing reference image: {source}")
            target_name = f"tutorial_graph_001_{condition}.png"
            copy2(source, graphs_dir / target_name)
            images[condition] = target_name
        return {"graph_001": {"source": "graph_001", "images": images}}

    def latin_square_base_graph_sets(graphs: list[dict]) -> list[list[dict]]:
        """Create fixed Latin-Square base sets; runtime assigns visualizations."""
        base_graph_sets = []
        study_seed = sum(ord(character) for character in settings.study_id)
        for list_index in range(1, PARTICIPANT_LISTS + 1):
            selected = select_graphs(graphs, random.Random(20_260_800 + study_seed + list_index))
            if len(selected) != MAIN_TRIALS or len({graph["source"] for graph in selected}) != MAIN_TRIALS:
                raise ValueError("A participant list must contain 18 unique graphs")
            if {size: sum(graph["size"] == size for graph in selected) for size in SIZES} != {size: GRAPHS_PER_SIZE for size in SIZES}:
                raise ValueError("A participant list must contain six graphs per size")
            base_graph_sets.append(selected)
        return base_graph_sets

    def create_intro(tutorial: dict[str, dict]) -> None:
        settings.write_intro(assets_dir, settings.study_id, tutorial)
        (assets_dir / "study_start.md").write_text(
    f"""
<div style="max-width:1100px; margin:40px auto;">

<h1 style="margin-bottom:12px;">
The {settings.property_name} Section
</h1>

<p style="font-size:18px; line-height:1.7; color:#555; margin-bottom:30px;">
You are now about to begin the <strong>{settings.property_name}</strong> part of the study.
Please read the following instructions carefully.
</p>

<div style="
background:#f8fafc;
border:1px solid #e5e7eb;
border-radius:16px;
padding:24px;
margin-bottom:28px;
">

<h2 style="margin-top:0;">What will happen?</h2>

<ul style="font-size:17px; line-height:1.9; padding-left:22px; margin-bottom:0;">
<li>You will be shown <strong>18 graphs</strong>, one after another.</li>
<li>For each graph, answer the question by selecting <strong>Yes</strong> or <strong>No</strong>.</li>
<li>Please answer as <strong>quickly</strong> as possible while maintaining a high level of <strong>accuracy</strong>.</li>
</ul>

</div>

<div style="
background:#f8fafc;
border:1px solid #e5e7eb;
border-radius:16px;
padding:24px;
margin-bottom:28px;
">

<h2 style="margin-top:0;">Time limit</h2>

<ul style="font-size:17px; line-height:1.9; padding-left:22px; margin-bottom:0;">
<li>Each graph will be displayed for <strong>{RESPONSE_TIME_MS // 1000} seconds</strong>.</li>
<li>After the graph disappears, you will still have time to submit your answer.</li>
<li>After answering, you will be asked how confident you are that your answer was correct.</li>
</ul>

</div>

<div style="
background:#ecfdf5;
border:1px solid #10b981;
border-radius:12px;
padding:18px;
text-align:center;
font-size:18px;
">

When you are ready, press <strong>Next</strong> to begin.

</div>

</div>
""",
    encoding="utf-8",
)

    sidebar_instruction = f'''## Reminder: {settings.property_name}

{settings.sidebar_explanation}
'''

    def trial_id(list_index: int, graph: dict, condition: str) -> str:
        return f"list_{list_index}_{graph['source']}_{condition}"

    def write_markdown_files(base_graph_sets: list[list[dict]]) -> None:
        for pattern in ("list_*.md", "tutorial_graph_*_*.md"):
            for stale_file in assets_dir.glob(pattern):
                stale_file.unlink()

        def write_stimulus(trial: dict, filename: str, timed: bool) -> None:
            timer = ""
            image_animation = ""
            if timed:
                timer = f'''<div aria-label="Six-second response timer" style="height: 8px; width: min(100%, 720px); margin: 12px auto 0; background: #e9ecef; border-radius: 4px; overflow: hidden;"><div style="height: 100%; width: 100%; background: #228be6; transform-origin: left; animation: visual-proof-countdown {RESPONSE_TIME_MS / 1000:g}s linear forwards;"></div></div><style>@keyframes visual-proof-countdown {{ from {{ transform: scaleX(1); }} to {{ transform: scaleX(0); }} }} @keyframes visual-proof-hide-graph {{ from {{ opacity: 1; }} to {{ opacity: 0; }} }}</style>'''
                image_animation = f"animation: visual-proof-hide-graph 0s steps(1, end) {RESPONSE_TIME_MS / 1000:g}s forwards;"
            (assets_dir / filename).write_text(
                f'''{timer}<img src="{settings.study_id}/assets/graphs/{trial["image"]}" alt="{settings.title} graph {trial["source"]}" style="display: block; max-width: min(100%, 800px); max-height: 64vh; margin: 12px auto 0; object-fit: contain; {image_animation}" />\n''', encoding="utf-8")

        for list_index, graph_set in enumerate(base_graph_sets, start=1):
            for graph in graph_set:
                for condition in CONDITIONS:
                    trial = {**graph, "condition": condition, "image": graph["images"][condition]}
                    write_stimulus(trial, f'{trial_id(list_index, graph, condition)}.md', timed=True)

    def timing_options() -> dict:
        return {"nextButtonAutoAdvanceTime": RESPONSE_TIME_MS, "nextButtonAutoAdvanceWarningTime": 0} if AUTO_ADVANCE_ON_TIMEOUT else {}

    def verify_component(trial: dict, tutorial: bool) -> dict:
        component = {
            "type": "markdown", "path": f'{settings.study_id}/assets/{trial["id"]}.md', "nextButtonLocation": "belowStimulus",
            "instruction": sidebar_instruction, "instructionLocation": "sidebar",
            "response": [{"id": f'{settings.response_prefix}_{trial["id"]}', "prompt": settings.verification_prompt, "location": "belowStimulus", "type": "radio", "options": [{"label": settings.yes_label, "value": "yes"}, {"label": settings.no_label, "value": "no"}]}],
            "meta": {"condition": trial["condition"], "sourceGraph": trial["source"], "phase": "tutorial" if tutorial else "study"},
        }
        if not tutorial:
            component.update(timing_options())
        return component

    def confidence_component(trial: dict, tutorial: bool) -> dict:
        return {"type": "questionnaire", "instruction": sidebar_instruction, "instructionLocation": "sidebar", "response": [{"id": f'confidence_{trial["id"]}', "prompt": "Rate your confidence on a scale of 1 to 5.", "location": "aboveStimulus", "type": "likert", "numItems": 5, "start": 1, "spacing": 1, "leftLabel": "Very low confidence", "rightLabel": "Very high confidence", "labelLocation": "inline"}], "meta": {"condition": trial["condition"], "sourceGraph": trial["source"], "phase": "tutorial" if tutorial else "study"}}

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
    graphs, tutorial = copy_main_stimuli(), copy_reference_stimuli()
    base_graph_sets = latin_square_base_graph_sets(graphs)
    create_intro(tutorial)
    write_markdown_files(base_graph_sets)
    runtime_randomizer_source = script_path.resolve().parent / "graph_trial_randomizer.ts"
    if not runtime_randomizer_source.is_file():
        raise FileNotFoundError(f"Missing runtime trial randomizer: {runtime_randomizer_source}")
    copy2(runtime_randomizer_source, assets_dir / "graph_trial_randomizer.ts")
    components: dict = {
        "intro": {"type": "markdown", "path": f"{settings.study_id}/assets/intro.md", "response": [], "nextButtonText": "Next", "nextButtonLocation": "belowStimulus"},
        "study_start": {"type": "markdown", "path": f"{settings.study_id}/assets/study_start.md", "response": [], "nextButtonText": "Next", "nextButtonLocation": "belowStimulus"},
    }
    main_lists = []
    for list_index, graph_set in enumerate(base_graph_sets, start=1):
        for graph in graph_set:
            for condition in CONDITIONS:
                trial = {
                    **graph,
                    "id": trial_id(list_index, graph, condition),
                    "condition": condition,
                    "image": graph["images"][condition],
                }
                components[f'verify_{trial["id"]}'] = verify_component(trial, False)
                components[f'confidence_{trial["id"]}'] = confidence_component(trial, False)
        main_lists.append({
            "id": f"latin_list_{list_index}",
            "order": "dynamic",
            "functionPath": f"{settings.study_id}/assets/graph_trial_randomizer.ts",
            "parameters": {
                "listId": f"list_{list_index}",
                "graphs": [{key: graph[key] for key in ("source", "size", "vertices")} for graph in graph_set],
            },
        })
    config = {
        "$schema": "https://raw.githubusercontent.com/revisit-studies/study/v2.4.3/src/parser/StudyConfigSchema.json",
        "studyMetadata": {"title": settings.title, "version": "0.2.0", "authors": ["Visual Proof Study Team"], "date": "2026-07-28", "description": f"Counterbalanced {settings.property_name} graph verification study.", "organizations": ["Technische Universitat Munchen"]},
        "uiConfig": {"contactEmail": "", "logoPath": "revisitAssets/revisitLogoSquare.svg", "withProgressBar": True, "autoDownloadStudy": False, "withSidebar": True, "nextButtonLocation": "belowStimulus"},
        "components": components,
        "sequence": {"order": "fixed", "components": ["intro", "study_start", {"id": "participant_list", "order": "latinSquare", "numSamples": 1, "components": main_lists}]},
    }
    missing_markdown = [
        component["path"]
        for component in components.values()
        if component.get("type") == "markdown" and not (public_dir / component["path"]).is_file()
    ]
    if missing_markdown:
        raise FileNotFoundError(f"Generated configuration references missing Markdown assets: {missing_markdown}")
    write_json(assets_dir / "graphs.json", {"graphs": graphs, "latinSquareBaseGraphSets": base_graph_sets})
    write_json(study_dir / "config.json", config)
    global_path = public_dir / "global.json"
    global_config = json.loads(global_path.read_text(encoding="utf-8"))
    if settings.study_id not in global_config.setdefault("configsList", []):
        global_config["configsList"].append(settings.study_id)
    global_config.setdefault("configs", {})[settings.study_id] = {"path": f"{settings.study_id}/config.json"}
    write_json(global_path, global_config)
    print(f"Created study '{settings.study_id}' at {study_dir}")
