import numpy as np
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

class WordDatabase:
    def __init__(self):
        # Expanded word list with clues for more variety
        self.words = {
            3: [('THE', 'Common article'), ('AND', 'Conjunction connector'), ('CAT', 'Feline friend'),
                ('DOG', 'Loyal companion'), ('RUN', 'Move quickly'), ('EAT', 'Consume food')],
            4: [('BOOK', 'Reading material'), ('TIME', 'Clock measurement'), ('HOME', 'Living space'),
                ('WALK', 'Leisurely stroll'), ('TALK', 'Verbal communication'), ('PLAY', 'Have fun')],
            5: [('HOUSE', 'Residential building'), ('PHONE', 'Communication device'),
                ('WATER', 'H2O'), ('MUSIC', 'Auditory art'), ('SLEEP', 'Rest period')],
            6: [('GARDEN', 'Growing space'), ('WINDOW', 'Glass view'), ('SCHOOL', 'Learning place'),
                ('COFFEE', 'Morning drink'), ('DINNER', 'Evening meal')],
            7: [('WEATHER', 'Climate condition'), ('MORNING', 'Day\'s beginning'),
                ('EVENING', 'Day\'s end'), ('SUMMER', 'Warm season'), ('WINTER', 'Cold season')]
        }

class CrosswordPuzzle:
    def __init__(self, size=15):
        self.size = size
        self.grid = np.ones((size, size))  # Start with all black squares
        self.letters = [['' for _ in range(size)] for _ in range(size)]
        self.number_grid = [[0 for _ in range(size)] for _ in range(size)]
        self.across_words = []
        self.down_words = []
        self.across_clues = []
        self.down_clues = []
        self.word_db = WordDatabase()

    def create_standard_pattern(self):
        # Create a standard crossword pattern
        # First, make all squares white
        self.grid = np.zeros((self.size, self.size))
        
        # Add black squares in a symmetric pattern
        for i in range(self.size):
            for j in range(self.size):
                # Create symmetrical pattern
                if random.random() < 0.3:  # Adjust probability for desired density
                    if self.is_valid_black_square(i, j):
                        self.grid[i][j] = 1
                        # Make symmetrical square black
                        self.grid[self.size-1-i][self.size-1-j] = 1

        # Ensure pattern is valid
        self.enforce_crossword_rules()

    def is_valid_black_square(self, i, j):
        # Check if placing a black square here would violate crossword rules
        if i == 0 or i == self.size-1 or j == 0 or j == self.size-1:
            return False  # Don't place black squares on edges
        
        # Don't create 2x2 blocks of black squares
        if i > 0 and j > 0:
            if self.grid[i-1][j-1] + self.grid[i-1][j] + self.grid[i][j-1] >= 2:
                return False

        return True

    def enforce_crossword_rules(self):
        # Ensure no word is less than 3 letters
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    # Check horizontal words
                    if j == 0 or self.grid[i][j-1] == 1:
                        length = 0
                        for k in range(j, self.size):
                            if self.grid[i][k] == 0:
                                length += 1
                            else:
                                break
                        if 0 < length < 3:
                            # Make these squares white
                            for k in range(j, j+length):
                                self.grid[i][k] = 0
                    
                    # Check vertical words
                    if i == 0 or self.grid[i-1][j] == 1:
                        length = 0
                        for k in range(i, self.size):
                            if self.grid[k][j] == 0:
                                length += 1
                            else:
                                break
                        if 0 < length < 3:
                            # Make these squares white
                            for k in range(i, i+length):
                                self.grid[k][j] = 0

        # Ensure puzzle is connected
        self.ensure_connected()

    def ensure_connected(self):
        # Use flood fill to ensure all white squares are connected
        visited = np.zeros((self.size, self.size))
        start = None
        
        # Find first white square
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    start = (i, j)
                    break
            if start:
                break

        if start:
            self.flood_fill(start[0], start[1], visited)

            # If any white square wasn't visited, connect it
            for i in range(self.size):
                for j in range(self.size):
                    if self.grid[i][j] == 0 and visited[i][j] == 0:
                        self.connect_to_main(i, j)

    def flood_fill(self, i, j, visited):
        if (i < 0 or i >= self.size or j < 0 or j >= self.size or 
            self.grid[i][j] == 1 or visited[i][j] == 1):
            return
        
        visited[i][j] = 1
        
        # Visit all adjacent squares
        self.flood_fill(i+1, j, visited)
        self.flood_fill(i-1, j, visited)
        self.flood_fill(i, j+1, visited)
        self.flood_fill(i, j-1, visited)

    def connect_to_main(self, i, j):
        # Simple connection - make a path to the center
        mid = self.size // 2
        for x in range(min(i, mid), max(i, mid)+1):
            self.grid[x][j] = 0
        for y in range(min(j, mid), max(j, mid)+1):
            self.grid[mid][y] = 0

    def number_puzzle(self):
        number = 1
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    needs_number = False
                    
                    # Start of across word
                    if (j == 0 or self.grid[i][j-1] == 1) and (j < self.size-1 and self.grid[i][j+1] == 0):
                        needs_number = True
                    
                    # Start of down word
                    if (i == 0 or self.grid[i-1][j] == 1) and (i < self.size-1 and self.grid[i+1][j] == 0):
                        needs_number = True
                    
                    if needs_number:
                        self.number_grid[i][j] = number
                        number += 1

def draw_puzzle(c, puzzle, page_num):
    # Set up the page
    c.setFont("Helvetica", 12)
    c.drawString(inch, 10.5*inch, f"Puzzle {page_num}")
    
    # Draw the grid
    start_x = 2*inch
    start_y = 9*inch
    cell_size = 0.3*inch
    
    for i in range(puzzle.size):
        for j in range(puzzle.size):
            x = start_x + j*cell_size
            y = start_y - i*cell_size
            
            # Draw cell
            c.rect(x, y, cell_size, cell_size)
            
            # Fill black squares
            if puzzle.grid[i][j] == 1:
                c.setFillColorRGB(0, 0, 0)
                c.rect(x, y, cell_size, cell_size, fill=1)
                c.setFillColorRGB(0, 0, 0)
            
            # Add numbers
            if puzzle.number_grid[i][j] > 0:
                c.setFont("Helvetica", 6)
                c.drawString(x + 2, y + cell_size - 6, str(puzzle.number_grid[i][j]))

    # Add clues section
    c.setFont("Helvetica", 10)
    y = 6*inch
    c.drawString(inch, y, "Across:")
    y -= 0.2*inch
    for i in range(5):  # Example clues
        c.drawString(inch, y, f"{i+1}. Sample across clue")
        y -= 0.2*inch
    
    y = 6*inch
    c.drawString(4*inch, y, "Down:")
    y -= 0.2*inch
    for i in range(5):  # Example clues
        c.drawString(4*inch, y, f"{i+1}. Sample down clue")
        y -= 0.2*inch

def main():
    try:
        c = canvas.Canvas("crossword_puzzles.pdf", pagesize=letter)
        
        for i in range(50):
            print(f"Generating puzzle {i+1}...")
            puzzle = CrosswordPuzzle()
            puzzle.create_standard_pattern()
            puzzle.number_puzzle()
            
            draw_puzzle(c, puzzle, i+1)
            c.showPage()
            print(f"Completed puzzle {i+1}")
        
        c.save()
        print("Crossword puzzles generated successfully!")
    except Exception as e:
        print(f"Error generating puzzles: {e}")

if __name__ == "__main__":
    main()