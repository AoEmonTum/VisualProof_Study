
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
    <div class="study-kicker">Hamiltonian cycle</div>
    <div class="study-title">The Hamiltonian property</div>
    <p class="study-lead">Think of planning a tour through several cities. You want to start in one city, visit every other city exactly once, and finally return to where you started. The connections between the cities represent the links of a network, and the cities represent its nodes.</p>
    <div class="study-card" style="margin-top: 24px;">
      <h3>Cycles and Hamiltonian cycles</h3>
      <p>A cycle is a path through nodes (in our example the cities) that starts and ends at the same node. If we continue with our example, a cycle that visits every city in the network exactly once is called a Hamiltonian cycle. A network is called Hamiltonian if it contains a Hamiltonian cycle.</p>
    </div>
    <div class="study-figure">
      <h3 style="margin: 0; font-size: 18px; color: #10213a;">A Hamiltonian cycle</h3>
      <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">The highlighted cycle starts at a node, visits every other node exactly once, and finally returns to the starting node. Therefore, the network contains a Hamiltonian cycle.</p>
      <img src="VisualProofsForGraphPropertiesStudy_prolific/assets/hamiltonian-cycle-component/graphs/tutorial_graph_001_proof_property.png" alt="Example of a Hamiltonian cycle">
    </div>
    <div class="study-figure">
      <h3 style="margin: 0; font-size: 18px; color: #10213a;">A more difficult example</h3>
      <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">At first glance, this network may appear to contain a Hamiltonian cycle. However, the two highlighted nodes cannot both be included in the same cycle without visiting another node more than once. Therefore, the network does not contain a Hamiltonian cycle.</p>
      <img src="VisualProofsForGraphPropertiesStudy_prolific/assets/hamiltonian-cycle-component/graphs/tutorial_graph_001_proof_noproperty.png" alt="Example of a network without a Hamiltonian cycle">
    </div>
    <div class="study-figure">
          <h3 style="margin: 0; font-size: 18px; color: #10213a;">A network without a Hamiltonian cycle</h3>
          <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">In this network, it is impossible to find a cycle that visits every node exactly once and returns to the starting node. Therefore, this network does not contain a Hamiltonian cycle. (Try to find one yourself :))</p>
          <img src="VisualProofsForGraphPropertiesStudy_prolific/assets/hamiltonian-cycle-component/graphs/tutorial_graph_001_noproof_noproperty.png" alt="Example of a network without a Hamiltonian cycle">
        </div>
  </div>
</div>
