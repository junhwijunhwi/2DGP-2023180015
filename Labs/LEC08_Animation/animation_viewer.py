from pathlib import Path

from pico2d import *


FRAME_WIDTH = 80
FRAME_HEIGHT = 105
# 아래쪽 행부터 각 행에 들어 있는 프레임 수
FRAME_COUNTS = (8, 6, 6, 8)

open_canvas()
character = load_image(str(Path(__file__).with_name('Robot_sprite_sheet.png')))


def play_animation(row, positions):
    for frame, x in enumerate(positions):
        clear_canvas()
        character.clip_draw(
            (frame % FRAME_COUNTS[row]) * FRAME_WIDTH,
            row * FRAME_HEIGHT,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            x,
            90,
        )
        update_canvas()
        delay(0.05)


play_animation(1, range(0, 800, 5))
play_animation(0, range(800, 50, -5))
play_animation(3, range(0, 800, 5))
play_animation(2, range(800, 50, -5))

close_canvas()
