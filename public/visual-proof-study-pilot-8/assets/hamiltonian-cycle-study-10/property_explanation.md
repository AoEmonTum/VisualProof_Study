
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
    <div class="study-kicker">Hamiltonian Cycle</div>
    <div class="study-title">The Hamiltonian Cycle Property</div>
    <p class="study-lead">
      A graph has a Hamiltonian cycle if there exists a cycle that visits every node exactly once and then returns to the starting node.
      If a node is skipped, repeated, or the same link is used twice, the graph does not contain a Hamiltonian cycle.
    </p>

<div class="study-grid">
      <div class="study-card">
        <h3>What makes it Hamiltonian?</h3>
        <ul>
          <li>Every node appears exactly once in the cycle.</li>
          <li>The cycle closes by returning to the starting node.</li>
          <li>A link is used at most once.</li>
        </ul>
      </div>
    <div class="study-card">
        <h3>What makes it not Hamiltonian?</h3>
        <ul>
          <li>A node is left out of the cycle.</li>
          <li>A node is visited more than once.</li>
          <li>A link is used more than once.</li>
        </ul>
      </div>
    </div>

<div class="study-note">
      The key idea is simple: follow one closed path that touches every node once and only once and use each link at most once.
    </div>

<div class="study-figure">
      <h3 style="margin: 0; font-size: 18px; color: #10213a;">A Hamiltonian cycle</h3>
      <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">
        The highlighted cycle visits every node exactly once.
      </p>
<img src="visual-proof-study-pilot-8/assets/hamiltonian-cycle-study-10/graphs/tutorial_graph_001_proof_property.png" alt="Example of a Hamiltonian cycle">
    </div>

<div class="study-figure">
      <h3 style="margin: 0; font-size: 18px; color: #10213a;">A known example for a graph without a Hamiltonian cycle</h3>
      <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">
        In this graph it is impossible to find a cycle that visits every node exactly once and returns to the starting node. So this graph does not contain a Hamiltonian cycle. (Try to find one yourself :)
      </p>
<img src="visual-proof-study-pilot-8/assets/hamiltonian-cycle-study-10/graphs/tutorial_graph_001_noproof_noproperty.png" alt="Example of a cycle that skips a node">
    </div>

<div class="study-figure">
      <h3 style="margin: 0; font-size: 18px; color: #10213a;">Looks like a Hamiltonian cycle but does not contain one</h3>
      <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">
        Reusing a link means the cycle is not Hamiltonian. One node has only one link so to reach it you have to use it and then there is no way to leave it without using the same link twice. So this graph does not contain a Hamiltonian cycle.
      </p>
<img src="visual-proof-study-pilot-8/assets/hamiltonian-cycle-study-10/graphs/tutorial_graph_001_proof_noproperty.png" alt="Example of a non-Hamiltonian cycle">
    </div>
  </div>
</div>
