import os
from pathlib import Path

from pico2d import open_canvas, close_canvas
import game_framework

import play_mode as start_mode

if __name__ == '__main__':
    os.chdir(Path(__file__).resolve().parent)
    open_canvas(1600, 600)
    try:
        game_framework.run(start_mode)
    finally:
        close_canvas()

