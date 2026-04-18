import pygame
import os
import random
from cell import Cell, Pacman, Ghost
from config import *
from collections import deque

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

# Initialize Pygame
pygame.init()
sc = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption("PACMAN KEY HUNT - AI Edition")
clock = pygame.time.Clock()

# Load logo image
logo_path = os.path.join(PROJECT_DIR, "images", "logo.png")
try:
    image = pygame.image.load(logo_path)
    image = pygame.transform.scale(image, (240, 120))
except (FileNotFoundError, pygame.error):
    image = pygame.Surface((240, 120))
    image.fill((30, 30, 60))

# Map dimensions (customizable)
map_width = 16
map_height = 12
ghost_count = 2

# Calculate tile size based on map dimensions
def calculate_tile_size(width, height):
    """Calculate tile size to fit the screen."""
    max_width = 900
    max_height = 680
    tile_w = max_width // width
    tile_h = max_height // height
    return min(tile_w, tile_h, 50)

game_tile = calculate_tile_size(map_width, map_height)

# Key class
class Key:
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.collected = False
    
    def draw(self, sc, tile_size):
        if self.collected:
            return
        px = self.x * tile_size + MAZE_OFFSET + tile_size // 2
        py = self.y * tile_size + 2 + tile_size // 2
        
        key_size = tile_size // 3
        pygame.draw.circle(sc, pygame.Color(self.color), (px, py - key_size // 2), key_size // 2, 3)
        pygame.draw.line(sc, pygame.Color(self.color), (px, py), (px, py + key_size), 3)
        pygame.draw.line(sc, pygame.Color(self.color), (px, py + key_size // 2), (px + key_size // 3, py + key_size // 2), 3)
        pygame.draw.line(sc, pygame.Color(self.color), (px, py + key_size), (px + key_size // 3, py + key_size), 3)

# Create initial grid with all walls
def create_grid_with_walls(cols, rows):
    """Create grid with all walls intact (for maze generation)."""
    grid = []
    for row in range(rows):
        for col in range(cols):
            cell = Cell(col, row)
            cell.generated = False
            cell.has_dot = False
            cell.walls = {"top": True, "bottom": True, "left": True, "right": True}
            cell.is_obstacle = False
            grid.append(cell)
    return grid

def get_cell(grid, x, y, cols, rows):
    """Get cell at position, return None if out of bounds."""
    if 0 <= x < cols and 0 <= y < rows:
        return grid[y * cols + x]
    return None

def get_unvisited_neighbors(grid, cell, cols, rows):
    """Get list of unvisited neighboring cells."""
    neighbors = []
    x, y = cell.col, cell.row
    
    # Check all 4 directions
    directions = [(0, -1, "top", "bottom"), (0, 1, "bottom", "top"), 
                  (-1, 0, "left", "right"), (1, 0, "right", "left")]
    
    for dx, dy, wall1, wall2 in directions:
        neighbor = get_cell(grid, x + dx, y + dy, cols, rows)
        if neighbor and not neighbor.generated:
            neighbors.append((neighbor, wall1, wall2))
    
    return neighbors

def remove_wall_between(cell1, cell2, wall1, wall2):
    """Remove wall between two adjacent cells."""
    cell1.walls[wall1] = False
    cell2.walls[wall2] = False

def generate_maze_dfs(grid, cols, rows):
    """Generate maze using randomized DFS algorithm."""
    # Start from (0, 0)
    start_cell = grid[0]
    start_cell.generated = True
    stack = [start_cell]
    
    while stack:
        current = stack[-1]
        neighbors = get_unvisited_neighbors(grid, current, cols, rows)
        
        if neighbors:
            # Choose random neighbor
            neighbor, wall1, wall2 = random.choice(neighbors)
            # Remove wall between current and neighbor
            remove_wall_between(current, neighbor, wall1, wall2)
            neighbor.generated = True
            stack.append(neighbor)
        else:
            stack.pop()

def add_extra_paths(grid, cols, rows, extra_paths_ratio=0.15):
    """Remove additional walls to create multiple paths in the maze."""
    # Collect all internal walls that can be removed
    removable_walls = []
    
    for cell in grid:
        x, y = cell.col, cell.row
        
        # Check right wall (not on right edge)
        if x < cols - 1 and cell.walls["right"]:
            right_cell = get_cell(grid, x + 1, y, cols, rows)
            if right_cell:
                removable_walls.append((cell, right_cell, "right", "left"))
        
        # Check bottom wall (not on bottom edge)
        if y < rows - 1 and cell.walls["bottom"]:
            bottom_cell = get_cell(grid, x, y + 1, cols, rows)
            if bottom_cell:
                removable_walls.append((cell, bottom_cell, "bottom", "top"))
    
    # Remove a portion of walls to create loops/multiple paths
    num_to_remove = int(len(removable_walls) * extra_paths_ratio)
    walls_to_remove = random.sample(removable_walls, min(num_to_remove, len(removable_walls)))
    
    for cell1, cell2, wall1, wall2 in walls_to_remove:
        remove_wall_between(cell1, cell2, wall1, wall2)

def create_maze_with_multiple_paths(cols, rows):
    """Create a maze with multiple possible paths."""
    grid = create_grid_with_walls(cols, rows)
    
    # Generate base maze using DFS
    generate_maze_dfs(grid, cols, rows)
    
    # Add extra paths by removing some walls (creates multiple routes)
    extra_ratio = 0.2 if cols * rows > 150 else 0.15
    add_extra_paths(grid, cols, rows, extra_ratio)
    
    return grid

def get_valid_key_positions(grid, cols, rows, count=3):
    """Get valid positions for keys (not on obstacles or start/end)."""
    valid_positions = []
    excluded = [(0, 0), (cols - 1, rows - 1)]
    
    for cell in grid:
        if not cell.is_obstacle and (cell.col, cell.row) not in excluded:
            # Avoid positions too close to start
            if cell.col + cell.row > 3:
                valid_positions.append((cell.col, cell.row))
    
    # Select random positions spread across the map
    if len(valid_positions) < count:
        return valid_positions
    
    # Divide map into regions and pick from each
    positions = []
    region_size = len(valid_positions) // count
    for i in range(count):
        start_idx = i * region_size
        end_idx = (i + 1) * region_size if i < count - 1 else len(valid_positions)
        pos = random.choice(valid_positions[start_idx:end_idx])
        positions.append(pos)
    
    return positions

# Game state
grid_cells = create_maze_with_multiple_paths(map_width, map_height)
pacman = None
ghosts = []
keys = []
game_mode = "menu"  # menu, playing, won, gameover, ghost_settings
pending_direction = None
move_delay = 0
PACMAN_SPEED = 8  # Higher = slower

# Ghost settings (customizable per ghost)
# Format: {ghost_index: {"speed": value, "algorithm": algo, "behavior": mode}}
ghost_settings = {
    0: {"speed": 12, "algorithm": "bfs", "behavior": "chase"},      # Blinky - Red
    1: {"speed": 15, "algorithm": "bfs", "behavior": "predict"},    # Pinky - Pink
    2: {"speed": 18, "algorithm": "bfs", "behavior": "flank"},      # Inky - Cyan
    3: {"speed": 20, "algorithm": "bfs", "behavior": "patrol"}      # Clyde - Orange
}
ALGORITHM_OPTIONS = ["bfs", "astar", "dfs", "gbfs", "dijkstra"]
ALGORITHM_NAMES = {
    "bfs": "BFS", 
    "astar": "A*", 
    "dfs": "DFS",
    "gbfs": "GBFS",
    "dijkstra": "Dijkstra"
}
BEHAVIOR_OPTIONS = ["chase", "predict", "flank", "random", "patrol"]
BEHAVIOR_NAMES = {
    "chase": "Chase", 
    "predict": "Predict", 
    "flank": "Flank", 
    "random": "Random",
    "patrol": "Patrol"
}
GHOST_COLORS = ["#FF0000", "#FFB8FF", "#00FFFF", "#FFB852"]
GHOST_NAMES_LIST = ["Blinky", "Pinky", "Inky", "Clyde"]
selected_ghost = 0  # Currently selected ghost for editing

# UI Button rectangles
play_btn = None
retry_btn = None
width_minus_btn = None
width_plus_btn = None
height_minus_btn = None
height_plus_btn = None
ghost1_btn = None
ghost2_btn = None
ghost3_btn = None
ghost4_btn = None
ghost_settings_btn = None
speed_minus_btn = None
speed_plus_btn = None
algo_prev_btn = None
algo_next_btn = None
behavior_prev_btn = None
behavior_next_btn = None
back_btn = None
ghost_select_btns = [None, None, None, None]  # Per-ghost selection buttons

def reset_game():
    """Reset game to start playing."""
    global grid_cells, pacman, ghosts, keys, game_mode, game_tile, pending_direction, move_delay
    
    game_tile = calculate_tile_size(map_width, map_height)
    
    # Generate maze with multiple paths
    grid_cells = create_maze_with_multiple_paths(map_width, map_height)
    
    # Create Pacman at start
    pacman = Pacman(0, 0)
    
    # Create ghosts using individual custom settings
    ghosts = []
    
    for i in range(min(ghost_count, 4)):
        gx = map_width - 2 - (i % 2)
        gy = 1 + (i // 2)
        # Use individual ghost settings
        speed = ghost_settings[i]["speed"]
        algorithm = ghost_settings[i]["algorithm"]
        behavior = ghost_settings[i]["behavior"]
        ghost = Ghost(gx, gy, GHOST_COLORS[i], speed)
        ghost.name = GHOST_NAMES_LIST[i]
        ghost.algorithm = algorithm
        ghost.behavior = behavior
        
        ghosts.append(ghost)
    
    # Create keys at valid positions
    key_positions = get_valid_key_positions(grid_cells, map_width, map_height, 3)
    key_colors = [("#FFD700", "Gold"), ("#00BFFF", "Blue"), ("#FF4444", "Red")]
    keys = []
    for i, (kx, ky) in enumerate(key_positions):
        color, name = key_colors[i]
        keys.append(Key(kx, ky, color, name))
    
    game_mode = "playing"
    pending_direction = None
    move_delay = 0

# Drawing functions
def draw_small_button(sc, text, x, y, w, h, color, selected=False):
    """Draw a small button."""
    rect = pygame.Rect(x, y, w, h)
    border_color = "#FFFFFF" if selected else "#888888"
    pygame.draw.rect(sc, pygame.Color(color), rect)
    pygame.draw.rect(sc, pygame.Color(border_color), rect, 2 if selected else 1)
    
    font = pygame.font.SysFont(FONT, 14, bold=True)
    text_surf = font.render(text, True, "#FFFFFF")
    text_rect = text_surf.get_rect(center=rect.center)
    sc.blit(text_surf, text_rect)
    return rect

def draw_button(sc, text, x, y, color="#FFD700", width=150, height=40):
    """Draw a button and return its rect."""
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(sc, pygame.Color(color), rect, border_radius=5)
    pygame.draw.rect(sc, pygame.Color("#FFFFFF"), rect, 2, border_radius=5)
    
    font = pygame.font.SysFont(FONT, 18, bold=True)
    text_surf = font.render(text, True, "#000000")
    text_rect = text_surf.get_rect(center=rect.center)
    sc.blit(text_surf, text_rect)
    return rect

def draw_map_custom(grid, sc, tile_size, cols, rows):
    """Draw the maze with walls."""
    wall_color = pygame.Color("#2244AA")
    wall_thickness = max(2, tile_size // 12)
    
    for cell in grid:
        x = cell.col * tile_size + MAZE_OFFSET
        y = cell.row * tile_size + 2
        
        # Draw floor
        pygame.draw.rect(sc, pygame.Color("#111122"), (x, y, tile_size, tile_size))
        
        # Draw all walls
        if cell.walls["top"]:
            pygame.draw.line(sc, wall_color, (x, y), (x + tile_size, y), wall_thickness)
        if cell.walls["bottom"]:
            pygame.draw.line(sc, wall_color, (x, y + tile_size), (x + tile_size, y + tile_size), wall_thickness)
        if cell.walls["left"]:
            pygame.draw.line(sc, wall_color, (x, y), (x, y + tile_size), wall_thickness)
        if cell.walls["right"]:
            pygame.draw.line(sc, wall_color, (x + tile_size, y), (x + tile_size, y + tile_size), wall_thickness)

def draw_goal(sc, cols, rows, tile_size):
    """Draw the goal position."""
    gx = (cols - 1) * tile_size + MAZE_OFFSET + tile_size // 2
    gy = (rows - 1) * tile_size + 2 + tile_size // 2
    
    pygame.draw.circle(sc, pygame.Color("#00FF00"), (gx, gy), tile_size // 3)
    pygame.draw.circle(sc, pygame.Color("#00AA00"), (gx, gy), tile_size // 3, 2)
    
    font = pygame.font.SysFont(FONT, tile_size // 3, bold=True)
    text = font.render("EXIT", True, "#000000")
    text_rect = text.get_rect(center=(gx, gy))
    sc.blit(text, text_rect)

def draw_game_info(sc, pacman, game_mode, keys_list, ghosts_list):
    """Draw game information panel."""
    info_font = pygame.font.SysFont(FONT, 16, bold=True)
    
    # Score
    score_text = info_font.render(f"Score: {pacman.score}", True, "#FFFFFF")
    sc.blit(score_text, (20, 400))
    
    # Keys collected
    key_y = 425
    collected_text = info_font.render("Keys:", True, "#FFFFFF")
    sc.blit(collected_text, (20, key_y))
    
    for i, key in enumerate(keys_list):
        color = key.color if key.collected else "#444444"
        pygame.draw.circle(sc, pygame.Color(color), (80 + i * 30, key_y + 8), 8)
        if key.collected:
            pygame.draw.circle(sc, pygame.Color("#FFFFFF"), (80 + i * 30, key_y + 8), 8, 2)
    
    # Game status
    if game_mode == "won":
        win_font = pygame.font.SysFont(FONT, 24, bold=True)
        win_text = win_font.render("YOU WIN!", True, "#00FF00")
        sc.blit(win_text, (20, 460))
    elif game_mode == "gameover":
        lose_font = pygame.font.SysFont(FONT, 24, bold=True)
        lose_text = lose_font.render("GAME OVER!", True, "#FF0000")
        sc.blit(lose_text, (20, 460))

def draw_pacman_custom(pacman, sc, tile_size):
    """Draw Pacman with animation."""
    px = pacman.x * tile_size + MAZE_OFFSET + tile_size // 2
    py = pacman.y * tile_size + 2 + tile_size // 2
    radius = tile_size // 2 - 3
    
    mouth_angle = 30
    
    if pacman.direction == "right":
        start_angle, end_angle = mouth_angle, 360 - mouth_angle
    elif pacman.direction == "left":
        start_angle, end_angle = 180 + mouth_angle, 180 - mouth_angle + 360
    elif pacman.direction == "up":
        start_angle, end_angle = 90 + mouth_angle, 90 - mouth_angle + 360
    else:
        start_angle, end_angle = 270 + mouth_angle, 270 - mouth_angle + 360
    
    import math
    points = [(px, py)]
    for angle in range(int(start_angle), int(end_angle), 5):
        rad = math.radians(angle)
        points.append((px + radius * math.cos(rad), py - radius * math.sin(rad)))
    if len(points) > 2:
        pygame.draw.polygon(sc, pygame.Color(PACMAN_COLOR), points)

def draw_ghost_custom(ghost, sc, tile_size):
    """Draw ghost."""
    px = ghost.x * tile_size + MAZE_OFFSET + tile_size // 2
    py = ghost.y * tile_size + 2 + tile_size // 2
    radius = tile_size // 2 - 3
    
    pygame.draw.circle(sc, pygame.Color(ghost.color), (px, py - 2), radius)
    pygame.draw.rect(sc, pygame.Color(ghost.color), (px - radius, py - 2, radius * 2, radius))
    
    eye_size = max(3, radius // 4)
    pupil_size = max(1, eye_size // 2)
    eye_offset = radius // 3
    
    pupil_dx, pupil_dy = 0, 0
    if ghost.direction == "left": pupil_dx = -1
    elif ghost.direction == "right": pupil_dx = 1
    elif ghost.direction == "up": pupil_dy = -1
    elif ghost.direction == "down": pupil_dy = 1
    
    pygame.draw.circle(sc, "#FFFFFF", (px - eye_offset, py - 3), eye_size)
    pygame.draw.circle(sc, "#0000FF", (px - eye_offset + pupil_dx, py - 3 + pupil_dy), pupil_size)
    pygame.draw.circle(sc, "#FFFFFF", (px + eye_offset, py - 3), eye_size)
    pygame.draw.circle(sc, "#0000FF", (px + eye_offset + pupil_dx, py - 3 + pupil_dy), pupil_size)

def check_key_collision(pacman, keys_list):
    """Check if Pacman collects a key."""
    for key in keys_list:
        if not key.collected and pacman.x == key.x and pacman.y == key.y:
            key.collected = True
            pacman.score += 50

def check_win_condition(pacman, keys_list, cols, rows):
    """Check if player won."""
    all_keys = all(k.collected for k in keys_list)
    at_exit = pacman.x == cols - 1 and pacman.y == rows - 1
    return all_keys and at_exit

# Main game loop
while True:
    sc.fill(pygame.Color(BACKGROUND_COLOR))
    sc.blit(image, (3, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        
        if event.type == pygame.KEYDOWN and game_mode == "playing" and pacman:
            if event.key == pygame.K_UP:
                pending_direction = "up"
            elif event.key == pygame.K_DOWN:
                pending_direction = "down"
            elif event.key == pygame.K_LEFT:
                pending_direction = "left"
            elif event.key == pygame.K_RIGHT:
                pending_direction = "right"
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Width buttons (menu only)
            if width_minus_btn and width_minus_btn.collidepoint(mouse_pos) and game_mode == "menu":
                map_width = max(8, map_width - 2)
                game_tile = calculate_tile_size(map_width, map_height)
                grid_cells = create_maze_with_multiple_paths(map_width, map_height)
            elif width_plus_btn and width_plus_btn.collidepoint(mouse_pos) and game_mode == "menu":
                map_width = min(28, map_width + 2)
                game_tile = calculate_tile_size(map_width, map_height)
                grid_cells = create_maze_with_multiple_paths(map_width, map_height)
            
            # Height buttons (menu only)
            elif height_minus_btn and height_minus_btn.collidepoint(mouse_pos) and game_mode == "menu":
                map_height = max(6, map_height - 2)
                game_tile = calculate_tile_size(map_width, map_height)
                grid_cells = create_maze_with_multiple_paths(map_width, map_height)
            elif height_plus_btn and height_plus_btn.collidepoint(mouse_pos) and game_mode == "menu":
                map_height = min(18, map_height + 2)
                game_tile = calculate_tile_size(map_width, map_height)
                grid_cells = create_maze_with_multiple_paths(map_width, map_height)
            
            # Ghost count buttons (menu only)
            elif ghost1_btn and ghost1_btn.collidepoint(mouse_pos) and game_mode == "menu":
                ghost_count = 1
            elif ghost2_btn and ghost2_btn.collidepoint(mouse_pos) and game_mode == "menu":
                ghost_count = 2
            elif ghost3_btn and ghost3_btn.collidepoint(mouse_pos) and game_mode == "menu":
                ghost_count = 3
            elif ghost4_btn and ghost4_btn.collidepoint(mouse_pos) and game_mode == "menu":
                ghost_count = 4
            
            # Ghost settings button (menu only)
            elif ghost_settings_btn and ghost_settings_btn.collidepoint(mouse_pos) and game_mode == "menu":
                game_mode = "ghost_settings"
            
            # Ghost settings controls
            elif game_mode == "ghost_settings":
                # Ghost selection buttons
                for i in range(4):
                    if ghost_select_btns[i] and ghost_select_btns[i].collidepoint(mouse_pos):
                        selected_ghost = i
                        break
                
                # Speed controls for selected ghost
                if speed_minus_btn and speed_minus_btn.collidepoint(mouse_pos):
                    ghost_settings[selected_ghost]["speed"] = max(5, ghost_settings[selected_ghost]["speed"] - 1)
                elif speed_plus_btn and speed_plus_btn.collidepoint(mouse_pos):
                    ghost_settings[selected_ghost]["speed"] = min(40, ghost_settings[selected_ghost]["speed"] + 1)
                
                # Algorithm controls for selected ghost
                elif algo_prev_btn and algo_prev_btn.collidepoint(mouse_pos):
                    current_idx = ALGORITHM_OPTIONS.index(ghost_settings[selected_ghost]["algorithm"])
                    ghost_settings[selected_ghost]["algorithm"] = ALGORITHM_OPTIONS[(current_idx - 1) % len(ALGORITHM_OPTIONS)]
                elif algo_next_btn and algo_next_btn.collidepoint(mouse_pos):
                    current_idx = ALGORITHM_OPTIONS.index(ghost_settings[selected_ghost]["algorithm"])
                    ghost_settings[selected_ghost]["algorithm"] = ALGORITHM_OPTIONS[(current_idx + 1) % len(ALGORITHM_OPTIONS)]
                
                # Behavior controls for selected ghost
                elif behavior_prev_btn and behavior_prev_btn.collidepoint(mouse_pos):
                    current_idx = BEHAVIOR_OPTIONS.index(ghost_settings[selected_ghost]["behavior"])
                    ghost_settings[selected_ghost]["behavior"] = BEHAVIOR_OPTIONS[(current_idx - 1) % len(BEHAVIOR_OPTIONS)]
                elif behavior_next_btn and behavior_next_btn.collidepoint(mouse_pos):
                    current_idx = BEHAVIOR_OPTIONS.index(ghost_settings[selected_ghost]["behavior"])
                    ghost_settings[selected_ghost]["behavior"] = BEHAVIOR_OPTIONS[(current_idx + 1) % len(BEHAVIOR_OPTIONS)]
                
                elif back_btn and back_btn.collidepoint(mouse_pos):
                    game_mode = "menu"
            
            # Play button (menu)
            elif play_btn and play_btn.collidepoint(mouse_pos) and game_mode == "menu":
                reset_game()
            
            # Retry button (game over or won)
            elif retry_btn and retry_btn.collidepoint(mouse_pos) and game_mode in ["gameover", "won"]:
                game_mode = "menu"
    
    # Handle movement (only on KEYDOWN, not continuous)
    if game_mode == "playing" and pacman:
        if move_delay <= 0 and pending_direction:
            if pacman.move(pending_direction, grid_cells):
                move_delay = PACMAN_SPEED
                check_key_collision(pacman, keys)
                if check_win_condition(pacman, keys, map_width, map_height):
                    game_mode = "won"
                    pacman.score += 200
            pending_direction = None
        elif move_delay > 0:
            move_delay -= 1
        
        # Check collision before ghosts move (catches Pacman walking into a ghost)
        if game_mode == "playing":
            for ghost in ghosts:
                if ghost.check_collision(pacman):
                    game_mode = "gameover"
                    break
        
        # Move ghosts and check collision after (catches ghost walking into Pacman)
        if game_mode == "playing":
            for ghost in ghosts:
                ghost.move(grid_cells, pacman)
                if ghost.check_collision(pacman):
                    game_mode = "gameover"
                    break
    
    # Draw settings panel
    settings_font = pygame.font.SysFont(FONT, 14, bold=True)
    small_font = pygame.font.SysFont(FONT, 12)
    
    if game_mode == "ghost_settings":
        # Ghost Settings Panel
        title = settings_font.render("GHOST SETTINGS", True, "#FFD700")
        sc.blit(title, (20, 125))
        
        # Ghost selection buttons
        select_label = settings_font.render("Select Ghost:", True, "#FFFFFF")
        sc.blit(select_label, (20, 150))
        
        for i in range(4):
            is_selected = (i == selected_ghost)
            ghost_select_btns[i] = draw_small_button(
                sc, GHOST_NAMES_LIST[i][:1], 
                20 + i * 42, 170, 38, 28, 
                GHOST_COLORS[i], is_selected
            )
        
        # Current ghost info
        current_name = GHOST_NAMES_LIST[selected_ghost]
        ghost_info = settings_font.render(f"Editing: {current_name}", True, GHOST_COLORS[selected_ghost])
        sc.blit(ghost_info, (20, 210))
        
        # Speed setting for selected ghost
        speed_label = settings_font.render("Speed:", True, "#FFFFFF")
        sc.blit(speed_label, (20, 240))
        
        current_speed = ghost_settings[selected_ghost]["speed"]
        speed_value = settings_font.render(f"{current_speed}", True, "#00FF00")
        sc.blit(speed_value, (85, 240))
        
        speed_minus_btn = draw_small_button(sc, "-", 110, 237, 28, 22, "#555555")
        speed_plus_btn = draw_small_button(sc, "+", 143, 237, 28, 22, "#555555")
        
        speed_hint = small_font.render("(Higher = Slower)", True, "#888888")
        sc.blit(speed_hint, (20, 262))
        
        # Algorithm setting for selected ghost
        algo_label = settings_font.render("Algorithm:", True, "#FFFFFF")
        sc.blit(algo_label, (20, 285))
        
        current_algo = ghost_settings[selected_ghost]["algorithm"]
        algo_value = settings_font.render(f"{ALGORITHM_NAMES[current_algo]}", True, "#00FF00")
        sc.blit(algo_value, (95, 285))
        
        algo_prev_btn = draw_small_button(sc, "<", 125, 282, 28, 22, "#555555")
        algo_next_btn = draw_small_button(sc, ">", 158, 282, 28, 22, "#555555")
        
        # Behavior setting for selected ghost
        behav_label = settings_font.render("Behavior:", True, "#FFFFFF")
        sc.blit(behav_label, (20, 315))
        
        current_behav = ghost_settings[selected_ghost]["behavior"]
        behav_value = settings_font.render(f"{BEHAVIOR_NAMES[current_behav]}", True, "#00FFFF")
        sc.blit(behav_value, (90, 315))
        
        behavior_prev_btn = draw_small_button(sc, "<", 155, 312, 28, 22, "#555555")
        behavior_next_btn = draw_small_button(sc, ">", 188, 312, 28, 22, "#555555")
        
        # Behavior descriptions
        behav_desc = {
            "chase": "Direct chase to Pacman",
            "predict": "Target 2 cells ahead",
            "flank": "Ambush from behind",
            "random": "Random movement",
            "patrol": "Patrol map corners"
        }
        desc_text = small_font.render(behav_desc[current_behav], True, "#888888")
        sc.blit(desc_text, (20, 340))
        
        # Show all ghosts summary
        summary_y = 365
        summary_label = small_font.render("All Ghosts:", True, "#AAAAAA")
        sc.blit(summary_label, (20, summary_y))
        for i in range(4):
            g_speed = ghost_settings[i]["speed"]
            g_algo = ALGORITHM_NAMES[ghost_settings[i]["algorithm"]]
            g_behav = BEHAVIOR_NAMES[ghost_settings[i]["behavior"]][:3]
            g_text = small_font.render(f"{GHOST_NAMES_LIST[i][:1]}: {g_algo} {g_behav}", True, GHOST_COLORS[i])
            sc.blit(g_text, (20 + (i % 2) * 95, summary_y + 18 + (i // 2) * 16))
        
        # Back button
        back_btn = draw_button(sc, "BACK", 20, 425, "#FF6600", 100, 35)
        
        # Clear other buttons
        play_btn = None
        ghost_settings_btn = None
    else:
        # Normal menu panel
        dim_label = settings_font.render("MAP SIZE:", True, "#FFFFFF")
        sc.blit(dim_label, (20, 125))
        
        width_label = settings_font.render(f"Width: {map_width}", True, "#AAAAAA")
        sc.blit(width_label, (20, 148))
        width_minus_btn = draw_small_button(sc, "-", 100, 145, 30, 22, "#555555")
        width_plus_btn = draw_small_button(sc, "+", 135, 145, 30, 22, "#555555")
        
        height_label = settings_font.render(f"Height: {map_height}", True, "#AAAAAA")
        sc.blit(height_label, (20, 175))
        height_minus_btn = draw_small_button(sc, "-", 100, 172, 30, 22, "#555555")
        height_plus_btn = draw_small_button(sc, "+", 135, 172, 30, 22, "#555555")
        
        ghost_label = settings_font.render("GHOSTS:", True, "#FFFFFF")
        sc.blit(ghost_label, (20, 205))
        ghost1_btn = draw_small_button(sc, "1", 20, 225, 35, 25, "#FF0000", ghost_count == 1)
        ghost2_btn = draw_small_button(sc, "2", 60, 225, 35, 25, "#FFB8FF", ghost_count == 2)
        ghost3_btn = draw_small_button(sc, "3", 100, 225, 35, 25, "#00FFFF", ghost_count == 3)
        ghost4_btn = draw_small_button(sc, "4", 140, 225, 35, 25, "#FFB852", ghost_count == 4)
        
        keys_info = settings_font.render("Collect 3 KEYS:", True, "#FFFFFF")
        sc.blit(keys_info, (20, 260))
        pygame.draw.circle(sc, "#FFD700", (30, 285), 8)
        pygame.draw.circle(sc, "#00BFFF", (70, 285), 8)
        pygame.draw.circle(sc, "#FF4444", (110, 285), 8)
        
        # Show AI algorithms in use
        algos_used = set(ghost_settings[i]["algorithm"] for i in range(min(ghost_count, 4)))
        algo_text = ", ".join(ALGORITHM_NAMES[a] for a in algos_used)
        ai_label = settings_font.render(f"AI: {algo_text}", True, "#00FF00")
        sc.blit(ai_label, (20, 310))
        
        # Ghost Settings button (menu only)
        if game_mode == "menu":
            ghost_settings_btn = draw_button(sc, "GHOST SETTINGS", 20, 340, "#9932CC", 150, 35)
            play_btn = draw_button(sc, "PLAY GAME", 20, 385, "#FFD700")
        else:
            ghost_settings_btn = None
            play_btn = None
        
        # Clear settings buttons
        speed_minus_btn = None
        speed_plus_btn = None
        algo_prev_btn = None
        algo_next_btn = None
        behavior_prev_btn = None
        behavior_next_btn = None
        back_btn = None
    
    # Retry button (game over or won)
    if game_mode in ["gameover", "won"]:
        retry_btn = draw_button(sc, "PLAY AGAIN", 20, 500, "#FF6600" if game_mode == "gameover" else "#00FF00")
    else:
        retry_btn = None

    # Draw the map
    draw_map_custom(grid_cells, sc, game_tile, map_width, map_height)
    
    # Draw start marker (menu and ghost_settings)
    if game_mode in ["menu", "ghost_settings"]:
        start_x = 0 * game_tile + MAZE_OFFSET + game_tile // 2
        start_y = 0 * game_tile + 2 + game_tile // 2
        pygame.draw.circle(sc, pygame.Color("#00FF00"), (start_x, start_y), 8)
    
    # Draw goal
    draw_goal(sc, map_width, map_height, game_tile)
    
    # Draw keys
    if game_mode in ["playing", "won", "gameover"]:
        for key in keys:
            key.draw(sc, game_tile)
    
    # Draw Pacman and ghosts
    if pacman and game_mode in ["playing", "won", "gameover"]:
        draw_pacman_custom(pacman, sc, game_tile)
        for ghost in ghosts:
            draw_ghost_custom(ghost, sc, game_tile)
        draw_game_info(sc, pacman, game_mode, keys, ghosts)

    pygame.display.flip()
    clock.tick(60)
