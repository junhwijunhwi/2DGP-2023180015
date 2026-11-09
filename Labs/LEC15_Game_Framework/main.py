import os
from pathlib import Path

from pico2d import open_canvas, close_canvas
import game_framework
import logo_mode


def main():
    os.chdir(Path(__file__).resolve().parent)
    open_canvas()
    try:
        game_framework.run(logo_mode)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
