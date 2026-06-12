"""Логика бразильских шашек (без GUI) для обучения с подкреплением."""
import copy

BLACK = 1
BLACK_KING = 2
WHITE = -1
WHITE_KING = -2
EMPTY = 0

DIRS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def initial_board():
    return [
        [0, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [-1, 0, -1, 0, -1, 0, -1, 0],
        [0, -1, 0, -1, 0, -1, 0, -1],
        [-1, 0, -1, 0, -1, 0, -1, 0],
    ]


def copy_board(board):
    return [row[:] for row in board]


def board_key(board):
    return tuple(tuple(row) for row in board)


def in_bounds(x, y):
    return 0 <= x < 8 and 0 <= y < 8


def is_black(p):
    return p in (BLACK, BLACK_KING)


def is_white(p):
    return p in (WHITE, WHITE_KING)


def is_king(p):
    return abs(p) == 2


def enemy_values(side):
    return {-1, -2} if side > 0 else {1, 2}


def promote(board):
    b = copy_board(board)
    for x in range(8):
        for y in range(8):
            if b[x][y] == BLACK and x == 7:
                b[x][y] = BLACK_KING
            if b[x][y] == WHITE and x == 0:
                b[x][y] = WHITE_KING
    return b


def count_pieces(board, side):
    n = 0
    for x in range(8):
        for y in range(8):
            p = board[x][y]
            if side > 0 and is_black(p):
                n += 1
            elif side < 0 and is_white(p):
                n += 1
    return n


def can_capture_cell(board, x, y, dx, dy, enemies):
    nx, ny = x + dx, y + dy
    nx2, ny2 = x + 2 * dx, y + 2 * dy
    if not (in_bounds(nx, ny) and in_bounds(nx2, ny2)):
        return False
    return board[nx][ny] in enemies and board[nx2][ny2] == EMPTY


def get_step_moves(board, x, y):
    p = board[x][y]
    if p == EMPTY:
        return []
    moves = []
    if p == BLACK:
        candidates = [(1, -1), (1, 1)]
    elif p == WHITE:
        candidates = [(-1, -1), (-1, 1)]
    else:
        candidates = DIRS

    if is_king(p):
        for dx, dy in DIRS:
            step = 1
            while True:
                nx, ny = x + step * dx, y + step * dy
                if not in_bounds(nx, ny) or board[nx][ny] != EMPTY:
                    break
                moves.append((x, y, nx, ny, []))
                step += 1
    else:
        for dx, dy in candidates:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and board[nx][ny] == EMPTY:
                moves.append((x, y, nx, ny, []))
    return moves


def capture_recursive(board, x, y, caps, enemies, is_king_piece, origin):
    """caps — координаты съеденных шашек; origin — начальная клетка ходящей фигуры."""
    moves = []
    ox, oy = origin
    for dx, dy in DIRS:
        if is_king_piece:
            step = 1
            while True:
                nx, ny = x + step * dx, y + step * dy
                if not in_bounds(nx, ny):
                    break
                if board[nx][ny] in enemies:
                    for jump in range(step + 1, 8):
                        tx, ty = x + jump * dx, y + jump * dy
                        if not in_bounds(tx, ty) or board[tx][ty] != EMPTY:
                            break
                        nb = copy_board(board)
                        nb[x][y] = EMPTY
                        nb[nx][ny] = EMPTY
                        piece = board[x][y]
                        nb[tx][ty] = piece
                        cap = caps + [(nx, ny)]
                        further = capture_recursive(
                            nb, tx, ty, cap, enemies, is_king_piece, origin
                        )
                        if further:
                            moves.extend(further)
                        else:
                            moves.append((ox, oy, tx, ty, cap))
                    break
                if board[nx][ny] != EMPTY:
                    break
                step += 1
        else:
            if can_capture_cell(board, x, y, dx, dy, enemies):
                nx, ny = x + dx, y + dy
                tx, ty = x + 2 * dx, y + 2 * dy
                nb = copy_board(board)
                piece = board[x][y]
                nb[x][y] = EMPTY
                nb[nx][ny] = EMPTY
                nb[tx][ty] = piece
                cap = caps + [(nx, ny)]
                further = capture_recursive(nb, tx, ty, cap, enemies, False, origin)
                if further:
                    moves.extend(further)
                else:
                    moves.append((ox, oy, tx, ty, cap))
    return moves


def get_capture_moves(board, x, y, side):
    p = board[x][y]
    if (side > 0 and not is_black(p)) or (side < 0 and not is_white(p)):
        return []
    enemies = enemy_values(side)
    return capture_recursive(board, x, y, [], enemies, is_king(p), origin=(x, y))


def jump_exists(board, side):
    for x in range(8):
        for y in range(8):
            if get_capture_moves(board, x, y, side):
                return True
    return False


def get_all_moves(board, side):
    """Список ходов: (new_board, n_captured)."""
    if jump_exists(board, side):
        result = []
        for x in range(8):
            for y in range(8):
                for sx, sy, tx, ty, caps in get_capture_moves(board, x, y, side):
                    nb = copy_board(board)
                    piece = board[sx][sy]
                    nb[sx][sy] = EMPTY
                    for cx, cy in caps:
                        nb[cx][cy] = EMPTY
                    nb[tx][ty] = piece
                    nb = promote(nb)
                    result.append((nb, len(caps)))
        return result

    result = []
    for x in range(8):
        for y in range(8):
            for sx, sy, tx, ty, _ in get_step_moves(board, x, y):
                p = board[sx][sy]
                if (side > 0 and not is_black(p)) or (side < 0 and not is_white(p)):
                    continue
                nb = copy_board(board)
                nb[sx][sy] = EMPTY
                nb[tx][ty] = p
                nb = promote(nb)
                result.append((nb, 0))
    return result


def has_legal_move(board, side):
    return len(get_all_moves(board, side)) > 0


def game_winner(board, side_to_move):
    """None — игра идёт; иначе 1 (чёрные) или -1 (белые)."""
    if count_pieces(board, BLACK) == 0:
        return WHITE
    if count_pieces(board, WHITE) == 0:
        return BLACK
    if not has_legal_move(board, side_to_move):
        return -side_to_move
    return None


def evaluate_board(board, side):
    """Эвристика для обучения: позиция с точки зрения side."""
    score = 0.0
    for x in range(8):
        for y in range(8):
            p = board[x][y]
            if p == BLACK:
                score += 10 + x * 0.5
            elif p == BLACK_KING:
                score += 25 + x * 0.3
            elif p == WHITE:
                score -= 10 + (7 - x) * 0.5
            elif p == WHITE_KING:
                score -= 25 + (7 - x) * 0.3
    return score if side > 0 else -score


def move_signature(sx, sy, tx, ty, caps):
    return (sx, sy, tx, ty, tuple(caps))


def apply_move(board, sx, sy, tx, ty, caps):
    nb = copy_board(board)
    piece = nb[sx][sy]
    nb[sx][sy] = EMPTY
    for cx, cy in caps:
        nb[cx][cy] = EMPTY
    nb[tx][ty] = piece
    return promote(nb)


def moves_with_signatures(board, side):
    """[(signature, new_board, n_captured), ...]"""
    out = []
    seen = set()
    must_jump = jump_exists(board, side)
    for x in range(8):
        for y in range(8):
            p = board[x][y]
            if (side > 0 and not is_black(p)) or (side < 0 and not is_white(p)):
                continue
            if must_jump:
                for sx, sy, tx, ty, caps in get_capture_moves(board, x, y, side):
                    sig = move_signature(sx, sy, tx, ty, caps)
                    if sig in seen:
                        continue
                    seen.add(sig)
                    nb = apply_move(board, sx, sy, tx, ty, caps)
                    out.append((sig, nb, len(caps)))
            else:
                for sx, sy, tx, ty, _ in get_step_moves(board, x, y):
                    p2 = board[sx][sy]
                    if (side > 0 and not is_black(p2)) or (side < 0 and not is_white(p2)):
                        continue
                    sig = move_signature(sx, sy, tx, ty, [])
                    if sig in seen:
                        continue
                    seen.add(sig)
                    nb = apply_move(board, sx, sy, tx, ty, [])
                    out.append((sig, nb, 0))
    return out


def best_black_move(board, depth=3):
    """Сильный ход чёрных: макс. взятие + мини-макс по оценке позиции."""
    moves = moves_with_signatures(board, BLACK)
    if not moves:
        return None

    max_cap = max(m[2] for m in moves)
    moves = [m for m in moves if m[2] == max_cap]

    def minimax(b, d, maximizing):
        w = game_winner(b, WHITE if maximizing else BLACK)
        if w == BLACK:
            return 100000
        if w == WHITE:
            return -100000
        if d == 0:
            return evaluate_board(b, BLACK)
        side = BLACK if maximizing else WHITE
        ms = moves_with_signatures(b, side)
        if not ms:
            return evaluate_board(b, BLACK) if maximizing else -evaluate_board(b, BLACK)
        mc = max(m[2] for m in ms)
        ms = [m for m in ms if m[2] == mc]
        scores = []
        for _, nb, _ in ms:
            scores.append(minimax(nb, d - 1, not maximizing))
        return max(scores) if maximizing else min(scores)

    best = None
    best_score = -10**9
    for m in moves:
        _, nb, _ = m
        sc = minimax(nb, depth - 1, False)
        if sc > best_score:
            best_score = sc
            best = m
    return best


def best_white_move(board, depth=3):
    """Сильный ход белых: макс. взятие + мини-макс (оценка с точки зрения белых)."""
    moves = moves_with_signatures(board, WHITE)
    if not moves:
        return None

    max_cap = max(m[2] for m in moves)
    moves = [m for m in moves if m[2] == max_cap]

    def minimax(b, d, whites_turn):
        side_to_move = WHITE if whites_turn else BLACK
        w = game_winner(b, side_to_move)
        if w == WHITE:
            return 100000
        if w == BLACK:
            return -100000
        if d == 0:
            return evaluate_board(b, WHITE)
        ms = moves_with_signatures(b, side_to_move)
        if not ms:
            return evaluate_board(b, WHITE)
        mc = max(m[2] for m in ms)
        ms = [m for m in ms if m[2] == mc]
        scores = [minimax(nb, d - 1, not whites_turn) for _, nb, _ in ms]
        return max(scores) if whites_turn else min(scores)

    best = None
    best_score = -10**9
    for m in moves:
        _, nb, _ = m
        sc = minimax(nb, depth - 1, False)
        if sc > best_score:
            best_score = sc
            best = m
    return best
