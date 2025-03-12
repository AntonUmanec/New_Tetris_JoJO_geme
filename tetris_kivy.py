from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.core.image import Image as KivyImage
import random
import os

# Constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30

# Colors (RGBA format for Kivy)
BLACK = (0, 0, 0, 1)
WHITE = (1, 1, 1, 1)
GRAY = (0.5, 0.5, 0.5, 1)
RED = (1, 0, 0, 1)
GREEN = (0, 1, 0, 1)
BLUE = (0, 0, 1, 1)
CYAN = (0, 1, 1, 1)
MAGENTA = (1, 0, 1, 1)
YELLOW = (1, 1, 0, 1)
ORANGE = (1, 0.65, 0, 1)

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

# Load textures
TEXTURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'texturs')

# Available textures
TEXTURES = [
    KivyImage(os.path.join(TEXTURE_PATH, 'retengle.jpg')).texture,
    KivyImage(os.path.join(TEXTURE_PATH, 'Untitled design (1).jpg')).texture,
    KivyImage(os.path.join(TEXTURE_PATH, 'Untitled design (2).jpg')).texture,
    # Reuse textures for the remaining shapes
    KivyImage(os.path.join(TEXTURE_PATH, 'retengle.jpg')).texture,
    KivyImage(os.path.join(TEXTURE_PATH, 'Untitled design (1).jpg')).texture,
    KivyImage(os.path.join(TEXTURE_PATH, 'Untitled design (2).jpg')).texture,
    KivyImage(os.path.join(TEXTURE_PATH, 'retengle.jpg')).texture,
]

class Tetrimino:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_index]
        self.color = SHAPE_COLORS[self.shape_index]
        self.texture = TEXTURES[self.shape_index]
        self.rotation = 0
    
    def rotate(self, grid):
        # Transpose the matrix and reverse each row for clockwise rotation
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]
        
        # Check if rotation is valid
        if not self.collision(0, 0, rotated, grid):
            self.shape = rotated
    
    def collision(self, dx=0, dy=0, shape=None, grid=None):
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

class TetrisGrid(Widget):
    def __init__(self, **kwargs):
        super(TetrisGrid, self).__init__(**kwargs)
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.size = (GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
        self.current_piece = None
        self.next_piece = None
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.update_rect()
    
    def update_rect(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Draw grid background
            Color(0, 0, 0, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Draw grid lines
            Color(0.5, 0.5, 0.5, 1)
            for x in range(GRID_WIDTH + 1):
                Rectangle(pos=(self.pos[0] + x * CELL_SIZE, self.pos[1]), 
                          size=(1, self.height))
            for y in range(GRID_HEIGHT + 1):
                Rectangle(pos=(self.pos[0], self.pos[1] + y * CELL_SIZE), 
                          size=(self.width, 1))
    
    def draw(self):
        self.canvas.clear()
        
        # Draw locked pieces
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    with self.canvas:
                        # Use texture if it's a tuple containing texture
                        if isinstance(self.grid[y][x], tuple) and len(self.grid[y][x]) == 2:
                            texture, color = self.grid[y][x]
                            Color(*color)
                            Rectangle(pos=(self.pos[0] + x * CELL_SIZE, 
                                        self.pos[1] + (GRID_HEIGHT - 1 - y) * CELL_SIZE), 
                                    size=(CELL_SIZE, CELL_SIZE),
                                    texture=texture)
                        else:
                            # Fallback to color only
                            Color(*self.grid[y][x])
                            Rectangle(pos=(self.pos[0] + x * CELL_SIZE, 
                                        self.pos[1] + (GRID_HEIGHT - 1 - y) * CELL_SIZE), 
                                    size=(CELL_SIZE, CELL_SIZE))
        
        # Draw current piece
        if self.current_piece:
            for y, row in enumerate(self.current_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        with self.canvas:
                            Color(*self.current_piece.color)
                            Rectangle(pos=(self.pos[0] + (self.current_piece.x + x) * CELL_SIZE, 
                                        self.pos[1] + (GRID_HEIGHT - 1 - (self.current_piece.y + y)) * CELL_SIZE), 
                                    size=(CELL_SIZE, CELL_SIZE),
                                    texture=self.current_piece.texture)

class NextPieceWidget(Widget):
    def __init__(self, **kwargs):
        super(NextPieceWidget, self).__init__(**kwargs)
        self.next_piece = None
        self.size = (4 * CELL_SIZE, 4 * CELL_SIZE)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.update_rect()
    
    def update_rect(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 0, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            Color(1, 1, 1, 1)
            Rectangle(pos=self.pos, size=self.size, width=1.5)
    
    def draw(self):
        self.canvas.clear()
        
        if self.next_piece:
            shape_width = len(self.next_piece.shape[0]) * CELL_SIZE
            shape_height = len(self.next_piece.shape) * CELL_SIZE
            
            center_x = self.pos[0] + (self.width - shape_width) / 2
            center_y = self.pos[1] + (self.height - shape_height) / 2
            
            for y, row in enumerate(self.next_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        with self.canvas:
                            Color(*self.next_piece.color)
                            Rectangle(pos=(center_x + x * CELL_SIZE, 
                                          center_y + (len(self.next_piece.shape) - 1 - y) * CELL_SIZE), 
                                     size=(CELL_SIZE, CELL_SIZE),
                                     texture=self.next_piece.texture)

class LevelSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super(LevelSelectionScreen, self).__init__(**kwargs)
        self.selected_level = 1
        self.create_layout()
    
    def create_layout(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title_label = Label(text='TETRIS', font_size=48, size_hint=(1, 0.2))
        layout.add_widget(title_label)
        
        # Level selection label
        select_label = Label(text='Select Starting Level (1-10):', font_size=24, size_hint=(1, 0.1))
        layout.add_widget(select_label)
        
        # Level buttons
        level_layout = GridLayout(cols=10, spacing=5, size_hint=(1, 0.2))
        self.level_buttons = []
        
        for i in range(1, 11):
            btn = Button(text=str(i), background_color=(0, 1, 1, 1) if i == 1 else (0.5, 0.5, 0.5, 1))
            btn.bind(on_press=lambda btn, level=i: self.select_level(level))
            level_layout.add_widget(btn)
            self.level_buttons.append(btn)
        
        layout.add_widget(level_layout)
        
        # Start button
        start_btn = Button(text='START', font_size=32, size_hint=(0.5, 0.15), 
                          pos_hint={'center_x': 0.5}, background_color=(0, 1, 0, 1))
        start_btn.bind(on_press=self.start_game)
        layout.add_widget(start_btn)
        
        # Controls instructions
        controls_label1 = Label(text='Controls: Arrow Keys to move, Up to rotate, Space to drop', 
                              font_size=14, size_hint=(1, 0.1))
        controls_label2 = Label(text='Press R to restart after game over', 
                              font_size=14, size_hint=(1, 0.1))
        
        layout.add_widget(controls_label1)
        layout.add_widget(controls_label2)
        
        self.add_widget(layout)
    
    def select_level(self, level):
        # Update button colors
        for i, btn in enumerate(self.level_buttons):
            btn.background_color = (0, 1, 1, 1) if i+1 == level else (0.5, 0.5, 0.5, 1)
        
        self.selected_level = level
    
    def start_game(self, instance):
        game_screen = self.manager.get_screen('game')
        game_screen.start_game(self.selected_level)
        self.manager.current = 'game'

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5  # seconds per grid cell
        self.last_fall_time = 0
        self.create_layout()
        
        # Set up keyboard
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
    
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self.game_over:
            if keycode[1] == 'r':
                self.manager.current = 'level_selection'
            return True
        
        if keycode[1] == 'left':
            self.move(-1, 0)
        elif keycode[1] == 'right':
            self.move(1, 0)
        elif keycode[1] == 'down':
            self.move(0, 1)
        elif keycode[1] == 'up':
            self.current_piece.rotate(self.grid.grid)
        elif keycode[1] == 'spacebar':
            self.drop()
        return True
    
    def create_layout(self):
        layout = BoxLayout(orientation='horizontal', padding=10, spacing=10)
        
        # Left side - score, level, etc.
        left_layout = BoxLayout(orientation='vertical', size_hint=(0.3, 1))
        
        self.score_label = Label(text='Score: 0', font_size=24, halign='left', size_hint=(1, 0.1))
        self.level_label = Label(text='Level: 1', font_size=24, halign='left', size_hint=(1, 0.1))
        self.lines_label = Label(text='Lines: 0', font_size=24, halign='left', size_hint=(1, 0.1))
        
        left_layout.add_widget(self.score_label)
        left_layout.add_widget(self.level_label)
        left_layout.add_widget(self.lines_label)
        
        # Next piece preview
        next_label = Label(text='Next:', font_size=24, halign='left', size_hint=(1, 0.1))
        left_layout.add_widget(next_label)
        
        self.next_piece_widget = NextPieceWidget(size_hint=(1, 0.2))
        left_layout.add_widget(self.next_piece_widget)
        
        # Center - Tetris grid
        self.grid = TetrisGrid(size_hint=(None, None))
        
        # Right side - empty for now, for balance
        right_layout = BoxLayout(orientation='vertical', size_hint=(0.3, 1))
        
        # Game over label (initially hidden)
        self.game_over_label = Label(text='GAME OVER\nPress R to restart', 
                                   font_size=36, halign='center', opacity=0)
        right_layout.add_widget(self.game_over_label)
        
        # Add all layouts
        layout.add_widget(left_layout)
        layout.add_widget(self.grid)
        layout.add_widget(right_layout)
        
        self.add_widget(layout)
    
    def start_game(self, level):
        # Reset game state
        self.grid.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.game_over = False
        self.score = 0
        self.level = level
        self.lines_cleared = (level - 1) * 10
        self.fall_speed = max(0.05, 0.5 - (level - 1) * 0.05)
        
        # Reset labels
        self.score_label.text = f'Score: {self.score}'
        self.level_label.text = f'Level: {self.level}'
        self.lines_label.text = f'Lines: {self.lines_cleared}'
        self.game_over_label.opacity = 0
        
        # Create initial pieces
        self.grid.current_piece = self.new_piece()
        self.grid.next_piece = self.new_piece()
        self.next_piece_widget.next_piece = self.grid.next_piece
        
        # Start game loop
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, 1/60)
    
    def new_piece(self):
        return Tetrimino(GRID_WIDTH // 2 - 1, 0)
    
    def move(self, dx, dy):
        if not self.grid.current_piece.collision(dx, dy, None, self.grid.grid):
            self.grid.current_piece.x += dx
            self.grid.current_piece.y += dy
            return True
        return False
    
    def drop(self):
        while self.move(0, 1):
            pass
        self.lock_piece()
    
    def lock_piece(self):
        for y, row in enumerate(self.grid.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    if self.grid.current_piece.y + y < 0:
                        self.game_over = True
                        self.game_over_label.opacity = 1
                        Clock.unschedule(self.update)
                        return
                    self.grid.grid[self.grid.current_piece.y + y][self.grid.current_piece.x + x] = (self.grid.current_piece.texture, self.grid.current_piece.color)
        
        self.clear_lines()
        self.grid.current_piece = self.grid.next_piece
        self.grid.next_piece = self.new_piece()
        self.next_piece_widget.next_piece = self.grid.next_piece
        
        # Check if the new piece can be placed
        if self.grid.current_piece.collision(0, 0, None, self.grid.grid):
            self.game_over = True
            self.game_over_label.opacity = 1
            Clock.unschedule(self.update)
    
    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.grid.grid[y]):
                lines_to_clear.append(y)
        
        if lines_to_clear:
            for line in lines_to_clear:
                del self.grid.grid[line]
                self.grid.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            
            self.lines_cleared += len(lines_to_clear)
            self.score += (len(lines_to_clear) ** 2) * 100
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
            
            # Update labels
            self.score_label.text = f'Score: {self.score}'
            self.level_label.text = f'Level: {self.level}'
            self.lines_label.text = f'Lines: {self.lines_cleared}'
    
    def update(self, dt):
        if self.game_over:
            return
        
        self.last_fall_time += dt
        if self.last_fall_time > self.fall_speed:
            if not self.move(0, 1):
                self.lock_piece()
            self.last_fall_time = 0
        
        self.grid.draw()
        self.next_piece_widget.draw()

class TetrisApp(App):
    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(LevelSelectionScreen(name='level_selection'))
        sm.add_widget(GameScreen(name='game'))
        
        return sm

if __name__ == '__main__':
    TetrisApp().run()
