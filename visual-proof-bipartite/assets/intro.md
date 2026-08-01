
<b style="font-size: 22px; font-weight: 650;">The bipartite property</b>

<style>
.example-title {
    margin-top: 20px;
    padding: 3px 6px;
    font-size: 20px;
    font-weight: 650;
}

.example-text {
    font-size: 16px;
    line-height: 1.9;
}

.code-line {
    display: inline;
    box-decoration-break: clone;
    -webkit-box-decoration-break: clone;
    
    padding: 3px 6px;
    line-height: 1.9;
    font-size: 16px;
}
</style>

<div style="max-width:1150px; margin-left: 20px; line-height:1.6;">

<p style="font-size:18px;">
A <b>bipartite graph</b> is a graph whose vertices can be divided into two disjoint groups such that no edge connects two vertices belonging to the same group.
</p>

<p style="font-size:17px;">
You can recognize a bipartite graph in several equivalent ways:
</p>

<div class="code-line">
- The vertices can be divided into <b>two disjoint groups</b>.<br>
- The graph can be colored using only <b>two colors</b> such that no two adjacent vertices have the same color.<br>
- Every cycle has <b>even length</b>. Therefore, if a graph contains an <b>odd cycle</b>, it is <b>not bipartite</b>.
</div>

<hr style="margin:35px 0;">

<div style="display:grid;grid-template-columns:42% 58%;gap:35px;align-items:center;margin-bottom:40px;">

<div>

<h3 class="example-title">
Partition into two groups
</h3>

<div class="example-text">
<div class="code-line">
This graph can be divided into <b>two disjoint groups</b> of vertices.<br>
Every edge connects a vertex from one group with a vertex from the other group.
</div>
</div>

</div>

<div align="center">
<img src="visual-proof-bipartite/assets/graphs/tutorial_graph_001_proof_property.png"
style="width:100%;max-height:290px;object-fit:contain;">
</div>

</div>

<hr>

<div style="display:grid;grid-template-columns:42% 58%;gap:35px;align-items:center;margin:40px 0">

<div>

<h3 class="example-title">
Two-coloring
</h3>

<div class="example-text">
<div class="code-line">
The graph can be colored using only <b>two colors</b>.<br>
No edge connects two vertices of the same color.
</div>
</div>

</div>

<div align="center">
<img src="visual-proof-bipartite/assets/graphs/tutorial_graph_001_noproof_property.png"
style="width:100%;max-height:290px;object-fit:contain;">
</div>

</div>

<hr>

<div style="display:grid;grid-template-columns:42% 58%;gap:35px;align-items:center;margin:40px 0;">

<div>

<h3 class="example-title">
Odd cycle
</h3>

<div class="example-text">
<div class="code-line">
This graph contains an <b>odd cycle</b>.<br>
Since bipartite graphs contain only cycles of even length, the graph is <b>not bipartite</b>.
</div>
</div>

</div>

<div align="center">
<img src="visual-proof-bipartite/assets/graphs/tutorial_graph_001_noproof_noproperty.png"
style="width:100%;max-height:290px;object-fit:contain;">
</div>

</div>
<hr style="margin: 0 0 40px 0;">
</div>
