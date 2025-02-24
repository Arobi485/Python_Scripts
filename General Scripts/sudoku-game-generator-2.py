import pygame
import random
import sys
import time
import csv
import os

# Initialize Pygame
pygame.init()

# Set up the window
WIDTH, HEIGHT = 550, 750  # Increased height to provide space at the bottom
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")

# Fonts
FONT = pygame.font.SysFont('Arial', 40)
SMALL_FONT = pygame.font.SysFont('Arial', 20)
CONFIRM_FONT = pygame.font.SysFont('Arial', 24)
MENU_FONT = pygame.font.SysFont('Arial', 32)
LEADERBOARD_FONT = pygame.font.SysFont('Arial', 24)

# Colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (220, 220, 220)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
BLUE = (50, 50, 255)
RED = (255, 0, 0)

# Top margin to make space for the Back button
TOP_MARGIN = 60

# Leaderboard file
LEADERBOARD_FILE = 'leaderboard.csv'

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
        pygame.draw.line(window, BLACK, (i * gap, TOP_MARGIN), (i * gap, WIDTH + TOP_MARGIN), thick)
        # Horizontal lines
        pygame.draw.line(window, BLACK, (0, i * gap + TOP_MARGIN), (WIDTH, i * gap + TOP_MARGIN), thick)

def draw_numbers(window, board, selected, incorrect):
    gap = WIDTH // 9
    for i in range(9):
        for j in range(9):
            x = j * gap
            y = i * gap + TOP_MARGIN
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
    # Draw the "Back" button at the top-left corner within the top margin
    back_button = pygame.Rect(10, 10, 80, 40)
    pygame.draw.rect(window, GRAY, back_button)

    back_text = SMALL_FONT.render("Back", True, BLACK)
    window.blit(back_text, (back_button.x + (back_button.width - back_text.get_width()) // 2,
                            back_button.y + (back_button.height - back_text.get_height()) // 2))

    # Calculate positions for "Check" and "Solve" buttons
    grid_bottom = TOP_MARGIN + WIDTH  # Bottom of the grid
    buttons_y = grid_bottom + 20      # 20 pixels gap below the grid

    # Draw the "Check" and "Solve" buttons below the grid
    check_button = pygame.Rect(150, buttons_y, 100, 40)
    solve_button = pygame.Rect(300, buttons_y, 100, 40)
    pygame.draw.rect(window, GRAY, check_button)
    pygame.draw.rect(window, GRAY, solve_button)

    check_text = SMALL_FONT.render("Check", True, BLACK)
    solve_text = SMALL_FONT.render("Solve", True, BLACK)
    window.blit(check_text, (check_button.x + (check_button.width - check_text.get_width()) // 2,
                             check_button.y + 10))
    window.blit(solve_text, (solve_button.x + (solve_button.width - solve_text.get_width()) // 2,
                             solve_button.y + 10))

    return back_button, check_button, solve_button

def message_dialog(window, message, buttons, multi_line=False):
    # Draw a semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with opacity

    # Draw the dialog box
    dialog_width, dialog_height = 500, 400
    dialog_x = (WIDTH - dialog_width) // 2
    dialog_y = (HEIGHT - dialog_height) // 2 - 50
    pygame.draw.rect(overlay, LIGHT_GRAY, (dialog_x, dialog_y, dialog_width, dialog_height), 0, 5)

    # Draw the text
    if multi_line:
        lines = message.split('\n')
        y_offset = dialog_y + 60
        for line in lines:
            text = SMALL_FONT.render(line, True, BLACK)
            text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
            overlay.blit(text, text_rect)
            y_offset += 30  # Adjust line spacing
    else:
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
        btn_y = dialog_y + dialog_height - 80
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

def show_instructions():
    instructions_pages = [
        "Welcome to Sudoku!\n\n"
        "Objective:\n"
        "Fill the grid so that every row, column, \nand 3x3 box contains the digits 1 to 9 \nwithout repeating.",
        
        "How to Play:\n"
        "- Click on a cell to select it.\n"
        "- Use number keys (1-9) to fill in a number.\n"
        "- Press 'Delete' or 'Backspace' to clear a cell.\n"
        "- Click 'Check' to verify your solution.",
        
        "Controls:\n"
        "- 'Back' button: Return to the main menu.\n"
        "- 'Check' button: Verifies your entries.\n"
        "- 'Solve' button: Reveals the solution \n   (confirmation required).",
        
        "Tips:\n"
        "- Use logic to eliminate possibilities.\n"
        "- Start with rows, columns, or boxes \n  that are nearly complete.\n"
        "- There's only one correct solution \n  for each puzzle."
    ]

    current_page = 0
    total_pages = len(instructions_pages)

    running = True
    while running:
        page_text = instructions_pages[current_page] + f"\n\nPage {current_page + 1} of {total_pages}"
        buttons = []
        if current_page > 0:
            buttons.append(("Previous", "prev"))
        buttons.append(("OK", "ok"))  # The 'OK' button will exit the instructions
        if current_page < total_pages - 1:
            buttons.append(("Next", "next"))
        
        action = message_dialog(WINDOW, page_text, buttons, multi_line=True)
        if action == "next":
            current_page += 1
        elif action == "prev":
            current_page -= 1
        else:
            running = False  # Exit the instructions

def show_leaderboard():
    # Read leaderboard data from CSV file
    leaderboard_data = []

    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            leaderboard_data = list(reader)

    if not leaderboard_data:
        message_dialog(WINDOW, "No leaderboard data available.", [("OK", "ok")])
        return

    # Display leaderboard
    page_text = "Leaderboard:\n\n" + \
                "Rank  Name         Time    Difficulty\n" + \
                "----------------------------------------\n"
    for idx, entry in enumerate(leaderboard_data[:10]):  # Show top 10 entries
        rank = idx + 1
        name, time_str, difficulty = entry
        line = f"{rank:<5}{name:<12}{time_str:<8}{difficulty}"
        page_text += line + "\n"

    message_dialog(WINDOW, page_text, [("OK", "ok")], multi_line=True)

def main_menu():
    running = True
    selected = "Medium"  # Default difficulty
    while running:
        WINDOW.fill(WHITE)

        # Title
        title_text = MENU_FONT.render("Sudoku Game", True, BLACK)
        WINDOW.blit(title_text, ((WIDTH - title_text.get_width()) // 2, 50))

        # Start button
        start_button = pygame.Rect((WIDTH - 200) // 2, 130, 200, 50)
        pygame.draw.rect(WINDOW, GRAY, start_button)

        start_text = SMALL_FONT.render("Start Game", True, BLACK)
        WINDOW.blit(start_text, (start_button.x + (start_button.width - start_text.get_width()) // 2, start_button.y + 15))

        # Difficulty buttons
        difficulties = ["Easy", "Medium", "Hard"]
        difficulty_buttons = []
        for idx, difficulty in enumerate(difficulties):
            btn_x = (WIDTH - 200) // 2
            btn_y = 200 + idx * 60
            button_rect = pygame.Rect(btn_x, btn_y, 200, 50)
            pygame.draw.rect(WINDOW, GRAY if selected != difficulty else DARK_GRAY, button_rect)

            btn_text = SMALL_FONT.render(difficulty, True, WHITE if selected == difficulty else BLACK)
            WINDOW.blit(btn_text, (button_rect.x + (button_rect.width - btn_text.get_width()) // 2, button_rect.y + 15))

            difficulty_buttons.append((button_rect, difficulty))

        # Leaderboard button
        leaderboard_button = pygame.Rect((WIDTH - 200) // 2, 380, 200, 50)
        pygame.draw.rect(WINDOW, GRAY, leaderboard_button)

        leaderboard_text = SMALL_FONT.render("Leaderboard", True, BLACK)
        WINDOW.blit(leaderboard_text, (leaderboard_button.x + (leaderboard_button.width - leaderboard_text.get_width()) // 2,
                                       leaderboard_button.y + 15))

        # Instructions button
        instr_button = pygame.Rect((WIDTH - 200) // 2, 450, 200, 50)
        pygame.draw.rect(WINDOW, GRAY, instr_button)

        instr_text = SMALL_FONT.render("Instructions", True, BLACK)
        WINDOW.blit(instr_text, (instr_button.x + (instr_button.width - instr_text.get_width()) // 2, instr_button.y + 15))

        # Exit button
        exit_button = pygame.Rect((WIDTH - 200) // 2, 520, 200, 50)
        pygame.draw.rect(WINDOW, GRAY, exit_button)

        exit_text = SMALL_FONT.render("Exit", True, BLACK)
        WINDOW.blit(exit_text, (exit_button.x + (exit_button.width - exit_text.get_width()) // 2, exit_button.y + 15))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if start_button.collidepoint(pos):
                    return selected  # Return the selected difficulty
                for button_rect, difficulty in difficulty_buttons:
                    if button_rect.collidepoint(pos):
                        selected = difficulty
                if leaderboard_button.collidepoint(pos):
                    show_leaderboard()
                if instr_button.collidepoint(pos):
                    show_instructions()
                if exit_button.collidepoint(pos):
                    pygame.quit()
                    sys.exit()

def get_player_name():
    # Prompt the user to enter their name
    name = ""
    input_active = True

    # Create an input box area
    input_box = pygame.Rect((WIDTH - 300) // 2, (HEIGHT - 50) // 2, 300, 50)

    while input_active:
        WINDOW.fill(WHITE)

        # Prompt text
        prompt_text = CONFIRM_FONT.render("Enter your name:", True, BLACK)
        WINDOW.blit(prompt_text, ((WIDTH - prompt_text.get_width()) // 2, input_box.y - 60))

        # Draw input box
        pygame.draw.rect(WINDOW, LIGHT_GRAY, input_box)

        # Render the current name
        name_text = CONFIRM_FONT.render(name, True, BLACK)
        WINDOW.blit(name_text, (input_box.x + 10, input_box.y + 10))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name.strip() if name.strip() != "" else "Anonymous"
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 20:  # Limit name length
                        name += event.unicode

def save_to_leaderboard(name, time_str, difficulty):
    # Save the player's name, time, and difficulty to a CSV file
    with open(LEADERBOARD_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([name, time_str, difficulty])

def main():
    while True:
        difficulty = main_menu()

        # Set the number of empty spaces based on difficulty
        if difficulty == "Easy":
            empties = 30
        elif difficulty == "Medium":
            empties = 40
        elif difficulty == "Hard":
            empties = 50
        else:
            empties = 40  # Default to Medium if undefined

        board = generate_sudoku(empties=empties)
        solution = solve(board)
        original_board = copy_board(board)

        selected = None
        incorrect = []
        start_time = time.time()  # Start the timer

        running = True
        while running:
            WINDOW.fill(WHITE)
            draw_grid(WINDOW)
            draw_numbers(WINDOW, board, selected, incorrect)
            back_button, check_button, solve_button = draw_buttons(WINDOW)

            elapsed_time = int(time.time() - start_time)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            time_text = SMALL_FONT.render(f"Time: {minutes:02}:{seconds:02}", True, BLACK)
            WINDOW.blit(time_text, (WIDTH - 150, 20))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if back_button.collidepoint(pos):
                        action = message_dialog(WINDOW,
                                                "Are you sure you want to return to the main menu?",
                                                [("Yes", "yes"), ("No", "no")])
                        if action == "yes":
                            running = False  # Exit game loop to go back to menu
                            break
                    elif check_button.collidepoint(pos):
                        incorrect = []
                        for i in range(9):
                            for j in range(9):
                                if board[i][j] != solution[i][j]:
                                    incorrect.append((i, j))
                        if not incorrect:
                            # Stop the timer
                            total_time = int(time.time() - start_time)
                            minutes = total_time // 60
                            seconds = total_time % 60
                            time_str = f"{minutes}m {seconds}s"

                            # Get player's name
                            name = get_player_name()

                            # Save to leaderboard
                            save_to_leaderboard(name, time_str, difficulty)

                            # Show completion message with time
                            message_dialog(WINDOW, f"Congratulations {name}!\nYou solved the puzzle in {time_str}.",
                                           [("OK", "ok")], multi_line=True)

                            running = False  # Exit game loop to go back to menu
                            break
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
                        if x < WIDTH and y > TOP_MARGIN and y < TOP_MARGIN + WIDTH:
                            gap = WIDTH // 9
                            row = (y - TOP_MARGIN) // gap
                            col = x // gap
                            if original_board[row][col] == 0:
                                selected = (row, col)
                            else:
                                selected = None
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