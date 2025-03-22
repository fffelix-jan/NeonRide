import pygame
from scratch_pen import *
from nrconstants import *
from nrutil import *

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

def level2(x: int, y: int, pen: ScratchPen) -> None:
    pass

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