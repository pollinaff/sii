"""
Л.р. №6. Обучение Q-learning для бразильских шашек.

"""

import os
import sys
from pathlib import Path

BC_DIR = Path(__file__).resolve().parent / "brasil checkers"
os.chdir(BC_DIR)
sys.path.insert(0, str(BC_DIR))

from rl_agent import train_agent  # noqa: E402

EPISODES = 35000

if __name__ == "__main__":
    train_agent(episodes=EPISODES, verbose_every=3000)
