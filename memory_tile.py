import pygame
import random
import sys
from pygame.locals import *

pygame.init()


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 30
BG_COLOR = (230, 230, 250)
GRID_COLORS = [(255, 179, 186), (255, 223, 186), (255, 255, 186), 
               (186, 255, 201), (186, 225, 255), (225, 186, 255),
               (255, 160, 160), (200, 255, 200), (200, 200, 255)]
TILE_BACK = (189, 189, 189)

class MemoryTileGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Memory Tile Puzzle')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        
        self.set_difficulty("medium")  
        
        
        self.pairs_found = 0
        self.moves = 0
        self.first_tile = None
        self.second_tile = None
        self.waiting = False
        self.wait_time = 0
        self.board = []
        self.tile_images = []
        
        self._create_tile_images()
        self._new_game()
    
    def set_difficulty(self, difficulty):
        """Set the game difficulty"""
        size_map = {"easy": 4, "medium": 5, "hard": 6}
        self.board_size = size_map.get(difficulty, 5)
        self.tile_size = 720 // (self.board_size * 1.2)  
        self.tile_padding = 5
        self.margin_x = (WINDOW_WIDTH - (self.board_size * (self.tile_size + self.tile_padding))) // 2
        self.margin_y = 120
    
    def _create_tile_images(self):
        """Generate tile images with different colors/patterns"""
        
        required_pairs = (self.board_size * self.board_size) // 2
        pairs_per_color = max(1, (required_pairs + len(GRID_COLORS) - 1) // len(GRID_COLORS))
        
        self.tile_images = []
        for i in range(min(required_pairs, len(GRID_COLORS))):
            for variant in range(pairs_per_color):
                if len(self.tile_images) >= required_pairs:
                    break
                    
                
                surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                base_color = GRID_COLORS[i]
                pygame.draw.rect(surf, base_color, (0, 0, self.tile_size, self.tile_size))
                
                
                pattern_color = (min(255, base_color[0]+50), 
                                 min(255, base_color[1]+50), 
                                 min(255, base_color[2]+50))
                
                if variant % 3 == 0:
                    pygame.draw.circle(surf, pattern_color, 
                                      (self.tile_size//2, self.tile_size//2), 
                                      self.tile_size//3)
                elif variant % 3 == 1:
                    pygame.draw.rect(surf, pattern_color, 
                                    (self.tile_size//4, self.tile_size//4, 
                                     self.tile_size//2, self.tile_size//2))
                else:
                    pygame.draw.polygon(surf, pattern_color, [
                        (self.tile_size//2, self.tile_size//4),
                        (self.tile_size//4, 3*self.tile_size//4),
                        (3*self.tile_size//4, 3*self.tile_size//4)
                    ])
                
                self.tile_images.append(surf)
    
    def _new_game(self):
        """Initialize a new game board"""
        
        num_tiles = self.board_size * self.board_size
        tile_values = [i % len(self.tile_images) for i in range(num_tiles)]
        
        
        for i in range(len(self.tile_images)):
            count = tile_values.count(i)
            if count % 2 != 0:
                
                for j in range(len(tile_values)):
                    if tile_values[j] == i:
                        tile_values.append(i)
                        break
        
        random.shuffle(tile_values)
        
        
        self.board = []
        tile_index = 0
        for row in range(self.board_size):
            board_row = []
            for col in range(self.board_size):
                if tile_index < len(tile_values):
                    value = tile_values[tile_index]
                else:
                    value = 0 
                
                board_row.append({
                    'value': value,
                    'revealed': False,
                    'solved': False
                })
                tile_index += 1
            self.board.append(board_row)
        
        self.pairs_found = 0
        self.moves = 0
        self.first_tile = None
        self.second_tile = None
    
    def draw(self):
        """Draw the game elements"""
        self.screen.fill(BG_COLOR)
        
        title = self.font.render("Memory Tile Puzzle", True, (70, 70, 70))
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 20))
        
        moves_text = self.small_font.render(f"Moves: {self.moves}", True, (70, 70, 70))
        self.screen.blit(moves_text, (20, 20))
        
        pairs_text = self.small_font.render(f"Pairs Found: {self.pairs_found}/{self.board_size*self.board_size//2}", 
                                          True, (70, 70, 70))
        self.screen.blit(pairs_text, (WINDOW_WIDTH - pairs_text.get_width() - 20, 20))
        
        diff_text = self.small_font.render("Difficulty: (E)asy (M)edium (H)ard", True, (100, 100, 100))
        self.screen.blit(diff_text, (WINDOW_WIDTH//2 - diff_text.get_width()//2, 70))
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                tile = self.board[row][col]
                rect = pygame.Rect(
                    self.margin_x + col * (self.tile_size + self.tile_padding),
                    self.margin_y + row * (self.tile_size + self.tile_padding),
                    self.tile_size,
                    self.tile_size)
                
                if tile['solved']:
                    pygame.draw.rect(self.screen, (200, 255, 200), rect, border_radius=4)
                    pygame.draw.rect(self.screen, (0, 150, 0), rect, 3, border_radius=4)
                    self.screen.blit(self.tile_images[tile['value']], rect)
                elif tile['revealed']:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=4)
                    self.screen.blit(self.tile_images[tile['value']], rect)
                else:
                    pygame.draw.rect(self.screen, TILE_BACK, rect, border_radius=4)
                    pygame.draw.rect(self.screen, (100, 100, 100), rect, 2, border_radius=4)
    
    def handle_click(self, pos):
        """Handle tile clicks"""
        if self.waiting:
            return
            
        for row in range(self.board_size):
            for col in range(self.board_size):
                rect = pygame.Rect(
                    self.margin_x + col * (self.tile_size + self.tile_padding),
                    self.margin_y + row * (self.tile_size + self.tile_padding),
                    self.tile_size,
                    self.tile_size)
                
                if rect.collidepoint(pos) and not self.board[row][col]['revealed'] and not self.board[row][col]['solved']:
                    if self.first_tile is None:
                        self.first_tile = (row, col)
                        self.board[row][col]['revealed'] = True
                    elif self.second_tile is None and (row, col) != self.first_tile:
                        self.second_tile = (row, col)
                        self.board[row][col]['revealed'] = True
                        self.moves += 1
                        self._check_match()
    
    def _check_match(self):
        """Check if the revealed tiles match"""
        row1, col1 = self.first_tile
        row2, col2 = self.second_tile
        
        if self.board[row1][col1]['value'] == self.board[row2][col2]['value']:
            self.board[row1][col1]['solved'] = True
            self.board[row2][col2]['solved'] = True
            self.pairs_found += 1
            self.first_tile = None
            self.second_tile = None
            
            if self.pairs_found == (self.board_size * self.board_size) // 2:
                self._show_win_message()
        else:
            self.waiting = True
            self.wait_time = pygame.time.get_ticks() + 1000  
    
    def update(self):
        """Update game state"""
        if self.waiting and pygame.time.get_ticks() > self.wait_time:
            row1, col1 = self.first_tile
            row2, col2 = self.second_tile
            self.board[row1][col1]['revealed'] = False
            self.board[row2][col2]['revealed'] = False
            self.first_tile = None
            self.second_tile = None
            self.waiting = False
    
    def _show_win_message(self):
        """Display win message and restart option"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        win_surf = pygame.Surface((400, 200), pygame.SRCALPHA)
        win_surf.fill((240, 240, 240))
        pygame.draw.rect(win_surf, (0, 0, 0), win_surf.get_rect(), 2)
        
        win_text = self.font.render("Congratulations!", True, (0, 150, 0))
        moves_text = self.font.render(f"You won in {self.moves} moves", True, (70, 70, 70))
        restart_text = self.font.render("Press SPACE to play again", True, (70, 70, 70))
        
        win_surf.blit(win_text, (200 - win_text.get_width()//2, 40))
        win_surf.blit(moves_text, (200 - moves_text.get_width()//2, 90))
        win_surf.blit(restart_text, (200 - restart_text.get_width()//2, 140))
        
        self.screen.blit(win_surf, (WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2 - 100))
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        waiting = False
                        self._new_game()
                    elif event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            self.clock.tick(FPS)
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  
                        self.handle_click(event.pos)
                elif event.type == KEYDOWN:
                    if event.key == K_r:
                        self._new_game()
                    elif event.key == K_ESCAPE:
                        running = False
                    elif event.key in (K_e, K_m, K_h):
                        difficulty = {K_e: "easy", K_m: "medium", K_h: "hard"}[event.key]
                        self.set_difficulty(difficulty)
                        self._create_tile_images()
                        self._new_game()
            
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = MemoryTileGame()
    game.run()
