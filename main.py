# Neon Ride: Platformer Game drawn with pen (originally from Scratch)

# Note to self: All the display scaling stuff is useless
# Just use this: https://stackoverflow.com/questions/68156731/how-to-avoid-automatic-resolution-adjustment-by-pygame-fullscreen

debug = True

import pygame
import sys
import os
import math
import time
if debug:
    import platform

# from nrlevels import *

# Constants
NATIVE_WIDTH = 960
NATIVE_HEIGHT = 720
SCALE_FACTOR = 2
ASPECT_RATIO = NATIVE_WIDTH / NATIVE_HEIGHT
BACKGROUND_COLOR = (0, 0, 0)
OVERLAY_COLOR = (255, 255, 255)
CHARACTER_COLOR = "#EE7D16"
ZERO_POINT_ONE_COLOR = "#202020"
ZERO_POINT_FIVE_COLOR = "#9C9EA2"

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

# Function to print debug messages
def debug_print(*args, **kwargs):
    if debug:
        print(*args, **kwargs)

# Initialize Pygame
pygame.init()

# Initialize the mixer
pygame.mixer.init()

# Set initial window size
screen = pygame.display.set_mode((NATIVE_WIDTH, NATIVE_HEIGHT), pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("Neon Ride")

# Create an output buffer
output_buffer = pygame.Surface((NATIVE_WIDTH, NATIVE_HEIGHT))

# Frame rate control
clock = pygame.time.Clock()

# Function to draw the debug overlay
def draw_debug_overlay(fps):
    font = pygame.font.SysFont('Arial', 12)
    overlay_text = [
        f"Neon Ride++",
        f"Python: {platform.python_version()}",
        f"Pygame: {pygame.version.ver}",
        f"FPS: {round(fps)}"
    ]

    y_offset = 5
    for line in overlay_text:
        text_surface = font.render(line, True, OVERLAY_COLOR)
        screen.blit(text_surface, (5, y_offset))
        y_offset += 12

## Timers
# Timers that trigger the different stages of the start animation
START_ANI_STAGE_1_TIMER = pygame.USEREVENT + 1
START_ANI_STAGE_2_TIMER = pygame.USEREVENT + 2
START_ANI_STATE_4_TO_11_TIMER = pygame.USEREVENT + 3
START_ANI_STAGE_12_TIMER = pygame.USEREVENT + 4
START_ANI_STAGE_13_TIMER = pygame.USEREVENT + 5
START_ANI_STAGE_14_TIMER = pygame.USEREVENT + 6
START_ANI_STAGE_15_TIMER = pygame.USEREVENT + 7
START_ANI_STAGE_16_TIMER = pygame.USEREVENT + 8
START_ANI_STAGE_17_TO_27_TIMER = pygame.USEREVENT + 9
START_ANI_STAGE_28_TIMER = pygame.USEREVENT + 10
START_ANI_STAGE_29_TO_43_TIMER = pygame.USEREVENT + 11
## End of Timers


# Game states
STATE_ANIMATION = 0
STATE_WAITING_FOR_INPUT = 1
STATE_GAME_SCREEN = 2   # 't' in the original game
STATE_INSTRUCTION_SCREEN = 3    # 'i' in the original game
STATE_EMERGENCY = 4 # 'e' in the original game
STATE_MENU_SCREEN = 5

# Variables to track state and animation progress
current_state = STATE_ANIMATION
animation_step = 0

# Convert Scratch colour integer to hex code
# This still does not work properly, any help would be appreciated
def scratch_color_to_hex(color_value):
    # Handle Scratch's HSB color model (hue 0-100)
    # Hue adjustment: Scratch's 50 → 120° (green), not 180°
    scratch_hue = color_value % 100
    saturation = 100  # Full saturation
    brightness = 100  # Full brightness

    # Convert Scratch hue (0-100) to standard hue (0-360°)
    # Adjusted scaling factor to map 50 → 120°
    hue_degrees = scratch_hue * 2.4  # 50 * 2.4 = 120°
    h = hue_degrees / 360.0  # Normalize to 0-1
    s = saturation / 100.0
    v = brightness / 100.0

    # HSB-to-RGB conversion
    if s == 0:
        r = g = b = int(v * 255)
    else:
        h_i = int(h * 6)
        f = h * 6 - h_i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        if h_i == 0:
            r, g, b = v, t, p
        elif h_i == 1:
            r, g, b = q, v, p
        elif h_i == 2:
            r, g, b = p, v, t
        elif h_i == 3:
            r, g, b = p, q, v
        elif h_i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
    
    return f"#{r:02X}{g:02X}{b:02X}"

# Function to convert Scratch coordinates (center is 0,0) to Pygame coordinates (top-left is 0,0)
def scratch_to_pygame_coordinates(x, y):
    scaled_x = x * SCALE_FACTOR
    scaled_y = y * SCALE_FACTOR
    pygame_x = scaled_x + (NATIVE_WIDTH // 2)
    pygame_y = (NATIVE_HEIGHT // 2) - scaled_y
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
        print(f"about to set the color to {scratch_color_to_hex(int(color_int))}")
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
pen = ScratchPen(output_buffer)
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
    # Calculate scaled thickness
    thickness = round(thickness * SCALE_FACTOR)
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
        pen.point_in_direction(0)
        pen.move(1)
    elif letter == '!':
        pen.change_x_by(5 * (size / 100))
        pen.pen_down()
        pen.change_y_by(-20 * (size / 100))
        pen.pen_up()
        pen.change_y_by(-10 * (size / 100))
        pen.pen_down()
        pen.change_y_by(1 * (size / 100))
    elif letter == '?':
        pen.change_x_by(10 * (size / 100))
        pen.change_y_by(-15 * (size / 100))
        pen.change_x_by(-5 * (size / 100))
        pen.change_y_by(-5 * (size / 100))
        pen.pen_up()
        pen.change_y_by(-10 * (size / 100))
        pen.pen_down()
        pen.change_y_by(1 * (size / 100))
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
    # This does not work properly, which is why the constants are used
    if color == "0.1":
        pen.set_pen_color('#202020')
    elif color == "0.5":
        pen.set_pen_color('#9C9EA2')
    # If the color value is a hex code, set the pen color directly
    elif isinstance(color, str) and color.startswith("#"):
        pen.set_pen_color(color)
    # If the color value is a Scratch color value, convert it to a hex code
    else:
        pen.set_pen_color_scratch(color)
    for doods in range(len(message)):
        pen.set_pen_size(2.5 * (size / 100))
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

# Character moving at end of start animation
def move_start_animation(step):
    pen.erase_all()
    pen.set_pen_size(15)
    pen.goto(-240, -20)
    pen.pen_down()
    pen.set_pen_color("#4A6CD4")
    pen.goto(240, -20)
    pen.pen_up()
    pen.goto(step * 10, 140)
    pen.set_pen_color(CHARACTER_COLOR)
    pen.set_pen_shade(50)
    pen.set_pen_size(10)
    pen.pen_down()
    pen.point_in_direction(112)
    for i in range(8):
        pen.move(60)
        pen.turn_right(45)
    pen.pen_up()
    pen.change_x_by(-5)
    pen.change_y_by(-30)
    pen.pen_down()
    pen.change_y_by(-40)
    pen.pen_up()
    pen.change_x_by(40)
    pen.pen_down()
    pen.change_y_by(40)
    pen.pen_up()
    load_message_at("Neon/Ride", -200, -50, 300, 0)

# Start animation
timer_set = False
def start_animation(state):
    global timer_set
    global animation_step
    if not timer_set:
        if state == 0:
            pen.erase_all()
            dark_field()
            debug_print("Setting stage 1 timer")
            pygame.time.set_timer(START_ANI_STAGE_1_TIMER, 500)
            timer_set = True
        elif state == 1:
            pen.set_pen_size(15)
            pen.goto(-5000, -20)
            pen.pen_down()
            pen.set_pen_color("#4A6CD4")
            pen.goto(5000, -20)
            pen.pen_up()
            debug_print("Setting stage 2 timer")
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
            debug_print("Setting state 4 to 10 timer")
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
            pygame.time.set_timer(START_ANI_STAGE_13_TIMER, 1000)
            timer_set = True
        elif state == 13:
            load_message_at("greenyman/presents...", -230, -90, 150, 50)
            pygame.time.set_timer(START_ANI_STAGE_14_TIMER, 1000)
            timer_set = True
        elif state == 14:
            load_message_at("greenyman/presents...", -230, -90, 150, ZERO_POINT_ONE_COLOR)
            pygame.time.set_timer(START_ANI_STAGE_15_TIMER, 1000)
            timer_set = True
        elif state == 15:
            load_message_at("greenyman/presents...", -230, -90, 150, 50)
            pygame.time.set_timer(START_ANI_STAGE_16_TIMER, 1000)
            timer_set = True
        elif state == 16:
            load_message_at("greenyman/presents...", -230, -90, 150, ZERO_POINT_ONE_COLOR)
            pygame.time.set_timer(START_ANI_STAGE_17_TO_27_TIMER, 1000)
            timer_set = True
            pen.set_pen_size(80)
            pen.goto(-240, -100)
            pen.pen_down()
            pen.set_pen_color("#000000")
            pen.goto(240, -100)
            pen.pen_up()
        elif 17 <= state <= 26:
            # Flash the title
            # Lit
            if state % 2 == 1:
                load_message_at("Neon/Ride", -200, -50, 300, 0)
            # Not lit
            else:
                load_message_at("Neon/Ride", -200, -50, 300, ZERO_POINT_ONE_COLOR)
            
            # Set the next timer
            pygame.time.set_timer(START_ANI_STAGE_17_TO_27_TIMER, 30)
            timer_set = True
        elif state == 27:
            # Light up the title
            load_message_at("Neon/Ride", -200, -50, 300, 0)
            pygame.time.set_timer(START_ANI_STAGE_28_TIMER, 3000)
            timer_set = True
        elif 28 <= state <= 43:
            # Start the 0.05 s timer first
            pygame.time.set_timer(START_ANI_STAGE_29_TO_43_TIMER, 50)
            timer_set = True
            # Call the title animation move function
            debug_print(f"Calling move_start_animation with state {state - 27}")
            move_start_animation(state - 27)
        elif state == 44:
            global enter_exit
            global grid
            global grid_size
            global start
            global level
            global falling
            global y
            global x
            global xvel
            global current_state
            # Prepare all the variables and exit the start animation
            enter_exit = 1
            grid = 1
            grid_size = 100
            start = STATE_MENU_SCREEN
            level = 1
            falling = False
            y = 0
            x = 0
            xvel = 0
            # Reset the timer set flag
            timer_set = False

            # Set the current state to the main menu screen
            current_state = STATE_MENU_SCREEN
        else:
            debug_print("Invalid start animation state: " + str(state))
            # Invalid state, draw debug text
            font = pygame.font.SysFont('Arial', 24)
            text_surface = font.render("Invalid start animation state: " + str(state), True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(NATIVE_WIDTH // 2, NATIVE_HEIGHT // 2))  # Center the text
            screen.blit(text_surface, text_rect)  # Draw the text at the centered position

# Menu screen
def menu_screen():
    global timer_set
    if not timer_set:
        pen.erase_all()
        pen.set_pen_size(50)
        load_message_at("play", -210, 150, 500, 50)
        load_message_at("instructions", -220, -70, 200, "#7F01FF")
        load_message_at("press/in/case", 110, 30, 50, 0)
        load_message_at("of/emergency", 113, 10, 50, 0)
        clean_username = ''.join(filter(str.isalnum, os.getlogin()))
        welcome_string = "Welcome/" + clean_username + "..."
        load_message_at(welcome_string, 240 - len(welcome_string) * 7.5, -150, 50, len(clean_username) * 141)
        pen.goto(155, 90)
        pen.set_pen_size(80)
        pen.set_pen_color("#F50E02")
        pen.pen_down()
        pen.move(1)
        pen.pen_up()
        # TODO: handle mouse input
        timer_set = True

# Invalid state screen
def invalid_state_screen():
    global timer_set
    if not timer_set:
        pen.erase_all()
        # Invalid state
        debug_print("Invalid game state: " + str(current_state))
        # Invalid state, draw debug text
        font = pygame.font.SysFont('Arial', 24)
        text_surface = font.render("Invalid game state: " + str(current_state), True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(NATIVE_WIDTH // 2, NATIVE_HEIGHT // 2))  # Center the text
        output_buffer.blit(text_surface, text_rect)  # Draw the text at the centered position
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

# Load and play the background music
pygame.mixer.music.load(os.path.join(os.path.dirname(sys.argv[0]), "assets", "sounds", "nrmusic.mp3"))
pygame.mixer.music.play(-1)

while running:
    # Clear the screen
    screen.fill(BACKGROUND_COLOR)
    
    # Do not change any pen settings in the main loop.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == START_ANI_STAGE_1_TIMER:
            debug_print("Stage 1 timer")
            animation_step = 1
            pygame.time.set_timer(START_ANI_STAGE_1_TIMER, 0)
            timer_set = False
        elif event.type == START_ANI_STAGE_2_TIMER:
            debug_print("Stage 2 timer")
            animation_step = 2
            pygame.time.set_timer(START_ANI_STAGE_2_TIMER, 0)
            timer_set = False
        elif event.type == START_ANI_STATE_4_TO_11_TIMER:
            debug_print("State 4 to 10 timer")
            animation_step += 1
            pygame.time.set_timer(START_ANI_STATE_4_TO_11_TIMER, 0)
            timer_set = False
        elif event.type == START_ANI_STAGE_12_TIMER:
            debug_print("Stage 12 timer")
            animation_step = 12
            pygame.time.set_timer(START_ANI_STAGE_12_TIMER, 0)
            timer_set = False
        elif event.type == START_ANI_STAGE_13_TIMER:
            debug_print("Stage 13 timer")
            animation_step = 13
            pygame.time.set_timer(START_ANI_STAGE_13_TIMER, 0)
            timer_set = False
        elif event.type == START_ANI_STAGE_14_TIMER:
            debug_print("Stage 14 timer")
            animation_step = 14
            pygame.time.set_timer(START_ANI_STAGE_14_TIMER, 0)
            timer_set = False
        elif event.type == START_ANI_STAGE_15_TIMER:
            debug_print("Stage 15 timer")
            animation_step = 15
            pygame.time.set_timer(START_ANI_STAGE_15_TIMER, 0)
            timer_set = False
        elif event.type == START_ANI_STAGE_16_TIMER:
            debug_print("Stage 16 timer")
            animation_step = 16
            pygame.time.set_timer(START_ANI_STAGE_16_TIMER, 0)
            timer_set = False
        elif event.type == START_ANI_STAGE_17_TO_27_TIMER:
            debug_print("Stage 17 to 27 timer")
            animation_step += 1
            pygame.time.set_timer(START_ANI_STAGE_17_TO_27_TIMER, 0)
            timer_set = False
        elif event.type == START_ANI_STAGE_28_TIMER:
            debug_print("Stage 28 timer")
            animation_step = 28
            pygame.time.set_timer(START_ANI_STAGE_28_TIMER, 0)
            timer_set = False
        elif event.type == START_ANI_STAGE_29_TO_43_TIMER:
            debug_print("Stage 29 to 43 timer")
            animation_step += 1
            pygame.time.set_timer(START_ANI_STAGE_29_TO_43_TIMER, 0)
            timer_set = False

    if current_state == STATE_ANIMATION:
        start_animation(animation_step)
    elif current_state == STATE_GAME_SCREEN:
        pass # TODO: Add game code here
    elif current_state == STATE_INSTRUCTION_SCREEN:
        pass # TODO: Add instruction screen code here
    elif current_state == STATE_EMERGENCY:
        pass # TODO: Add emergency screen code here
    elif current_state == STATE_MENU_SCREEN:
        menu_screen()
    else:
        invalid_state_screen()

    # Blit the output buffer onto the main screen
    scaled_buffer = pygame.transform.scale(output_buffer, (NATIVE_WIDTH, NATIVE_HEIGHT))
    screen.blit(scaled_buffer, (0, 0))

    # Calculate FPS
    fps = clock.get_fps()
    
    # Draw the debug overlay
    if debug:
        draw_debug_overlay(fps)
    
    pygame.display.flip()
    clock.tick(120)

# Quit Pygame
pygame.quit()