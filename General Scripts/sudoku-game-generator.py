import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set up the window
WIDTH, HEIGHT = 550, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")

# Fonts
FONT = pygame.font.SysFont('Arial', 40)
SMALL_FONT = pygame.font.SysFont('Arial', 20)
CONFIRM_FONT = pygame.font.SysFont('Arial', 24)

# Colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (220, 220, 220)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
BLUE = (50, 50, 255)
RED = (255, 0, 0)

def pattern(r, c, base=3):
    return (base * (r % base) + r // base + c) % (base * base)

def shuffle(s):
    return random.sample(s, len(s))

def generate_sudoku(base=3, empties=40):
    side = base * base

    nums = shuffle(range(1, side + 1))
    rows = [g * base + r for g in shuffle(range(base)) for r in shuffle(range(base))]
    cols = [g * base + c for g in shuffle(range(base)) for c in shuffle(range(base))]

    board = [[nums[pattern(r, c, base)] for c in cols] for r in rows]

    squares = side * side
    positions = random.sample(range(squares), empties)
    for pos in positions:
        row = pos // side
        col = pos % side
        board[row][col] = 0

    return board

def copy_board(board):
    return [row[:] for row in board]

def solve(board):
    side = len(board)
    base = int(side ** 0.5)

    def is_valid(board, row, col, num):
        for x in range(side):
            if board[row][x] == num or board[x][col] == num:
                return False
        start_row, start_col = base * (row // base), base * (col // base)
        for i in range(base):
            for j in range(base):
                if board[start_row + i][start_col + j] == num:
                    return False
        return True

    def solve_util(board):
        for i in range(side):
            for j in range(side):
                if board[i][j] == 0:
                    for num in range(1, side + 1):
                        if is_valid(board, i, j, num):
                            board[i][j] = num
                            if solve_util(board):
                                return True
                            board[i][j] = 0
                    return False
        return True

    board_copy = copy_board(board)
    solve_util(board_copy)
    return board_copy

def draw_grid(window):
    gap = WIDTH // 9
    for i in range(10):
        if i % 3 == 0:
            thick = 4
        else:
            thick = 1
        # Vertical lines
        pygame.draw.line(window, BLACK, (i * gap, 0), (i * gap, WIDTH), thick)
        # Horizontal lines
        pygame.draw.line(window, BLACK, (0, i * gap), (WIDTH, i * gap), thick)

def draw_numbers(window, board, selected, incorrect):
    gap = WIDTH // 9
    for i in range(9):
        for j in range(9):
            x = j * gap
            y = i * gap
            num = board[i][j]
            if num != 0:
                color = BLACK
                if (i, j) in incorrect:
                    color = RED
                text = FONT.render(str(num), True, color)
                window.blit(text, (x + (gap - text.get_width()) // 2, y + (gap - text.get_height()) // 2))
            if (i, j) == selected:
                pygame.draw.rect(window, BLUE, (x, y, gap, gap), 3)

def draw_buttons(window):
    check_button = pygame.Rect(150, 560, 100, 30)
    solve_button = pygame.Rect(300, 560, 100, 30)
    pygame.draw.rect(window, GRAY, check_button)
    pygame.draw.rect(window, GRAY, solve_button)

    check_text = SMALL_FONT.render("Check", True, BLACK)
    solve_text = SMALL_FONT.render("Solve", True, BLACK)
    window.blit(check_text, (check_button.x + (check_button.width - check_text.get_width()) // 2, check_button.y + 5))
    window.blit(solve_text, (solve_button.x + (solve_button.width - solve_text.get_width()) // 2, solve_button.y + 5))

    return check_button, solve_button

def message_dialog(window, message, buttons):
    # Draw a semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with opacity

    # Draw the dialog box
    dialog_width, dialog_height = 400, 200
    dialog_x = (WIDTH - dialog_width) // 2
    dialog_y = (HEIGHT - dialog_height) // 2 - 50
    pygame.draw.rect(overlay, LIGHT_GRAY, (dialog_x, dialog_y, dialog_width, dialog_height), 0, 5)

    # Draw the text
    text = CONFIRM_FONT.render(message, True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, dialog_y + 60))
    overlay.blit(text, text_rect)

    button_rects = []
    button_width = 100
    button_height = 40
    button_spacing = 20
    total_buttons_width = len(buttons) * button_width + (len(buttons) - 1) * button_spacing
    start_x = (WIDTH - total_buttons_width) // 2

    for idx, (button_text, _) in enumerate(buttons):
        btn_x = start_x + idx * (button_width + button_spacing)
        btn_y = dialog_y + 120
        button_rect = pygame.Rect(btn_x, btn_y, button_width, button_height)
        pygame.draw.rect(overlay, GRAY, button_rect)

        btn_text = SMALL_FONT.render(button_text, True, BLACK)
        btn_text_rect = btn_text.get_rect(center=(btn_x + button_width // 2, btn_y + button_height // 2))
        overlay.blit(btn_text, btn_text_rect)

        button_rects.append((button_rect, buttons[idx][1]))  # Store rect and associated action

    window.blit(overlay, (0, 0))
    pygame.display.update()

    # Wait for user response
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for button_rect, action in button_rects:
                    if button_rect.collidepoint(pos):
                        return action  # Return the associated action

def main():
    board = generate_sudoku(empties=40)
    solution = solve(board)
    original_board = copy_board(board)

    selected = None
    incorrect = []

    running = True
    while running:
        WINDOW.fill(WHITE)
        draw_grid(WINDOW)
        draw_numbers(WINDOW, board, selected, incorrect)
        check_button, solve_button = draw_buttons(WINDOW)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if check_button.collidepoint(pos):
                    incorrect = []
                    for i in range(9):
                        for j in range(9):
                            if board[i][j] != solution[i][j]:
                                incorrect.append((i, j))
                    if not incorrect:
                        # Show congratulations message
                        message_dialog(WINDOW, "Congratulations! You solved the puzzle.", [("OK", "ok")])
                    else:
                        # Show error message
                        message_dialog(WINDOW, "There are some incorrect entries.", [("OK", "ok")])
                elif solve_button.collidepoint(pos):
                    action = message_dialog(WINDOW,
                                            "Are you sure you want to reveal the solution?",
                                            [("Yes", "yes"), ("No", "no")])
                    if action == "yes":
                        board = solution
                        selected = None
                        incorrect = []
                else:
                    x, y = pos
                    if x < WIDTH and y < WIDTH:
                        gap = WIDTH // 9
                        row = y // gap
                        col = x // gap
                        if original_board[row][col] == 0:
                            selected = (row, col)
                        else:
                            selected = None

            elif event.type == pygame.KEYDOWN and selected:
                key = event.key
                if key in [pygame.K_KP1, pygame.K_1]:
                    board[selected[0]][selected[1]] = 1
                elif key in [pygame.K_KP2, pygame.K_2]:
                    board[selected[0]][selected[1]] = 2
                elif key in [pygame.K_KP3, pygame.K_3]:
                    board[selected[0]][selected[1]] = 3
                elif key in [pygame.K_KP4, pygame.K_4]:
                    board[selected[0]][selected[1]] = 4
                elif key in [pygame.K_KP5, pygame.K_5]:
                    board[selected[0]][selected[1]] = 5
                elif key in [pygame.K_KP6, pygame.K_6]:
                    board[selected[0]][selected[1]] = 6
                elif key in [pygame.K_KP7, pygame.K_7]:
                    board[selected[0]][selected[1]] = 7
                elif key in [pygame.K_KP8, pygame.K_8]:
                    board[selected[0]][selected[1]] = 8
                elif key in [pygame.K_KP9, pygame.K_9]:
                    board[selected[0]][selected[1]] = 9
                elif key == pygame.K_DELETE or key == pygame.K_BACKSPACE:
                    board[selected[0]][selected[1]] = 0

        pygame.display.update()

if __name__ == '__main__':
    main()