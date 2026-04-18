"""
Script tạo video demo GIF cho 4 thuật toán × 5 hành vi = 20 GIF + 1 GIF tạo maze.
Chạy: python generate_demos.py
Output: thư mục demos/ với các subfolder:
  demos/maze_generation/   — 1 GIF tạo mê cung
  demos/BFS/               — 5 GIF (5 behaviors)
  demos/A-Star/            — 5 GIF
  demos/GBFS/              — 5 GIF
  demos/Dijkstra/          — 5 GIF
"""
import os
import shutil
import random
import heapq
import time
from collections import deque

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_DIR, "demos")

# ── Speed config ────────────────────────────────────────────────
MAZE_FPS = 12         # maze generation
MAZE_INTERVAL = 80    # ms between frames
ALGO_FPS = 12         # algorithm demos
ALGO_INTERVAL = 80    # ms between frames

# ─── Maze helpers ───────────────────────────────────────────────
class SimpleCell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.col = x
        self.row = y
        self.walls = {"top": True, "bottom": True, "left": True, "right": True}
        self.generated = False

def create_grid(cols, rows):
    return [SimpleCell(col, row) for row in range(rows) for col in range(cols)]

def _get_cell(grid, x, y, cols, rows):
    if 0 <= x < cols and 0 <= y < rows:
        return grid[y * cols + x]
    return None

def generate_maze_dfs(grid, cols, rows):
    start_cell = grid[0]
    start_cell.generated = True
    stack = [start_cell]
    steps = []  # record for animation
    while stack:
        current = stack[-1]
        x, y = current.col, current.row
        directions = [(0, -1, "top", "bottom"), (0, 1, "bottom", "top"),
                      (-1, 0, "left", "right"), (1, 0, "right", "left")]
        neighbors = []
        for dx, dy, w1, w2 in directions:
            n = _get_cell(grid, x + dx, y + dy, cols, rows)
            if n and not n.generated:
                neighbors.append((n, w1, w2))
        if neighbors:
            neighbor, w1, w2 = random.choice(neighbors)
            current.walls[w1] = False
            neighbor.walls[w2] = False
            neighbor.generated = True
            stack.append(neighbor)
            steps.append((neighbor.col, neighbor.row, list(stack)))
        else:
            stack.pop()
            steps.append((current.col, current.row, list(stack)))
    return steps

def add_extra_paths(grid, cols, rows, ratio=0.15):
    removable = []
    for cell in grid:
        x, y = cell.col, cell.row
        if x < cols - 1 and cell.walls["right"]:
            r = _get_cell(grid, x + 1, y, cols, rows)
            if r:
                removable.append((cell, r, "right", "left"))
        if y < rows - 1 and cell.walls["bottom"]:
            b = _get_cell(grid, x, y + 1, cols, rows)
            if b:
                removable.append((cell, b, "bottom", "top"))
    num = int(len(removable) * ratio)
    for c1, c2, w1, w2 in random.sample(removable, min(num, len(removable))):
        c1.walls[w1] = False
        c2.walls[w2] = False

def create_maze(cols, rows, seed=42):
    random.seed(seed)
    grid = create_grid(cols, rows)
    steps = generate_maze_dfs(grid, cols, rows)
    add_extra_paths(grid, cols, rows, 0.15)
    return grid, steps

def get_neighbors(grid, cx, cy, cols, rows):
    idx = cx + cy * cols
    cell = grid[idx]
    result = []
    for dx, dy, wall in [(0, -1, "top"), (0, 1, "bottom"), (-1, 0, "left"), (1, 0, "right")]:
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < cols and 0 <= ny < rows and not cell.walls[wall]:
            result.append((nx, ny))
    return result

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# ─── Search algorithms (return path, explored_order frame by frame) ─────
def bfs_search(grid, cols, rows, start, goal):
    queue = deque([(start, [start])])
    visited = {start}
    explored_order = []
    while queue:
        (cx, cy), path = queue.popleft()
        explored_order.append((cx, cy))
        if (cx, cy) == goal:
            return path, explored_order
        for nx, ny in get_neighbors(grid, cx, cy, cols, rows):
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))
    return None, explored_order

def dfs_search(grid, cols, rows, start, goal):
    stack = [(start, [start])]
    visited = {start}
    explored_order = []
    while stack:
        (cx, cy), path = stack.pop()
        explored_order.append((cx, cy))
        if (cx, cy) == goal:
            return path, explored_order
        for nx, ny in get_neighbors(grid, cx, cy, cols, rows):
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                stack.append(((nx, ny), path + [(nx, ny)]))
    return None, explored_order

def astar_search(grid, cols, rows, start, goal):
    counter = 0
    open_set = [(heuristic(start, goal), 0, counter, start, [start])]
    visited = set()
    explored_order = []
    while open_set:
        f, g, _, (cx, cy), path = heapq.heappop(open_set)
        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))
        explored_order.append((cx, cy))
        if (cx, cy) == goal:
            return path, explored_order
        for nx, ny in get_neighbors(grid, cx, cy, cols, rows):
            if (nx, ny) not in visited:
                counter += 1
                new_g = g + 1
                heapq.heappush(open_set, (new_g + heuristic((nx, ny), goal), new_g, counter, (nx, ny), path + [(nx, ny)]))
    return None, explored_order

def gbfs_search(grid, cols, rows, start, goal):
    counter = 0
    open_set = [(heuristic(start, goal), counter, start, [start])]
    visited = set()
    explored_order = []
    while open_set:
        h, _, (cx, cy), path = heapq.heappop(open_set)
        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))
        explored_order.append((cx, cy))
        if (cx, cy) == goal:
            return path, explored_order
        for nx, ny in get_neighbors(grid, cx, cy, cols, rows):
            if (nx, ny) not in visited:
                counter += 1
                heapq.heappush(open_set, (heuristic((nx, ny), goal), counter, (nx, ny), path + [(nx, ny)]))
    return None, explored_order

def dijkstra_search(grid, cols, rows, start, goal):
    counter = 0
    open_set = [(0, counter, start, [start])]
    visited = set()
    explored_order = []
    while open_set:
        cost, _, (cx, cy), path = heapq.heappop(open_set)
        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))
        explored_order.append((cx, cy))
        if (cx, cy) == goal:
            return path, explored_order
        for nx, ny in get_neighbors(grid, cx, cy, cols, rows):
            if (nx, ny) not in visited:
                counter += 1
                heapq.heappush(open_set, (cost + 1, counter, (nx, ny), path + [(nx, ny)]))
    return None, explored_order

ALGORITHMS = {
    "BFS": bfs_search,
    "A-Star": astar_search,
    "GBFS": gbfs_search,
    "Dijkstra": dijkstra_search,
}

ALGO_COLORS = {
    "BFS": "#2196F3",
    "A-Star": "#4CAF50",
    "GBFS": "#9C27B0",
    "Dijkstra": "#FF9800",
}

# ─── Behavior system ────────────────────────────────────────────
def get_behavior_target(behavior, ghost_pos, pacman_pos, pacman_dir, cols, rows):
    px, py = pacman_pos
    if behavior == "Chase":
        return px, py
    elif behavior == "Predict":
        ahead = 3
        tx, ty = px, py
        if pacman_dir == "up":    ty = max(0, py - ahead)
        elif pacman_dir == "down":  ty = min(rows - 1, py + ahead)
        elif pacman_dir == "left":  tx = max(0, px - ahead)
        elif pacman_dir == "right": tx = min(cols - 1, px + ahead)
        return tx, ty
    elif behavior == "Flank":
        flank_dist = 3
        tx, ty = px, py
        if pacman_dir == "up":    ty = min(rows - 1, py + flank_dist)
        elif pacman_dir == "down":  ty = max(0, py - flank_dist)
        elif pacman_dir == "left":  tx = min(cols - 1, px + flank_dist)
        elif pacman_dir == "right": tx = max(0, px - flank_dist)
        return tx, ty
    elif behavior == "Patrol":
        corners = [(1, 1), (cols - 2, 1), (cols - 2, rows - 2), (1, rows - 2)]
        gx, gy = ghost_pos
        best = min(corners, key=lambda c: abs(c[0] - gx) + abs(c[1] - gy))
        if abs(best[0] - gx) + abs(best[1] - gy) <= 1:
            idx = (corners.index(best) + 1) % 4
            best = corners[idx]
        return best
    elif behavior == "Random":
        return random.randint(0, cols - 1), random.randint(0, rows - 1)
    return px, py

BEHAVIORS = ["Chase", "Predict", "Flank", "Patrol", "Random"]

# ─── Drawing helpers ────────────────────────────────────────────
def draw_walls(ax, grid, cols, rows):
    """Draw maze walls."""
    for cell in grid:
        x, y = cell.col, cell.row
        lw = 1.5
        wc = "#3355CC"
        if cell.walls["top"]:
            ax.plot([x - 0.5, x + 0.5], [y - 0.5, y - 0.5], color=wc, linewidth=lw)
        if cell.walls["bottom"]:
            ax.plot([x - 0.5, x + 0.5], [y + 0.5, y + 0.5], color=wc, linewidth=lw)
        if cell.walls["left"]:
            ax.plot([x - 0.5, x - 0.5], [y - 0.5, y + 0.5], color=wc, linewidth=lw)
        if cell.walls["right"]:
            ax.plot([x + 0.5, x + 0.5], [y - 0.5, y + 0.5], color=wc, linewidth=lw)

def setup_ax(ax, cols, rows):
    ax.set_xlim(-0.5, cols - 0.5)
    ax.set_ylim(rows - 0.5, -0.5)
    ax.set_aspect("equal")
    ax.set_facecolor("#111122")
    ax.set_xticks([])
    ax.set_yticks([])

# ─── 1. Maze generation animation ──────────────────────────────
def create_maze_generation_gif(cols, rows, seed=42):
    print("  Generating maze animation...")

    # ── Phase 1: DFS Backtracking ──
    random.seed(seed)
    gen_grid = create_grid(cols, rows)
    gen_grid[0].generated = True
    stack = [gen_grid[0]]
    dfs_frames = []  # (generated_set, current_pos)
    generated_set = {(0, 0)}
    dfs_frames.append((set(generated_set), (0, 0)))

    while stack:
        current = stack[-1]
        x, y = current.col, current.row
        directions = [(0, -1, "top", "bottom"), (0, 1, "bottom", "top"),
                      (-1, 0, "left", "right"), (1, 0, "right", "left")]
        neighbors = []
        for dx, dy, w1, w2 in directions:
            n = _get_cell(gen_grid, x + dx, y + dy, cols, rows)
            if n and not n.generated:
                neighbors.append((n, w1, w2))
        if neighbors:
            neighbor, w1, w2 = random.choice(neighbors)
            current.walls[w1] = False
            neighbor.walls[w2] = False
            neighbor.generated = True
            stack.append(neighbor)
            generated_set.add((neighbor.col, neighbor.row))
            dfs_frames.append((set(generated_set), (neighbor.col, neighbor.row)))
        else:
            stack.pop()
            if stack:
                dfs_frames.append((set(generated_set), (stack[-1].col, stack[-1].row)))

    # ── Phase 2: Identify extra walls to remove (DON'T remove yet) ──
    # (no re-seed — keep same random state as create_maze for consistency)
    removable = []
    for cell in gen_grid:
        x, y = cell.col, cell.row
        if x < cols - 1 and cell.walls["right"]:
            r = _get_cell(gen_grid, x + 1, y, cols, rows)
            if r:
                removable.append((cell, r, "right", "left"))
        if y < rows - 1 and cell.walls["bottom"]:
            b = _get_cell(gen_grid, x, y + 1, cols, rows)
            if b:
                removable.append((cell, b, "bottom", "top"))
    num = int(len(removable) * 0.15)
    walls_to_remove = random.sample(removable, min(num, len(removable)))

    # Store as (cell1_idx, wall1_dir, cell2_idx, wall2_dir, highlight_pos)
    extra_wall_ops = []
    for c1, c2, w1, w2 in walls_to_remove:
        idx1 = c1.row * cols + c1.col
        idx2 = c2.row * cols + c2.col
        mx, my = (c1.col + c2.col) / 2, (c1.row + c2.row) / 2
        extra_wall_ops.append((idx1, w1, idx2, w2, (mx, my)))

    # ── Sample DFS frames ──
    dfs_step = max(1, len(dfs_frames) // 120)
    sampled_dfs = dfs_frames[::dfs_step]
    if dfs_frames[-1] not in sampled_dfs:
        sampled_dfs.append(dfs_frames[-1])

    n_dfs = len(sampled_dfs)
    n_extra = len(extra_wall_ops)
    hold_count = 15
    total_anim = n_dfs + n_extra + hold_count

    fig, ax = plt.subplots(figsize=(8, 6), facecolor="#000000")

    # Track which extra walls have been removed so far (mutated during animation)
    extra_removed_set = set()  # set of (cell_idx, wall_dir) already removed

    def animate(frame_idx):
        ax.clear()
        setup_ax(ax, cols, rows)

        if frame_idx < n_dfs:
            # ── DFS phase ──
            gen_set, cur_pos = sampled_dfs[frame_idx]

            for (cx, cy) in gen_set:
                rect = plt.Rectangle((cx - 0.45, cy - 0.45), 0.9, 0.9,
                                     facecolor="#1a1a2e", edgecolor="none")
                ax.add_patch(rect)

            cx, cy = cur_pos
            rect = plt.Rectangle((cx - 0.45, cy - 0.45), 0.9, 0.9,
                                  facecolor="#FF4444", edgecolor="none", alpha=0.8)
            ax.add_patch(rect)

            # Draw walls (DFS state only — no extra removed yet)
            for cell in gen_grid:
                if (cell.col, cell.row) in gen_set:
                    x, y = cell.col, cell.row
                    lw, wc = 1.5, "#3355CC"
                    if cell.walls["top"]:
                        ax.plot([x - 0.5, x + 0.5], [y - 0.5, y - 0.5], color=wc, linewidth=lw)
                    if cell.walls["bottom"]:
                        ax.plot([x - 0.5, x + 0.5], [y + 0.5, y + 0.5], color=wc, linewidth=lw)
                    if cell.walls["left"]:
                        ax.plot([x - 0.5, x - 0.5], [y - 0.5, y + 0.5], color=wc, linewidth=lw)
                    if cell.walls["right"]:
                        ax.plot([x + 0.5, x + 0.5], [y - 0.5, y + 0.5], color=wc, linewidth=lw)

            progress = int(100 * (frame_idx + 1) / n_dfs)
            ax.set_title(f"Maze Generation — Phase 1: DFS Backtracking — {min(progress, 100)}%\n"
                         f"Cells: {len(gen_set)}/{cols * rows}",
                         fontsize=12, fontweight="bold", color="white")
        else:
            # ── Extra Path / Hold phase ──
            gen_set = generated_set  # all cells

            # Determine how many extra walls removed so far
            if frame_idx < n_dfs + n_extra:
                ep_idx = frame_idx - n_dfs
                # Remove wall for this frame
                idx1, w1, idx2, w2, _ = extra_wall_ops[ep_idx]
                gen_grid[idx1].walls[w1] = False
                gen_grid[idx2].walls[w2] = False
                extra_removed_set.add(ep_idx)

            for (cx, cy) in gen_set:
                rect = plt.Rectangle((cx - 0.45, cy - 0.45), 0.9, 0.9,
                                     facecolor="#1a1a2e", edgecolor="none")
                ax.add_patch(rect)

            # Highlight removed extra paths
            removed_count = min(frame_idx - n_dfs + 1, n_extra) if frame_idx < n_dfs + n_extra else n_extra
            for k in range(removed_count):
                _, _, _, _, (mx, my) = extra_wall_ops[k]
                alpha = 0.4 if frame_idx >= n_dfs + n_extra else 0.6
                rect = plt.Rectangle((mx - 0.45, my - 0.45), 0.9, 0.9,
                                     facecolor="#00FF88", edgecolor="none", alpha=alpha, zorder=3)
                ax.add_patch(rect)

            # Bright highlight on current removal
            if frame_idx < n_dfs + n_extra:
                _, _, _, _, (mx, my) = extra_wall_ops[ep_idx]
                rect = plt.Rectangle((mx - 0.45, my - 0.45), 0.9, 0.9,
                                     facecolor="#00FF88", edgecolor="white", linewidth=2, alpha=0.9, zorder=4)
                ax.add_patch(rect)

            # Draw walls (with extra removals applied progressively)
            for cell in gen_grid:
                x, y = cell.col, cell.row
                lw, wc = 1.5, "#3355CC"
                if cell.walls["top"]:
                    ax.plot([x - 0.5, x + 0.5], [y - 0.5, y - 0.5], color=wc, linewidth=lw)
                if cell.walls["bottom"]:
                    ax.plot([x - 0.5, x + 0.5], [y + 0.5, y + 0.5], color=wc, linewidth=lw)
                if cell.walls["left"]:
                    ax.plot([x - 0.5, x - 0.5], [y - 0.5, y + 0.5], color=wc, linewidth=lw)
                if cell.walls["right"]:
                    ax.plot([x + 0.5, x + 0.5], [y - 0.5, y + 0.5], color=wc, linewidth=lw)

            if frame_idx < n_dfs + n_extra:
                ax.set_title(f"Maze Generation — Phase 2: Extra Path Removal\n"
                             f"Walls removed: {ep_idx + 1}/{n_extra} (ratio ~15%)",
                             fontsize=12, fontweight="bold", color="#00FF88")
            else:
                ax.set_title(f"Maze Generation — Complete\n"
                             f"Cells: {cols * rows} | Extra paths: {n_extra}",
                             fontsize=12, fontweight="bold", color="white")

        # Outer border
        ax.plot([-0.5, cols - 0.5], [-0.5, -0.5], color="#5577FF", linewidth=2)
        ax.plot([-0.5, cols - 0.5], [rows - 0.5, rows - 0.5], color="#5577FF", linewidth=2)
        ax.plot([-0.5, -0.5], [-0.5, rows - 0.5], color="#5577FF", linewidth=2)
        ax.plot([cols - 0.5, cols - 0.5], [-0.5, rows - 0.5], color="#5577FF", linewidth=2)

    maze_dir = os.path.join(OUTPUT_DIR, "maze_generation")
    os.makedirs(maze_dir, exist_ok=True)

    anim = FuncAnimation(fig, animate, frames=total_anim, interval=MAZE_INTERVAL, repeat=False)
    path_out = os.path.join(maze_dir, "maze_generation.gif")
    anim.save(path_out, writer=PillowWriter(fps=MAZE_FPS))
    plt.close(fig)
    print(f"  Saved: {path_out}")

# ─── 2. Algorithm × Behavior animation ─────────────────────────
def create_algo_behavior_gif(grid, cols, rows, algo_name, algo_func, behavior, ghost_pos, pacman_pos, pacman_dir, idx):
    """Create GIF showing ghost pathfinding step by step."""
    # Seed by behavior (not idx) so same behavior = same target across all algorithms
    random.seed(99 + BEHAVIORS.index(behavior))
    target = get_behavior_target(behavior, ghost_pos, pacman_pos, pacman_dir, cols, rows)

    # Time the search
    t_start = time.perf_counter()
    path, explored = algo_func(grid, cols, rows, ghost_pos, target)
    t_end = time.perf_counter()
    search_time = t_end - t_start

    if path is None:
        path = []

    color = ALGO_COLORS[algo_name]

    # Create frames: progressively reveal explored nodes, then path
    total_explored = len(explored)
    total_path = len(path)

    # Sample explored frames — smooth reveal
    explore_step = max(1, total_explored // 60)
    explore_frames = list(range(0, total_explored, explore_step))
    if total_explored - 1 not in explore_frames:
        explore_frames.append(total_explored - 1)

    # Path frames — smooth path drawing
    path_step = max(1, total_path // 30)
    path_frames = list(range(0, total_path, path_step))
    if total_path > 0 and total_path - 1 not in path_frames:
        path_frames.append(total_path - 1)

    # Hold last frame
    hold_frames = 15

    fig, ax = plt.subplots(figsize=(8, 6), facecolor="#000000")

    def animate(frame_idx):
        ax.clear()
        setup_ax(ax, cols, rows)

        n_explore = len(explore_frames)
        n_path = len(path_frames)

        if frame_idx < n_explore:
            # Exploring phase
            show_explored = explored[:explore_frames[frame_idx] + 1]
            show_path = []
            phase = "Exploring..."
        elif frame_idx < n_explore + n_path:
            # Path drawing phase
            show_explored = explored
            p_idx = frame_idx - n_explore
            show_path = path[:path_frames[p_idx] + 1]
            phase = "Path found!"
        else:
            # Hold
            show_explored = explored
            show_path = path
            phase = "Complete"

        # Draw explored nodes
        for i, (ex, ey) in enumerate(show_explored):
            alpha = 0.15 + 0.35 * (i / max(len(show_explored), 1))
            r, g, b = int(color[1:3], 16) / 255, int(color[3:5], 16) / 255, int(color[5:7], 16) / 255
            rect = plt.Rectangle((ex - 0.45, ey - 0.45), 0.9, 0.9,
                                 facecolor=(r, g, b, min(alpha, 0.5)),
                                 edgecolor="none")
            ax.add_patch(rect)

        # Draw walls
        draw_walls(ax, grid, cols, rows)

        # Draw path
        if show_path and len(show_path) > 1:
            ppx = [p[0] for p in show_path]
            ppy = [p[1] for p in show_path]
            ax.plot(ppx, ppy, color=color, linewidth=3, alpha=0.9, zorder=5)

        # Ghost
        gx, gy = ghost_pos
        ghost_circle = plt.Circle((gx, gy), 0.35, facecolor="#FF0000",
                                  edgecolor="white", linewidth=2, zorder=10)
        ax.add_patch(ghost_circle)
        ax.text(gx, gy, "G", ha="center", va="center", fontsize=10,
                color="white", fontweight="bold", zorder=11)

        # Target
        tx, ty = target
        target_circle = plt.Circle((tx, ty), 0.35, facecolor="#FFFF00",
                                   edgecolor="white", linewidth=2, zorder=10)
        ax.add_patch(target_circle)
        ax.text(tx, ty, "P", ha="center", va="center", fontsize=10,
                color="black", fontweight="bold", zorder=11)

        ax.set_title(f"{algo_name} + {behavior} — {phase}\n"
                     f"Explored: {len(show_explored)} | Path: {len(show_path)} | Time: {search_time*1000:.2f}ms",
                     fontsize=12, fontweight="bold", color="white",
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="#222244",
                               edgecolor=color, linewidth=2))

    total_anim_frames = len(explore_frames) + len(path_frames) + hold_frames
    anim = FuncAnimation(fig, animate, frames=total_anim_frames, interval=ALGO_INTERVAL, repeat=False)

    # Save into subfolder: demos/<AlgoName>/<behavior>.gif
    safe_algo = algo_name.replace("*", "Star").replace(" ", "_")
    safe_behav = behavior.replace(" ", "_")
    algo_dir = os.path.join(OUTPUT_DIR, safe_algo)
    os.makedirs(algo_dir, exist_ok=True)
    filename = f"{safe_behav}.gif"
    path_out = os.path.join(algo_dir, filename)
    anim.save(path_out, writer=PillowWriter(fps=ALGO_FPS))
    plt.close(fig)
    print(f"  Saved: {path_out}")

# ─── Main ───────────────────────────────────────────────────────
def main():
    COLS, ROWS = 16, 12
    SEED = 42

    print("=" * 60)
    print("  PACMAN MAZE SOLVER — Demo Video Generator")
    print("=" * 60)

    # Clean old demos folder and recreate
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Maze generation GIF (single demo)
    print("\n[1/2] Maze generation animation:")
    create_maze_generation_gif(COLS, ROWS, SEED)

    # 2. Algorithm × Behavior GIFs
    total = len(ALGORITHMS) * len(BEHAVIORS)
    print(f"\n[2/2] Algorithm x Behavior animations ({len(ALGORITHMS)} x {len(BEHAVIORS)} = {total}):")
    grid, _ = create_maze(COLS, ROWS, SEED)

    ghost_pos = (COLS - 2, 1)
    pacman_pos = (3, ROWS // 2)
    pacman_dir = "right"

    idx = 1
    for algo_name, algo_func in ALGORITHMS.items():
        for behavior in BEHAVIORS:
            print(f"  [{idx:2d}/{total}] {algo_name} + {behavior}")
            create_algo_behavior_gif(grid, COLS, ROWS, algo_name, algo_func,
                                     behavior, ghost_pos, pacman_pos, pacman_dir, idx)
            idx += 1

    # Print folder structure
    print(f"\nDone! 21 GIFs saved to: {OUTPUT_DIR}")
    print("Folder structure:")
    for name in sorted(os.listdir(OUTPUT_DIR)):
        sub = os.path.join(OUTPUT_DIR, name)
        if os.path.isdir(sub):
            files = sorted(os.listdir(sub))
            print(f"  {name}/")
            for f in files:
                print(f"    {f}")
    print("=" * 60)

if __name__ == "__main__":
    main()
