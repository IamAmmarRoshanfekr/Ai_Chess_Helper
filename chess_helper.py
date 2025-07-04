import os
import sys
import pygame
import chess
import chess.pgn
import chess.engine
import io
import math

# Configuration
IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), 'images')
SOUND_FOLDER = os.path.join(os.path.dirname(__file__), 'sounds')
STOCKFISH_PATH = '../stockfish.exe'  # place your stockfish.exe file path here
SCREEN_SIZE = 640
BOARD_MARGIN = 40
SQUARE_SIZE = (SCREEN_SIZE - 2 * BOARD_MARGIN) // 8
FPS = 60
ENGINE_TIME = 0.1  # seconds to think

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 80))
pygame.display.set_caption('Chess Helper')
clock = pygame.time.Clock()

# Load sounds
move_sound = pygame.mixer.Sound(os.path.join(SOUND_FOLDER, 'move.wav'))
capture_sound = pygame.mixer.Sound(os.path.join(SOUND_FOLDER, 'capture.wav'))
check_sound = pygame.mixer.Sound(os.path.join(SOUND_FOLDER, 'check.wav'))

# Load piece images
piece_images = {}
for piece in ['p', 'n', 'b', 'r', 'q', 'k']:
    for color in ['w', 'b']:
        filename = f"{color}{piece}.png"
        path = os.path.join(IMAGE_FOLDER, filename)
        img = pygame.image.load(path)
        img = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))
        key = color + piece.upper()
        piece_images[key] = img

# Elo strength variable and initialization
elo_level = 1350  # default Elo

def init_engine():
    try:
        eng = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        eng.configure({
            "UCI_LimitStrength": True,
            "UCI_Elo": elo_level
        })
        return eng
    except Exception as e:
        print("Failed to launch Stockfish engine:", e)
        sys.exit(1)

engine = init_engine()
board = chess.Board()

# UI state
selected_square = None
pgn_input = ''
suggestion = None
promotion_move = None
promotion_choices = False
ai_helper_enabled = True
font = pygame.font.SysFont(None, 24)
small_font = pygame.font.SysFont(None, 18)

# Buttons
def draw_button(rect, text):
    pygame.draw.rect(screen, pygame.Color('lightgray'), rect)
    pygame.draw.rect(screen, pygame.Color('black'), rect, 2)
    label = font.render(text, True, pygame.Color('black'))
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)

reset_button = pygame.Rect(BOARD_MARGIN, SCREEN_SIZE + 20, 100, 40)
ai_toggle_button = pygame.Rect(SCREEN_SIZE - 140, SCREEN_SIZE + 20, 120, 40)

# Elo slider UI elements
elo_slider_rect = pygame.Rect(BOARD_MARGIN + 110, SCREEN_SIZE + 35, 200, 10)
elo_handle_rect = pygame.Rect(elo_slider_rect.x, elo_slider_rect.y - 5, 10, 20)

def draw_elo_slider():
    pygame.draw.rect(screen, pygame.Color('black'), elo_slider_rect)
    pygame.draw.rect(screen, pygame.Color('blue'), elo_handle_rect)
    label = font.render(f"Elo: {elo_level}", True, pygame.Color('white'))
    screen.blit(label, (elo_slider_rect.x, elo_slider_rect.y - 22))

# Promotion menu
promotion_rects = []
def draw_promotion_menu():
    global promotion_rects
    if not promotion_move:
        return
    promotion_rects = []
    color = board.turn
    y = BOARD_MARGIN + 3 * SQUARE_SIZE
    x = SCREEN_SIZE // 2 - 2 * SQUARE_SIZE
    for i, piece_type in enumerate([chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]):
        rect = pygame.Rect(x + i * SQUARE_SIZE, y, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, pygame.Color('lightgray'), rect)
        pygame.draw.rect(screen, pygame.Color('black'), rect, 2)
        piece = chess.Piece(piece_type, color)
        color_prefix = 'w' if piece.color == chess.WHITE else 'b'
        symbol = piece.symbol().upper()
        key = color_prefix + symbol
        img = piece_images.get(key)
        if img:
            screen.blit(img, (rect.x, rect.y))
        promotion_rects.append((rect, piece_type))

# Arrow drawing for suggested move
def draw_arrow(from_sq, to_sq):
    fx = BOARD_MARGIN + chess.square_file(from_sq) * SQUARE_SIZE + SQUARE_SIZE//2
    fy = BOARD_MARGIN + (7 - chess.square_rank(from_sq)) * SQUARE_SIZE + SQUARE_SIZE//2
    tx = BOARD_MARGIN + chess.square_file(to_sq) * SQUARE_SIZE + SQUARE_SIZE//2
    ty = BOARD_MARGIN + (7 - chess.square_rank(to_sq)) * SQUARE_SIZE + SQUARE_SIZE//2
    pygame.draw.line(screen, pygame.Color('red'), (fx, fy), (tx, ty), 4)
    angle = math.atan2(ty-fy, tx-fx)
    head_len = 15
    for i in (math.pi/6, -math.pi/6):
        ax = tx - head_len * math.cos(angle + i)
        ay = ty - head_len * math.sin(angle + i)
        pygame.draw.line(screen, pygame.Color('red'), (tx, ty), (ax, ay), 4)

# Legal move dots: green for normal moves, red dot above piece for captures
def draw_move_dots():
    if selected_square is None:
        return [], []
    piece = board.piece_at(selected_square)
    if not piece or piece.color != board.turn:
        return [], []
    capture_dots = []
    normal_dots = []
    for move in board.legal_moves:
        if move.from_square == selected_square:
            to_sq = move.to_square
            col = chess.square_file(to_sq)
            row = chess.square_rank(to_sq)
            x = BOARD_MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2
            y = BOARD_MARGIN + (7 - row) * SQUARE_SIZE + SQUARE_SIZE // 2
            if board.piece_at(to_sq):
                # Red dot above the piece (higher by a quarter square)
                capture_dots.append((x, y - SQUARE_SIZE // 4))
            else:
                normal_dots.append((x, y))
    return capture_dots, normal_dots

# Draw board and pieces
def draw_board():
    colors = [pygame.Color('white'), pygame.Color('gray')]
    for r in range(8):
        for c in range(8):
            color = colors[(r + c) % 2]
            rect = pygame.Rect(BOARD_MARGIN + c * SQUARE_SIZE,
                               BOARD_MARGIN + r * SQUARE_SIZE,
                               SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

            # Draw file and rank labels
            file_char = 'abcdefgh'[c]
            rank_char = str(8 - r)
            if r == 7:
                lbl = small_font.render(file_char, True, pygame.Color('black'))
                screen.blit(lbl, (rect.x + SQUARE_SIZE//2 - lbl.get_width()//2, rect.y + SQUARE_SIZE + 2))
            if c == 0:
                lbl = small_font.render(rank_char, True, pygame.Color('black'))
                screen.blit(lbl, (rect.x - lbl.get_width() - 2, rect.y + SQUARE_SIZE//2 - lbl.get_height()//2))

    if ai_helper_enabled and suggestion:
        draw_arrow(suggestion.from_square, suggestion.to_square)

    # Draw legal move dots **after pieces**
    capture_dots, normal_dots = draw_move_dots()

    # Draw pieces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = chess.square_file(square)
            row = chess.square_rank(square)
            color_prefix = 'w' if piece.color == chess.WHITE else 'b'
            symbol = piece.symbol().upper()
            key = color_prefix + symbol
            img = piece_images.get(key)
            if img:
                x = BOARD_MARGIN + col * SQUARE_SIZE
                y = BOARD_MARGIN + (7 - row) * SQUARE_SIZE
                screen.blit(img, (x, y))

    # Highlight selected square
    if selected_square is not None:
        col = chess.square_file(selected_square)
        row = chess.square_rank(selected_square)
        x = BOARD_MARGIN + col * SQUARE_SIZE
        y = BOARD_MARGIN + (7 - row) * SQUARE_SIZE
        highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight.fill((255, 255, 0, 100))
        screen.blit(highlight, (x, y))

    # Draw legal move dots on top of pieces
    for (x, y) in normal_dots:
        pygame.draw.circle(screen, pygame.Color('green'), (x, y), 8)
    for (x, y) in capture_dots:
        pygame.draw.circle(screen, pygame.Color('red'), (x, y), 10)

def show_suggestion():
    if ai_helper_enabled and suggestion:
        text = font.render(f'Best move: {suggestion.uci()}', True, pygame.Color('blue'))
        screen.blit(text, (SCREEN_SIZE - 180, SCREEN_SIZE - 10))

def suggest_move():
    global suggestion
    try:
        result = engine.play(board, chess.engine.Limit(time=ENGINE_TIME))
        suggestion = result.move
    except Exception:
        suggestion = None

def load_pgn(pgn):
    try:
        game = chess.pgn.read_game(io.StringIO(pgn))
        if game is None:
            return None
        b = game.board()
        for m in game.mainline_moves():
            b.push(m)
        return b
    except Exception:
        return None

running = True
suggest_move()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if promotion_choices:
                for rect, piece_type in promotion_rects:
                    if rect.collidepoint(mx, my):
                        move = chess.Move(promotion_move.from_square, promotion_move.to_square, promotion=piece_type)
                        board.push(move)
                        move_sound.play()
                        if board.is_check():
                            check_sound.play()
                        promotion_choices = False
                        promotion_move = None
                        selected_square = None
                        suggest_move()
                        break
                continue

            if reset_button.collidepoint(mx, my):
                board.reset()
                suggestion = None
                suggest_move()
            elif ai_toggle_button.collidepoint(mx, my):
                ai_helper_enabled = not ai_helper_enabled
            elif elo_slider_rect.collidepoint(mx, my) or elo_handle_rect.collidepoint(mx, my):
                relative_x = max(0, min(mx - elo_slider_rect.x, elo_slider_rect.width))
                percent = relative_x / elo_slider_rect.width
                elo_level = int(1350 + percent * (2850 - 1350))
                elo_handle_rect.x = elo_slider_rect.x + relative_x - elo_handle_rect.width // 2
                engine.quit()
                engine = init_engine()
                suggest_move()
            elif BOARD_MARGIN <= mx < BOARD_MARGIN + 8 * SQUARE_SIZE and BOARD_MARGIN <= my < BOARD_MARGIN + 8 * SQUARE_SIZE:
                c = (mx - BOARD_MARGIN) // SQUARE_SIZE
                r = (my - BOARD_MARGIN) // SQUARE_SIZE
                sq = chess.square(c, 7-r)
                if selected_square is None:
                    if board.piece_at(sq):
                        selected_square = sq
                else:
                    move = chess.Move(selected_square, sq)
                    if board.piece_at(selected_square) and board.piece_at(selected_square).piece_type == chess.PAWN and (chess.square_rank(sq) == 0 or chess.square_rank(sq) == 7):
                        if chess.Move(selected_square, sq, promotion=chess.QUEEN) in board.legal_moves:
                            promotion_move = move
                            promotion_choices = True
                            continue
                    if move in board.legal_moves:
                        capture = board.piece_at(sq) is not None
                        board.push(move)
                        (capture_sound if capture else move_sound).play()
                        if board.is_check():
                            check_sound.play()
                        suggestion = None
                        suggest_move()
                    selected_square = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                new_board = load_pgn(pgn_input)
                if new_board:
                    board = new_board
                    suggestion = None
                    suggest_move()
                pgn_input = ''
            elif event.key == pygame.K_BACKSPACE:
                pgn_input = pgn_input[:-1]
            else:
                pgn_input += event.unicode

    screen.fill(pygame.Color('darkgreen'))
    draw_board()
    input_rect = pygame.Rect(BOARD_MARGIN, 10, SCREEN_SIZE - 2 * BOARD_MARGIN, 24)
    pygame.draw.rect(screen, pygame.Color('white'), input_rect)
    placeholder = 'Enter PGN and press Enter...'
    txt = pgn_input if pgn_input else placeholder
    txt_surf = font.render(txt, True, pygame.Color('black'))
    screen.blit(txt_surf, (input_rect.x + 4, input_rect.y + 2))
    draw_button(reset_button, 'Reset')
    draw_button(ai_toggle_button, 'AI Helper: On' if ai_helper_enabled else 'AI Helper: Off')
    draw_elo_slider()
    show_suggestion()
    if promotion_choices:
        draw_promotion_menu()
    pygame.display.flip()
    clock.tick(FPS)

engine.quit()
pygame.quit()

# you can modify sounds, pieces or game UI 