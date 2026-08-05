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
    """Namespace traditional sequence blocks without changing Dynamic Blocks."""
    result = copy.deepcopy(block)
    # Dynamic Blocks are leaves: they have functionPath/parameters, but no
    # child components to namespace. Keeping them unchanged also preserves the
    # runtime function's block identifier and parameters.
    if "components" not in result:
        return result
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
"""<h1 style="margin-bottom:12px;">
Visual Proof Certificates for Graph Properties
</h1>

<p style="font-size:18px; line-height:1.7; color:#555; margin-bottom:28px;">
Graphs are a powerful way of representing relationships between objects.
Throughout this study, you will analyze graphs and learn how visualizations can help identify important graph properties.
</p>

<div style="
    background:#f8fafc;
    border:1px solid #e5e7eb;
    border-radius:16px;
    padding:24px;
    margin:30px 0;
">

<h2 style="margin-top:0;">Example: A transportation network</h2>

<p style="line-height:1.7;">
Imagine a simplified transportation network in Germany.
Each <strong>vertex</strong> represents a city and each <strong>edge</strong>
represents a direct road between two cities.
</p>

<div style="
display:flex;
gap:32px;
justify-content:center;
align-items:flex-start;
margin:28px 0;
">

<div style="flex:1; text-align:center;">

<img
src="intro_utilities/map.png"
style="max-width:100%; border-radius:12px; box-shadow:0 4px 16px rgba(0,0,0,.12);">

<p style="margin-top:12px; color:#666;">
Road network
</p>

</div>

<div style="flex:1; text-align:center;">

<img
src="intro_utilities/graph.png"
style="max-width:100%; border-radius:12px; box-shadow:0 4px 16px rgba(0,0,0,.12);">

<p style="margin-top:12px; color:#666;">
Corresponding graph
</p>

</div>

</div>

<p style="line-height:1.7;">
Although the map contains geographical information, many questions only depend
on <strong>which cities are connected</strong>.
For these questions, the transportation network can be represented simply as a graph.
</p>

<div style="
background:#fff7ed;
border-left:5px solid #f59e0b;
padding:16px 20px;
border-radius:10px;
margin-top:22px;
">

<strong>Example:</strong><br><br>

Frankfurt is a <strong>cut vertex</strong>.
If Frankfurt became inaccessible, Munich could no longer be reached from the rest of the transportation network.

</div>

</div>

<hr style="margin:42px 0; border:none; border-top:1px solid #ddd;">

<h2>What will you do?</h2>

<p style="line-height:1.7;">
During this study we will introduce three graph properties and see how different visualizations help in analyzing them.
Each section first introduces the property and then presents <strong>18 graph trials</strong>.
</p>

<div style="
display:grid;
grid-template-columns:repeat(3,1fr);
gap:18px;
margin:28px 0;
">

<div style="
padding:18px;
border:1px solid #e5e7eb;
border-radius:14px;
text-align:center;
background:white;
">

<h3 style="margin-top:0;">Bipartiteness</h3>

Determine whether a graph is bipartite.

</div>

<div style="
padding:18px;
border:1px solid #e5e7eb;
border-radius:14px;
text-align:center;
background:white;
">

<h3 style="margin-top:0;">Hamiltonian Cycles</h3>

Determine whether a graph contains a Hamiltonian cycle.

</div>

<div style="
padding:18px;
border:1px solid #e5e7eb;
border-radius:14px;
text-align:center;
background:white;
">

<h3 style="margin-top:0;">Cut Vertices</h3>

Determine whether a graph contains a cut vertex.

</div>

</div>

<p style="line-height:1.7;">
The order of the three sections as well as the order of the graph trials is counterbalanced across participants.
</p>

<div style="
margin-top:36px;
padding:18px;
background:#ecfdf5;
border:1px solid #10b981;
border-radius:12px;
text-align:center;
font-size:18px;
">

Press <strong>Next</strong> to begin.

</div>
""",
encoding="utf-8",
    )
    (ASSETS_DIR / "outro.md").write_text(
"""
<div style="
max-width:900px;
margin:40px auto;
text-align:center;
">

<h1 style="margin-bottom:16px;">
Thank You!
</h1>

<p style="
font-size:18px;
line-height:1.7;
color:#555;
margin-bottom:32px;
">
You have successfully completed the
<strong>Visual Proof Certificates for Graph Properties</strong>
study.
</p>

<div style="
background:#f8fafc;
border:1px solid #e5e7eb;
border-radius:16px;
padding:28px;
margin:30px 0;
">

<p style="
font-size:17px;
line-height:1.8;
margin:0;
">
Your participation is greatly appreciated and will help us better understand
how different visualizations support the analysis of graph properties.
</p>

</div>
</div>
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
    sections_by_property = {}
    for prefix, source_study_id in PROPERTY_STUDIES:
        namespace = f"{prefix}_"
        source_components, source_sequence = load_property_section(namespace, source_study_id)
        components.update(source_components)
        sections_by_property[prefix] = {
            "id": f"{prefix}_section",
            "order": "fixed",
            "components": source_sequence,
        }

    # The three cyclic permutations form a Latin Square for property order.
    property_names = [prefix for prefix, _ in PROPERTY_STUDIES]
    property_order_lists = []
    for order_index in range(len(property_names)):
        ordered_properties = property_names[order_index:] + property_names[:order_index]
        property_order_lists.append({
            "id": f"property_order_{order_index + 1}",
            "order": "fixed",
            "components": [sections_by_property[property_name] for property_name in ordered_properties],
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
            "components": [
                "intro",
                {
                    "id": "property_order",
                    "order": "latinSquare",
                    "numSamples": 1,
                    "components": property_order_lists,
                },
                "outro",
            ],
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
