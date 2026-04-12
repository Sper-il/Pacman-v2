import pygame
import math
import random
import heapq
from collections import deque
from config import *


class Ghost:
    """
    Represents a ghost enemy that chases Pacman using AI pathfinding.
    """
    
    def __init__(self, start_x, start_y, color="#FF0000", speed=15):
        self.x = start_x
        self.y = start_y
        self.color = color
        self.name = "Ghost"
        self.direction = random.choice(["up", "down", "left", "right"])
        self.move_counter = 0
        self.move_delay = speed  # Ghost speed (higher = slower)
        self.path_to_pacman = []  # AI pathfinding result
        
        # Pathfinding algorithm: bfs, astar, dfs
        self.algorithm = "bfs"
        
        # Behavior mode:
        # chase: Direct chase (Blinky)
        # predict: Predict ahead of Pacman (Pinky)
        # flank: Flank from opposite side (Inky)
        # random: Random movement (no pathfinding)
        # patrol: Patrol corners of the map
        self.behavior = "chase"
        self.patrol_corners = []  # For patrol mode
        self.patrol_index = 0
        self.cached_path = []  # Cache path for DFS
        self.path_recalc_counter = 0  # Recalculate path every N moves
        
    def draw(self, sc):
        """Draw ghost at current position."""
        px = self.x * TILE_SIZE + MAZE_OFFSET + TILE_SIZE // 2
        py = self.y * TILE_SIZE + 2 + TILE_SIZE // 2
        radius = TILE_SIZE // 2 - 4
        
        # Draw ghost body (rounded top, wavy bottom)
        pygame.draw.circle(sc, pygame.Color(self.color), (px, py - 2), radius)
        pygame.draw.rect(sc, pygame.Color(self.color), 
                        (px - radius, py - 2, radius * 2, radius))
        
        # Wavy bottom
        wave_width = radius * 2 // 3
        for i in range(3):
            wave_x = px - radius + wave_width // 2 + i * wave_width
            wave_y = py + radius - 4
            pygame.draw.circle(sc, pygame.Color(self.color), (wave_x, wave_y), wave_width // 2)
        
        # Draw eyes (looking towards movement direction)
        eye_offset_x = 5
        eye_offset_y = -5
        pupil_offset_x, pupil_offset_y = 0, 0
        
        if self.direction == "left":
            pupil_offset_x = -2
        elif self.direction == "right":
            pupil_offset_x = 2
        elif self.direction == "up":
            pupil_offset_y = -2
        elif self.direction == "down":
            pupil_offset_y = 2
            
        # Left eye
        pygame.draw.circle(sc, pygame.Color("#FFFFFF"), (px - eye_offset_x, py + eye_offset_y), 5)
        pygame.draw.circle(sc, pygame.Color("#0000FF"), (px - eye_offset_x + pupil_offset_x, py + eye_offset_y + pupil_offset_y), 2)
        # Right eye
        pygame.draw.circle(sc, pygame.Color("#FFFFFF"), (px + eye_offset_x, py + eye_offset_y), 5)
        pygame.draw.circle(sc, pygame.Color("#0000FF"), (px + eye_offset_x + pupil_offset_x, py + eye_offset_y + pupil_offset_y), 2)
    
    def bfs_find_path(self, grid_cells, target_x, target_y):
        """Use BFS to find shortest path to target - AI pathfinding."""
        # Calculate grid dimensions from grid_cells
        grid_cols = max(cell.x for cell in grid_cells) + 1
        grid_rows = max(cell.y for cell in grid_cells) + 1
        
        start = (self.x, self.y)
        goal = (target_x, target_y)
        
        if start == goal:
            return []
        
        queue = deque([(start, [])])
        visited = {start}
        
        while queue:
            (cx, cy), path = queue.popleft()
            
            # Get current cell
            idx = cx + cy * grid_cols
            if idx < 0 or idx >= len(grid_cells):
                continue
            current_cell = grid_cells[idx]
            
            # Check all directions
            directions = [
                ("up", 0, -1, "top"),
                ("down", 0, 1, "bottom"),
                ("left", -1, 0, "left"),
                ("right", 1, 0, "right")
            ]
            
            for direction, dx, dy, wall in directions:
                nx, ny = cx + dx, cy + dy
                
                # Check bounds
                if nx < 0 or nx >= grid_cols or ny < 0 or ny >= grid_rows:
                    continue
                
                # Check if wall blocks
                if current_cell.walls[wall]:
                    continue
                
                # Check if target cell is obstacle
                n_idx = nx + ny * grid_cols
                if n_idx < len(grid_cells) and hasattr(grid_cells[n_idx], 'is_obstacle') and grid_cells[n_idx].is_obstacle:
                    continue
                
                if (nx, ny) in visited:
                    continue
                
                new_path = path + [direction]
                
                if (nx, ny) == goal:
                    return new_path
                
                visited.add((nx, ny))
                queue.append(((nx, ny), new_path))
        
        return []  # No path found
    
    def astar_find_path(self, grid_cells, target_x, target_y):
        """Use A* algorithm to find optimal path to target."""
        grid_cols = max(cell.x for cell in grid_cells) + 1
        grid_rows = max(cell.y for cell in grid_cells) + 1
        
        start = (self.x, self.y)
        goal = (target_x, target_y)
        
        if start == goal:
            return []
        
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance
        
        # Priority queue: (f_cost, g_cost, position, path)
        open_set = [(heuristic(start, goal), 0, start, [])]
        visited = set()
        
        while open_set:
            f_cost, g_cost, (cx, cy), path = heapq.heappop(open_set)
            
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            
            idx = cx + cy * grid_cols
            if idx < 0 or idx >= len(grid_cells):
                continue
            current_cell = grid_cells[idx]
            
            directions = [
                ("up", 0, -1, "top"),
                ("down", 0, 1, "bottom"),
                ("left", -1, 0, "left"),
                ("right", 1, 0, "right")
            ]
            
            for direction, dx, dy, wall in directions:
                nx, ny = cx + dx, cy + dy
                
                if nx < 0 or nx >= grid_cols or ny < 0 or ny >= grid_rows:
                    continue
                if current_cell.walls[wall]:
                    continue
                n_idx = nx + ny * grid_cols
                if n_idx < len(grid_cells) and hasattr(grid_cells[n_idx], 'is_obstacle') and grid_cells[n_idx].is_obstacle:
                    continue
                if (nx, ny) in visited:
                    continue
                
                new_path = path + [direction]
                if (nx, ny) == goal:
                    return new_path
                
                new_g = g_cost + 1
                new_f = new_g + heuristic((nx, ny), goal)
                heapq.heappush(open_set, (new_f, new_g, (nx, ny), new_path))
        
        return []
    
    def dfs_find_path(self, grid_cells, target_x, target_y):
        """Use DFS to find path to target (unpredictable paths)."""
        grid_cols = max(cell.x for cell in grid_cells) + 1
        grid_rows = max(cell.y for cell in grid_cells) + 1
        
        start = (self.x, self.y)
        goal = (target_x, target_y)
        
        if start == goal:
            return []
        
        stack = [(start, [])]
        visited = {start}
        
        while stack:
            (cx, cy), path = stack.pop()
            
            idx = cx + cy * grid_cols
            if idx < 0 or idx >= len(grid_cells):
                continue
            current_cell = grid_cells[idx]
            
            # Randomize direction order for unpredictability
            directions = [
                ("up", 0, -1, "top"),
                ("down", 0, 1, "bottom"),
                ("left", -1, 0, "left"),
                ("right", 1, 0, "right")
            ]
            random.shuffle(directions)
            
            for direction, dx, dy, wall in directions:
                nx, ny = cx + dx, cy + dy
                
                if nx < 0 or nx >= grid_cols or ny < 0 or ny >= grid_rows:
                    continue
                if current_cell.walls[wall]:
                    continue
                n_idx = nx + ny * grid_cols
                if n_idx < len(grid_cells) and hasattr(grid_cells[n_idx], 'is_obstacle') and grid_cells[n_idx].is_obstacle:
                    continue
                if (nx, ny) in visited:
                    continue
                
                new_path = path + [direction]
                if (nx, ny) == goal:
                    return new_path
                
                visited.add((nx, ny))
                stack.append(((nx, ny), new_path))
        
        return []
    
    def get_ai_target(self, pacman, grid_cells):
        """Get target position based on ghost's behavior."""
        grid_cols = max(cell.x for cell in grid_cells) + 1
        grid_rows = max(cell.y for cell in grid_cells) + 1
        
        if self.behavior == "chase":
            # Blinky: Direct chase
            return pacman.x, pacman.y
            
        elif self.behavior == "predict":
            # Pinky: Target 2 cells ahead of Pacman
            target_x, target_y = pacman.x, pacman.y
            ahead = 2
            if pacman.direction == "up":
                target_y = max(0, pacman.y - ahead)
            elif pacman.direction == "down":
                target_y = min(grid_rows - 1, pacman.y + ahead)
            elif pacman.direction == "left":
                target_x = max(0, pacman.x - ahead)
            elif pacman.direction == "right":
                target_x = min(grid_cols - 1, pacman.x + ahead)
            return target_x, target_y
            
        elif self.behavior == "flank":
            # Inky: Ambush from opposite direction Pacman is moving
            # Go to position behind Pacman (opposite of Pacman's direction)
            target_x, target_y = pacman.x, pacman.y
            flank_dist = 3
            if pacman.direction == "up":
                target_y = min(grid_rows - 1, pacman.y + flank_dist)
            elif pacman.direction == "down":
                target_y = max(0, pacman.y - flank_dist)
            elif pacman.direction == "left":
                target_x = min(grid_cols - 1, pacman.x + flank_dist)
            elif pacman.direction == "right":
                target_x = max(0, pacman.x - flank_dist)
            return target_x, target_y
            
        elif self.behavior == "patrol":
            # Patrol corners
            if not self.patrol_corners:
                self.patrol_corners = [
                    (1, 1),
                    (grid_cols - 2, 1),
                    (grid_cols - 2, grid_rows - 2),
                    (1, grid_rows - 2)
                ]
            target = self.patrol_corners[self.patrol_index % len(self.patrol_corners)]
            # Switch to next corner when close
            if abs(self.x - target[0]) <= 1 and abs(self.y - target[1]) <= 1:
                self.patrol_index = (self.patrol_index + 1) % len(self.patrol_corners)
                target = self.patrol_corners[self.patrol_index]
            return target
            
        elif self.behavior == "random":
            # No target, will use random movement
            return None
        
        return pacman.x, pacman.y
    
    def get_valid_directions(self, grid_cells):
        """Get list of valid directions ghost can move."""
        grid_cols = max(cell.x for cell in grid_cells) + 1
        grid_rows = max(cell.y for cell in grid_cells) + 1
        
        idx = self.x + self.y * grid_cols
        if idx < 0 or idx >= len(grid_cells):
            return []
        current_cell = grid_cells[idx]
        valid = []
        
        # Check each direction - no wall and target is not obstacle
        if not current_cell.walls["top"] and self.y > 0:
            n_idx = self.x + (self.y - 1) * grid_cols
            if not (hasattr(grid_cells[n_idx], 'is_obstacle') and grid_cells[n_idx].is_obstacle):
                valid.append("up")
        if not current_cell.walls["bottom"] and self.y < grid_rows - 1:
            n_idx = self.x + (self.y + 1) * grid_cols
            if not (hasattr(grid_cells[n_idx], 'is_obstacle') and grid_cells[n_idx].is_obstacle):
                valid.append("down")
        if not current_cell.walls["left"] and self.x > 0:
            n_idx = (self.x - 1) + self.y * grid_cols
            if not (hasattr(grid_cells[n_idx], 'is_obstacle') and grid_cells[n_idx].is_obstacle):
                valid.append("left")
        if not current_cell.walls["right"] and self.x < grid_cols - 1:
            n_idx = (self.x + 1) + self.y * grid_cols
            if not (hasattr(grid_cells[n_idx], 'is_obstacle') and grid_cells[n_idx].is_obstacle):
                valid.append("right")
        
        return valid
    
    def move(self, grid_cells, pacman=None):
        """Move ghost using AI pathfinding."""
        self.move_counter += 1
        if self.move_counter < self.move_delay:
            return
        self.move_counter = 0
        
        valid_directions = self.get_valid_directions(grid_cells)
        if not valid_directions:
            return
        
        # Random behavior - no pathfinding
        if self.behavior == "random":
            # Prefer continuing current direction to avoid zigzag
            if self.direction in valid_directions and random.random() < 0.7:
                pass  # keep direction
            else:
                self.direction = random.choice(valid_directions)
        elif pacman:
            # Get target based on behavior
            target = self.get_ai_target(pacman, grid_cells)
            
            if target is None:
                self.direction = random.choice(valid_directions)
            else:
                target_x, target_y = target
                
                # DFS: cache path, only recalculate every 5 moves or when path is empty
                if self.algorithm == "dfs":
                    self.path_recalc_counter += 1
                    if not self.cached_path or self.path_recalc_counter >= 5:
                        self.cached_path = self.dfs_find_path(grid_cells, target_x, target_y)
                        self.path_recalc_counter = 0
                    self.path_to_pacman = self.cached_path
                    # Consume first step from cache
                    if self.cached_path:
                        self.cached_path = self.cached_path[1:]
                elif self.algorithm == "astar":
                    self.path_to_pacman = self.astar_find_path(grid_cells, target_x, target_y)
                else:
                    # Default BFS
                    self.path_to_pacman = self.bfs_find_path(grid_cells, target_x, target_y)
                
                if self.path_to_pacman:
                    next_dir = self.path_to_pacman[0]
                    if next_dir in valid_directions:
                        self.direction = next_dir
                    else:
                        self.direction = random.choice(valid_directions)
                        self.cached_path = []  # Invalidate DFS cache
                else:
                    self.direction = random.choice(valid_directions)
        else:
            self.direction = random.choice(valid_directions)
        
        # Apply movement
        if self.direction == "up" and "up" in valid_directions:
            self.y -= 1
        elif self.direction == "down" and "down" in valid_directions:
            self.y += 1
        elif self.direction == "left" and "left" in valid_directions:
            self.x -= 1
        elif self.direction == "right" and "right" in valid_directions:
            self.x += 1
    
    def get_current_cell(self, grid_cells):
        """Get the cell object at current position."""
        grid_cols = max(cell.x for cell in grid_cells) + 1
        find_index = lambda x, y: x + y * grid_cols
        return grid_cells[find_index(self.x, self.y)]
    
    def check_collision(self, pacman):
        """Check if ghost caught Pacman."""
        return self.x == pacman.x and self.y == pacman.y


class Pacman:
    """
    Represents the Pacman character that the player controls.
    """
    
    def __init__(self, start_x, start_y=None):
        # Support both Pacman(x, y) and Pacman(cell) for backward compatibility
        if start_y is None and hasattr(start_x, 'x'):
            # Old API: passed a cell object
            self.x = start_x.x
            self.y = start_x.y
        else:
            # New API: passed x, y coordinates
            self.x = start_x
            self.y = start_y if start_y is not None else 0
        
        self.direction = "right"  # Current facing direction
        self.mouth_open = True  # For mouth animation
        self.animation_counter = 0
        self.score = 0
        
    def draw(self, sc):
        """Draw Pacman at current position with mouth animation."""
        # Calculate pixel position
        px = self.x * TILE_SIZE + MAZE_OFFSET + TILE_SIZE // 2
        py = self.y * TILE_SIZE + 2 + TILE_SIZE // 2
        radius = TILE_SIZE // 2 - 4
        
        # Animation for mouth
        self.animation_counter += 1
        if self.animation_counter % 8 == 0:
            self.mouth_open = not self.mouth_open
        
        # Calculate mouth angle based on direction
        if self.direction == "right":
            start_angle = 30 if self.mouth_open else 5
            end_angle = 330 if self.mouth_open else 355
        elif self.direction == "left":
            start_angle = 210 if self.mouth_open else 185
            end_angle = 150 if self.mouth_open else 175
        elif self.direction == "up":
            start_angle = 120 if self.mouth_open else 95
            end_angle = 60 if self.mouth_open else 85
        else:  # down
            start_angle = 300 if self.mouth_open else 275
            end_angle = 240 if self.mouth_open else 265
        
        # Draw Pacman as a pie shape (circle with mouth)
        if self.mouth_open:
            # Draw filled pacman with mouth
            points = [(px, py)]
            for angle in range(int(start_angle), int(end_angle) + 360 if end_angle < start_angle else int(end_angle) + 1, 5):
                angle_rad = math.radians(angle % 360)
                points.append((px + radius * math.cos(angle_rad), py - radius * math.sin(angle_rad)))
            points.append((px, py))
            if len(points) > 2:
                pygame.draw.polygon(sc, pygame.Color(PACMAN_COLOR), points)
        else:
            # Draw full circle when mouth closed
            pygame.draw.circle(sc, pygame.Color(PACMAN_COLOR), (px, py), radius)
    
    def can_move(self, direction, grid_cells):
        """Check if Pacman can move in the given direction."""
        current_cell = self.get_current_cell(grid_cells)
        grid_cols = max(cell.x for cell in grid_cells) + 1
        grid_rows = max(cell.y for cell in grid_cells) + 1
        
        # Check if direction is blocked by wall
        if direction == "up":
            if current_cell.walls["top"] or self.y <= 0:
                return False
            n_idx = self.x + (self.y - 1) * grid_cols
        elif direction == "down":
            if current_cell.walls["bottom"] or self.y >= grid_rows - 1:
                return False
            n_idx = self.x + (self.y + 1) * grid_cols
        elif direction == "left":
            if current_cell.walls["left"] or self.x <= 0:
                return False
            n_idx = (self.x - 1) + self.y * grid_cols
        elif direction == "right":
            if current_cell.walls["right"] or self.x >= grid_cols - 1:
                return False
            n_idx = (self.x + 1) + self.y * grid_cols
        else:
            return False
        
        # Check if target cell is an obstacle
        if n_idx < len(grid_cells):
            target_cell = grid_cells[n_idx]
            if hasattr(target_cell, 'is_obstacle') and target_cell.is_obstacle:
                return False
        
        return True
    
    def move(self, direction, grid_cells):
        """Move Pacman in the given direction if possible."""
        if self.can_move(direction, grid_cells):
            self.direction = direction
            if direction == "up":
                self.y -= 1
            elif direction == "down":
                self.y += 1
            elif direction == "left":
                self.x -= 1
            elif direction == "right":
                self.x += 1
            
            # Eat dot in the new cell
            new_cell = self.get_current_cell(grid_cells)
            if new_cell.has_dot:
                new_cell.has_dot = False
                self.score += 10
            return True
        return False
    
    def get_current_cell(self, grid_cells):
        """Get the cell object at current position."""
        grid_cols = max(cell.x for cell in grid_cells) + 1
        find_index = lambda x, y: x + y * grid_cols
        return grid_cells[find_index(self.x, self.y)]
    
    def has_reached_goal(self, destination_cell):
        """Check if Pacman reached the destination."""
        return self.x == destination_cell.x and self.y == destination_cell.y


class Cell:
    """
    Represents a single cell in the maze with coordinates, walls, and states for maze generation and solving.

    Attributes:
    - x (int): The x-coordinate of the cell in the grid.
    - y (int): The y-coordinate of the cell in the grid.
    - walls (dict): A dictionary indicating whether each wall ('top', 'right', 'bottom', 'left') exists (True)
      or has been removed (False).
    - generated (bool): Indicates if the cell has been visited during maze generation.
    - visited (bool): Indicates if the cell has been visited during the search/solving process.
    - is_solution (bool): Marks if the cell is part of the final solution path.
    """

    def __init__(self, x, y):
        """
        Initializes a Cell with specific x, y coordinates and sets up its walls and other states.

        Args:
        - x (int): The x-coordinate of the cell in the maze grid.
        - y (int): The y-coordinate of the cell in the maze grid.
        """

        # Grid cells position (support both x,y and col,row naming)
        self.x, self.y = x, y
        self.col, self.row = x, y  # Alias for compatibility
        self.walls = {"top": True,
                      "right": True,
                      "bottom": True,
                      "left": True}
        
        # Flags
        self.generated = False
        self.visited = False
        self.is_solution = False
        self.has_dot = True  # Each cell has a dot by default
        self.is_obstacle = False  # For obstacle-based maps

    def draw_current_cell(self, sc=None):
        """
        Highlights the current cell by drawing a rectangle on the screen with a distinct color.
        """
        if sc is None:
            sc = pygame.display.get_surface()
        # Calculate the position of the cell in the display based on grid coordinates
        x, y = self.x * TILE_SIZE + MAZE_OFFSET, self.y * TILE_SIZE + 2
        pygame.draw.rect(sc, pygame.Color(START_END_CELL_COLOR), (x, y, TILE_SIZE - 2, TILE_SIZE - 2))

    def draw(self, sc: pygame.Surface):
        """
        Draws the cell on the screen based on its current state, including walls and whether 
        it's generated, visited, or part of the solution.

        Args:
        - sc (pygame.Surface): The Pygame surface on which the cell is drawn.
        """

        # Calculate the position of the cell in the display based on grid coordinates
        x, y = self.x * TILE_SIZE + MAZE_OFFSET, self.y * TILE_SIZE + 2

        # Draw different colors depending on the state of the cell (generated, visited, part of the solution).
        if self.generated and not self.visited:
            pygame.draw.rect(sc, CELL_GENERATED_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
        if self.generated and self.visited and not self.is_solution:
            pygame.draw.rect(sc, CELL_VISITED_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
        if self.generated and self.visited and self.is_solution:
            pygame.draw.rect(sc, CELL_SOLUTION_COLOR, (x, y, TILE_SIZE, TILE_SIZE))

        # Draw dot if cell has one
        if self.generated and self.has_dot:
            dot_x = x + TILE_SIZE // 2
            dot_y = y + TILE_SIZE // 2
            pygame.draw.circle(sc, pygame.Color(DOT_COLOR), (dot_x, dot_y), 4)

        # Drawing the walls of the cell (top, right, bottom, left) if they exist.
        if self.walls['top']:
            pygame.draw.line(sc, WALL_COLOR, (x, y), (x + TILE_SIZE, y), 5)
        if self.walls['right']:
            pygame.draw.line(sc, WALL_COLOR, (x + TILE_SIZE, y), (x + TILE_SIZE, y + TILE_SIZE), 5)
        if self.walls['bottom']:
            pygame.draw.line(sc, WALL_COLOR, (x + TILE_SIZE, y + TILE_SIZE), (x , y + TILE_SIZE), 5)
        if self.walls['left']:
            pygame.draw.line(sc, WALL_COLOR, (x, y + TILE_SIZE), (x, y), 5)
    
    def check_cell(self, grid_cells, x, y):
        """
        Checks if a cell exists at the given (x, y) coordinates and returns the cell if valid.
        
        Args:
        - grid_cells (List[Cell]): List of all cells in the maze grid.
        - x (int): The x-coordinate of the cell to check.
        - y (int): The y-coordinate of the cell to check.
        
        Returns:
        - Cell or False: The cell at the given coordinates if valid, otherwise False.
        """
        # Calculate grid dimensions dynamically from grid_cells
        grid_cols = max(cell.x for cell in grid_cells) + 1
        grid_rows = max(cell.y for cell in grid_cells) + 1

        # Lambda function to calculate the index of the cell in the 1D list of grid cells.
        find_index = lambda x, y: x + y * grid_cols

        # If the coordinates are outside the valid grid range, return False.
        if x < 0 or x > grid_cols - 1 or y < 0 or y > grid_rows - 1:
            return False
        
        # Return the cell at the specified coordinates.
        return grid_cells[find_index(x, y)]
    
    def check_neighbors_for_maze_gen(self, grid_cells):
        """
        Finds and returns a list of unvisited neighboring cells for maze generation.
        
        Args:
        - grid_cells (List[Cell]): List of all cells in the maze grid.
        
        Returns:
        - neighbors (List[Cell]): A list of neighboring cells that have not yet been generated.
        
        Neighbors are identified by checking adjacent cells (top, right, bottom, left).
        If no unvisited neighbors are found, it returns False.
        """

        neighbors = []

        # Check each direction (top, right, bottom, left) for valid neighbors.
        top = self.check_cell(grid_cells, self.x, self.y - 1)
        right = self.check_cell(grid_cells, self.x + 1, self.y)
        bottom = self.check_cell(grid_cells, self.x, self.y + 1)
        left = self.check_cell(grid_cells, self.x - 1, self.y)

        # Append neighbors that haven't been generated yet (unvisited).
        if top and not top.generated:
            neighbors.append(top)
        if right and not right.generated:
            neighbors.append(right)
        if bottom and not bottom.generated:
            neighbors.append(bottom)
        if left and not left.generated:
            neighbors.append(left)

        # Return the list of available neighbors or False if no neighbors found.
        if len(neighbors) > 0:
            return neighbors
        else:
            return False 
    
    def check_neighbors_for_search(self, grid_cells):
        """
        Finds and returns a list of unvisited neighboring cells for maze-solving.

        Args:
        - grid_cells (List[Cell]): List of all cells in the maze grid.

        Returns:
        - neighbors: A list of unvisited neighboring cells that can be explored in the maze-solving process.
        
        This method checks for neighbors that have no walls separating them from the current cell, ensuring that they are reachable.
        """

        neighbors = []

        # Check each direction (top, right, bottom, left) for valid neighbors and make sure walls are open.
        top = self.check_cell(grid_cells, self.x, self.y - 1)
        right = self.check_cell(grid_cells, self.x + 1, self.y)
        bottom = self.check_cell(grid_cells, self.x, self.y + 1)
        left = self.check_cell(grid_cells, self.x - 1, self.y)

        # Append neighbors where walls are open and the neighbor is not visited.
        if top and not top.visited:
            if self.walls["top"] == False and top.walls["bottom"] == False:
                neighbors.append(top)
        if right and not right.visited:
            if self.walls["right"] == False and right.walls["left"] == False:
                neighbors.append(right)
        if bottom and not bottom.visited:
            if self.walls["bottom"] == False and bottom.walls["top"] == False:
                neighbors.append(bottom)
        if left and not left.visited:
            if self.walls["left"] == False and left.walls["right"] == False:
                neighbors.append(left)

        # Return the list of available neighbors.
        if len(neighbors) > 0:
            return neighbors
        else:
            return []