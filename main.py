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

from nrutil import *
from scratch_pen import *
from nrlevels import *
from nrconstants import *

# Get the base path for bundled assets
if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in development
    base_path = os.path.dirname(os.path.abspath(__file__))

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
pygame.display.set_caption("Neon Ride")
pygame.init()

# Initialize the mixer
pygame.mixer.init()

# Set initial window size
screen = pygame.display.set_mode((NATIVE_WIDTH, NATIVE_HEIGHT), pygame.RESIZABLE | pygame.SCALED)

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

# Variables to track state and animation progress
current_state = STATE_ANIMATION
animation_step = 0

# Create a pen object
pen = ScratchPen(output_buffer)
## End of Pen class


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
    load_message_at(pen, "Neon/Ride", -200, -50, 300, 0)

# Start animation
setup_complete = False
def start_animation(state):
    global setup_complete
    global animation_step
    if not setup_complete:
        if state == 0:
            pen.erase_all()
            dark_field()
            debug_print("Setting stage 1 timer")
            pygame.time.set_timer(START_ANI_STAGE_1_TIMER, 500)
            setup_complete = True
        elif state == 1:
            pen.set_pen_size(15)
            pen.goto(-5000, -20)
            pen.pen_down()
            pen.set_pen_color("#4A6CD4")
            pen.goto(5000, -20)
            pen.pen_up()
            debug_print("Setting stage 2 timer")
            pygame.time.set_timer(START_ANI_STAGE_2_TIMER, 2000)
            setup_complete = True
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
            setup_complete = True
        elif state == 11:
            pen.pen_up()
            pen.change_x_by(-20)
            pen.change_y_by(-30)
            pen.pen_down()
            pen.change_y_by(-40)
            pen.pen_up()
            pygame.time.set_timer(START_ANI_STAGE_12_TIMER, 100)
            setup_complete = True
        elif state == 12:
            pen.change_x_by(40)
            pen.pen_down()
            pen.change_y_by(40)
            pen.pen_up()
            pygame.time.set_timer(START_ANI_STAGE_13_TIMER, 1000)
            setup_complete = True
        elif state == 13:
            load_message_at(pen, "greenyman/presents...", -230, -90, 150, 50)
            pygame.time.set_timer(START_ANI_STAGE_14_TIMER, 1000)
            setup_complete = True
        elif state == 14:
            load_message_at(pen, "greenyman/presents...", -230, -90, 150, ZERO_POINT_ONE_COLOR)
            pygame.time.set_timer(START_ANI_STAGE_15_TIMER, 1000)
            setup_complete = True
        elif state == 15:
            load_message_at(pen, "greenyman/presents...", -230, -90, 150, 50)
            pygame.time.set_timer(START_ANI_STAGE_16_TIMER, 1000)
            setup_complete = True
        elif state == 16:
            load_message_at(pen, "greenyman/presents...", -230, -90, 150, ZERO_POINT_ONE_COLOR)
            pygame.time.set_timer(START_ANI_STAGE_17_TO_27_TIMER, 1000)
            setup_complete = True
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
                load_message_at(pen, "Neon/Ride", -200, -50, 300, 0)
            # Not lit
            else:
                load_message_at(pen, "Neon/Ride", -200, -50, 300, ZERO_POINT_ONE_COLOR)
            
            # Set the next timer
            pygame.time.set_timer(START_ANI_STAGE_17_TO_27_TIMER, 30)
            setup_complete = True
        elif state == 27:
            # Light up the title
            load_message_at(pen, "Neon/Ride", -200, -50, 300, 0)
            pygame.time.set_timer(START_ANI_STAGE_28_TIMER, 3000)
            setup_complete = True
        elif 28 <= state <= 43:
            # Start the 0.05 s timer first
            pygame.time.set_timer(START_ANI_STAGE_29_TO_43_TIMER, 50)
            setup_complete = True
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
            # Reset the setup complete flag
            setup_complete = False

            # Set the current state to the main menu screen
            current_state = STATE_MENU_SCREEN
        else:
            # This code should never be reached
            debug_print("Invalid start animation state: " + str(state))
            # Invalid state, draw debug text
            font = pygame.font.SysFont('Arial', 24)
            text_surface = font.render("Invalid start animation state: " + str(state), True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(NATIVE_WIDTH // 2, NATIVE_HEIGHT // 2))  # Center the text
            screen.blit(text_surface, text_rect)  # Draw the text at the centered position

# Menu screen
def menu_screen():
    global setup_complete
    global current_state

    if not setup_complete:
        pen.erase_all()
        pen.set_pen_size(50)
        load_message_at(pen, "play", -210, 150, 500, 50)
        load_message_at(pen, "instructions", -220, -70, 200, "#7F01FF")
        load_message_at(pen, "press/in/case", 110, 30, 50, 0)
        load_message_at(pen, "of/emergency", 113, 10, 50, 0)
        clean_username = ''.join(filter(str.isalnum, os.getlogin()))
        welcome_string = "Welcome/" + clean_username + "..."
        load_message_at(pen, welcome_string, 240 - len(welcome_string) * 7.5, -150, 50, len(clean_username) * 141)
        pen.goto(155, 90)
        pen.set_pen_size(80)
        pen.set_pen_color("#F50E02")
        pen.pen_down()
        pen.move(1)
        pen.pen_up()
        setup_complete = True

# Draw the grid
def draw_grid():
    pen.set_pen_size(1)
    pen.set_pen_color("#656565")
    pen.pen_up()
    pen.goto((x + 240) % grid_size - 240, 180)
    for i in range(480 // grid_size + 1):
        pen.pen_down()
        pen.goto(x, -180)
        pen.pen_up()
        pen.goto(x + grid_size, 180)
    pen.goto(-240, (y + 180) % grid_size - 180)
    for i in range(360 // grid_size + 1):
        pen.pen_down()
        pen.goto(240, y)
        pen.pen_up()
        pen.goto(-240, y + grid_size)

# Game screen
def game_screen():
    pen.erase_all()
    if grid:
        draw_grid()
    # Call the code in nrlevels.py to load the level
    # QUESTION: What variables must be passed to the load_level function in nrlevels.py?
    # ANSWER: The variables that must be passed to the load_level function in nrlevels.py are the level number and the pen object.
    

# Invalid state screen
def invalid_state_screen():
    global setup_complete
    if not setup_complete:
        pen.erase_all()
        # Invalid state
        debug_print("Invalid game state: " + str(current_state))
        # Invalid state, draw debug text
        font = pygame.font.SysFont('Arial', 24)
        text_surface = font.render("Invalid game state: " + str(current_state), True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(NATIVE_WIDTH // 2, NATIVE_HEIGHT // 2))  # Center the text
        output_buffer.blit(text_surface, text_rect)  # Draw the text at the centered position
        setup_complete = True
        
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
music_path = os.path.join(base_path, "assets", "sounds", "nrmusic.mp3")
if os.path.exists(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)
else:
    print(f"Error: Music file not found at {music_path}")

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
            setup_complete = False
        elif event.type == START_ANI_STAGE_2_TIMER:
            debug_print("Stage 2 timer")
            animation_step = 2
            pygame.time.set_timer(START_ANI_STAGE_2_TIMER, 0)
            setup_complete = False
        elif event.type == START_ANI_STATE_4_TO_11_TIMER:
            debug_print("State 4 to 10 timer")
            animation_step += 1
            pygame.time.set_timer(START_ANI_STATE_4_TO_11_TIMER, 0)
            setup_complete = False
        elif event.type == START_ANI_STAGE_12_TIMER:
            debug_print("Stage 12 timer")
            animation_step = 12
            pygame.time.set_timer(START_ANI_STAGE_12_TIMER, 0)
            setup_complete = False
        elif event.type == START_ANI_STAGE_13_TIMER:
            debug_print("Stage 13 timer")
            animation_step = 13
            pygame.time.set_timer(START_ANI_STAGE_13_TIMER, 0)
            setup_complete = False
        elif event.type == START_ANI_STAGE_14_TIMER:
            debug_print("Stage 14 timer")
            animation_step = 14
            pygame.time.set_timer(START_ANI_STAGE_14_TIMER, 0)
            setup_complete = False
        elif event.type == START_ANI_STAGE_15_TIMER:
            debug_print("Stage 15 timer")
            animation_step = 15
            pygame.time.set_timer(START_ANI_STAGE_15_TIMER, 0)
            setup_complete = False
        elif event.type == START_ANI_STAGE_16_TIMER:
            debug_print("Stage 16 timer")
            animation_step = 16
            pygame.time.set_timer(START_ANI_STAGE_16_TIMER, 0)
            setup_complete = False
        elif event.type == START_ANI_STAGE_17_TO_27_TIMER:
            debug_print("Stage 17 to 27 timer")
            animation_step += 1
            pygame.time.set_timer(START_ANI_STAGE_17_TO_27_TIMER, 0)
            setup_complete = False
        elif event.type == START_ANI_STAGE_28_TIMER:
            debug_print("Stage 28 timer")
            animation_step = 28
            pygame.time.set_timer(START_ANI_STAGE_28_TIMER, 0)
            setup_complete = False
        elif event.type == START_ANI_STAGE_29_TO_43_TIMER:
            debug_print("Stage 29 to 43 timer")
            animation_step += 1
            pygame.time.set_timer(START_ANI_STAGE_29_TO_43_TIMER, 0)
            setup_complete = False
    
        # Mouse event handler on the menu screen
        # Handle mouse clicks for the menu screen
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == STATE_MENU_SCREEN:
                mouse_x, mouse_y = event.pos
                scratch_x, scratch_y = pygame_to_scratch_coordinates(mouse_x, mouse_y)
                debug_print(f"Mouse clicked at ({scratch_x}, {scratch_y})")
                
                # Check Play button (approximate coordinates)
                if -200 < scratch_x < 80 and -30 < scratch_y < 150:
                    current_state = STATE_GAME_SCREEN
                    setup_complete = False
                    debug_print("Switching to game screen")
                # Check Instructions button
                elif -220 < scratch_x < 140 and -70 < scratch_y < -60:
                    current_state = STATE_INSTRUCTION_SCREEN
                    setup_complete = False
                    debug_print("Switching to instruction screen")
                # Check Emergency button (circle around (155, 90))
                elif math.sqrt((scratch_x - 155)**2 + (scratch_y - 90)**2) < 40:
                    current_state = STATE_EMERGENCY
                    setup_complete = False
                    debug_print("Switching to emergency state")
                else:
                    debug_print("Clicked outside buttons")

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