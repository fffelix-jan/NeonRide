import pygame
import math
from nrutil import *

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

## Functions to draw text
def draw_letter(pen, letter, size=100):
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
def load_message_at(pen, message, x, y, font_size, color):
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
        draw_letter(pen, message[doods], font_size)
        pen.goto(x + ((doods + 1) * 15) * (size / 100), y)
    
    # Restore the previous pen status
    pen.pen_down_status = prev_status