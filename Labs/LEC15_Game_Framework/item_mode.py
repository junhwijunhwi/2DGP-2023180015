import os
from pathlib import Path

from pico2d import *
import game_framework
import play_mode


def init():
    global image, font
    image = load_image(str(Path(__file__).with_name('item_select.png')))
    font_path = str(Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts' / 'arial.ttf')
    font = load_font(font_path, 20)


def finish():
    global image, font
    del image
    del font


def handle_events():
    for event in get_events():
        if event.type == SDL_KEYDOWN:
            if event.key in (SDLK_i, SDLK_ESCAPE):
                if not getattr(event, 'repeat', 0):
                    game_framework.pop_mode()
                    return
                continue
            if event.key in (SDLK_0, SDLK_1, SDLK_2):
                play_mode.boy.ball_size = {
                    SDLK_0: None,
                    SDLK_1: 21,
                    SDLK_2: 41,
                }[event.key]
                continue
        if play_mode.handle_event(event):
            return


def update():
    play_mode.update()


def draw():
    play_mode.draw()
    x, y = get_canvas_width() - 156, get_canvas_height() - 160
    image.draw(x, y)
    labels = {None: 'None', 21: 'Small ball', 41: 'Big ball'}
    lines = [
        (y + 130, 'ITEMS (game continues)'),
        (y - 130, 'Selected: ' + labels[play_mode.boy.ball_size]),
        (y - 155, 'I / ESC: Close  |  P: Pause'),
    ]
    for text_y, text in lines:
        font.draw(x - 136 + 1, text_y - 1, text, (0, 0, 0))
        font.draw(x - 136, text_y, text, (255, 255, 255))


def render():
    draw()
    update_canvas()


def pause():
    pass


def resume():
    pass
