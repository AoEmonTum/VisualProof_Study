#!/usr/bin/env python3
"""Create the counterbalanced Hamiltonian-cycle study with a custom introduction."""

from pathlib import Path

from create_graph_property_study import StudySettings, create_study


STUDY_ID = "visual-proof-hamiltonian-cycle"


def write_intro(assets_dir: Path, study_id: str, tutorial: dict[str, dict]) -> None:
    """Write the Hamiltonian-cycle-specific introduction; all other parts are shared."""
    img = tutorial["graph_001"]["images"]

    markdown = f"""
<div style="max-width:1100px; margin:40px auto;">

<h1 style="margin-bottom:12px;">
Hamiltonian Cycles
</h1>

<p style="font-size:18px; line-height:1.7; color:#555; margin-bottom:28px;">
A <strong>Hamiltonian cycle</strong> is a cycle that visits
<strong>every vertex exactly once</strong> before returning to the starting
vertex.
</p>

<div style="
background:#f8fafc;
border:1px solid #e5e7eb;
border-radius:16px;
padding:24px;
margin-bottom:36px;
">

<h2 style="margin-top:0;">How to recognize a Hamiltonian cycle</h2>

<ul style="font-size:17px; line-height:1.9; padding-left:22px; margin-bottom:0;">
<li>The cycle visits <strong>every vertex exactly once</strong> before returning to the starting vertex.</li>
<li>If <strong>even one vertex is missing</strong>, it is <strong>not</strong> a Hamiltonian cycle.</li>
<li>If a <strong>vertex or edge is used more than once</strong> (except for returning to the starting vertex), it is <strong>not</strong> a Hamiltonian cycle.</li>
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

<h2 style="margin-top:0;">Hamiltonian cycle</h2>

<p style="line-height:1.8;">
This graph contains a Hamiltonian cycle.
The highlighted cycle visits every vertex exactly once before returning to its starting vertex.
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
margin-bottom:28px;
">

<div style="display:grid;grid-template-columns:42% 58%;gap:32px;align-items:center;">

<div>

<h2 style="margin-top:0;">Missing a vertex</h2>

<p style="line-height:1.8;">
The highlighted cycle does <strong>not</strong> visit every vertex.
Since one vertex is missing, it is <strong>not</strong> a Hamiltonian cycle.
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
background:white;
border:1px solid #e5e7eb;
border-radius:16px;
padding:24px;
">

<div style="display:grid;grid-template-columns:42% 58%;gap:32px;align-items:center;">

<div>

<h2 style="margin-top:0;">No Hamiltonian cycle</h2>

<p style="line-height:1.8;">
This graph does <strong>not</strong> contain a Hamiltonian cycle because one edge would have to be traversed twice.
</p>

</div>

<div align="center">

<img
src="{study_id}/assets/graphs/{img["noproof_noproperty"]}"
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
            stimulus_folder="hamiltonian",
            title="Visual Proof Hamiltonian Cycle",
            property_name="Hamiltonian cycle",
            property_definition="A Hamiltonian cycle is a closed path that visits every vertex exactly once and returns to its starting vertex.",
            verification_prompt="Based on this visualization, does this graph have a Hamiltonian cycle?",
            response_prefix="canVerifyHamiltonianCycle",
            yes_label="Yes, this graph has a Hamiltonian cycle",
            no_label="No, this graph does not have a Hamiltonian cycle",
            sidebar_explanation="A Hamiltonian cycle is a cycle that visits every vertex exactly once and returns to the starting vertex.",
            write_intro=write_intro,
        ),
    )
