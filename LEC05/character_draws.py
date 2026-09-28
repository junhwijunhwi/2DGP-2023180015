from pico2d import *
import math

open_canvas(800, 600)

character = load_image('character.png')

def move_circle():
    print("CIRCLE")

    for degree in range(360):
        theta = math.radians(degree)
        x =400+200*math.cos(theta)
        y =300+200*math.sin(theta)

        draw_character(x,y)
        

def move_top():
    print('TOP')
    for y in range(50,550,5):
        draw_character(50,y)
           
def move_right():
    print('RIGHT')
    for x in range(50,750,5):
        draw_character(x,550)
        
def move_left():
    print('LEFT')
    for x in range(750,50,-5):
        draw_character(x,50)

def move_bottom():
    print('BOTTOM')
    for y in range(550, 50, -5):
        draw_character(750, y)

        
def draw_character(x,y):
    clear_canvas()
    character.draw(x,y)
    update_canvas()
    delay(0.05)

def move_rectangle():
    print("RECTANGLE")
    move_right()
    move_bottom()
    move_left()
    move_top()
    pass

def move_straight():
    print('STRAIGHT')
    for x in range(50,750,5):
        draw_character(x,50)
    
def move_topmiddle():
    print('TOPMIDDLE')
    pass
def move_base():
    print('BASE')
    pass

def move_triangle():
    print("TRIANGLE")
    move_straight()
    move_topmiddle()
    move_base()
    pass


while True:
    # move_circle()
    # move_rectangle()
    move_triangle()
    pass

close_canvas()