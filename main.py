# Neon Ride: Platformer Game drawn with pen (originally from Scratch)

# Note to self: All the display scaling stuff is useless
# Just use this: https://stackoverflow.com/questions/68156731/how-to-avoid-automatic-resolution-adjustment-by-pygame-fullscreen

import pygame
import sys
import math
import time

# Constants
NATIVE_WIDTH = 480
NATIVE_HEIGHT = 360
ASPECT_RATIO = NATIVE_WIDTH / NATIVE_HEIGHT
BACKGROUND_COLOR = (0, 0, 0)

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
animation_timer = 0

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

## Pen class (used globally)
# This is a reimplmentation of the Scratch pen in Pygame
class Pen:
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
        radians = math.radians(self.direction)
        
        # Calculate the new position using trigonometry
        delta_x = n * math.cos(radians)
        delta_y = -n * math.sin(radians)  # Negating because in pygame, positive y is down
        
        # Move the pen to the new position
        self.goto(self.x + delta_x, self.y + delta_y)

# Create a pen object
pen = Pen(screen)
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
    # Draw the main line
    pygame.draw.line(surface, color, start_pos, end_pos, round(thickness))
    
    # Draw circles at both ends to create rounded ends
    radius = thickness / 2
    pygame.draw.circle(surface, color, (start_pos[0] + thickness / 4, start_pos[1] + thickness / 4), radius)
    pygame.draw.circle(surface, color, (end_pos[0] + thickness / 4, end_pos[1] + thickness / 4), radius)


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
        pen.change_y_by(15 * (size / 100))
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
        pen.change_x_by(-5 * (size / 100))
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

# Main game loop
running = True
fullscreen = True

# Testing code
# Clear the screen
pen.erase_all()

# Set the pen properties
pen.set_pen_color('#ff0000')  # Red
pen.set_pen_size(3)

# Testing code
# Clear the screen
pen.erase_all()

# Set the pen properties
pen.set_pen_color('#ff0000')  # Red
pen.set_pen_size(3)

# Define the characters to draw
characters = 'abcdefghijklmnopqrstuvwxyz0123456789'

# Function to draw a circle using the pen
def draw_circle(pen, radius):
    circumference = 2 * math.pi * radius
    steps = int(circumference / 2)  # Number of steps to approximate the circle
    step_length = circumference / steps
    step_angle = 360 / steps

    pen.pen_down()
    for _ in range(steps):
        pen.move(step_length)
        pen.turn_right(step_angle)
        pygame.display.flip()  # Update the display
        #time.sleep(0.01)  # Pause for 0.01 seconds to see the drawing
    pen.pen_up()

# Set the pen properties
pen.set_pen_color('#ff0000')  # Red
pen.set_pen_size(3)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background
    screen.fill((255, 255, 255))

    # Load message at the center of the screen
    message = 'bye/calvin'
    x = -230  # Adjust x to center the text
    y = 0
    font_size = 200
    color = '50'
    
    
    pen.goto(0,0)
    pen.set_pen_color("#00FF00")
    pen.pen_down()
    pen.change_y_by(100)
    pen.change_x_by(100)
    pen.change_y_by(-100)
    pen.change_x_by(-100)
    load_message_at(message, x, y, font_size, color)

    # Update the display
    pygame.display.flip()
    pen.pen_up()

# Quit Pygame
pygame.quit()