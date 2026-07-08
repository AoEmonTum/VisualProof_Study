#!/usr/bin/env python3
"""Generate Hamiltonian-cycle graph SVGs from the graph_tests Rome GraphML archive.

This is adapted from graph_tests/visualize_hamiltonian_circles.py.
"""

from __future__ import annotations

import math
import os
import tarfile
import tempfile
import time
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
MAX_NODES_TO_SEARCH = 40
TIMEOUT_PER_GRAPH = 2.0


def find_hamiltonian_cycle(graph, timeout=TIMEOUT_PER_GRAPH):
    if not nx.is_connected(graph):
        return None
    if any(degree < 2 for _, degree in graph.degree()):
        return None

    node_count = graph.number_of_nodes()
    start_nodes = sorted(graph.nodes(), key=lambda node: -graph.degree(node))
    start_time = time.time()

    def search(path, visited):
        if time.time() - start_time > timeout:
            return None

        current = path[-1]
        if len(path) == node_count:
            return path if path[0] in graph[current] else None

        neighbors = sorted(graph[current], key=lambda node: -graph.degree(node))
        for neighbor in neighbors:
            if neighbor in visited:
                continue
            visited.add(neighbor)
            path.append(neighbor)
            result = search(path, visited)
            if result is not None:
                return result
            path.pop()
            visited.remove(neighbor)

        return None

    for start in start_nodes:
        result = search([start], {start})
        if result is not None:
            return result
        if time.time() - start_time > timeout:
            break

    return None


def cycle_edge_set(cycle):
    return {
        frozenset({cycle[index], cycle[(index + 1) % len(cycle)]})
        for index in range(len(cycle))
    }


def load_graph(graphml_file):
    graph = nx.read_graphml(graphml_file)
    if graph.is_directed():
        graph = nx.Graph(graph)
    graph.remove_edges_from(nx.selfloop_edges(graph))
    return graph


def load_hamiltonian_graphs(count, tar_path=DEFAULT_TAR_PATH):
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
                graph = load_graph(file_obj)
            except Exception:
                continue

            if graph.number_of_nodes() > MAX_NODES_TO_SEARCH:
                continue

            cycle = find_hamiltonian_cycle(graph)
            if cycle is None:
                continue

            graphs.append(
                {
                    "name": os.path.basename(member.name),
                    "graph": graph,
                    "cycle": cycle,
                }
            )

    if len(graphs) < count:
        raise RuntimeError(f"Only found {len(graphs)} Hamiltonian graphs; needed {count}.")

    return graphs


def draw_hamiltonian_graph(graph, cycle, pos, output_path, circular=False):
    cycle_edges = cycle_edge_set(cycle)
    non_cycle_edges = [edge for edge in graph.edges() if frozenset(edge) not in cycle_edges]
    highlighted_edges = [edge for edge in graph.edges() if frozenset(edge) in cycle_edges]

    fig, ax = plt.subplots(1, 1, figsize=(7, 7))

    nx.draw_networkx_nodes(
        graph,
        pos,
        node_size=160,
        node_color="#d9d9d9",
        edgecolors="#111827",
        linewidths=0.4,
        ax=ax,
    )
    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=non_cycle_edges,
        edge_color="#64748b",
        alpha=0.55,
        width=1.0,
        ax=ax,
    )
    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=highlighted_edges,
        edge_color="#dc2626",
        width=2.0,
        ax=ax,
    )

    ax.set_aspect("equal", adjustable="box")
    if circular:
        ax.set_xlim(-1.15, 1.15)
        ax.set_ylim(-1.15, 1.15)
    ax.axis("off")
    fig.tight_layout(pad=0.1)
    fig.savefig(output_path, format="svg", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def cycle_layout(cycle):
    node_count = len(cycle)
    return {
        node: (
            math.cos(2 * math.pi * index / node_count),
            math.sin(2 * math.pi * index / node_count),
        )
        for index, node in enumerate(cycle)
    }


def save_hamiltonian_svgs(graph, cycle, output_dir, index):
    force_filename = f"hamiltonian_{index:02d}_force.svg"
    cyclic_filename = f"hamiltonian_{index:02d}_cyclic.svg"

    force_pos = nx.spring_layout(graph, seed=42 + index)
    cyclic_pos = cycle_layout(cycle)

    draw_hamiltonian_graph(
        graph,
        cycle,
        force_pos,
        output_dir / force_filename,
    )
    draw_hamiltonian_graph(
        graph,
        cycle,
        cyclic_pos,
        output_dir / cyclic_filename,
        circular=True,
    )

    return force_filename, cyclic_filename


def generate_hamiltonian_cycle_svgs(output_dir, count=10, tar_path=DEFAULT_TAR_PATH):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    graphs = load_hamiltonian_graphs(count=count, tar_path=Path(tar_path))
    metadata = []

    for index, item in enumerate(graphs, start=1):
        force_filename, cyclic_filename = save_hamiltonian_svgs(
            item["graph"],
            item["cycle"],
            output_dir,
            index,
        )
        metadata.append(
            {
                "index": index,
                "force_filename": force_filename,
                "cyclic_filename": cyclic_filename,
                "source": item["name"],
                "cycle": [str(node) for node in item["cycle"]],
            }
        )

    return metadata


if __name__ == "__main__":
    target = SCRIPT_DIR.parent / "public" / "visual-proof-hamiltonian-cycle" / "assets" / "graphs"
    generated = generate_hamiltonian_cycle_svgs(target, count=10)
    for item in generated:
        print(f"{item['index']:02d}: {item['source']} cycle_length={len(item['cycle'])}")
