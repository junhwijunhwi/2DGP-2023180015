from pathlib import Path
import sys

from pico2d import *
import game_framework


def init():
    global image
    image = load_image(str(Path(__file__).with_name('title.png')))


def finish():
    global image
    del image


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            import play_mode
            game_framework.change_mode(play_mode)
            return


def update():
    pass


def render():
    clear_canvas()
    width, height = get_canvas_width(), get_canvas_height()
    image.draw(width / 2, height / 2, width, height)
    update_canvas()


def pause():
    pass


def resume():
    pass


if __name__ == '__main__':
    open_canvas()
    try:
        game_framework.run(sys.modules[__name__])
    finally:
        close_canvas()
