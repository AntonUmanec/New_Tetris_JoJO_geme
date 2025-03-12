import pygame
import random
import time

# Initialize pygame
pygame.init()
pygame.font.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_X = (SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2
GRID_Y = SCREEN_HEIGHT - (GRID_HEIGHT * BLOCK_SIZE) - 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Tetrimino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # J
    [[1, 1, 1], [0, 0, 1]],  # L
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Colors for each shape
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, BLUE, ORANGE, GREEN, RED]

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# Game clock
clock = pygame.time.Clock()

class Tetrimino:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_index]
        self.color = SHAPE_COLORS[self.shape_index]
        self.rotation = 0
    
    def rotate(self):
        # Transpose the matrix and reverse each row for clockwise rotation
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]
        
        # Check if rotation is valid
        if not self.collision(0, 0, rotated):
            self.shape = rotated
    
    def collision(self, dx=0, dy=0, shape=None):
        if shape is None:
            shape = self.shape
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pos_x = self.x + x + dx
                    pos_y = self.y + y + dy
                    
                    # Check if out of bounds
                    if (pos_x < 0 or pos_x >= GRID_WIDTH or 
                        pos_y >= GRID_HEIGHT or 
                        (pos_y >= 0 and grid[pos_y][pos_x])):
                        return True
        return False

class Game:
    def __init__(self):
        self.in_level_selection = True
        self.selected_level = 1
        self.reset()
    
    def reset(self, level=None):
        global grid
        grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = level if level is not None else self.selected_level
        self.lines_cleared = (self.level - 1) * 10  # Set lines cleared based on level
        self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)  # Adjust speed based on level
        self.last_fall_time = time.time()
    
    def new_piece(self):
        return Tetrimino(GRID_WIDTH // 2 - 1, 0)
    
    def lock_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    if self.current_piece.y + y < 0:
                        self.game_over = True
                        return
                    grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.color
        
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        # Check if the new piece can be placed
        if self.current_piece.collision():
            self.game_over = True
    
    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(grid[y]):
                lines_to_clear.append(y)
        
        if lines_to_clear:
            for line in lines_to_clear:
                del grid[line]
                grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            
            self.lines_cleared += len(lines_to_clear)
            self.score += (len(lines_to_clear) ** 2) * 100
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
    
    def move(self, dx, dy):
        if not self.current_piece.collision(dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False
    
    def drop(self):
        while self.move(0, 1):
            pass
        self.lock_piece()
    
    def update(self):
        current_time = time.time()
        if current_time - self.last_fall_time > self.fall_speed:
            if not self.move(0, 1):
                self.lock_piece()
            self.last_fall_time = current_time
    
    def draw_level_selection(self):
        # Draw background
        screen.fill(BLACK)
        
        # Draw title
        font_title = pygame.font.SysFont('Arial', 48)
        title_text = font_title.render("TETRIS", True, WHITE)
        screen.blit(title_text, 
                   (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 
                    100))
        
        # Draw level selection instructions
        font = pygame.font.SysFont('Arial', 36)
        select_text = font.render("Select Starting Level (1-10):", True, WHITE)
        screen.blit(select_text, 
                   (SCREEN_WIDTH // 2 - select_text.get_width() // 2, 
                    200))
        
        # Draw level buttons
        button_width = 50
        button_height = 50
        button_margin = 10
        total_width = (button_width + button_margin) * 10 - button_margin
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i in range(1, 11):
            button_x = start_x + (i - 1) * (button_width + button_margin)
            button_y = 300
            button_color = CYAN if i == self.selected_level else GRAY
            
            pygame.draw.rect(screen, button_color, 
                             (button_x, button_y, button_width, button_height))
            pygame.draw.rect(screen, WHITE, 
                             (button_x, button_y, button_width, button_height), 2)
            
            level_num = font.render(str(i), True, BLACK if i == self.selected_level else WHITE)
            screen.blit(level_num, 
                       (button_x + button_width // 2 - level_num.get_width() // 2, 
                        button_y + button_height // 2 - level_num.get_height() // 2))
        
        # Draw start game button
        start_button_width = 200
        start_button_height = 60
        start_button_x = (SCREEN_WIDTH - start_button_width) // 2
        start_button_y = 400
        
        pygame.draw.rect(screen, GREEN, 
                         (start_button_x, start_button_y, 
                          start_button_width, start_button_height))
        pygame.draw.rect(screen, WHITE, 
                         (start_button_x, start_button_y, 
                          start_button_width, start_button_height), 2)
        
        start_text = font.render("START", True, BLACK)
        screen.blit(start_text, 
                   (start_button_x + start_button_width // 2 - start_text.get_width() // 2, 
                    start_button_y + start_button_height // 2 - start_text.get_height() // 2))
        
        # Draw controls instructions
        font_small = pygame.font.SysFont('Arial', 20)
        controls_text1 = font_small.render("Controls: Arrow Keys to move, Up to rotate, Space to drop", True, WHITE)
        controls_text2 = font_small.render("Press R to restart after game over", True, WHITE)
        
        screen.blit(controls_text1, 
                   (SCREEN_WIDTH // 2 - controls_text1.get_width() // 2, 
                    500))
        screen.blit(controls_text2, 
                   (SCREEN_WIDTH // 2 - controls_text2.get_width() // 2, 
                    530))
    
    def handle_level_selection_click(self, pos):
        button_width = 50
        button_height = 50
        button_margin = 10
        total_width = (button_width + button_margin) * 10 - button_margin
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        # Check if a level button was clicked
        for i in range(1, 11):
            button_x = start_x + (i - 1) * (button_width + button_margin)
            button_y = 300
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            if button_rect.collidepoint(pos):
                self.selected_level = i
                return
        
        # Check if start button was clicked
        start_button_width = 200
        start_button_height = 60
        start_button_x = (SCREEN_WIDTH - start_button_width) // 2
        start_button_y = 400
        start_button_rect = pygame.Rect(start_button_x, start_button_y, start_button_width, start_button_height)
        
        if start_button_rect.collidepoint(pos):
            self.in_level_selection = False
            self.reset(self.selected_level)
    
    def draw_grid(self):
        # Draw background
        screen.fill(BLACK)
        
        # Draw grid border
        pygame.draw.rect(screen, WHITE, 
                         (GRID_X - 2, GRID_Y - 2, 
                          GRID_WIDTH * BLOCK_SIZE + 4, 
                          GRID_HEIGHT * BLOCK_SIZE + 4), 2)
        
        # Draw grid cells
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(screen, GRAY, 
                                 (GRID_X + x * BLOCK_SIZE, 
                                  GRID_Y + y * BLOCK_SIZE, 
                                  BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Draw locked pieces
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x]:
                    pygame.draw.rect(screen, grid[y][x], 
                                     (GRID_X + x * BLOCK_SIZE, 
                                      GRID_Y + y * BLOCK_SIZE, 
                                      BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, WHITE, 
                                     (GRID_X + x * BLOCK_SIZE, 
                                      GRID_Y + y * BLOCK_SIZE, 
                                      BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Draw current piece
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.current_piece.color, 
                                     (GRID_X + (self.current_piece.x + x) * BLOCK_SIZE, 
                                      GRID_Y + (self.current_piece.y + y) * BLOCK_SIZE, 
                                      BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, WHITE, 
                                     (GRID_X + (self.current_piece.x + x) * BLOCK_SIZE, 
                                      GRID_Y + (self.current_piece.y + y) * BLOCK_SIZE, 
                                      BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Draw next piece preview
        self.draw_next_piece()
        
        # Draw score and level
        font = pygame.font.SysFont('Arial', 24)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        lines_text = font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        
        screen.blit(score_text, (50, 50))
        screen.blit(level_text, (50, 90))
        screen.blit(lines_text, (50, 130))
        
        # Draw game over message
        if self.game_over:
            font = pygame.font.SysFont('Arial', 48)
            game_over_text = font.render("GAME OVER", True, RED)
            restart_text = font.render("Press R to restart", True, WHITE)
            
            screen.blit(game_over_text, 
                       (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                        SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
            screen.blit(restart_text, 
                       (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                        SCREEN_HEIGHT // 2 + game_over_text.get_height()))
    
    def draw_next_piece(self):
        # Draw next piece preview box
        next_box_x = SCREEN_WIDTH - 150
        next_box_y = 50
        next_box_width = 120
        next_box_height = 120
        
        pygame.draw.rect(screen, WHITE, 
                         (next_box_x, next_box_y, 
                          next_box_width, next_box_height), 2)
        
        font = pygame.font.SysFont('Arial', 24)
        next_text = font.render("Next:", True, WHITE)
        screen.blit(next_text, (next_box_x, next_box_y - 30))
        
        # Calculate center position for the next piece
        shape_width = len(self.next_piece.shape[0]) * BLOCK_SIZE
        shape_height = len(self.next_piece.shape) * BLOCK_SIZE
        
        center_x = next_box_x + (next_box_width - shape_width) // 2
        center_y = next_box_y + (next_box_height - shape_height) // 2
        
        # Draw the next piece
        for y, row in enumerate(self.next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.next_piece.color, 
                                     (center_x + x * BLOCK_SIZE, 
                                      center_y + y * BLOCK_SIZE, 
                                      BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, WHITE, 
                                     (center_x + x * BLOCK_SIZE, 
                                      center_y + y * BLOCK_SIZE, 
                                      BLOCK_SIZE, BLOCK_SIZE), 1)

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game.in_level_selection:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    game.handle_level_selection_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and game.selected_level > 1:
                        game.selected_level -= 1
                    elif event.key == pygame.K_RIGHT and game.selected_level < 10:
                        game.selected_level += 1
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        game.in_level_selection = False
                        game.reset(game.selected_level)
            elif not game.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        game.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        game.move(0, 1)
                    elif event.key == pygame.K_UP:
                        game.current_piece.rotate()
                    elif event.key == pygame.K_SPACE:
                        game.drop()
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    game.in_level_selection = True
        
        if game.in_level_selection:
            game.draw_level_selection()
        else:
            if not game.game_over:
                game.update()
            game.draw_grid()
            
        pygame.display.update()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
