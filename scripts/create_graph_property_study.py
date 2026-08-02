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
BLOCKS_PER_PARTICIPANT = 3
TRIALS_PER_BLOCK = 6
TRIALS_PER_BLOCK_SIZE = 2
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


def assign_visualizations(selected_graphs: list[dict], rng: random.Random) -> list[dict]:
    """Give every selected graph one balanced visualization variant.

    Every size group receives all four variants at least once. The final
    18-trial distribution is a shuffled 5/5/4/4 allocation.
    """
    by_size = {size: [graph for graph in selected_graphs if graph["size"] == size] for size in SIZES}
    if any(len(graphs) != GRAPHS_PER_SIZE for graphs in by_size.values()):
        raise ValueError("Visualization assignment requires six graphs per size group")

    target_conditions = list(CONDITIONS)
    rng.shuffle(target_conditions)
    target_counts = {condition: 5 if condition in target_conditions[:2] else 4 for condition in CONDITIONS}
    remaining_extras = {condition: target_counts[condition] - len(SIZES) for condition in CONDITIONS}

    # Allocate the two extra slots in each size group while meeting the global
    # 5/5/4/4 target. A small randomized backtracking search keeps this robust.
    extra_pairs = [(first, second) for first in CONDITIONS for second in CONDITIONS]
    rng.shuffle(extra_pairs)
    size_extras: dict[str, tuple[str, str]] = {}

    def allocate_extras(size_index: int) -> bool:
        if size_index == len(SIZES):
            return all(count == 0 for count in remaining_extras.values())
        size = SIZES[size_index]
        for first, second in extra_pairs:
            needed = {condition: (first, second).count(condition) for condition in CONDITIONS}
            if any(needed[condition] > remaining_extras[condition] for condition in CONDITIONS):
                continue
            for condition in CONDITIONS:
                remaining_extras[condition] -= needed[condition]
            size_extras[size] = (first, second)
            if allocate_extras(size_index + 1):
                return True
            for condition in CONDITIONS:
                remaining_extras[condition] += needed[condition]
            del size_extras[size]
        return False

    if not allocate_extras(0):
        raise RuntimeError("Could not construct a balanced visualization assignment")

    trials = []
    for size in SIZES:
        graphs = list(by_size[size])
        rng.shuffle(graphs)
        assigned_conditions = [*CONDITIONS, *size_extras[size]]
        rng.shuffle(assigned_conditions)
        trials.extend({
            "source": graph["source"],
            "size": graph["size"],
            "vertices": graph["vertices"],
            "condition": condition,
            "image": graph["images"][condition],
        } for graph, condition in zip(graphs, assigned_conditions))
    return trials


def build_blocks(trials: list[dict], rng: random.Random) -> list[list[dict]] | None:
    """Arrange trials into three balanced blocks, or return None if impossible."""
    remaining = {size: [trial for trial in trials if trial["size"] == size] for size in SIZES}
    slots = []
    for block_index in range(BLOCKS_PER_PARTICIPANT):
        block_sizes = [size for size in SIZES for _ in range(TRIALS_PER_BLOCK_SIZE)]
        rng.shuffle(block_sizes)
        slots.extend((block_index, size) for size in block_sizes)
    blocks = [[] for _ in range(BLOCKS_PER_PARTICIPANT)]
    block_conditions = [set() for _ in range(BLOCKS_PER_PARTICIPANT)]

    def fill(slot_index: int) -> bool:
        if slot_index == len(slots):
            return all(len(conditions) == len(CONDITIONS) for conditions in block_conditions)
        block_index, size = slots[slot_index]
        candidates = list(remaining[size])
        rng.shuffle(candidates)
        candidates.sort(key=lambda trial: trial["condition"] in block_conditions[block_index])
        for trial in candidates:
            remaining[size].remove(trial)
            blocks[block_index].append(trial)
            previous_conditions = set(block_conditions[block_index])
            block_conditions[block_index].add(trial["condition"])

            future_slots = [future_size for future_block, future_size in slots[slot_index + 1:] if future_block == block_index]
            missing = set(CONDITIONS) - block_conditions[block_index]
            feasible = len(missing) <= len(future_slots)
            for condition in missing:
                if not any(candidate["condition"] == condition for future_size in future_slots for candidate in remaining[future_size]):
                    feasible = False
                    break
            if feasible and fill(slot_index + 1):
                return True

            block_conditions[block_index] = previous_conditions
            blocks[block_index].pop()
            remaining[size].append(trial)
        return False

    return blocks if fill(0) else None


def generate_trial_order(graphs: list[dict], rng: random.Random, list_index: int) -> list[list[dict]]:
    """Select graphs, assign variants, and create the constrained trial blocks."""
    for _ in range(100):
        trials = assign_visualizations(select_graphs(graphs, rng), rng)
        blocks = build_blocks(trials, rng)
        if blocks is None:
            continue
        for block_index, block in enumerate(blocks, start=1):
            rng.shuffle(block)
            for trial_index, trial in enumerate(block, start=1):
                trial["id"] = f"list_{list_index}_block_{block_index}_trial_{trial_index:02d}"
        return blocks
    raise RuntimeError("Could not build balanced trial blocks after 100 attempts")


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

    def latin_square_trials(graphs: list[dict]) -> list[list[list[dict]]]:
        """Create reproducible, independently randomized participant lists."""
        trial_lists = []
        study_seed = sum(ord(character) for character in settings.study_id)
        for list_index in range(1, PARTICIPANT_LISTS + 1):
            blocks = generate_trial_order(graphs, random.Random(20_260_800 + study_seed + list_index), list_index)
            flattened = [trial for block in blocks for trial in block]
            if len(flattened) != MAIN_TRIALS or len({trial["source"] for trial in flattened}) != MAIN_TRIALS:
                raise ValueError("A participant list must contain 18 unique graphs")
            if {size: sum(trial["size"] == size for trial in flattened) for size in SIZES} != {size: GRAPHS_PER_SIZE for size in SIZES}:
                raise ValueError("A participant list must contain six graphs per size")
            if any(sum(trial["condition"] == condition for trial in flattened) > 5 for condition in CONDITIONS):
                raise ValueError("No visualization may occur more than five times")
            for size in SIZES:
                if set(trial["condition"] for trial in flattened if trial["size"] == size) != set(CONDITIONS):
                    raise ValueError("Every visualization must occur in every graph-size group")
            for block in blocks:
                if len(block) != TRIALS_PER_BLOCK:
                    raise ValueError("Each trial block must contain six trials")
                if {size: sum(trial["size"] == size for trial in block) for size in SIZES} != {size: TRIALS_PER_BLOCK_SIZE for size in SIZES}:
                    raise ValueError("Each trial block must contain two graphs per size")
                if set(trial["condition"] for trial in block) != set(CONDITIONS):
                    raise ValueError("Each trial block must contain every visualization type")
            trial_lists.append(blocks)
        return trial_lists

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

    def write_markdown_files(trial_lists: list[list[list[dict]]]) -> None:
        for pattern in ("list_*_trial_*.md", "tutorial_graph_*_*.md"):
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

        for trial_list in trial_lists:
            for block in trial_list:
                for trial in block:
                    write_stimulus(trial, f'{trial["id"]}.md', timed=True)

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
    graphs, tutorial = copy_main_stimuli(), copy_reference_stimuli()
    trial_lists = latin_square_trials(graphs)
    create_intro(tutorial)
    write_markdown_files(trial_lists)
    components: dict = {
        "intro": {"type": "markdown", "path": f"{settings.study_id}/assets/intro.md", "response": [], "nextButtonText": "Next", "nextButtonLocation": "belowStimulus"},
        "study_start": {"type": "markdown", "path": f"{settings.study_id}/assets/study_start.md", "response": [], "nextButtonText": "Next", "nextButtonLocation": "belowStimulus"},
    }
    main_lists = [
        {
            "id": f"latin_list_{list_index}",
            "order": "fixed",
            "components": [
                {
                    "id": f"list_{list_index}_block_{block_index}",
                    "order": "random",
                    "components": [trial_block(trial, components, False) for trial in block],
                }
                for block_index, block in enumerate(trial_list, start=1)
            ],
        }
        for list_index, trial_list in enumerate(trial_lists, start=1)
    ]
    config = {
        "$schema": "https://raw.githubusercontent.com/revisit-studies/study/v2.4.3/src/parser/StudyConfigSchema.json",
        "studyMetadata": {"title": settings.title, "version": "0.2.0", "authors": ["Visual Proof Study Team"], "date": "2026-07-28", "description": f"Counterbalanced {settings.property_name} graph verification study.", "organizations": ["Technische Universitat Munchen"]},
        "uiConfig": {"contactEmail": "", "logoPath": "revisitAssets/revisitLogoSquare.svg", "withProgressBar": True, "autoDownloadStudy": False, "withSidebar": True, "nextButtonLocation": "belowStimulus"},
        "components": components,
        "sequence": {"order": "fixed", "components": ["intro", "study_start", {"id": "participant_list", "order": "latinSquare", "numSamples": 1, "components": main_lists}]},
    }
    write_json(assets_dir / "graphs.json", {"graphs": graphs, "latinSquareLists": trial_lists})
    write_json(study_dir / "config.json", config)
    global_path = public_dir / "global.json"
    global_config = json.loads(global_path.read_text(encoding="utf-8"))
    if settings.study_id not in global_config.setdefault("configsList", []):
        global_config["configsList"].append(settings.study_id)
    global_config.setdefault("configs", {})[settings.study_id] = {"path": f"{settings.study_id}/config.json"}
    write_json(global_path, global_config)
    print(f"Created study '{settings.study_id}' at {study_dir}")
