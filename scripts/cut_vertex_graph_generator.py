#!/usr/bin/env python3
"""Generate cut-vertex graph SVGs from the graph_tests Rome GraphML archive.

This is adapted from graph_tests/visualize_graphs.py.
"""

from __future__ import annotations

import math
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


def find_valid_cut_vertices(graph):
    original_components = nx.number_connected_components(graph)
    valid_cut_vertices = []

    for node in graph.nodes():
        temp_graph = graph.copy()
        temp_graph.remove_node(node)
        components = [len(comp) for comp in nx.connected_components(temp_graph)]

        if len(components) > original_components and all(size > 5 for size in components):
            valid_cut_vertices.append((node, components))
            break

    return valid_cut_vertices


def point_segment_distance(point, start, end):
    px, py = point
    sx, sy = start
    ex, ey = end
    dx = ex - sx
    dy = ey - sy

    if dx == 0 and dy == 0:
        return math.dist(point, start)

    t = ((px - sx) * dx + (py - sy) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    closest = (sx + t * dx, sy + t * dy)
    return math.dist(point, closest)


def orientation(a, b, c):
    return (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])


def segments_intersect(a, b, c, d):
    o1 = orientation(a, b, c)
    o2 = orientation(a, b, d)
    o3 = orientation(c, d, a)
    o4 = orientation(c, d, b)
    return o1 * o2 < 0 and o3 * o4 < 0


def largest_empty_angle(pos, cut_vertex):
    center = pos[cut_vertex]
    angles = []

    for node, point in pos.items():
        if node == cut_vertex:
            continue
        angles.append(math.atan2(point[1] - center[1], point[0] - center[0]))

    if not angles:
        return -math.pi / 2

    angles.sort()
    best_gap = -1.0
    best_angle = -math.pi / 2

    for index, angle in enumerate(angles):
        next_angle = angles[(index + 1) % len(angles)]
        if index == len(angles) - 1:
            next_angle += 2 * math.pi

        gap = next_angle - angle
        if gap > best_gap:
            best_gap = gap
            best_angle = angle + gap / 2

    return math.atan2(math.sin(best_angle), math.cos(best_angle))


def find_cut_vertex_position(graph, pos, cut_vertex):
    center = pos[cut_vertex]
    other_nodes = [node for node in graph.nodes() if node != cut_vertex]
    other_points = [pos[node] for node in other_nodes]

    width = max(point[0] for point in pos.values()) - min(point[0] for point in pos.values())
    height = max(point[1] for point in pos.values()) - min(point[1] for point in pos.values())
    scale = max(width, height, 1.0)
    node_clearance = 0.07 * scale
    edge_clearance = 0.04 * scale
    min_shift = 0.18 * scale
    max_shift = 0.75 * scale

    base_angle = largest_empty_angle(pos, cut_vertex)
    angle_offsets = [0, 15, -15, 30, -30, 45, -45, 60, -60, 90, -90, 120, -120, 150, -150, 180]
    distances = [min_shift + (max_shift - min_shift) * step / 12 for step in range(13)]
    non_cut_edges = [(u, v) for u, v in graph.edges() if cut_vertex not in (u, v)]
    cut_neighbors = list(graph.neighbors(cut_vertex))

    best_candidate = None
    best_score = float("inf")

    for offset in angle_offsets:
        angle = base_angle + math.radians(offset)
        direction = (math.cos(angle), math.sin(angle))

        for shift in distances:
            candidate = (
                center[0] + direction[0] * shift,
                center[1] + direction[1] * shift,
            )

            score = 0.0

            for point in other_points:
                distance = math.dist(candidate, point)
                if distance < node_clearance:
                    score += (node_clearance - distance) * 1000

            for u, v in non_cut_edges:
                distance = point_segment_distance(candidate, pos[u], pos[v])
                if distance < edge_clearance:
                    score += (edge_clearance - distance) * 700

            for neighbor in cut_neighbors:
                incident_segment = (candidate, pos[neighbor])

                for node in other_nodes:
                    if node == neighbor:
                        continue
                    distance = point_segment_distance(pos[node], incident_segment[0], incident_segment[1])
                    if distance < node_clearance * 0.65:
                        score += (node_clearance * 0.65 - distance) * 400

                for u, v in non_cut_edges:
                    if neighbor in (u, v):
                        continue
                    if segments_intersect(incident_segment[0], incident_segment[1], pos[u], pos[v]):
                        score += 250

            score += shift * 0.02 + abs(offset) * 0.01

            if score < best_score:
                best_score = score
                best_candidate = candidate

            if score < 1e-9:
                return candidate

    return best_candidate


def load_cut_vertex_graphs(count, tar_path=DEFAULT_TAR_PATH):
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

            valid_cut_vertices = find_valid_cut_vertices(graph)
            if len(valid_cut_vertices) != 1:
                continue

            cut_vertex, component_sizes = valid_cut_vertices[0]
            graphs.append(
                {
                    "name": os.path.basename(member.name),
                    "graph": graph,
                    "cut_vertex": cut_vertex,
                    "component_sizes": component_sizes,
                }
            )

    if len(graphs) < count:
        raise RuntimeError(f"Only found {len(graphs)} valid cut-vertex graphs; needed {count}.")

    return graphs


def save_cut_vertex_svg(graph, cut_vertex, output_path, seed=42):
    pos = nx.spring_layout(
        graph,
        pos={cut_vertex: (0.0, 0.0)},
        fixed=[cut_vertex],
        seed=seed,
        k=0.5,
        iterations=1000,
    )
    pos[cut_vertex] = find_cut_vertex_position(graph, pos, cut_vertex)

    graph_without_cut = graph.copy()
    graph_without_cut.remove_node(cut_vertex)
    components = list(nx.connected_components(graph_without_cut))
    component_colors = ["#d9d9d9", "#d9d9d9", "#d9d9d9", "#d9d9d9", "#d9d9d9"]

    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw_networkx_edges(graph, pos, edge_color="#64748b", width=1.0, alpha=0.75, ax=ax)

    for index, component in enumerate(components):
        nx.draw_networkx_nodes(
            graph,
            pos,
            nodelist=list(component),
            node_color=component_colors[index % len(component_colors)],
            node_size=220,
            edgecolors="#111827",
            linewidths=0.5,
            ax=ax,
        )

    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=[cut_vertex],
        node_color="#dc2626",
        node_size=260,
        edgecolors="#111827",
        linewidths=1.0,
        ax=ax,
    )

    ax.axis("off")
    fig.tight_layout(pad=0.1)
    fig.savefig(output_path, format="svg", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def generate_cut_vertex_svgs(output_dir, count=10, tar_path=DEFAULT_TAR_PATH):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    graphs = load_cut_vertex_graphs(count=count, tar_path=Path(tar_path))
    metadata = []

    for index, item in enumerate(graphs, start=1):
        filename = f"cut_vertex_{index:02d}.svg"
        output_path = output_dir / filename
        save_cut_vertex_svg(item["graph"], item["cut_vertex"], output_path, seed=42 + index)
        metadata.append(
            {
                "index": index,
                "filename": filename,
                "source": item["name"],
                "cut_vertex": str(item["cut_vertex"]),
                "component_sizes": item["component_sizes"],
            }
        )

    return metadata


if __name__ == "__main__":
    target = SCRIPT_DIR.parent / "public" / "visual-proof-cut-vertex" / "assets" / "graphs"
    generated = generate_cut_vertex_svgs(target, count=10)
    for item in generated:
        print(f"{item['filename']}: {item['source']} cut_vertex={item['cut_vertex']}")
