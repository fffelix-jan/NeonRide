# Neon Ride: Platformer Game drawn with pen (originally from Scratch)

import pygame
import sys
import math

# Constants
NATIVE_WIDTH = 480
NATIVE_HEIGHT = 360
ASPECT_RATIO = NATIVE_WIDTH / NATIVE_HEIGHT

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
screen = pygame.display.set_mode((NATIVE_WIDTH, NATIVE_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Neon Ride")

# Convert Scratch colour integer to hex code
def scratch_color_to_hex(color_int):
    # Extract red, green, and blue components
    r = (color_int // 65536) % 256
    g = (color_int // 256) % 256
    b = color_int % 256
    
    # Convert to hex string
    hex_code = f'#{r:02x}{g:02x}{b:02x}'
    return hex_code

## Pen class (used globally)
class Pen:
    def __init__(self, surface):
        self.surface = surface
        self.x = NATIVE_WIDTH // 2
        self.y = NATIVE_HEIGHT // 2
        self.direction = 0  # In degrees, 0 means right
        self.pen_down_status = False
        self.pen_size = 1
        self.pen_color = (0, 0, 0)  # Default black
        self.pen_shade = 100  # Representing 100% shade (normal)
        self.pen_visible_size = 15  # The pen's circle diameter for collision detection

        # Pen history for drawing
        self.last_pos = (self.x, self.y)  # Store the last position for line drawing

        # Scaling factors (set initially)
        self.scale_factor = 1
        self.x_offset = 0
        self.y_offset = 0

    # Turn clockwise by n degrees
    def turn_right(self, n):
        self.direction += n
        self.direction %= 360
    
    # Turn counter-clockwise by n degrees
    def turn_left(self, n):
        self.direction -= n
        self.direction %= 360

    # Helper method to scale coordinates
    def scale_coordinates(self, x, y):
        return scale_coordinates(x, y, self.scale_factor, self.x_offset, self.y_offset)

    # Move pen to new position
    def goto(self, x, y):
        new_x, new_y = self.scale_coordinates(x, y)
        if self.pen_down:
            draw_scaled_rounded_line(self.surface, self.pen_color, (self.x, self.y), (new_x, new_y), self.pen_size, self.scale_factor, self.x_offset, self.y_offset)
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
        self.surface.fill((255, 255, 255))  # Fill screen with white

    # Adjust color brightness based on shade percentage
    def adjust_color_brightness(self, color, percent):
        # Percent is between 0 and 100
        factor = max(0, min(percent / 100, 1))  # Clamped between 0 and 1
        new_color = pygame.Color(int(color.r * factor),
                                 int(color.g * factor),
                                 int(color.b * factor))
        return new_color

    # Check if pen is touching a specific color
    def touching_color(self, color):
        scaled_x, scaled_y = self.scale_coordinates(self.x, self.y)
        pen_rect = pygame.Rect(scaled_x - self.pen_visible_size // 2,
                               scaled_y - self.pen_visible_size // 2,
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

    # Update scaling factors
    def update_scaling(self, scale_factor, x_offset, y_offset):
        self.scale_factor, self.x_offset, self.y_offset = scale_factor, x_offset, y_offset
    
    # Move the pen n steps forward in the current direction
    def move(self, n):
        # Convert Scratch's direction system to standard trigonometric angles:
        # 0 degrees is up, 90 is right, 180 is down, 270 is left.
        # We need to rotate this by -90 degrees for standard math angles.
        radians = math.radians(90 - self.direction)
        
        # Calculate the new position using trigonometry
        delta_x = n * math.cos(radians)
        delta_y = -n * math.sin(radians)  # Negating because in pygame, positive y is down
        
        # Move the pen to the new position
        self.goto(self.x + delta_x, self.y + delta_y)

# Create a pen object
pen = Pen(screen)
## End of Pen class

## Functions to aid display scaling (don't edit)
# Function to get scaling factors and letterboxing
def get_scaling_factors(screen_width, screen_height):
    screen_aspect_ratio = screen_width / screen_height

    if screen_aspect_ratio > ASPECT_RATIO:
        # Letterbox on the sides (16:9 or wider)
        scale_factor = screen_height / NATIVE_HEIGHT
        scaled_width = int(NATIVE_WIDTH * scale_factor)
        x_offset = (screen_width - scaled_width) // 2
        y_offset = 0
    else:
        # Letterbox on the top and bottom
        scale_factor = screen_width / NATIVE_WIDTH
        scaled_height = int(NATIVE_HEIGHT * scale_factor)
        x_offset = 0
        y_offset = (screen_height - scaled_height) // 2

    return scale_factor, x_offset, y_offset

# Function to scale coordinates
def scale_coordinates(x, y, scale_factor, x_offset, y_offset):
    scaled_x = int(x * scale_factor) + x_offset
    scaled_y = int(y * scale_factor) + y_offset
    return scaled_x, scaled_y

# Function to scale thickness (for neon lines)
def scale_thickness(thickness, scale_factor):
    return max(1, int(thickness * scale_factor))

# Function to draw with scaling and letterboxing
def draw_with_scaling(surface, color, start_pos, end_pos, thickness, scale_factor, x_offset, y_offset):
    scaled_start = scale_coordinates(start_pos[0], start_pos[1], scale_factor, x_offset, y_offset)
    scaled_end = scale_coordinates(end_pos[0], end_pos[1], scale_factor, x_offset, y_offset)
    scaled_thickness = scale_thickness(thickness, scale_factor)
    pygame.draw.line(surface, color, scaled_start, scaled_end, scaled_thickness)

# Function to draw a scaled circle
def draw_scaled_circle(surface, color, center, radius, scale_factor, x_offset, y_offset):
    scaled_center = scale_coordinates(center[0], center[1], scale_factor, x_offset, y_offset)
    scaled_radius = int(radius * scale_factor)
    pygame.draw.circle(surface, color, scaled_center, scaled_radius)

# Function to draw a scaled equilateral triangle
def draw_scaled_equilateral_triangle(surface, color, center, side_length, scale_factor, x_offset, y_offset):
    # Calculate the height of an equilateral triangle
    height = (math.sqrt(3) / 2) * side_length
    half_side = side_length / 2

    # Calculate the three vertices of the triangle
    p1 = (center[0], center[1] - height / 2)  # Top point
    p2 = (center[0] - half_side, center[1] + height / 2)  # Bottom-left point
    p3 = (center[0] + half_side, center[1] + height / 2)  # Bottom-right point

    # Scale all points
    p1_scaled = scale_coordinates(p1[0], p1[1], scale_factor, x_offset, y_offset)
    p2_scaled = scale_coordinates(p2[0], p2[1], scale_factor, x_offset, y_offset)
    p3_scaled = scale_coordinates(p3[0], p3[1], scale_factor, x_offset, y_offset)

    # Draw the triangle
    pygame.draw.polygon(surface, color, [p1_scaled, p2_scaled, p3_scaled])

def draw_scaled_rounded_line(surface, color, start_pos, end_pos, thickness, scale_factor, x_offset, y_offset):
    """
    Draws a scaled line with rounded ends.
    
    Args:
        surface: The Pygame surface to draw on.
        color: The color of the line.
        start_pos: The starting position of the line (x, y).
        end_pos: The ending position of the line (x, y).
        thickness: The thickness of the line.
        scale_factor: The scale factor for adjusting the size.
        x_offset: The horizontal offset (for letterboxing).
        y_offset: The vertical offset (for letterboxing).
    """
    # Scale the start and end points
    scaled_start = scale_coordinates(start_pos[0], start_pos[1], scale_factor, x_offset, y_offset)
    scaled_end = scale_coordinates(end_pos[0], end_pos[1], scale_factor, x_offset, y_offset)
    
    # Scale the thickness
    scaled_thickness = scale_thickness(thickness, scale_factor)
    
    # Draw the main line
    pygame.draw.line(surface, color, scaled_start, scaled_end, scaled_thickness)
    
    # Draw circles at both ends to create rounded ends
    radius = scaled_thickness // 2
    draw_scaled_circle(surface, color, start_pos, radius, scale_factor, x_offset, y_offset)
    draw_scaled_circle(surface, color, end_pos, radius, scale_factor, x_offset, y_offset)
## End of functions to aid display scaling

## Functions to draw text
def draw_letter(letter):
    if letter == '/':
        return
    letter = letter.lower() # Scratch uses case-insensitive letter comparison
    if not(letter == '.' or letter == '!' or letter == '-'):
        pen.pen_down()

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
    # That's it for this super long function!
    # I'm surprised GitHub Copilot knew EXACTLY what I was gonna write next!


# Function to draw a message at a specific location
def load_message_at(message, x, y, font_size, color):
    pen.goto(x, y)
    size = font_size
    for doods in range(len(message)):
        if color == "0.1":
            pen.set_pen_color('#202020')
        elif color == "0.5":
            pen.set_pen_color('#9C9EA2')
        else:
            pen.set_pen_color_scratch(color)
            pen.set_pen_shade(50)
        
        pen.set_pen_size(3 * (size / 100))
        draw_letter(message[doods])
        pen.goto(pen.x + (doods * 15) * (size / 100), pen.y)


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

## Levels and screens
# This function is complete
def dark_field():
    pen.pen_up()
    pen.set_pen_size(15)
    pen.goto(-240, -20)
    pen.pen_down()
    pen.set_pen_color('#0A0D09')
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

# This function is complete
def move():
    pen.erase_all()
    pen.set_pen_size(15)
    pen.goto(-240, -20)
    pen.pen_down()
    pen.set_pen_color('#4A6CD4')
    pen.goto(240, -20)
    pen.pen_up()
    pen.goto(start_animation * 10, 140)
    pen.set_pen_color('#EE7D16')
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
    start_animation += 1


def start_animation():
    pen.erase_all()
    dark_field()
    pygame.display.flip()  # Update the screen after drawing
    pygame.time.wait(500)
    
    pen.set_pen_size(15)
    pen.goto(-240, -20)
    pen.pen_down()
    pen.set_pen_color('#4A6CD4')
    pen.goto(240, -20)
    pygame.display.flip()  # Update the screen after drawing
    pen.pen_up()
    
    pygame.time.wait(2000)
    start_animation = 1
    pen.set_pen_color('#EE7D16')
    pen.set_pen_shade(50)
    pen.set_pen_size(10)
    pen.goto(0, 140)
    pen.pen_down()
    pen.point_in_direction(112)
    
    for i in range(8):
        pen.move(60)
        pen.turn_right(45)
        pygame.display.flip()  # Update the screen after drawing
        pygame.time.wait(100)
    
    pen.pen_up()
    pen.change_x_by(-20)
    pen.change_y_by(-30)
    pen.pen_down()
    pen.change_y_by(-40)
    pygame.display.flip()  # Update the screen after drawing
    pen.pen_up()
    pen.change_x_by(40)
    pen.pen_down()
    pen.change_y_by(40)
    pygame.display.flip()  # Update the screen after drawing
    pen.pen_up()
    pygame.time.wait(1000)

    # Draw the creator's name
    load_message_at("greenyman/presents...", -230, -90, 150, 50)
    pygame.display.flip()  # Update the screen after drawing
    pygame.time.wait(1000)
    
    load_message_at("greenyman/presents...", -230, -90, 150, 0.1)
    pygame.display.flip()  # Update the screen after drawing
    pygame.time.wait(1000)
    
    load_message_at("greenyman/presents...", -230, -90, 150, 50)
    pygame.display.flip()  # Update the screen after drawing
    pygame.time.wait(1000)
    
    load_message_at("greenyman/presents...", -230, -90, 150, 0.1)
    pygame.display.flip()  # Update the screen after drawing
    
    pen.set_pen_size(80)
    pen.goto(-240, -100)
    pen.pen_down()
    pen.set_pen_color('#000000')
    pen.goto(240, -100)
    pygame.display.flip()  # Update the screen after drawing
    pen.pen_up()
    pygame.time.wait(1000)

    for i in range(5):
        load_message_at("Neon/Ride", -200, -50, 300, 0)
        pygame.display.flip()  # Update the screen after drawing
        pygame.time.wait(30)
        
        load_message_at("Neon/Ride", -200, -50, 300, 0.1)
        pygame.display.flip()  # Update the screen after drawing
        pygame.time.wait(30)
    
    load_message_at("Neon/Ride", -200, -50, 300, 0)
    pygame.display.flip()  # Update the screen after drawing
    pygame.time.wait(3000)
    for i in range(15):
        pygame.time.wait(50)
        # TODO: Call move() function


# Main game loop
running = True
fullscreen = False

# Original start of "when green flag clicked" section
while running:
    screen.fill((0, 0, 0))
    start_animation()

    while running:
        screen.fill((0, 0, 0))
        if start == 't':
            pass # TODO: call game_screen()
        elif start == 'i':
            pass # TODO: call instruction_screen()
        elif start == 'e':
            pass # TODO: call emergency()
        else:
            pass # TODO: call menu_screen()

        if check_key_pressed('y'):
            if not y_pressed:
                if grid:
                    grid = False
                else:
                    grid = True
            else:
                y_pressed = True
        else:
            y_pressed = False
        
        # Refresh the display
        pygame.display.flip()


# Quit Pygame
pygame.quit()
sys.exit()