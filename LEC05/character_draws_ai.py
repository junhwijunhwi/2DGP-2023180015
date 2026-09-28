import math
from pathlib import Path

from pico2d import (
    SDL_KEYDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    clear_canvas,
    close_canvas,
    delay,
    get_events,
    load_image,
    open_canvas,
    update_canvas,
)


FRAME_DELAY = 0.01


def circle_path():
    for degree in range(360):
        angle = math.radians(degree)
        yield 400 + 200 * math.cos(angle), 300 + 200 * math.sin(angle)


def line_path(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    steps = max(1, math.ceil(max(abs(dx), abs(dy)) / 5))

    for step in range(steps + 1):
        progress = step / steps
        yield start[0] + dx * progress, start[1] + dy * progress


def polygon_path(corners):
    for index in range(len(corners)):
        yield from line_path(corners[index], corners[(index + 1) % len(corners)])


def draw_path(character, positions):
    for x, y in positions:
        for event in get_events():
            if event.type == SDL_QUIT or (
                event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE
            ):
                return False

        clear_canvas()
        character.draw(x, y)
        update_canvas()
        delay(FRAME_DELAY)

    return True


def main():
    open_canvas(800, 600)
    try:
        character = load_image(str(Path(__file__).with_name("character.png")))
        rectangle = [(50, 50), (750, 50), (750, 550), (50, 550)]
        triangle = [(50, 50), (750, 50), (400, 400)]

        while True:
            for positions in (circle_path(), polygon_path(rectangle), polygon_path(triangle)):
                if not draw_path(character, positions):
                    return
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
