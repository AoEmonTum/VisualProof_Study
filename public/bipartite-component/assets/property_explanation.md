
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
    <div class="study-kicker">Bipartite</div>
    <div class="study-title">The bipartite property</div>
    <p class="study-lead">To understand what the bipartite property means, let's consider an example: Imagine a network that shows people and the movies they have watched. One group of nodes represents people, and the other group represents movies. A link connects a person to a movie if that person has watched that movie.</p>
    <div class="study-card" style="margin-top: 24px;">
      <h3>Two groups</h3>
      <p>Every node belongs to one of two groups: people or movies. Links only connect nodes from different groups. There are no links between two people or between two movies.</p>
    </div>
    <div class="study-card" style="margin-top: 24px;">
      <h3>The bipartite property</h3>
      <p>A network is called bipartite if its nodes can be divided into two groups like in our example so that every link connects a node from one group to a node from the other group.</p>
    </div>
    <div class="study-figure">
      <h3 style="margin: 0; font-size: 18px; color: #10213a;">A bipartite network</h3>
      <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">In this example, the nodes can be separated into two groups. Every link goes from one group to the other, and no two nodes within the same group are directly linked. The left side could represent people, and the right side movies.</p>
      <img src="bipartite-component/assets/graphs/tutorial_graph_001_proof_property.png" alt="Example of a bipartite network">
    </div>
    <div class="study-figure">
          <h3 style="margin: 0; font-size: 18px; color: #10213a;">Another bipartite network</h3>
          <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">This is another example of a bipartite network. The nodes are not arranged in a way that makes the two groups obvious, but if you color the nodes with two different colors, you can see the two groups. You can imagine the green nodes as the people and the blue nodes as the movies. If you watch closely no movie is linked to an other movie and no person is linked to another person</p>
          <img src="bipartite-component/assets/graphs/tutorial_graph_001_noproof_property.png" alt="Example of a bipartite network">
        </div>
    <div class="study-figure">
      <h3 style="margin: 0; font-size: 18px; color: #10213a;">A network that is not bipartite</h3>
      <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.75; color: #445469;">In this network, it is not possible to divide all nodes into two groups so that every link connects nodes from different groups. This is because there is a cycle of odd length. (As remainder: a cycle is a path that starts and ends at the same node) If there is a cycle of odd length, and you try to assign each node in that cycle to a group this will create a contradiction: The first node could be assigned to the people, the second node to the movies, the third node back to the people, the fourth node to the movies, the fifth node back to the people, and when going back to the first node you would have to assign it to the movies, which would create a contradiction as we said the first node sould be assigned to the people. </p>
      <img src="bipartite-component/assets/graphs/tutorial_graph_001_noproof_noproperty.png" alt="Example of a network that is not bipartite">
    </div>
  </div>
</div>
