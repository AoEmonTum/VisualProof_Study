#!/usr/bin/env python3
"""Generate bipartite graph SVGs from the graph_tests Rome GraphML archive.

This is adapted from graph_tests/visualize_bipartite.py and the existing generators.
"""

from __future__ import annotations

import os
import tarfile
import tempfile
from pathlib import Path

os.environ.setdefault("XDG_CACHE_HOME", str(Path(tempfile.gettempdir()) / "visual-proof-cache"))
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "visual-proof-matplotlib"))

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_TAR_PATH = WORKSPACE_ROOT / "graph_tests" / "rome_graphml.tar.gz"
MAX_NODES_TO_SEARCH = 100


def find_bipartition(graph):
    color = {}
    A = set()
    B = set()

    for start in graph.nodes():
        if start in color:
            continue
        color[start] = 0
        stack = [start]
        while stack:
            u = stack.pop()
            for v in graph.neighbors(u):
                if v not in color:
                    color[v] = 1 - color[u]
                    stack.append(v)
                elif color[v] == color[u]:
                    return None

    for n, c in color.items():
        (A if c == 0 else B).add(n)

    return list(A), list(B)


def load_bipartite_graphs(count, tar_path=DEFAULT_TAR_PATH):
    graphs = []

    with tarfile.open(tar_path, "r:gz") as tar:
        members = sorted(
            (member for member in tar.getmembers() if member.name.endswith(".graphml")),
            key=lambda member: member.name,
        )

        for member in members:
            if len(graphs) >= count:
                break

            file_obj = tar.extractfile(member)
            if file_obj is None:
                continue

            try:
                graph = nx.read_graphml(file_obj)
            except Exception:
                continue

            if graph.is_directed():
                graph = nx.Graph(graph)
            graph.remove_edges_from(nx.selfloop_edges(graph))

            if graph.number_of_nodes() > MAX_NODES_TO_SEARCH:
                continue

            part = find_bipartition(graph)
            if part is None:
                continue
            A, B = part
            if len(A) == 0 or len(B) == 0:
                continue

            graphs.append({"name": os.path.basename(member.name), "graph": graph, "A": A, "B": B})

    if len(graphs) < count:
        raise RuntimeError(f"Only found {len(graphs)} bipartite graphs; needed {count}.")

    return graphs


def draw_bipartite_graph_line(graph, A, B, output_path):
    # line layout: A on left, B on right
    def ys_for(n, span=4.0):
        if n == 1:
            return [0.0]
        step = span / (n - 1)
        start = -span / 2
        return [start + i * step for i in range(n)]

    ysA = ys_for(len(A))
    ysB = ys_for(len(B))
    pos_line = {}
    for i, node in enumerate(sorted(A, key=str)):
        pos_line[node] = (-1.0, ysA[i])
    for i, node in enumerate(sorted(B, key=str)):
        pos_line[node] = (1.0, ysB[i])

    fig, ax = plt.subplots(figsize=(7, 7))
    colorA = '#7f9fb3'
    colorB = '#bfa5a5'
    nx.draw_networkx_nodes(graph, pos_line, nodelist=A, node_color=colorA, node_size=160, ax=ax)
    nx.draw_networkx_nodes(graph, pos_line, nodelist=B, node_color=colorB, node_size=160, ax=ax)
    nx.draw_networkx_edges(graph, pos_line, edge_color='#64748b', alpha=0.7, ax=ax)
    ax.axis('off')
    fig.tight_layout(pad=0.1)
    fig.savefig(output_path, format='svg', bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)


def draw_bipartite_graph_force(graph, A, B, output_path, seed=42):
    try:
        pos = nx.spring_layout(graph, seed=seed)
    except Exception:
        pos = nx.random_layout(graph)

    fig, ax = plt.subplots(figsize=(7, 7))
    colorA = '#7f9fb3'
    colorB = '#bfa5a5'
    nx.draw_networkx_nodes(graph, pos, nodelist=A, node_color=colorA, node_size=160, ax=ax)
    nx.draw_networkx_nodes(graph, pos, nodelist=B, node_color=colorB, node_size=160, ax=ax)
    nx.draw_networkx_edges(graph, pos, edge_color='#64748b', alpha=0.7, ax=ax)
    ax.axis('off')
    fig.tight_layout(pad=0.1)
    fig.savefig(output_path, format='svg', bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)


def save_bipartite_svgs(graph, A, B, output_dir, index):
    line_filename = f"bipartite_{index:02d}_line.svg"
    force_filename = f"bipartite_{index:02d}_force.svg"

    draw_bipartite_graph_line(graph, A, B, output_dir / line_filename)
    draw_bipartite_graph_force(graph, A, B, output_dir / force_filename, seed=42 + index)

    return line_filename, force_filename


def generate_bipartite_svgs(output_dir, count=10, tar_path=DEFAULT_TAR_PATH):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    graphs = load_bipartite_graphs(count=count, tar_path=Path(tar_path))
    metadata = []

    for index, item in enumerate(graphs, start=1):
        line_filename, force_filename = save_bipartite_svgs(item['graph'], item['A'], item['B'], output_dir, index)
        metadata.append({
            'index': index,
            'line_filename': line_filename,
            'force_filename': force_filename,
            'source': item['name'],
            'A_size': len(item['A']),
            'B_size': len(item['B']),
        })

    return metadata


if __name__ == '__main__':
    target = SCRIPT_DIR.parent / 'public' / 'visual-proof-bipartite' / 'assets' / 'graphs'
    generated = generate_bipartite_svgs(target, count=10)
    for item in generated:
        print(f"{item['index']:02d}: {item['source']} A={item['A_size']} B={item['B_size']}")
