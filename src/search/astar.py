import pygame
import heapq
from cell import Cell
from typing import List
from config import *
from utils import draw_text_of_running_alg, reconstruct_path, draw_button, manhattan_distance


def solve_maze_AStar(grid_cells: List[Cell], sc: pygame.Surface):
    """
    Solve the maze using A* Search.

    A* combines the actual cost from start (g_cost) with a heuristic estimate
    to the goal (h_cost) to guide the search. It guarantees the shortest path
    while typically exploring fewer nodes than BFS or Dijkstra.

    Args:
    - grid_cells (List[Cell]): A list of all the cells in the maze.
    - sc (pygame.Surface): The pygame screen surface for visualization.

    Returns:
    - path (List[Cell]): the path from start to destination, or None.
    - visited_cells_count (int): The total number of cells visited during the search.
    """
    start_cell = grid_cells[0]
    destination_cell = grid_cells[-1]

    # Priority queue: (f_cost, counter, cell)
    # f_cost = g_cost + h_cost
    counter = 0
    open_set = []
    heapq.heappush(open_set, (manhattan_distance(start_cell, destination_cell), counter, start_cell))
    parent = {}
    parent[start_cell] = None
    g_cost = {start_cell: 0}
    visited = set()

    visited_cells_count = 0

    while open_set:
        f, _, current_cell = heapq.heappop(open_set)

        if current_cell in visited:
            continue
        visited.add(current_cell)
        current_cell.visited = True
        visited_cells_count += 1

        pygame.time.delay(60)
        pygame.display.flip()

        for cell in grid_cells:
            cell.draw(sc)

        draw_text_of_running_alg(sc, "RUNNING: A*", FONT, 17, 20, 200, "#FFFFFF")
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

        current_g = g_cost[current_cell]
        neighbors = current_cell.check_neighbors_for_search(grid_cells)
        for neighbor in neighbors:
            new_g = current_g + 1
            if neighbor not in visited and (neighbor not in g_cost or new_g < g_cost[neighbor]):
                g_cost[neighbor] = new_g
                parent[neighbor] = current_cell
                counter += 1
                f_cost = new_g + manhattan_distance(neighbor, destination_cell)
                heapq.heappush(open_set, (f_cost, counter, neighbor))

    return None, visited_cells_count