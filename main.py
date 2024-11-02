# Neon Ride: Platformer Game drawn with pen (originally from Scratch)

# Note to self: All the display scaling stuff is useless
# Just use this: https://stackoverflow.com/questions/68156731/how-to-avoid-automatic-resolution-adjustment-by-pygame-fullscreen

import pygame
import sys
import math
import time

from nrlevels import *

# Constants
NATIVE_WIDTH = 480
NATIVE_HEIGHT = 360
ASPECT_RATIO = NATIVE_WIDTH / NATIVE_HEIGHT
BACKGROUND_COLOR = (0, 0, 0)
CHARACTER_COLOR = "#EE7D16"

# Global variables
move = 0
time_global = 0
enter_exit = 1
grid = False
grid_size = 100
start = 'f'
level = 1
falling = False
y = 0
x = 0
xvel = 0
y_pressed = False
size = 0

# Initialize Pygame
pygame.init()

# Set initial window size
screen = pygame.display.set_mode((NATIVE_WIDTH, NATIVE_HEIGHT), pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("Neon Ride")

# Frame rate control
clock = pygame.time.Clock()

## Timers
# Timers that trigger the different stages of the start animation
START_ANI_STAGE_1_TIMER = pygame.USEREVENT + 1
START_ANI_STAGE_2_TIMER = pygame.USEREVENT + 2
START_ANI_STATE_4_TO_11_TIMER = pygame.USEREVENT + 3
START_ANI_STAGE_12_TIMER = pygame.USEREVENT + 4
## End of Timers


# Game states
STATE_ANIMATION = "animation"
STATE_WAITING_FOR_INPUT = "waiting_for_input"
STATE_GAME_SCREEN = "game_screen"
STATE_INSTRUCTION_SCREEN = "instruction_screen"
STATE_EMERGENCY = "emergency"
STATE_MENU_SCREEN = "menu_screen"

# Variables to track state and animation progress
current_state = STATE_ANIMATION
animation_step = 0

# Convert Scratch colour integer to hex code
def scratch_color_to_hex(color_int):
    # Extract red, green, and blue components
    r = (color_int // 65536) % 256
    g = (color_int // 256) % 256
    b = color_int % 256
    
    # Convert to hex string
    hex_code = f'#{r:02x}{g:02x}{b:02x}'
    return hex_code

# Function to convert Scratch coordinates (center is 0,0) to Pygame coordinates (top-left is 0,0)
def scratch_to_pygame_coordinates(x, y):
    pygame_x = x + (NATIVE_WIDTH // 2)
    pygame_y = (NATIVE_HEIGHT // 2) - y
    return pygame_x, pygame_y

## ScratchPen class (used globally)
# This is a reimplmentation of the Scratch pen in Pygame
class ScratchPen:
    def __init__(self, surface):
        self.surface = surface
        self.x = 0
        self.y = 0
        self.direction = 90  # In degrees, 90 means right
        self.pen_down_status = False
        self.pen_size = 1
        self.pen_color = (0, 255, 0)  # Default color is green
        self.pen_shade = 50  # Representing 50% shade (normal)
        self.pen_visible_size = 15  # The pen's circle diameter for collision detection

        # Pen history for drawing
        self.last_pos = (self.x, self.y)  # Store the last position for line drawing

    # Turn clockwise by n degrees
    def turn_right(self, n):
        self.direction += n
        self.direction %= 360
    
    # Turn counter-clockwise by n degrees
    def turn_left(self, n):
        self.direction -= n
        self.direction %= 360

    # Move pen to new position
    def goto(self, x, y):
        if self.pen_down_status:
            draw_rounded_line(self.surface, self.pen_color, scratch_to_pygame_coordinates(self.x, self.y), scratch_to_pygame_coordinates(x, y), self.pen_size)
        self.x, self.y = x, y  # Update native coordinates
        self.last_pos = (self.x, self.y)  # Update for the next movement

    # Change x by n
    def change_x_by(self, n):
        self.goto(self.x + n, self.y)

    # Change y by n
    def change_y_by(self, n):
        self.goto(self.x, self.y + n)

    # Point pen in a specific direction (in degrees)
    def point_in_direction(self, degrees):
        self.direction = degrees

    # Set pen size
    def set_pen_size(self, size):
        self.pen_size = size

    # Set pen color (hex code)
    def set_pen_color(self, hex_code):
        self.pen_color = pygame.Color(hex_code)
    
    # Set pen color (Scratch color integer)
    def set_pen_color_scratch(self, color_int):
        self.pen_color = pygame.Color(scratch_color_to_hex(int(color_int)))

    # Set pen shade
    def set_pen_shade(self, shade_percent):
        self.pen_shade = shade_percent
        # Adjust the brightness of the color based on the shade
        self.pen_color = self.adjust_color_brightness(self.pen_color, shade_percent)

    # Pen down
    def pen_down(self):
        self.pen_down_status = True

    # Pen up
    def pen_up(self):
        self.pen_down_status = False

    # Erase all
    def erase_all(self):
        self.surface.fill(BACKGROUND_COLOR)

    # Adjust color brightness based on shade percentage
    def adjust_color_brightness(self, color, percent):
        # Percent is between 0 and 100
        if percent < 50:
            factor = percent / 50  # Scale between 0 and 1
            new_color = pygame.Color(int(color.r * factor),
                                    int(color.g * factor),
                                    int(color.b * factor))
        else:
            factor = (percent - 50) / 50  # Scale between 0 and 1
            new_color = pygame.Color(int(color.r + (255 - color.r) * factor),
                                    int(color.g + (255 - color.g) * factor),
                                    int(color.b + (255 - color.b) * factor))
        return new_color

    # Check if pen is touching a specific color
    def touching_color(self, color):
        pen_rect = pygame.Rect(self.x - self.pen_visible_size // 2,
                            self.y - self.pen_visible_size // 2,
                            self.pen_visible_size, self.pen_visible_size)

        # Get pixel array for current surface
        pixels = pygame.PixelArray(self.surface)

        # Loop through the pen's area to check for the color
        for x in range(pen_rect.left, pen_rect.right):
            for y in range(pen_rect.top, pen_rect.bottom):
                if x < 0 or y < 0 or x >= self.surface.get_width() or y >= self.surface.get_height():
                    continue  # Skip out-of-bounds pixels
                if pixels[x, y] == self.surface.map_rgb(color):
                    pixels.close()
                    return True
        pixels.close()
        return False
    
    # Move the pen n steps forward in the current direction
    def move(self, n):
        # Convert Scratch's direction system to standard trigonometric angles:
        # 0 degrees is up, 90 is right, 180 is down, 270 is left.
        # We need to rotate this by -90 degrees for standard math angles.
        radians = math.radians(self.direction - 90)
        
        # Calculate the new position using trigonometry
        delta_x = n * math.cos(radians)
        delta_y = -n * math.sin(radians)  # Negating because in pygame, positive y is down
        
        # Move the pen to the new position
        self.goto(self.x + delta_x, self.y + delta_y)

# Create a pen object
pen = ScratchPen(screen)
## End of Pen class

def draw_rounded_line(surface, color, start_pos, end_pos, thickness):
    """
    Draws a line with rounded ends.
    
    Args:
        surface: The Pygame surface to draw on.
        color: The color of the line.
        start_pos: The starting position of the line (x, y).
        end_pos: The ending position of the line (x, y).
        thickness: The thickness of the line.
    """
    p1v = pygame.math.Vector2(start_pos)
    p2v = pygame.math.Vector2(end_pos)
    lv = (p2v - p1v).normalize()
    lnv = pygame.math.Vector2(-lv.y, lv.x) * thickness // 2
    pts = [p1v + lnv, p2v + lnv, p2v - lnv, p1v - lnv]
    pygame.draw.polygon(surface, color, pts)
    pygame.draw.circle(surface, color, start_pos, round(thickness / 2))
    pygame.draw.circle(surface, color, end_pos, round(thickness / 2))


## Functions to draw text
def draw_letter(letter, size=100):
    if letter == '/':
        return
    letter = letter.lower() # Scratch uses case-insensitive letter comparison
    if not(letter == '.' or letter == '!' or letter == '-'):
        pen.pen_down()
    else:
        pen.pen_up()

    # GitHub Copilot seems to know most of this letter-drawing code by itself
    # Maybe someone ported this to Python before me...
    if letter == 'a':
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-30 * (size / 100))
        pen.change_y_by(15 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_y_by(30 * (size / 100))
    elif letter == 'b':
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-13 * (size / 100))
        pen.change_y_by(13 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(8 * (size / 100))
        pen.change_x_by(-8 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(13 * (size / 100))
    elif letter == 'c':
        pen.change_x_by(10 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(-30 * (size / 100))
        pen.change_x_by(10 * (size / 100))
    elif letter == 'd':
        pen.change_x_by(8 * (size / 100))
        pen.change_x_by(-8 * (size / 100))
        pen.change_y_by(-30 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(28 * (size / 100))
    elif letter == 'e':
        pen.change_x_by(10 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(5 * (size / 100))
        pen.change_x_by(-5 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(10 * (size / 100))
    elif letter == 'f':
        pen.change_x_by(10 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(5 * (size / 100))
        pen.change_x_by(-5 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
    elif letter == 'g':
        pen.change_x_by(10 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(-30 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(15 * (size / 100))
        pen.change_x_by(-5 * (size / 100))
    elif letter == 'h':
        pen.change_y_by(-30 * (size / 100))
        pen.change_y_by(15 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(15 * (size / 100))
        pen.change_y_by(-30 * (size / 100))
    elif letter == 'i':
        pen.change_x_by(10 * (size / 100))
        pen.change_x_by(-5 * (size / 100))
        pen.change_y_by(-30 * (size / 100))
        pen.change_x_by(-5 * (size / 100))
        pen.change_x_by(10 * (size / 100))
    elif letter == 'j':
        pen.change_x_by(10 * (size / 100))
        pen.change_x_by(-5 * (size / 100))
        pen.change_y_by(-30 * (size / 100))
        pen.change_x_by(-5 * (size / 100))
    elif letter == 'k':
        pen.change_y_by(-30 * (size / 100))
        pen.change_y_by(15 * (size / 100))
        pen.change_x_by(5 * (size / 100))
        pen.change_y_by(10 * (size / 100))
        pen.change_y_by(-10 * (size / 100))
        pen.change_x_by(5 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
    elif letter == 'l':
        pen.change_y_by(-30 * (size / 100))
        pen.change_x_by(10 * (size / 100))
    elif letter == 'm':
        pen.change_y_by(-30 * (size / 100))
        pen.change_y_by(30 * (size / 100))
        pen.change_x_by(5 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_y_by(15 * (size / 100))
        pen.change_x_by(5 * (size / 100))
        pen.change_y_by(-30 * (size / 100))
    elif letter == 'n':
        pen.change_y_by(-30 * (size / 100))
        pen.change_y_by(30 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-30 * (size / 100))
    elif letter == 'o':
        pen.change_y_by(-30 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(30 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
    elif letter == 'p':
        pen.change_y_by(-30 * (size / 100))
        pen.change_y_by(30 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
    elif letter == 'q':
        pen.change_y_by(-25 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-5 * (size / 100))
        pen.change_y_by(30 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
    elif letter == 'r':
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_y_by(30 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(8 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
    elif letter == 's':
        pen.change_x_by(10 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
    elif letter == 't':
        pen.change_x_by(10 * (size / 100))
        pen.change_x_by(-5 * (size / 100))
        pen.change_y_by(-30 * (size / 100))
    elif letter == 'u':
        pen.change_y_by(-30 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(30 * (size / 100))
    elif letter == 'v':
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(2 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(6 * (size / 100))
        pen.change_y_by(15 * (size / 100))
        pen.change_x_by(2 * (size / 100))
        pen.change_y_by(15 * (size / 100))
    elif letter == 'w':
        pen.change_y_by(-30 * (size / 100))
        pen.change_x_by(5 * (size / 100))
        pen.change_y_by(15 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(5 * (size / 100))
        pen.change_y_by(30 * (size / 100))
    elif letter == 'x':
        pen.change_y_by(-10 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(10 * (size / 100))
        pen.change_y_by(-10 * (size / 100))
        pen.change_x_by(-5 * (size / 100))
        pen.change_y_by(-10 * (size / 100))
        pen.change_x_by(5 * (size / 100))
        pen.change_y_by(-10 * (size / 100))
        pen.change_y_by(10 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(-10 * (size / 100))
    elif letter == 'y':
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(15 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(-5 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
    elif letter == 'z':
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(10 * (size / 100))
    elif letter == '.':
        pen.change_y_by(-30 * (size / 100))
        pen.pen_down()
    elif letter == '!':
        pen.change_x_by(5 * (size / 100))
        pen.pen_down()
        pen.change_y_by(-20 * (size / 100))
        pen.pen_up()
        pen.change_y_by(-10 * (size / 100))
        pen.pen_down()
    elif letter == '?':
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(-5 * (size / 100))
        pen.change_y_by(-5 * (size / 100))
        pen.pen_up()
        pen.change_y_by(-10 * (size / 100))
        pen.pen_down()
    elif letter == '"':
        pen.change_y_by(-10 * (size / 100))
        pen.pen_up()
        pen.change_y_by(10 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.pen_down()
        pen.change_y_by(-10 * (size / 100))
    elif letter == '0':
        pen.change_y_by(-30 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(30 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.pen_up()
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(5 * (size / 100))
        pen.pen_down()
        pen.change_y_by(1 * (size / 100))
    elif letter == '1':
        pen.change_x_by(5 * (size / 100))
        pen.change_y_by(-30 * (size / 100))
        pen.change_x_by(5 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
    elif letter == '2':
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-10 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(-20 * (size / 100))
        pen.change_x_by(10 * (size / 100))
    elif letter == '3':
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
    elif letter == '4':
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_y_by(30 * (size / 100))
    elif letter == '5':
        pen.change_x_by(10 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(-10 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-20 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
    elif letter == '6':
        pen.change_y_by(-30 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(15 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
    elif letter == '7':
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-30 * (size / 100))
    elif letter == '8':
        pen.change_y_by(-30 * (size / 100))
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(30 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(10 * (size / 100))
    elif letter == '9':
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-30 * (size / 100))
        pen.change_y_by(15 * (size / 100))
        pen.change_x_by(-10 * (size / 100))
        pen.change_y_by(15 * (size / 100))
    elif letter == '-':
        pen.change_y_by(-15 * (size / 100))
        pen.pen_down()
        pen.change_x_by(10 * (size / 100))
    else:
        print(f"WARN: Letter '{letter}' is not supported for drawing.")
    pen.pen_up()
    # That's it for this super long function!
    # I'm surprised GitHub Copilot knew EXACTLY what I was gonna write next!


# Function to draw a message at a specific location
def load_message_at(message, x, y, font_size, color):
    prev_status = pen.pen_down_status
    pen.pen_up()
    pen.goto(x, y)
    size = font_size
    if color == "0.1":
        pen.set_pen_color('#202020')
    elif color == "0.5":
        pen.set_pen_color('#9C9EA2')
    else:
        pen.set_pen_color_scratch(color)
        pen.set_pen_shade(50)
    for doods in range(len(message)):
        pen.set_pen_size(3 * (size / 100))
        draw_letter(message[doods], font_size)
        pen.goto(x + ((doods + 1) * 15) * (size / 100), y)
    
    # Restore the previous pen status
    pen.pen_down_status = prev_status


## Input functions
# Function to check if a key is pressed
def check_key_pressed(char):
    # Get the current state of all keys
    keys = pygame.key.get_pressed()
    
    # Convert the input character to its corresponding pygame key code
    key_code = getattr(pygame, f'K_{char.lower()}', None)
    
    if key_code is None:
        # Invalid key character
        raise ValueError(f"The character '{char}' is not a valid key.")
    
    # Check if the specified key is pressed
    return keys[key_code]
## End of input functions


## Screens 'n' stuff
# Dark field - the initial dimmed state of the intro screen
def dark_field():
    pen.pen_up()
    pen.set_pen_size(15)
    pen.goto(-240, -20)
    pen.pen_down()
    pen.set_pen_color("#0A0D09")
    pen.goto(240, -20)
    pen.pen_up()
    pen.set_pen_size(10)
    pen.goto(0, 140)
    pen.pen_down()
    pen.point_in_direction(112)
    for i in range(8):
        pen.move(60)
        pen.turn_right(45)
    pen.pen_up()
    pen.change_x_by(-20)
    pen.change_y_by(-30)
    pen.pen_down()
    pen.change_y_by(-40)
    pen.pen_up()
    pen.change_x_by(40)
    pen.pen_down()
    pen.change_y_by(40)
    pen.pen_up()



timer_set = False
def start_animation(state):
    global timer_set
    global animation_step
    if not timer_set:
        if state == 0:
            pen.erase_all()
            dark_field()
            print("Setting stage 1 timer")
            pygame.time.set_timer(START_ANI_STAGE_1_TIMER, 500)
            timer_set = True
        elif state == 1:
            pen.set_pen_size(15)
            pen.goto(-240, -20)
            pen.pen_down()
            pen.set_pen_color("#4A6CD4")
            pen.goto(240, -20)
            pen.pen_up()
            print("Setting stage 2 timer")
            pygame.time.set_timer(START_ANI_STAGE_2_TIMER, 2000)
            timer_set = True
        elif state == 2:
            start_animation = 1
            pen.set_pen_color(CHARACTER_COLOR)
            pen.set_pen_shade(50)
            pen.set_pen_size(10)
            pen.goto(0, 140)
            pen.pen_down()
            pen.point_in_direction(112)
            animation_step = 3
        elif 3 <= state <= 10:
            pen.move(60)
            pen.turn_right(45)
            print("Setting state 4 to 10 timer")
            pygame.time.set_timer(START_ANI_STATE_4_TO_11_TIMER, 100)
            timer_set = True
        elif state == 11:
            pen.pen_up()
            pen.change_x_by(-20)
            pen.change_y_by(-30)
            pen.pen_down()
            pen.change_y_by(-40)
            pen.pen_up()
            pygame.time.set_timer(START_ANI_STAGE_12_TIMER, 100)
            timer_set = True
        elif state == 12:
            pen.change_x_by(40)
            pen.pen_down()
            pen.change_y_by(40)
            pen.pen_up()
            animation_step = 12

            # Temporarily lock the function (for test)
            timer_set = True

        
## End of screens 'n' stuff

# Main game loop
running = True
fullscreen = True

# Testing code
# Clear the screen
pen.erase_all()

# Set the pen properties
pen.set_pen_color('#ff0000')  # Red
pen.set_pen_size(3)

# Main loop
running = True
while running:
    # Do not change any pen settings in the main loop.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == START_ANI_STAGE_1_TIMER:
            print("Stage 1 timer")
            animation_step = 1
            pygame.time.set_timer(START_ANI_STAGE_1_TIMER, 0)
            timer_set = False
        elif event.type == START_ANI_STAGE_2_TIMER:
            print("Stage 2 timer")
            animation_step = 2
            pygame.time.set_timer(START_ANI_STAGE_2_TIMER, 0)
            timer_set = False
        elif event.type == START_ANI_STATE_4_TO_11_TIMER:
            print("State 4 to 10 timer")
            animation_step += 1
            pygame.time.set_timer(START_ANI_STATE_4_TO_11_TIMER, 0)
            timer_set = False
        elif event.type == START_ANI_STAGE_12_TIMER:
            print("Stage 12 timer")
            animation_step = 12
            pygame.time.set_timer(START_ANI_STAGE_12_TIMER, 0)
            timer_set = False
    start_animation(animation_step)
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()