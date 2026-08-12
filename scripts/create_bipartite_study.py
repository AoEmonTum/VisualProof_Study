#!/usr/bin/env python3
"""Create the counterbalanced bipartite study with a custom introduction."""

from pathlib import Path

from create_graph_property_study import StudySettings, create_study


STUDY_ID = "bipartite-study-5"


def write_intro(assets_dir: Path, study_id: str, tutorial: dict[str, dict]) -> None:
    """Write the bipartite-specific section introduction."""
    img = tutorial["graph_001"]["images"]

    markdown = f"""
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

.study-grid {{
    display: grid;
    gap: 18px;
    margin-top: 22px;
}}

.study-card {{
    padding: 18px 20px;
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

.study-figure {{
    margin-top: 22px;
    padding: 18px 20px;
    border-radius: 20px;
    background: white;
    border: 1px solid #dce7f5;
}}

.study-figure img {{
    width: 100%;
    max-height: 280px;
    object-fit: contain;
    display: block;
    margin-top: 16px;
}}
</style>

<div class="study-shell">
  <div class="study-hero">
    <div class="study-kicker">Bipartite</div>
    <div class="study-title">The bipartite property</div>
    <p class="study-lead">
      A graph is bipartite if its nodes can be split into two groups so that every link goes from one group to the other and no links exist within the same group.
    </p>
<div class="study-grid">
      <div class="study-card">
        <h3>What makes a graph bipartite?</h3>
        <ul>
          <li>The nodes can be divided into two groups, without any links within a group.</li>
          <li>You can color the nodes in such a way that adjacent nodes always have different colors.</li>
          <li>All loops in the graph have an even number of nodes.</li>
        </ul>
      </div>
    </div>

<div class="study-figure">
      <h3 style="margin: 0; font-size: 18px; color: #10213a;">Dividing into two groups</h3>
      <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">
        Every link goes from one side to the other. There is no link that connects two nodes on the same side.
      </p>
<img src="{study_id}/assets/graphs/{img["proof_property"]}" alt="Example of a bipartite graph">
    </div>

<div class="study-figure">
      <h3 style="margin: 0; font-size: 18px; color: #10213a;">Two-coloring</h3>
      <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">
        The graph can be colored with two colors so that no two linked nodes have the same color.
      </p>
<img src="{study_id}/assets/graphs/{img["noproof_property"]}" alt="Example of a graph that is not bipartite">
    </div>

<div class="study-figure">
      <h3 style="margin: 0; font-size: 18px; color: #10213a;">Odd loop</h3>
      <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">
        The highlighted nodes and links form a loop with an odd number of nodes. Since bipartite graphs contain only even loops, this graph is not bipartite.
      </p>
<img src="{study_id}/assets/graphs/{img["noproof_noproperty"]}" alt="Example of an odd loop">
    </div>
  </div>
</div>
"""

    (assets_dir / "property_explanation.md").write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    create_study(
        Path(__file__),
        StudySettings(
            study_id=STUDY_ID,
            stimulus_folder="bipartite",
            title="Visual Proof Bipartite Graphs",
            property_name="bipartite",
            property_definition="A bipartite graph is a graph whose nodes can be split into two groups so that every link goes from one group to the other.",
            verification_prompt="Based on this visualization, is this graph bipartite?",
            response_prefix="canVerifyBipartite",
            yes_label="Yes",
            no_label="No",
            sidebar_explanation="A bipartite graph is a graph whose nodes can be split into two groups so that every link goes from one group to the other.",
            write_intro=write_intro,
        ),
    )
