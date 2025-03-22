import pygame
from nrconstants import *

# Function to convert Scratch coordinates (center is 0,0) to Pygame coordinates (top-left is 0,0)
def scratch_to_pygame_coordinates(x, y):
    scaled_x = x * SCALE_FACTOR
    scaled_y = y * SCALE_FACTOR
    pygame_x = scaled_x + (NATIVE_WIDTH // 2)
    pygame_y = (NATIVE_HEIGHT // 2) - scaled_y
    return pygame_x, pygame_y

# Function to convert Pygame coordinates (top-left is 0,0) to Scratch coordinates (center is 0,0)
def pygame_to_scratch_coordinates(pygame_x, pygame_y):
    # Convert Pygame coordinates (top-left origin) to Scratch coordinates (center origin)
    scaled_x = (pygame_x - (NATIVE_WIDTH // 2)) / SCALE_FACTOR
    scaled_y = ((NATIVE_HEIGHT // 2) - pygame_y) / SCALE_FACTOR
    return scaled_x, scaled_y

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

