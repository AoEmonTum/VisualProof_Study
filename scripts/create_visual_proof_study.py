#!/usr/bin/env python3
"""Create the counterbalanced cut-vertex study with a custom introduction."""

from pathlib import Path

from create_graph_property_study import StudySettings, create_study


STUDY_ID = "cut-vertex-study"


def write_intro(assets_dir: Path, study_id: str, tutorial: dict[str, dict]) -> None:
    """Write the cut-vertex-specific introduction; all other parts are shared."""
    img = tutorial["graph_001"]["images"]

    markdown = f"""
<b style="font-size: 22px; font-weight: 650;">Cut vertex</b>

<style>
.intro-content h3 {{ margin-top: 20px; font-size: 20px; font-weight: 650; }}
</style>

<div class="intro-content" style="max-width:1150px; margin-left: 20px; line-height:1.6;">

<p style="font-size:18px;">
A <b>cut vertex</b> is a vertex whose removal disconnects the graph into two or more connected components.
</p>

<p style="font-size:17px;">
You can recognize a cut vertex by the following property:
</p>

<div style="font-size:17px;margin-bottom:35px;line-height:1.9;">
- If removing a vertex disconnects the graph into multiple connected components, then that vertex is a <b>cut vertex</b>.
</div>

<hr style="margin:35px 0;">

<div style="display:grid;grid-template-columns:42% 58%;gap:35px;align-items:center;margin-bottom:40px;">

<div>

<h3 style="margin-top:0;">Example for a graph with a cut vertex</h3>

<p>
The highlighted vertex is a <b style="color: #d62728;">cut vertex</b>.
</p>

</div>

<div align="center">
<img src="{study_id}/assets/graphs/{img["proof_property"]}"
style="width:100%;max-height:290px;object-fit:contain;">
</div>

</div>

<hr>

<div style="display:grid;grid-template-columns:42% 58%;gap:35px;align-items:center;margin:40px 0;">

<div>

<h3 style="margin-top:0;">The same graph with that cut vertex removed</h3>

<p>
The graph is now disconnected. Therefore the removed edge was a cut vertex
</p>

</div>

<div align="center">
<img src="{study_id}/assets/graphs/{img["proof_noproperty"]}"
style="width:100%;max-height:290px;object-fit:contain;">
</div>

</div>

<hr>

<p style="margin-top:40px;text-align:center;font-size:18px;">
You will now complete a short practice sequence before the main study.
</p>

</div>
"""
    (assets_dir / "intro.md").write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    create_study(
        Path(__file__),
        StudySettings(
            study_id=STUDY_ID,
            stimulus_folder="cut_vertex",
            title="Cut Vertex",
            property_name="cut vertex",
            property_definition="A cut vertex is a vertex whose removal disconnects the graph into separate parts.",
            verification_prompt="Based on this visualization, does this graph have a cut vertex?",
            response_prefix="canVerifyCutVertex",
            yes_label="Yes, this graph has a cut vertex",
            no_label="No, this graph does not have a cut vertex",
            sidebar_explanation="A cut vertex is a vertex whose removal disconnects the graph into separate parts.",
            write_intro=write_intro,
        ),
    )
