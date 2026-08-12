
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

.study-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 18px;
    margin-top: 22px;
}

.study-card {
    padding: 18px 20px;
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

.study-figure {
    margin-top: 22px;
    padding: 18px 20px;
    border-radius: 20px;
    background: white;
    border: 1px solid #dce7f5;
}

.study-figure img {
    width: 100%;
    max-height: 280px;
    object-fit: contain;
    display: block;
    margin-top: 16px;
}
</style>

<div class="study-shell">
  <div class="study-hero">
    <div class="study-kicker">Cut vertex</div>
    <div class="study-title">The cut vertex property</div>
    <p class="study-lead">
      A cut vertex is a node whose removal splits the graph into two or more connected components. A connected component is a group of nodes that are all connected to each other by paths of links.
    </p>

 <div class="study-grid">
      <div class="study-card">
        <h3>What is a connected component?</h3>
        <p>
          It is a group of nodes that are all connected to each other by paths of links.
        </p>
      </div>
      <div class="study-card">
        <h3>What makes a node a cut vertex?</h3>
        <p>
          If removing that node makes the graph split into separate parts, the node is a cut vertex.
        </p>
      </div>
    </div>

 <div class="study-note">
      You can think of a cut vertex as a train station where all routes between two regions pass through. If the station closes, passengers can no longer travel between the regions.
    </div>

<div class="study-figure">
      <h3 style="margin: 0; font-size: 18px; color: #10213a;">A graph with a cut vertex.</h3>
      <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">
        The highlighted node connects two parts of the graph that would otherwise be separate.
      </p>
<img src="visual-proof-study-pilot-8/assets/cut-vertex-study-10/graphs/tutorial_graph_001_proof_property.png" alt="Example of a graph with a cut vertex">
    </div>

<div class="study-figure">
      <h3 style="margin: 0; font-size: 18px; color: #10213a;">After removing the highlighted node</h3>
      <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">
        The graph now has separate connected components. The graph is no longer connected, so the removed node was a cut vertex.
      </p>
<img src="visual-proof-study-pilot-8/assets/cut-vertex-study-10/graphs/tutorial_graph_001_proof_noproperty.png" alt="Graph after removing the splitting node">
    </div>
<div class="study-figure">
      <h3 style="margin: 0; font-size: 18px; color: #10213a;">Removing some other node</h3>
      <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">
        The graph now still is connected. So this node was not a cut vertex.
      </p>
<img src="visual-proof-study-pilot-8/assets/cut-vertex-study-10/graphs/tutorial_graph_001_noproof_noproperty.png" alt="Graph after removing a random node">
    </div>
  </div>
