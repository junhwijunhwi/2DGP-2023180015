from pico2d import *
import game_framework
import game_world
from boy import Boy
from grass import Grass


def handle_events():
    for event in get_events():
        if handle_event(event):
            return


def handle_event(event):
    if event.type == SDL_QUIT:
        game_framework.quit()
        return True
    elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
        import title_mode
        game_framework.change_mode(title_mode)
        return True
    elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
        if not getattr(event, 'repeat', 0):
            import pause_mode
            game_framework.push_mode(pause_mode)
            return True
    elif event.type == SDL_KEYDOWN and event.key == SDLK_i:
        if not getattr(event, 'repeat', 0):
            import item_mode
            game_framework.push_mode(item_mode)
            return True
    else:
        boy.handle_event(event)
    return False



def init():
    global boy


    boy = Boy()
    game_world.add_oject(boy)

    grass = Grass()
    game_world.add_oject(grass, 0)



def update():
    game_world.update()


def draw():
    clear_canvas()
    game_world.render()


def render():
    draw()
    update_canvas()


def finish():
    global boy
    game_world.clear()
    del boy


def pause():
    pass


def resume():
    pass

