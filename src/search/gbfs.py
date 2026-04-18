import pygame
import heapq
from cell import Cell
from typing import List
from config import *
from utils import draw_text_of_running_alg, reconstruct_path, draw_button, manhattan_distance


def solve_maze_GBFS(grid_cells: List[Cell], sc: pygame.Surface):
    """
    Solve the maze using Greedy Best-First Search (GBFS).

    GBFS uses only the heuristic (Manhattan distance) to guide the search.
    It expands the node that appears to be closest to the goal, but does NOT
    guarantee the shortest path.

    Args:
    - grid_cells (List[Cell]): A list of all the cells in the maze.
    - sc (pygame.Surface): The pygame screen surface for visualization.

    Returns:
    - path (List[Cell]): the path from start to destination, or None.
    - visited_cells_count (int): The total number of cells visited during the search.
    """
    start_cell = grid_cells[0]
    destination_cell = grid_cells[-1]

    # Priority queue: (heuristic, counter, cell)
    counter = 0
    open_set = []
    heapq.heappush(open_set, (manhattan_distance(start_cell, destination_cell), counter, start_cell))
    parent = {}
    parent[start_cell] = None
    visited = set()

    visited_cells_count = 0

    while open_set:
        h_cost, _, current_cell = heapq.heappop(open_set)

        if current_cell in visited:
            continue
        visited.add(current_cell)
        current_cell.visited = True
        visited_cells_count += 1

        pygame.time.delay(60)
        pygame.display.flip()

        for cell in grid_cells:
            cell.draw(sc)

        draw_text_of_running_alg(sc, "RUNNING: GBFS", FONT, 17, 20, 200, "#FFFFFF")
        draw_text_of_running_alg(sc, "CELLS EXPLORED: " + str(visited_cells_count), FONT, 17, 20, 230, "#FFFFFF")

        draw_button(sc, "GENERATE MAZE", 20, 300, BUTTON_COLOR)
        draw_button(sc, "BFS", 20, 400, BUTTON_COLOR)
        draw_button(sc, "DFS", 20, 350, BUTTON_COLOR)
        draw_button(sc, "BIDIRECTIONAL BFS", 20, 450, BUTTON_COLOR)
        draw_button(sc, "A STAR", 20, 500, BUTTON_COLOR)
        draw_button(sc, "GBFS", 20, 550, BUTTON_COLOR)
        draw_button(sc, "DIJKSTRA", 20, 600, BUTTON_COLOR)

        current_cell.draw(sc)

        if current_cell == destination_cell:
            path = reconstruct_path(sc, parent, start_cell, destination_cell)
            return path, visited_cells_count

        neighbors = current_cell.check_neighbors_for_search(grid_cells)
        for neighbor in neighbors:
            if neighbor not in visited:
                if neighbor not in parent:
                    parent[neighbor] = current_cell
                counter += 1
                h = manhattan_distance(neighbor, destination_cell)
                heapq.heappush(open_set, (h, counter, neighbor))

    return None, visited_cells_count
