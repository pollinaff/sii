"""Q-learning агент для бразильских шашек (чёрные = компьютер)."""
import pickle
import random
from pathlib import Path

from checkers_core import (
    BLACK,
    WHITE,
    apply_move,
    board_key,
    evaluate_board,
    game_winner,
    initial_board,
    moves_with_signatures,
)

MODEL_PATH = Path(__file__).parent / "q_table.pkl"


class QLearningAgent:
    """Tabular Q-learning: состояние — доска, действие — подпись хода."""

    def __init__(
        self,
        alpha=0.15,
        gamma=0.95,
        epsilon=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.9997,
    ):
        self.q = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

    def q_value(self, state, action):
        return self.q.get((state, action), 0.0)

    def choose_move(self, board, training=True):
        moves = moves_with_signatures(board, BLACK)
        if not moves:
            return None
        state = board_key(board)

        if training and random.random() < self.epsilon:
            return random.choice(moves)

        # В игре обязательно съесть максимум (как у белых в GUI)
        if not training:
            max_cap = max(m[2] for m in moves)
            moves = [m for m in moves if m[2] == max_cap]

        def score(item):
            sig, _, n_cap = item
            cap_w = 12.0 if not training else 1.5
            return self.q_value(state, sig) + n_cap * cap_w

        return max(moves, key=score)

    def update(self, state, action, reward, next_state, next_actions):
        key = (state, action)
        old = self.q.get(key, 0.0)
        if next_actions:
            best_next = max(self.q_value(next_state, sig) for sig in next_actions)
        else:
            best_next = 0.0
        target = reward + self.gamma * best_next
        self.q[key] = old + self.alpha * (target - old)

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, path=None):
        path = Path(path or MODEL_PATH)
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "q": self.q,
                    "epsilon": self.epsilon,
                },
                f,
            )

    def load(self, path=None):
        path = Path(path or MODEL_PATH)
        if not path.exists():
            return False
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.q = data["q"]
        self.epsilon = data.get("epsilon", self.epsilon_min)
        return True


def _random_white_move(board):
    moves = moves_with_signatures(board, WHITE)
    return random.choice(moves) if moves else None


def _print_train_header():
    print(f"{'Эпизод':>8} {'Побед':>8} {'Пораж.':>8} {'Win%':>8} {'ε':>8} {'|Q|':>10}")


def _print_train_row(ep, wins, losses, epsilon, q_size):
    rate = wins / max(1, wins + losses) * 100
    print(f"{ep:>8} {wins:>8} {losses:>8} {rate:>7.1f}% {epsilon:>8.3f} {q_size:>10}")


def train_agent(episodes=25000, verbose_every=2500):
    agent = QLearningAgent()
    wins, losses = 0, 0
    _print_train_header()

    for ep in range(1, episodes + 1):
        board = initial_board()
        side = WHITE

        while True:
            winner = game_winner(board, side)
            if winner is not None:
                if winner == BLACK:
                    wins += 1
                else:
                    losses += 1
                break

            if side == BLACK:
                old_board = board
                state = board_key(board)
                move = agent.choose_move(board, training=True)
                if move is None:
                    losses += 1
                    break
                sig, board, n_cap = move
                reward = n_cap * 2.0 - 0.02
                reward += (evaluate_board(board, BLACK) - evaluate_board(old_board, BLACK)) * 0.02

                winner = game_winner(board, WHITE)
                if winner is not None:
                    final_r = 25.0 if winner == BLACK else -25.0
                    agent.update(state, sig, final_r + reward, board_key(board), [])
                    if winner == BLACK:
                        wins += 1
                    else:
                        losses += 1
                    break

                wm = _random_white_move(board)
                if wm is None:
                    agent.update(state, sig, 25.0 + reward, board_key(board), [])
                    wins += 1
                    break

                _, board, _ = wm
                next_state = board_key(board)
                next_moves = moves_with_signatures(board, BLACK)
                agent.update(state, sig, reward, next_state, [m[0] for m in next_moves])

                winner = game_winner(board, BLACK)
                if winner is not None:
                    if winner == BLACK:
                        wins += 1
                    else:
                        losses += 1
                    break
                side = WHITE
            else:
                wm = _random_white_move(board)
                if wm is None:
                    wins += 1
                    break
                _, board, _ = wm
                side = BLACK

        agent.decay_epsilon()

        if ep % verbose_every == 0 or ep == episodes:
            _print_train_row(ep, wins, losses, agent.epsilon, len(agent.q))

    agent.epsilon = agent.epsilon_min
    agent.save()
    return agent


def get_trained_agent():
    agent = QLearningAgent(epsilon=0.0)
    if not agent.load():
        print("Модель не найдена. Запустите сии лаба 6.py для обучения.")
        return None
    agent.epsilon = 0.0
    return agent


def best_move_for_board(board):
    agent = get_trained_agent()
    if agent is None:
        return None
    return agent.choose_move(board, training=False)
