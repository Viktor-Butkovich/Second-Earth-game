import networkx as nx
import numpy as np
import plotly.graph_objects as go
imageio = None # import imageio.v2 as imageio
import os
from collections import deque

def pos_toroid(m, n):
    # Torus radii
    R = 5
    r = 2

    pos_3d = {}
    for i in range(m):
        for j in range(n):
            u = 2*np.pi * i / m
            v = 2*np.pi * j / n
            x = (R + r*np.cos(v)) * np.cos(u)
            y = (R + r*np.cos(v)) * np.sin(u)
            z = r * np.sin(v)
            pos_3d[(i, j)] = (x, y, z)
    return pos_3d

def pos_spheroid(m, n):
    pos_3d = {}
    for i in range(m):
        for j in range(n):
            theta = 2 * np.pi * i / m      # longitude
            phi   = np.pi * j / n          # latitude

            x = np.sin(phi) * np.cos(theta)
            y = np.sin(phi) * np.sin(theta)
            z = np.cos(phi)

            pos_3d[(i, j)] = (x, y, z)
    return pos_3d

def bfs_layers(G, root):
    """Return nodes grouped by BFS distance from root."""
    dist = {root: 0}
    layers = {0: [root]}
    q = deque([root])

    while q:
        u = q.popleft()
        for v in G[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                layers.setdefault(dist[v], []).append(v)
                q.append(v)

    return dist, layers


def pos_spheroid_bfs(m, n, north=(0,0), south=(7,7)):
    """
    Embedding that:
    - picks arbitrary north and south poles
    - places them antipodally
    - assigns latitudes by BFS distance
    - keeps 4-adjacency
    - no coordinate collisions
    - sphere-like shape
    """
    G = nx.grid_2d_graph(m, n, periodic=True)

    # BFS from north and south
    distN, layersN = bfs_layers(G, north)
    distS, layersS = bfs_layers(G, south)

    # total BFS distance between poles
    D = distN[south]

    pos = {}

    for d in range(D+1):
        layer = layersN.get(d, [])
        if not layer:
            continue

        # latitude
        t = d / D
        phi = np.pi * t
        r = np.sin(phi)
        z = np.cos(phi)

        # evenly spaced longitudes
        k = len(layer)
        for idx, node in enumerate(layer):
            if k == 1:
                # pole
                pos[node] = (0.0, 0.0, z)
            else:
                theta = 2 * np.pi * idx / k
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                pos[node] = (x, y, z)

    return pos

def make_billboard_quad(center, normal, size=0.1):
    """
    Create a square quad (two triangles) centered at `center`,
    oriented so its normal is `normal`, with side length `size`.
    Returns 4 corner points in 3D.
    """
    normal = normal / np.linalg.norm(normal)

    # Pick an arbitrary vector not parallel to normal
    if abs(normal[2]) < 0.9:
        up = np.array([0, 0, 1])
    else:
        up = np.array([1, 0, 0])

    # Tangent axes
    tangent = np.cross(normal, up)
    tangent /= np.linalg.norm(tangent)

    bitangent = np.cross(normal, tangent)
    bitangent /= np.linalg.norm(bitangent)

    # Half-size
    hs = size / 2

    # Four corners
    c = np.array(center)
    p1 = c + hs * ( tangent + bitangent)
    p2 = c + hs * ( tangent - bitangent)
    p3 = c + hs * (-tangent - bitangent)
    p4 = c + hs * (-tangent + bitangent)

    return np.vstack([p1, p2, p3, p4])

def add_node_images(fig, pos, m, n, image_dir, size=0.12):
    """
    For each node (i,j), load image i_j.png and place it as a billboard quad.
    """
    for i in range(m):
        for j in range(n):
            node = (i, j)
            x, y, z = pos[node]
            center = np.array([x, y, z])
            normal = center  # outward from sphere

            # Build quad
            quad = make_billboard_quad(center, normal, size=size)
            X, Y, Z = quad[:,0], quad[:,1], quad[:,2]

            # Load image
            img_path = os.path.join(image_dir, f"{i}_{j}.png")
            img = imageio.imread(img_path)

            # Flatten image into facecolors
            # Mesh3d quad = 2 triangles = 2 faces
            # We assign the same texture to both faces
            facecolors = np.repeat(img.reshape(-1,3)[0:1], 2, axis=0)

            fig.add_trace(go.Mesh3d(
                x=X, y=Y, z=Z,
                i=[0, 0], j=[1, 2], k=[2, 3],  # two triangles
                facecolor=facecolors,
                showscale=False,
                lighting=dict(ambient=1.0, diffuse=0.0),
                hoverinfo='none'
            ))

def main():
    m = n = 15
    G = nx.grid_2d_graph(m, n, periodic=True)
    pos_3d = pos_spheroid_bfs(m, n)
    # pos_3d = pos_spheroid(m, n)
    # pos_3d = pos_toroid(m, n)

    # Extract node coordinates
    xs = [pos_3d[n][0] for n in G.nodes()]
    ys = [pos_3d[n][1] for n in G.nodes()]
    zs = [pos_3d[n][2] for n in G.nodes()]

    # Build edge coordinate lists
    edge_x = []
    edge_y = []
    edge_z = []

    for u, v in G.edges():
        x0, y0, z0 = pos_3d[u]
        x1, y1, z1 = pos_3d[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        edge_z += [z0, z1, None]

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(color='gray', width=2),
        hoverinfo='none'
    ))

    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode='markers',
        marker=dict(size=4, color='red'),
    ))

    fig.update_layout(
        scene=dict(aspectmode='data'),
        showlegend=False
    )

    # Add node images
    #IMAGE_DIR = "YOUR_IMAGE_DIRECTORY"   # <-- replace this
    #add_node_images(fig, pos_3d, m, n, IMAGE_DIR, size=0.12)

    #fig.update_layout(
    #    scene=dict(aspectmode='data'),
    #    showlegend=False
    #) # Try this out later, saving each square's appearance to the image directory

    fig.show()