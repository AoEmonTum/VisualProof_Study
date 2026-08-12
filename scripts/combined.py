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
from shutil import copytree, rmtree


ROOT = Path(__file__).resolve().parents[1]
SOCIAL_NETWORK_DIR = ROOT.parent.parent / "graph_tests" / "socialNetwork"
PUBLIC_DIR = ROOT / "public"
STUDY_ID = "visual-proof-study-pilot-5"
STUDY_DIR = PUBLIC_DIR / STUDY_ID
ASSETS_DIR = STUDY_DIR / "assets"
GLOBAL_CONFIG_PATH = PUBLIC_DIR / "global.json"
PROPERTY_STUDIES = (
    ("bipartite-study-8", "bipartite-study-8"),
    ("hamiltonian-cycle-study-8", "hamiltonian-cycle-study-8"),
    ("cut-vertex-study-8", "cut-vertex-study-8"),
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
    if target_assets_dir.exists():
        rmtree(target_assets_dir)
    copytree(source_assets_dir, target_assets_dir, dirs_exist_ok=True)
    for markdown_path in target_assets_dir.rglob("*.md"):
        markdown_path.write_text(
            markdown_path.read_text(encoding="utf-8").replace(
                f"{source_study_id}/assets/", f"{STUDY_ID}/assets/{source_study_id}/"
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
        if name not in {"consent", "intro"}
    }
    sequence = [
        item for item in rewrite_asset_paths(source["sequence"]["components"], source_study_id, section)
        if item != "consent" and item != "intro"
    ]
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
    consent_markdown = """
<style>
.study-shell {
    max-width: 1120px;
    margin: 0 auto;
    padding: 8px 20px 36px;
    color: #1f2937;
}

.study-hero {
    padding: 28px 30px;
    border-radius: 24px;
    background: linear-gradient(135deg, #f7fbff 0%, #eef4ff 100%);
    border: 1px solid #dce7f5;
    box-shadow: 0 16px 36px rgba(15, 23, 42, 0.06);
}

.study-kicker {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #3461d9;
}

.study-title {
    margin: 10px 0 10px;
    font-size: 34px;
    line-height: 1.1;
    font-weight: 750;
    color: #10213a;
}

.study-lead {
    margin: 0;
    font-size: 17px;
    line-height: 1.8;
    color: #354255;
    max-width: 72ch;
}

.study-stack {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 12px;
    margin-top: 22px;
}

.study-card {
    padding: 14px 16px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid #dce7f5;
}

.study-card h3 {
    margin: 0 0 8px;
    font-size: 18px;
    line-height: 1.3;
    color: #10213a;
}

.study-card p,
.study-card li {
    margin: 0;
    font-size: 15px;
    line-height: 1.75;
    color: #445469;
}

.study-card ul {
    margin: 0;
    padding-left: 18px;
}

.study-note {
    margin-top: 18px;
    padding: 16px 18px;
    border-radius: 16px;
    background: #f5f8fc;
    border-left: 4px solid #3461d9;
    font-size: 15px;
    line-height: 1.7;
    color: #344457;
}
</style>

<div class="study-shell">
  <div class="study-hero">
    <div class="study-kicker">Consent</div>
    <div class="study-title">Before we begin</div>
    <p class="study-lead">
      Please read the information below carefully. If you continue with the study, this will count as your informed consent.
    </p>

<div class="study-stack">
      <div class="study-card">
        <h3>Purpose</h3>
        <p>
          The purpose of this study is to learn how people understand graph drawings and recognize graph properties in visualizations.
        </p>
      </div>
      <div class="study-card">
        <h3>What you will do</h3>
        <p>
          You will look at graph drawings, answer a short yes-or-no question for each one, and then rate how confident you are.
        </p>
      </div>
      <div class="study-card">
        <h3>Duration</h3>
        <p>
          The study takes about 10 to 15 minutes.
        </p>
      </div>
      <div class="study-card">
        <h3>Data collected</h3>
        <ul>
          <li>Your answers</li>
          <li>Your response times</li>
        </ul>
      </div>
    </div>

<div class="study-note">
      Participation is voluntary. You may stop at any time. Continuing to the next page means that you agree to take part in the study.
    </div>
  </div>
</div>
"""
    (ASSETS_DIR / "consent.md").write_text(consent_markdown, encoding="utf-8")

    intro_markdown = f"""
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

.study-example {{
    margin-top: 18px;
    padding: 14px 16px;
    border-radius: 20px;
    background: white;
    border: 1px solid #dce7f5;
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

.study-example img {{
    width: 100%;
    max-height: 240px;
    object-fit: contain;
    display: block;
    margin-top: 16px;
}}
</style>

<div class="study-shell">
  <div class="study-hero">
    <div class="study-kicker">Introduction</div>
    <div class="study-title">What exactly are graphs?</div>
    <p class="study-lead">
      To understand what type of graphs we are talking about in this study, we will start with an example: Lets imagine we want to model a social network. We would want the network to represent people and friendships between people. For that we can depict people in a space and link them with lines if they are friends.
    </p>

<div class="study-example">
      <h3 style="margin:0;font-size:18px;color:#10213a;">Our social network example</h3>
      <img src="{STUDY_ID}/assets/socialNetwork/1.png" alt="Social network graph">
      <p style="margin:12px 0 0;font-size:15px;line-height:1.75;color:#445469;">
        Here we can see a group of seven people visualized on a white plane and positioned randomly. Their friendships are represented by lines connecting them. It's easy to see that Lara and Ben are friends as well as that Ida and Mia are not. But what about other properties of this group of people? Is there a person that connects these people, that without them, the group would be split into two? This is a much harder question to answer by just looking at the graph. The freedom to position the people in the space is a challenge, as different arrangements can make certain properties of the group easier or harder to recognize.
      </p>
    </div>

<div class="study-example">
      <h3 style="margin:0;font-size:18px;color:#10213a;">The same group arranged differently</h3>
      <img src="{STUDY_ID}/assets/socialNetwork/2.png" alt="Organized social network graph">
      <p style="margin:12px 0 0;font-size:15px;line-height:1.75;color:#445469;">
        By arranging the same people differently, it can become easier to answer questions about certain properties of the group. For example, it is now easier to see that without Zoë, the group would be split into two. So there is a person that connects the two groups of friends.
      </p>
    </div>
<div class="study-example">
      <h3 style="margin:0;font-size:18px;color:#10213a;">The graphs in computer science</h3>
      <img src="{STUDY_ID}/assets/socialNetwork/3.png" alt="Abstract social network graph">
      <p style="margin:12px 0 0;font-size:15px;line-height:1.75;color:#445469;">
        If we now strip away the visual details such as the names of the people, and we depict a person as a node, we can see that the graph is now an abstract representation of the social network. This is how graphs are used in computer science: they are abstract representations of relationships between objects. The objects are represented by nodes and the relationships by links.
      </p>
    </div>
<div class="study-example">
      <h3 style="margin:0;font-size:18px;color:#10213a;">The study</h3>
      <p style="margin:12px 0 0;font-size:15px;line-height:1.75;color:#445469;">
        In this study we will be focusing on three properties of graphs: bipartiteness, Hamiltonian cycles, and cut vertices. We will introduce and explain each property and then you will be asked to answer questions about graphs that either have or do not have the property. 
      </p>
    </div>
<div class="study-note">
        Let's start with the first property! Click on "Next" to continue.
    </div>

  </div>
</div>
"""
    (ASSETS_DIR / "intro.md").write_text(intro_markdown, encoding="utf-8")

    (ASSETS_DIR / "outro.md").write_text(
        """# Thank you!

Thank you for completing the study. Your contribution is greatly appreciated.
""",
        encoding="utf-8",
    )


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    target_social = ASSETS_DIR / "socialNetwork"
    if target_social.exists():
        rmtree(target_social)

    copytree(SOCIAL_NETWORK_DIR, target_social)
    write_intro_and_outro()

    components = {
        "consent": {
            "type": "markdown",
            "path": f"{STUDY_ID}/assets/consent.md",
            "response": [],
            "nextButtonText": "I agree",
            "nextButtonLocation": "belowStimulus",
        },
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
                "consent",
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
