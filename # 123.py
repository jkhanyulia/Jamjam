# The goal is to create a simple match 3 game using Python and Pygame.
# The game will feature a grid of colored emogis that the player can swap to create matches of three or more.
# The game will include basic mechanics such as swapping, matching, and clearing matched emogis.
# The game will also have a scoring system and a simple user interface.
# The game will use only standard libraries and Pygame for graphics and input handling.
# The game will be designed to be easily extendable for future features.
# The game will utilise five different colored emogis for variety.


import pygame
import random
from enum import Enum
from typing import List, Tuple, Optional, Set

# ============================================================================
# CONSTANTS
# ============================================================================

GRID_WIDTH = 8
GRID_HEIGHT = 8
TILE_SIZE = 60
PADDING = 10
WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE + PADDING * 2
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE + PADDING * 2 + 60  # Extra space for score
FPS = 60
ANIMATION_SPEED = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Emojis (representing different tile types)
EMOJIS = [""]

# ============================================================================
# TILE CLASS
# ============================================================================

class Tile:
    """Represents a single tile on the board."""
    
    def __init__(self, emoji: str, x: int, y: int):
        self.emoji = emoji
        self.x = x  # Grid position
        self.y = y
        self.render_x = x  # Rendering position (for animations)
        self.render_y = y
        self.falling = False
        self.fall_speed = 0
    
    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False
        return self.emoji == other.emoji
    
    def __hash__(self):
        return hash(self.emoji)
    
    def update(self):
        """Update tile animation state."""
        if self.falling:
            self.render_y += self.fall_speed
            if self.render_y >= self.y:
                self.render_y = self.y
                self.falling = False
                self.fall_speed = 0
    
    def start_fall(self):
        """Start the falling animation."""
        self.falling = True
        self.fall_speed = ANIMATION_SPEED
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw the tile on the surface."""
        # Draw background circle
        screen_x = PADDING + self.render_x * TILE_SIZE + TILE_SIZE // 2
        screen_y = PADDING + self.render_y * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(surface, GRAY, (screen_x, screen_y), TILE_SIZE // 2 - 5)
        
        # Draw emoji
        emoji_surface = font.render(self.emoji, True, BLACK)
        emoji_rect = emoji_surface.get_rect(center=(screen_x, screen_y))
        surface.blit(emoji_surface, emoji_rect)

# ============================================================================
# GAME BOARD CLASS
# ============================================================================

class Board:
    """Represents the game board."""
    
    def __init__(self):
        self.grid: List[List[Optional[Tile]]] = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.selected: Optional[Tuple[int, int]] = None
        self.score = 0
        self.initialize_board()
    
    def initialize_board(self):
        """Fill the board with random tiles."""
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                self.grid[y][x] = Tile(random.choice(EMOJIS), x, y)
        
        # Remove any initial matches
        while self.find_matches():
            self.clear_matches()
            self.apply_gravity()
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at position, with bounds checking."""
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            return self.grid[y][x]
        return None
    
    def swap_tiles(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Swap two tiles. Returns True if a match was found."""
        tile1 = self.get_tile(x1, y1)
        tile2 = self.get_tile(x2, y2)
        
        if not tile1 or not tile2:
            return False
        
        # Perform swap
        self.grid[y1][x1], self.grid[y2][x2] = self.grid[y2][x2], self.grid[y1][x1]
        tile1.x, tile1.y = x2, y2
        tile2.x, tile2.y = x1, y1
        
        # Check for matches
        if self.find_matches():
            self.clear_matches()
            return True
        else:
            # Swap back if no match
            self.grid[y1][x1], self.grid[y2][x2] = self.grid[y2][x2], self.grid[y1][x1]
            tile1.x, tile1.y = x1, y1
            tile2.x, tile2.y = x2, y2
            return False
    
    def find_matches(self) -> Set[Tuple[int, int]]:
        """Find all matched tiles. Returns a set of (x, y) positions."""
        matched = set()
        
        # Check horizontal matches
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH - 2):
                tile1 = self.get_tile(x, y)
                tile2 = self.get_tile(x + 1, y)
                tile3 = self.get_tile(x + 2, y)
                
                if tile1 and tile2 and tile3 and tile1 == tile2 == tile3:
                    matched.add((x, y))
                    matched.add((x + 1, y))
                    matched.add((x + 2, y))
        
        # Check vertical matches
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT - 2):
                tile1 = self.get_tile(x, y)
                tile2 = self.get_tile(x, y + 1)
                tile3 = self.get_tile(x, y + 2)
                
                if tile1 and tile2 and tile3 and tile1 == tile2 == tile3:
                    matched.add((x, y))
                    matched.add((x, y + 1))
                    matched.add((x, y + 2))
        
        return matched
    
    def clear_matches(self):
        """Remove matched tiles and update score."""
        matched = self.find_matches()
        if not matched:
            return
        
        # Clear matched tiles
        for x, y in matched:
            self.grid[y][x] = None
        
        # Update score
        self.score += len(matched) * 10
        
        # Apply gravity to fill gaps
        self.apply_gravity()
        
        # Recursively check for new matches
        if self.find_matches():
            self.clear_matches()
    
    def apply_gravity(self):
        """Apply gravity - tiles fall down to fill empty spaces."""
        for x in range(GRID_WIDTH):
            # Collect non-empty tiles from bottom to top
            tiles = []
            for y in range(GRID_HEIGHT - 1, -1, -1):
                if self.grid[y][x] is not None:
                    tiles.append(self.grid[y][x])
            
            # Clear column
            for y in range(GRID_HEIGHT):
                self.grid[y][x] = None
            
            # Place tiles from bottom, filling with new ones
            for i, tile in enumerate(tiles):
                new_y = GRID_HEIGHT - 1 - i
                self.grid[new_y][x] = tile
                tile.y = new_y
                if tile.render_y < new_y:
                    tile.start_fall()
            
            # Fill top with new tiles
            for y in range(GRID_HEIGHT - len(tiles)):
                new_tile = Tile(random.choice(EMOJIS), x, y)
                new_tile.render_y = -1
                new_tile.start_fall()
                self.grid[y][x] = new_tile
    
    def update(self):
        """Update all tiles."""
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    self.grid[y][x].update()
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click on the board."""
        x = (pos[0] - PADDING) // TILE_SIZE
        y = (pos[1] - PADDING) // TILE_SIZE
        
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            self.selected = None
            return
        
        if self.selected is None:
            self.selected = (x, y)
        else:
            sel_x, sel_y = self.selected
            # Check if adjacent
            if abs(sel_x - x) + abs(sel_y - y) == 1:
                if self.swap_tiles(sel_x, sel_y, x, y):
                    self.selected = None
                else:
                    self.selected = (x, y)
            else:
                self.selected = (x, y)
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw the board."""
        # Draw background
        pygame.draw.rect(surface, WHITE, (PADDING, PADDING, GRID_WIDTH * TILE_SIZE, GRID_HEIGHT * TILE_SIZE))
        
        # Draw grid
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(surface, DARK_GRAY, 
                            (PADDING + x * TILE_SIZE, PADDING), 
                            (PADDING + x * TILE_SIZE, PADDING + GRID_HEIGHT * TILE_SIZE))
        
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(surface, DARK_GRAY, 
                            (PADDING, PADDING + y * TILE_SIZE), 
                            (PADDING + GRID_WIDTH * TILE_SIZE, PADDING + y * TILE_SIZE))
        
        # Draw tiles
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    self.grid[y][x].draw(surface, font)
        
        # Draw selection highlight
        if self.selected:
            sel_x, sel_y = self.selected
            rect = pygame.Rect(PADDING + sel_x * TILE_SIZE, PADDING + sel_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, (255, 200, 0), rect, 3)
        
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        surface.blit(score_text, (PADDING, PADDING + GRID_HEIGHT * TILE_SIZE + 10))

# ============================================================================
# GAME CLASS
# ============================================================================

class Game:
    """Main game class."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Match 3 Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.board = Board()
        self.running = True
    
    def handle_events(self):
        """Handle user input and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.board.handle_click(event.pos)
    
    def update(self):
        """Update game state."""
        self.board.update()
    
    def draw(self):
        """Draw everything."""
        self.screen.fill(WHITE)
        self.board.draw(self.screen, self.font)
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    game = Game()
    game.run()
