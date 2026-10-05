from pico2d import *

open_canvas()

grass = load_image('grass.png')
character = load_image('animation_sheet.png')
frame = 0
action = 0

def draw_frame(k):
    global frame
    grass.draw(400,30)
    bottom = k
    character.clip_draw(
        frame * 100, k, # left, bottom
        100,100,
        x,90 # destination x,y
    )
    update_canvas()
    
    frame = (frame + 1) % 8
    delay(0.05)

for x in range(0,800,5):
    clear_canvas()
    draw_frame(100)
    
for x in range(800,50,-5):
    clear_canvas()
    draw_frame(0)

for x in range(0,800,5):
    clear_canvas()
    draw_frame(300)
    
for x in range(800,50,-5):
    clear_canvas()
    draw_frame(200)

close_canvas()

