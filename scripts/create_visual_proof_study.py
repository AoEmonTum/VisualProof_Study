#!/usr/bin/env python3
"""Create the counterbalanced cut-vertex study with a custom introduction."""

from pathlib import Path

from create_graph_property_study import StudySettings, create_study


STUDY_ID = "visual-proof-cut-vertex"


def write_intro(assets_dir: Path, study_id: str, tutorial: dict[str, dict]) -> None:
    """Write the cut-vertex-specific introduction; all other parts are shared."""
    img = tutorial["graph_001"]["images"]

    markdown = f"""
<div style="max-width:1100px; margin:40px auto;">

<h1 style="margin-bottom:12px;">
Cut Vertices
</h1>

<p style="font-size:18px; line-height:1.7; color:#555; margin-bottom:28px;">
A <strong>cut vertex</strong> is a vertex whose removal disconnects the graph
into two or more connected components.
</p>

<div style="
background:#f8fafc;
border:1px solid #e5e7eb;
border-radius:16px;
padding:24px;
margin-bottom:36px;
">

<h2 style="margin-top:0;">How to recognize a cut vertex</h2>

<ul style="font-size:17px; line-height:1.9; padding-left:22px; margin-bottom:0;">
<li>If removing a vertex disconnects the graph into multiple connected components, then that vertex is a <strong>cut vertex</strong>.</li>
</ul>

</div>

<div style="
background:white;
border:1px solid #e5e7eb;
border-radius:16px;
padding:24px;
margin-bottom:28px;
">

<div style="display:grid;grid-template-columns:42% 58%;gap:32px;align-items:center;">

<div>

<h2 style="margin-top:0;">Graph with a cut vertex</h2>

<p style="line-height:1.8;">
The highlighted vertex is a
<strong style="color:#d62728;">cut vertex</strong>.
Removing this vertex disconnects the graph.
</p>

</div>

<div align="center">

<img
src="{study_id}/assets/graphs/{img["proof_property"]}"
style="width:100%;max-height:300px;object-fit:contain;">

</div>

</div>

</div>

<div style="
background:white;
border:1px solid #e5e7eb;
border-radius:16px;
padding:24px;
">

<div style="display:grid;grid-template-columns:42% 58%;gap:32px;align-items:center;">

<div>

<h2 style="margin-top:0;">After removing the cut vertex</h2>

<p style="line-height:1.8;">
The graph is now disconnected into multiple connected components.
Therefore, the removed <strong>vertex</strong> was a cut vertex.
</p>

</div>

<div align="center">

<img
src="{study_id}/assets/graphs/{img["proof_noproperty"]}"
style="width:100%;max-height:300px;object-fit:contain;">

</div>

</div>

</div>

<div style="
margin-top:36px;
padding:18px;
background:#ecfdf5;
border:1px solid #10b981;
border-radius:12px;
text-align:center;
font-size:18px;
">

You will now complete a short practice sequence before the main study.

</div>

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
