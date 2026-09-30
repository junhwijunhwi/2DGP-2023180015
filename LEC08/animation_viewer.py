from pathlib import Path

from pico2d import *


FRAME_WIDTH = 80
FRAME_HEIGHT = 105
# 아래쪽 행부터 각 행에 들어 있는 프레임 수
FRAME_COUNTS = (8, 6, 6, 8)
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
SCALE = 5


def play_animation(character, row):
    for frame in range(FRAME_COUNTS[row]):
        clear_canvas()
        character.clip_draw(
            (frame % FRAME_COUNTS[row]) * FRAME_WIDTH,
            row * FRAME_HEIGHT,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            CANVAS_WIDTH // 2,
            CANVAS_HEIGHT // 2,
            FRAME_WIDTH * SCALE,
            FRAME_HEIGHT * SCALE,
        )
        update_canvas()
        delay(0.05)


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        character = load_image(str(Path(__file__).with_name('Robot_sprite_sheet.png')))
        for row in (3, 2, 1, 0):
            play_animation(character, row)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
