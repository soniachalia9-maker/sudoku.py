import pygame
import sys
import random
import time
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants for 4x4 Mini Sudoku
GRID_SIZE = 4
CELL_SIZE = 100
GRID_WIDTH = GRID_SIZE * CELL_SIZE
GRID_HEIGHT = GRID_SIZE * CELL_SIZE
MARGIN = 20
WINDOW_WIDTH = GRID_WIDTH + 2 * MARGIN + 200  # Extra space for controls
WINDOW_HEIGHT = GRID_HEIGHT + 2 * MARGIN + 50
FPS = 60




\

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
BLUE = (0, 120, 215)
RED = (255, 0, 0)
GREEN = (0, 150, 0)
YELLOW = (255, 255, 0)
BG_COLOR = (245, 245, 250)
GRID_COLOR = (150, 150, 200)
SELECTED_COLOR = (100, 150, 255)
CONFLICT_COLOR = (255, 200, 200)

class MiniSudoku:
    def __init__(self):
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Mini Sudoku - 4x4")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 40)
        self.small_font = pygame.font.SysFont('Arial', 24)
        self.timer_font = pygame.font.SysFont('Arial', 28)
        
        self.reset_game()
        
    def reset_game(self):
        """Reset the game state"""
        self.board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.solution = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.original_board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected_cell = None
        self.mistakes = 0
        self.max_mistakes = 3
        self.game_over = False
        self.game_won = False
        self.start_time = time.time()
        self.elapsed_time = 0
        self.generate_new_puzzle()
        
    def generate_new_puzzle(self):
        """Generate a new Sudoku puzzle"""
        # First generate a complete solution
        self.solution = self.generate_complete_board()
        
        # Copy to board and remove some numbers
        self.board = [row[:] for row in self.solution]
        self.original_board = [row[:] for row in self.solution]
        
        # Remove numbers to create puzzle (keep about 40% numbers)
        cells = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)]
        random.shuffle(cells)
        
        # Keep 6-8 numbers (37.5% to 50%)
        numbers_to_keep = random.randint(6, 8)
        for i in range(numbers_to_keep, len(cells)):
            row, col = cells[i]
            self.board[row][col] = 0
            self.original_board[row][col] = 0
            
    def generate_complete_board(self) -> List[List[int]]:
        """Generate a complete valid Sudoku board"""
        board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        def is_valid(board: List[List[int]], row: int, col: int, num: int) -> bool:
            # Check row
            if num in board[row]:
                return False
            
            # Check column
            for i in range(GRID_SIZE):
                if board[i][col] == num:
                    return False
            
            # Check 2x2 box
            box_row = (row // 2) * 2
            box_col = (col // 2) * 2
            for i in range(2):
                for j in range(2):
                    if board[box_row + i][box_col + j] == num:
                        return False
            
            return True
        
        def solve(board: List[List[int]]) -> bool:
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if board[row][col] == 0:
                        numbers = list(range(1, GRID_SIZE + 1))
                        random.shuffle(numbers)
                        for num in numbers:
                            if is_valid(board, row, col, num):
                                board[row][col] = num
                                if solve(board):
                                    return True
                                board[row][col] = 0
                        return False
            return True
        
        solve(board)
        return board
    
    def is_valid_move(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if a move is valid"""
        # Check row
        for c in range(GRID_SIZE):
            if board[row][c] == num and c != col:
                return False
        
        # Check column
        for r in range(GRID_SIZE):
            if board[r][col] == num and r != row:
                return False
        
        # Check 2x2 box
        box_row = (row // 2) * 2
        box_col = (col // 2) * 2
        for i in range(2):
            for j in range(2):
                r = box_row + i
                c = box_col + j
                if board[r][c] == num and (r != row or c != col):
                    return False
        
        return True
    
    def check_win(self) -> bool:
        """Check if the board is complete and correct"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] == 0:
                    return False
                if not self.is_valid_move(self.board, row, col, self.board[row][col]):
                    return False
        return True
    
    def get_conflicts(self, row: int, col: int, num: int) -> List[Tuple[int, int]]:
        """Get all conflicting cells for a number"""
        conflicts = []
        
        if num == 0:
            return conflicts
        
        # Check row
        for c in range(GRID_SIZE):
            if self.board[row][c] == num and c != col:
                conflicts.append((row, c))
        
        # Check column
        for r in range(GRID_SIZE):
            if self.board[r][col] == num and r != row:
                conflicts.append((r, col))
        
        # Check 2x2 box
        box_row = (row // 2) * 2
        box_col = (col // 2) * 2
        for i in range(2):
            for j in range(2):
                r = box_row + i
                c = box_col + j
                if self.board[r][c] == num and (r != row or c != col):
                    conflicts.append((r, c))
        
        return conflicts
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click"""
        if self.game_over or self.game_won:
            return
        
        x, y = pos
        grid_x = x - MARGIN
        grid_y = y - MARGIN - 30  # Account for timer space
        
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            col = grid_x // CELL_SIZE
            row = grid_y // CELL_SIZE
            self.selected_cell = (row, col)
        else:
            self.selected_cell = None
    
    def handle_key(self, key: int):
        """Handle keyboard input"""
        if self.game_over or self.game_won or not self.selected_cell:
            return
        
        row, col = self.selected_cell
        
        # Check if cell is editable (not original)
        if self.original_board[row][col] != 0:
            return
        
        if pygame.K_1 <= key <= pygame.K_4:
            num = key - pygame.K_0
            self.make_move(row, col, num)
        elif key == pygame.K_BACKSPACE or key == pygame.K_DELETE:
            self.make_move(row, col, 0)
        elif key == pygame.K_UP and row > 0:
            self.selected_cell = (row - 1, col)
        elif key == pygame.K_DOWN and row < GRID_SIZE - 1:
            self.selected_cell = (row + 1, col)
        elif key == pygame.K_LEFT and col > 0:
            self.selected_cell = (row, col - 1)
        elif key == pygame.K_RIGHT and col < GRID_SIZE - 1:
            self.selected_cell = (row, col + 1)
        elif key == pygame.K_SPACE:
            # Hint system - fill in one correct number
            self.provide_hint()
        elif key == pygame.K_r:
            self.reset_board()
    
    def make_move(self, row: int, col: int, num: int):
        """Make a move on the board"""
        if self.original_board[row][col] != 0:
            return
        
        old_num = self.board[row][col]
        self.board[row][col] = num
        
        # Check if move is valid
        if num != 0 and not self.is_valid_move(self.board, row, col, num):
            self.mistakes += 1
            if self.mistakes >= self.max_mistakes:
                self.game_over = True
        
        # Check for win
        if self.check_win():
            self.game_won = True
    
    def provide_hint(self):
        """Provide a hint by filling in one correct number"""
        if self.game_over or self.game_won:
            return
        
        # Find an empty cell
        empty_cells = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] == 0:
                    empty_cells.append((row, col))
        
        if empty_cells:
            row, col = random.choice(empty_cells)
            self.board[row][col] = self.solution[row][col]
            
            # Check for win
            if self.check_win():
                self.game_won = True
    
    def reset_board(self):
        """Reset board to original puzzle"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.board[row][col] = self.original_board[row][col]
        self.mistakes = 0
        self.game_over = False
        self.game_won = False
        self.selected_cell = None
    
    def draw(self):
        """Draw the game"""
        self.window.fill(BG_COLOR)
        
        # Draw timer
        self.elapsed_time = int(time.time() - self.start_time)
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        timer_text = f"Time: {minutes:02d}:{seconds:02d}"
        timer_surface = self.timer_font.render(timer_text, True, BLUE)
        self.window.blit(timer_surface, (MARGIN, 10))
        
        # Draw mistakes
        mistakes_text = f"Mistakes: {self.mistakes}/{self.max_mistakes}"
        mistakes_color = RED if self.mistakes > 0 else BLACK
        mistakes_surface = self.timer_font.render(mistakes_text, True, mistakes_color)
        self.window.blit(mistakes_surface, (WINDOW_WIDTH - MARGIN - 150, 10))
        
        # Draw grid background
        grid_rect = pygame.Rect(MARGIN, MARGIN + 30, GRID_WIDTH, GRID_HEIGHT)
        pygame.draw.rect(self.window, WHITE, grid_rect)
        pygame.draw.rect(self.window, GRID_COLOR, grid_rect, 3)
        
        # Draw grid lines and numbers
        for row in range(GRID_SIZE + 1):
            # Draw horizontal lines
            y = MARGIN + 30 + row * CELL_SIZE
            line_width = 3 if row % 2 == 0 else 1
            pygame.draw.line(self.window, GRID_COLOR, 
                           (MARGIN, y), (MARGIN + GRID_WIDTH, y), line_width)
            
            # Draw vertical lines
            x = MARGIN + row * CELL_SIZE
            line_width = 3 if row % 2 == 0 else 1
            pygame.draw.line(self.window, GRID_COLOR,
                           (x, MARGIN + 30), (x, MARGIN + 30 + GRID_HEIGHT), line_width)
        
        # Draw numbers and highlight conflicts
        conflicts = []
        if self.selected_cell:
            row, col = self.selected_cell
            if self.board[row][col] != 0:
                conflicts = self.get_conflicts(row, col, self.board[row][col])
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell_rect = pygame.Rect(
                    MARGIN + col * CELL_SIZE,
                    MARGIN + 30 + row * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                
                # Highlight selected cell
                if self.selected_cell == (row, col):
                    pygame.draw.rect(self.window, SELECTED_COLOR, cell_rect)
                
                # Highlight conflicting cells
                elif (row, col) in conflicts:
                    pygame.draw.rect(self.window, CONFLICT_COLOR, cell_rect)
                
                # Highlight original numbers
                elif self.original_board[row][col] != 0:
                    pygame.draw.rect(self.window, LIGHT_BLUE, cell_rect)
                
                # Draw number
                num = self.board[row][col]
                if num != 0:
                    color = BLUE if self.original_board[row][col] != 0 else BLACK
                    num_surface = self.font.render(str(num), True, color)
                    num_rect = num_surface.get_rect(center=cell_rect.center)
                    self.window.blit(num_surface, num_rect)
        
        # Draw control panel
        control_x = MARGIN + GRID_WIDTH + 20
        control_y = MARGIN + 30
        
        # Draw controls title
        controls_title = self.small_font.render("Controls", True, BLUE)
        self.window.blit(controls_title, (control_x, control_y))
        
        # Draw control instructions
        controls = [
            "1-4: Place number",
            "DEL: Clear cell",
            "Arrows: Move",
            "SPACE: Get hint",
            "R: Reset puzzle",
            "N: New puzzle",
            "ESC: Quit"
        ]
        
        for i, text in enumerate(controls):
            y_pos = control_y + 40 + i * 35
            text_surface = self.small_font.render(text, True, BLACK)
            self.window.blit(text_surface, (control_x, y_pos))
        
        # Draw numbers palette
        palette_y = control_y + 280
        palette_title = self.small_font.render("Click to select:", True, BLUE)
        self.window.blit(palette_title, (control_x, palette_y))
        
        for i in range(GRID_SIZE):
            num = i + 1
            palette_rect = pygame.Rect(control_x + i * 45, palette_y + 30, 40, 40)
            
            # Highlight if this number is selected
            if self.selected_cell:
                row, col = self.selected_cell
                if self.board[row][col] == num:
                    pygame.draw.rect(self.window, YELLOW, palette_rect)
                else:
                    pygame.draw.rect(self.window, WHITE, palette_rect)
            else:
                pygame.draw.rect(self.window, WHITE, palette_rect)
            
            pygame.draw.rect(self.window, BLUE, palette_rect, 2)
            num_surface = self.font.render(str(num), True, BLUE)
            num_rect = num_surface.get_rect(center=palette_rect.center)
            self.window.blit(num_surface, num_rect)
            
            # Store palette position for click detection
            self.palette_rects[num] = palette_rect
        
        # Draw game status
        status_y = WINDOW_HEIGHT - 100
        if self.game_won:
            status_text = "Congratulations! You won!"
            status_color = GREEN
            status_surface = self.timer_font.render(status_text, True, status_color)
            self.window.blit(status_surface, (MARGIN, status_y))
            
            # Draw restart button
            restart_rect = pygame.Rect(WINDOW_WIDTH - 200, status_y, 180, 40)
            pygame.draw.rect(self.window, GREEN, restart_rect, border_radius=5)
            pygame.draw.rect(self.window, BLACK, restart_rect, 2, border_radius=5)
            restart_text = self.small_font.render("Play Again", True, WHITE)
            restart_text_rect = restart_text.get_rect(center=restart_rect.center)
            self.window.blit(restart_text, restart_text_rect)
            self.restart_button = restart_rect
            
        elif self.game_over:
            status_text = f"Game Over! Too many mistakes."
            status_color = RED
            status_surface = self.timer_font.render(status_text, True, status_color)
            self.window.blit(status_surface, (MARGIN, status_y))
            
            # Show solution button
            solution_rect = pygame.Rect(WINDOW_WIDTH - 200, status_y, 180, 40)
            pygame.draw.rect(self.window, BLUE, solution_rect, border_radius=5)
            pygame.draw.rect(self.window, BLACK, solution_rect, 2, border_radius=5)
            solution_text = self.small_font.render("Show Solution", True, WHITE)
            solution_text_rect = solution_text.get_rect(center=solution_rect.center)
            self.window.blit(solution_text, solution_text_rect)
            self.solution_button = solution_rect
            
            # Restart button
            restart_rect = pygame.Rect(WINDOW_WIDTH - 200, status_y + 50, 180, 40)
            pygame.draw.rect(self.window, GREEN, restart_rect, border_radius=5)
            pygame.draw.rect(self.window, BLACK, restart_rect, 2, border_radius=5)
            restart_text = self.small_font.render("Try Again", True, WHITE)
            restart_text_rect = restart_text.get_rect(center=restart_rect.center)
            self.window.blit(restart_text, restart_text_rect)
            self.restart_button = restart_rect
        
        # Draw new puzzle button
        new_button_rect = pygame.Rect(control_x, WINDOW_HEIGHT - 60, 180, 40)
        pygame.draw.rect(self.window, BLUE, new_button_rect, border_radius=5)
        pygame.draw.rect(self.window, BLACK, new_button_rect, 2, border_radius=5)
        new_text = self.small_font.render("New Puzzle (N)", True, WHITE)
        new_text_rect = new_text.get_rect(center=new_button_rect.center)
        self.window.blit(new_text, new_text_rect)
        self.new_button = new_button_rect
    
    def handle_palette_click(self, pos: Tuple[int, int]):
        """Handle click on number palette"""
        for num, rect in self.palette_rects.items():
            if rect.collidepoint(pos):
                if self.selected_cell:
                    row, col = self.selected_cell
                    self.make_move(row, col, num)
                return True
        return False
    
    def show_solution(self):
        """Show the complete solution"""
        self.board = [row[:] for row in self.solution]
    
    def run(self):
        """Main game loop"""
        self.palette_rects = {}
        self.restart_button = None
        self.solution_button = None
        self.new_button = None
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Handle grid click
                        self.handle_click(event.pos)
                        
                        # Handle palette click
                        if not self.handle_palette_click(event.pos):
                            # Handle button clicks
                            if self.restart_button and self.restart_button.collidepoint(event.pos):
                                self.reset_game()
                            elif self.solution_button and self.solution_button.collidepoint(event.pos):
                                self.show_solution()
                            elif self.new_button and self.new_button.collidepoint(event.pos):
                                self.reset_game()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_n:
                        self.reset_game()
                    else:
                        self.handle_key(event.key)
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = MiniSudoku()
    game.run()

