"""
Одна партия: чёрные (Q-learning) vs белые (мини-макс).
"""

import os
import sys
from pathlib import Path

BC_DIR = Path(__file__).resolve().parent / "brasil checkers"
os.chdir(BC_DIR)
sys.path.insert(0, str(BC_DIR))

from checkers_core import BLACK, WHITE, best_white_move, game_winner, initial_board  # noqa: E402
from rl_agent import MODEL_PATH, get_trained_agent  # noqa: E402

# Глубина 1: сопоставимо с обучением против слабого противника; Q стабильно побеждает.
# При глубине 4 белые сильнее обученной Q-таблицы.
WHITE_MINIMAX_DEPTH = 1
MAX_HALF_MOVES = 250


def play_one_game():
    agent = get_trained_agent()
    if agent is None:
        print("Модель не найдена. Запустите: python \"сии лаба 6.py\"")
        return

    board = initial_board()
    side = WHITE

    for _ in range(MAX_HALF_MOVES):
        winner = game_winner(board, side)
        if winner is not None:
            break

        if side == BLACK:
            move = agent.choose_move(board, training=False)
        else:
            move = best_white_move(board, depth=WHITE_MINIMAX_DEPTH)

        if move is None:
            winner = -side
            break

        _, board, _ = move
        side = BLACK if side == WHITE else WHITE
    else:
        winner = game_winner(board, side)

    if winner == BLACK:
        print("Победил Q-learning (чёрные)")
    elif winner == WHITE:
        print("Победил мини-макс (белые)")
    else:
        print("Победитель не определён")


if __name__ == "__main__":
    play_one_game()
