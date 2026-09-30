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
    Animation('걷기', (
        Frame(10, 10, 62, 84, 31, 84),
        Frame(84, 10, 70, 84, 35, 84),
        Frame(166, 10, 72, 84, 36, 84),
        Frame(250, 10, 70, 84, 35, 84),
        Frame(332, 10, 62, 84, 31, 84),
        Frame(406, 10, 54, 84, 27, 84),
        Frame(472, 10, 52, 84, 26, 84),
        Frame(536, 10, 54, 84, 27, 84),
    )),
    Animation('달리기', (
        Frame(10, 116, 62, 84, 31, 84),
        Frame(84, 116, 78, 84, 39, 84),
        Frame(174, 116, 78, 84, 39, 84),
        Frame(264, 116, 62, 84, 31, 84),
        Frame(338, 116, 55, 84, 27.5, 84),
        Frame(405, 116, 55, 84, 27.5, 84),
    ), 0.08),
    Animation('점프', (
        Frame(10, 222, 62, 84, 31, 84),
        Frame(84, 222, 66, 80, 33, 84),
        Frame(162, 220, 70, 70, 35, 86),
        Frame(244, 220, 70, 62, 35, 86),
        Frame(326, 220, 66, 70, 33, 86),
        Frame(404, 222, 62, 80, 31, 84),
    )),
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
