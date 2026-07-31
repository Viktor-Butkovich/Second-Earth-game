# Exploratory, primarily AI-generated code to investigate spherical embedding and mesh-based planet rendering. Such simulations are held to a lower standard than the rest of the codebase.

import numpy as np
from PIL import Image
import imageio.v2 as imageio
import os
import networkx as nx
from collections import deque


def project_point(p, camera_pos, camera_dir, fov, img_w, img_h):
    forward = camera_dir / np.linalg.norm(camera_dir)
    right = np.cross(forward, np.array([0, 1, 0]))
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)

    v = p - camera_pos
    x = np.dot(v, right)
    y = np.dot(v, up)
    z = np.dot(v, forward)

    if z <= 0:
        return None

    f = 0.5 * img_w / np.tan(fov / 2)
    u = int(img_w / 2 + f * (x / z))
    v = int(img_h / 2 - f * (y / z))
    return (u, v, z)


def render_sphere(
    pos,
    m,
    n,
    image_dir,
    camera_pos=np.array([0.0, 0.0, 3.0]),
    camera_dir=np.array([0.0, 0.0, -1.0]),
    fov=np.radians(60.0),
    img_w=64,
    img_h=64,
    tile_res=16,
):
    """
    Render a sphere using nearest-tile raycasting.
    tile_res: resolution of each downsampled tile (e.g., 16 → 16x16)
    """

    # -----------------------------------------------------
    # Precompute tile data (vectorized)
    # -----------------------------------------------------
    tile_normals = []
    tile_east = []
    tile_north = []
    tile_images = []

    for i in range(m):
        for j in range(n):
            center = np.array(pos[(i, j)], dtype=np.float64)
            normal = center / np.linalg.norm(center)

            # orientation frame
            north_global = np.array([0.0, 0.0, 1.0])
            north_proj = north_global - np.dot(north_global, normal) * normal
            if np.linalg.norm(north_proj) < 1e-6:
                north_proj = np.array([1.0, 0.0, 0.0])
            north_proj = north_proj.astype(np.float64)  # keep this line
            north_proj /= np.linalg.norm(north_proj)

            east = np.cross(normal, north_proj)
            east /= np.linalg.norm(east)

            # load + downsample to tile_res × tile_res
            img = imageio.imread(os.path.join(image_dir, f"{i}_{j}.png"))
            img = np.array(Image.fromarray(img).resize((tile_res, tile_res)))

            tile_normals.append(normal)
            tile_east.append(east)
            tile_north.append(north_proj)
            tile_images.append(img)

    tile_normals = np.array(tile_normals)
    tile_east = np.array(tile_east)
    tile_north = np.array(tile_north)
    N = tile_normals.shape[0]

    # -----------------------------------------------------
    # Precompute camera ray directions
    # -----------------------------------------------------
    forward = camera_dir / np.linalg.norm(camera_dir)
    camera_up = np.array([0.0, 0.0, 1.0])  # global north pole

    right = np.cross(camera_up, forward)
    right /= np.linalg.norm(right)

    up = np.cross(forward, right)
    up /= np.linalg.norm(up)

    f = 0.5 * img_w / np.tan(fov / 2.0)

    xs = (np.arange(img_w) - img_w / 2.0) / f
    ys = -(np.arange(img_h) - img_h / 2.0) / f
    X, Y = np.meshgrid(xs, ys)

    ray_dirs = X[..., None] * right + Y[..., None] * up + forward
    ray_dirs /= np.linalg.norm(ray_dirs, axis=2)[..., None]

    # -----------------------------------------------------
    # Ray-sphere intersection (vectorized)
    # -----------------------------------------------------
    oc = camera_pos
    b = 2.0 * np.einsum("ijk,k->ij", ray_dirs, oc)
    c = np.dot(oc, oc) - 1.0

    disc = b * b - 4.0 * c
    hit_mask = disc > 0.0

    # safe t: only compute where valid
    t = np.full((img_h, img_w), np.inf, dtype=np.float64)
    valid = hit_mask
    t[valid] = (-b[valid] - np.sqrt(disc[valid])) / 2.0

    # hits: safe multiply
    hits = oc + np.where(valid[..., None], t[..., None] * ray_dirs, 0.0)

    # safe normalization
    norms = np.linalg.norm(hits, axis=2)
    hit_dirs = np.zeros_like(hits)
    nonzero = norms > 1e-12
    hit_dirs[nonzero] = hits[nonzero] / norms[nonzero, None]

    # -----------------------------------------------------
    # Output buffer
    # -----------------------------------------------------
    output_arr = np.zeros((img_h, img_w, 3), dtype=np.uint8)

    # -----------------------------------------------------
    # Main loop (fast)
    # -----------------------------------------------------
    for py in range(img_h):
        for px in range(img_w):

            if not hit_mask[py, px]:
                continue

            hd = hit_dirs[py, px]

            # nearest tile (vectorized dot)
            dots = tile_normals @ hd
            best_idx = np.argmax(dots)

            normal = tile_normals[best_idx]
            east = tile_east[best_idx]
            northp = tile_north[best_idx]
            img = tile_images[best_idx]

            # spherical UV mapping
            dot_center = np.dot(hd, normal)
            if dot_center < 1e-8:
                dot_center = 1e-8

            u = np.arctan2(np.dot(hd, east), dot_center)
            v = np.arctan2(np.dot(hd, northp), dot_center)

            # normalize to [-1,1]
            tile_half_angle = min(np.pi / m, 2 * np.pi / n) * 0.5
            u /= tile_half_angle
            v /= tile_half_angle

            # convert to texture coords
            tx = int((u * 0.5 + 0.5) * tile_res)
            ty = int((v * 0.5 + 0.5) * tile_res)

            tx = max(0, min(tile_res - 1, tx))
            ty = max(0, min(tile_res - 1, ty))

            """
            # local coords
            u = np.dot(hd, east)
            v = np.dot(hd, northp)

            # convert to texture coords
            tx = int((u * 0.5 + 0.5) * tile_res)
            ty = int((v * 0.5 + 0.5) * tile_res)

            tx = max(0, min(tile_res - 1, tx))
            ty = max(0, min(tile_res - 1, ty))
            """

            output_arr[py, px] = img[ty, tx]

    return Image.fromarray(output_arr)


def bfs_layers(G, root):
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


def pos_spheroid_bfs(m, n, north, south):
    G = nx.grid_2d_graph(m, n, periodic=True)
    distN, layersN = bfs_layers(G, north)
    D = distN[south]
    pos = {}
    for d in range(D + 1):
        layer = layersN.get(d, [])
        if not layer:
            continue
        t = d / D
        phi = np.pi * t
        r = np.sin(phi)
        z = np.cos(phi)
        k = len(layer)
        for idx, node in enumerate(layer):
            if k == 1:
                pos[node] = (0, 0, z)
            else:
                theta = 2 * np.pi * idx / k
                pos[node] = (r * np.cos(theta), r * np.sin(theta), z)
    return pos


def static_main():
    m = n = 17
    pos = pos_spheroid_bfs(m, n, north=(0, 0), south=(m // 2, n // 2))

    img = render_sphere(
        pos,
        m,
        n,
        "cached_images",
        camera_pos=np.array([3, 0, 0]),
        camera_dir=np.array([-1, 0, 0]),
        fov=np.radians(60),
    )

    img.save("sphere_render.png")


def main():
    m = n = 25
    pos = pos_spheroid_bfs(m, n, north=(0, 0), south=(m // 2, n // 2))

    frames = []
    num_frames = 32  # adjust for smoother rotation
    radius = 3.0

    for k in range(num_frames):
        theta = 2 * np.pi * (k / num_frames)

        # camera rotates around equator
        cam_x = radius * np.cos(theta)
        cam_y = radius * np.sin(theta)
        cam_z = 0.0

        camera_pos = np.array([cam_x, cam_y, cam_z], dtype=np.float64)

        # camera looks toward sphere center
        camera_dir = -camera_pos

        # enforce north-up orientation
        # (the renderer uses camera_dir only; up is implicit)
        img = render_sphere(
            pos,
            m,
            n,
            "cached_images",
            camera_pos=camera_pos,
            camera_dir=camera_dir,
            fov=np.radians(60),
            tile_res=16,  # configurable tile resolution
        )

        frames.append(img)

    # save GIF
    frames[0].save(
        "sphere_rotation.gif",
        save_all=True,
        append_images=frames[1:],
        duration=4.8 * 1000 / num_frames,  # 4.8 seconds per rotation
        loop=0,
    )
