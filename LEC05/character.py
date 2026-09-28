from pico2d import *
import math

open_canvas(800, 600)

character = load_image('character.png')
angle = 0

while True:
    x = 200 + 100 * math.sin(angle)
    y = 200 + 100 * math.cos(angle)

    clear_canvas()
    character.draw(x, y)
    update_canvas()
    delay(0.01)
    angle += 0.05

close_canvas()

