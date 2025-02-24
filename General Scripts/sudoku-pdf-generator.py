import random
import copy
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import os

def pattern(r, c, base):
    return (base * (r % base) + r // base + c) % (base * base)

def shuffle(s):
    return random.sample(s, len(s))

def generate_sudoku(base=3):
    # Generate a random complete Sudoku board
    side = base * base

    # Randomly shuffle rows, columns, and numbers
    r_base = range(base)
    rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
    cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
    nums = shuffle(range(1, side + 1))

    # Produce board using randomized baseline pattern
    board = [[nums[pattern(r, c, base)] for c in cols] for r in rows]

    return board

def remove_numbers(board, empty_slots, base=3):
    # Create a puzzle by removing numbers from the board
    side = base * base
    puzzle = copy.deepcopy(board)
    squares = side * side
    empties = empty_slots

    # Get positions to remove
    positions = random.sample(range(squares), empties)
    for pos in positions:
        row = pos // side
        col = pos % side
        puzzle[row][col] = 0

    return puzzle

def draw_sudoku(board, filename, base=3):
    side = base * base
    fig, ax = plt.subplots(figsize=(5, 5))
    # Create a blank 2D array
    puzzle_array = np.array(board)

    # Create grid
    for i in range(side + 1):
        lw = 2 if i % base == 0 else 1
        ax.axhline(i, lw=lw, color='black')
        ax.axvline(i, lw=lw, color='black')

    # Fill numbers
    for i in range(side):
        for j in range(side):
            num = puzzle_array[i][j]
            if num != 0:
                ax.text(j + 0.5, side - i - 0.5, str(num),
                        fontsize=16, ha='center', va='center')

    ax.axis('off')
    ax.set_xlim(0, side)
    ax.set_ylim(0, side)
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')
    plt.close(fig)  # Close the figure to free memory

def generate_and_save_puzzles(num_puzzles=500, empty_slots=40, base=3):
    puzzles = []
    solutions = []
    image_filenames = []
    solution_filenames = []

    for idx in range(num_puzzles):
        # Generate puzzle and solution
        solution = generate_sudoku(base)
        puzzle = remove_numbers(solution, empty_slots, base)

        puzzle_filename = f'puzzle_{idx + 1}.png'
        solution_filename = f'solution_{idx + 1}.png'

        # Draw puzzles and solutions
        draw_sudoku(puzzle, puzzle_filename, base)
        draw_sudoku(solution, solution_filename, base)

        puzzles.append(puzzle_filename)
        solutions.append(solution_filename)

    return puzzles, solutions

def save_puzzles_to_pdf(puzzle_images, solution_images, output_filename='sudoku_puzzles.pdf'):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)

    for idx, (puzzle_img, solution_img) in enumerate(zip(puzzle_images, solution_images)):
        # Add puzzle page
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'Sudoku Puzzle #{idx + 1}', ln=True, align='C')
        pdf.image(puzzle_img, x=20, y=30, w=170)
        pdf.ln(85)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 200, 'Solution on next page', ln=True, align='C')

        # Add solution page
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'Sudoku Puzzle #{idx + 1} Solution', ln=True, align='C')
        pdf.image(solution_img, x=20, y=30, w=170)

    pdf.output(output_filename)
    print(f"Sudoku puzzles saved to {output_filename}")

    # Clean up image files
    for file in puzzle_images + solution_images:
        if os.path.exists(file):
            os.remove(file)

if __name__ == '__main__':
    base = 3  # Base size, 3x3 blocks for standard Sudoku
    num_puzzles = 500  # Number of puzzles to generate
    empty_slots = 40  # Number of empty slots per puzzle

    puzzle_images, solution_images = generate_and_save_puzzles(
        num_puzzles=num_puzzles,
        empty_slots=empty_slots,
        base=base
    )

    save_puzzles_to_pdf(puzzle_images, solution_images)