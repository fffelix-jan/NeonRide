import pygame
from scratch_pen import *
from nrconstants import *
from nrutil import *

goal_x = [-1478, -2081, -1557, 1036, -2243, -3417, -2939, -1449]
goal_y = [-512, -634, -463, -713, -763, -1511, -2, -609]

def load_level(level: int, x: int, y: int, pen: ScratchPen) -> None:
    if level == 1:
        level1(x, y, pen)
    elif level == 2:
        level2(x, y, pen)
    elif level == 3:
        level3(x, y, pen)
    elif level == 4:
        level4(x, y, pen)
    elif level == 5:
        level5(x, y, pen)
    elif level == 6:
        level6(x, y, pen)
    elif level == 7:
        level7(x, y, pen)
    elif level == 8:
        level8(x, y, pen)
    else:
        the_other_level(x, y, pen)

def level1(x: int, y: int, pen: ScratchPen) -> None:
    pen.set_pen_size(5)
    pen.set_pen_color(LEVEL_COLOR)
    pen.pen_up()
    pen.goto(-1000 + x, 1200 + y)
    pen.pen_down()
    pen.goto(-400 + x, 1200 + y)
    pen.goto(-400 + x, 1150 + y)
    pen.goto(-500 + x, 1150 + y)
    pen.goto(-500 + x, 300 + y)
    pen.goto(-40 + x, 300 + y)
    pen.goto(-40 + x, -10 + y)
    pen.goto(300 + x, -10 + y)
    pen.goto(300 + x, 100 + y)
    pen.goto(400 + x, 100 + y)
    pen.goto(400 + x, 80 + y)
    pen.goto(420 + x, 80 + y)
    pen.goto(420 + x, 60 + y)
    pen.goto(440 + x, 60 + y)
    pen.goto(440 + x, 40 + y)
    pen.goto(460 + x, 40 + y)
    pen.goto(460 + x, -100 + y)
    pen.goto(700 + x, -100 + y)
    pen.goto(700 + x, -140 + y)
    pen.goto(925 + x, -140 + y)
    pen.goto(925 + x, 500 + y)
    pen.goto(1500 + x, 500 + y)
    pen.set_pen_color(GOAL_COLOR)
    pen.goto(1500 + x, 575 + y)
    pen.set_pen_color(LEVEL_COLOR)
    pen.goto(1500 + x, 1000 + y)
    pen.goto(1300 + x, 1000 + y)
    pen.goto(1300 + x, 1500 + y)
    pen.pen_up()
    pen.goto(800 + x, -100 + y)
    pen.pen_down()
    pen.goto(825 + x, -100 + y)
    pen.goto(825 + x, 500 + y)
    pen.goto(700 + x, 500 + y)
    pen.goto(700 + x, 475 + y)
    pen.goto(800 + x, 475 + y)
    pen.goto(800 + x, -100 + y)
    pen.pen_up()
    pen.goto(200 + x, 50 + y)
    pen.pen_down()
    pen.goto(250 + x, 50 + y)
    pen.goto(250 + x, 30 + y)
    pen.goto(200 + x, 30 + y)
    pen.goto(200 + x, 50 + y)
    pen.pen_up()
    if not((abs(730 + x) > 235 and abs(730 + x) - 26 * 7.5 > 235) or abs(-150 + y) > 175):
        load_message_at(pen, "wall/jump/to/climb/this/up", 730 + x, -150 + y, 50, ZERO_POINT_FIVE_COLOR)
        pen.set_pen_color(LEVEL_COLOR)

def level2(x: int, y: int, pen: ScratchPen) -> None:
    pen.set_pen_size(5)
    pen.set_pen_color(LEVEL_COLOR)
    pen.pen_up()
    pen.goto(-30 + x, -15 + y)
    pen.pen_down()
    pen.goto(30 + x, -15 + y)


def level3(x: int, y: int, pen: ScratchPen) -> None:
    pass

def level4(x: int, y: int, pen: ScratchPen) -> None:
    pass

def level5(x: int, y: int, pen: ScratchPen) -> None:
    pass

def level6(x: int, y: int, pen: ScratchPen) -> None:
    pass

def level7(x: int, y: int, pen: ScratchPen) -> None:
    pass

def level8(x: int, y: int, pen: ScratchPen) -> None:
    pass

def the_other_level(x: int, y: int, pen: ScratchPen) -> None:
    pass