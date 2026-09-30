from pathlib import Path
from dataclasses import dataclass

from pico2d import *


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
SCALE = 5
GROUND_Y = CANVAS_HEIGHT / 2 - 84 * SCALE / 2


@dataclass(frozen=True)
class Frame:
    left: int
    top: int
    width: int
    height: int
    anchor_x: float
    anchor_y: float


@dataclass(frozen=True)
class Animation:
    name: str
    frames: tuple[Frame, ...]
    frame_seconds: float = 0.12


def grid_frame(column, row):
    return Frame(column * 80, 422 - (row + 1) * 105, 80, 105, 40, 94)


ANIMATIONS = (
    Animation('걷기', tuple(grid_frame(i, 3) for i in range(8))),
    Animation('달리기', tuple(grid_frame(i, 2) for i in range(6))),
    Animation('점프', tuple(grid_frame(i, 1) for i in range(6))),
    Animation('공격', tuple(grid_frame(i, 0) for i in range(8))),
)


def draw_frame(character, frame):
    character.clip_draw(
        frame.left,
        character.h - frame.top - frame.height,
        frame.width,
        frame.height,
        CANVAS_WIDTH / 2 + (frame.width / 2 - frame.anchor_x) * SCALE,
        GROUND_Y + (frame.anchor_y - frame.height / 2) * SCALE,
        frame.width * SCALE,
        frame.height * SCALE,
    )


def play_animation(character, animation):
    for frame in animation.frames:
        clear_canvas()
        draw_frame(character, frame)
        update_canvas()
        delay(animation.frame_seconds)


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        character = load_image(str(Path(__file__).with_name('Robot_sprite_sheet.png')))
        for animation in ANIMATIONS:
            play_animation(character, animation)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
