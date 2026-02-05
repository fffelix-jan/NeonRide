# Neon Ride: Platformer Game drawn with pen (originally from Scratch)

# Note to self: All the display scaling stuff is useless
# Just use this: https://stackoverflow.com/questions/68156731/how-to-avoid-automatic-resolution-adjustment-by-pygame-fullscreen

from nrutil import *
from scratch_pen import *
from nrlevels import *
from nrconstants import *

import pygame
import sys
import os
import math
import time
if DEBUG:
    import platform

# Get the base path for bundled assets
if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in development
    base_path = os.path.dirname(os.path.abspath(__file__))

# Global variables
JUMP_HEIGHT = 8
HORIZ_SPEED = 2
GRAVITY_COEFF = 8
GRAVITY_MAX_STEP = 6
SKIP_START_ANIMATION = True
move = 0
time_global = 0
enter_exit = 1
grid = False
grid_size = 100
start = STATE_ANIMATION
level = 2
falling = False
remember = -4
jump = JUMP_HEIGHT
y = 0
x = 0
xvel = 0
y_pressed = False
t_pressed = False
q_pressed = 0
size = 0
doods = 0
current_direction_magic_number = 112
last_jump_time = 0

# Function to print debug messages
def debug_print(*args, **kwargs):
    if DEBUG:
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
        f"FPS: {round(fps)}",
        f"X: {x}, Y: {y}",
        f"{string_pressed_keys()}"
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
GAME_REDRAW_TIMER = pygame.USEREVENT + 12
## End of Timers

# Variables to track state and animation progress
current_state = STATE_ANIMATION
animation_step = 0

# Create a pen object
pen = ScratchPen(output_buffer)
## End of Pen class

# Optional fast-start for debugging
if SKIP_START_ANIMATION:
    current_state = STATE_GAME_SCREEN
    setup_complete = False


## Input functions
# Function to check if a key is pressed
def check_key_pressed(key):
    """
    Check if a specific key is pressed.
    
    Args:
        key (str or int): The key to check. Can be a character (e.g., 'a') or a Pygame key constant (e.g., pygame.K_LEFT).
    
    Returns:
        bool: True if the key is pressed, False otherwise.
    
    Raises:
        ValueError: If the key is invalid.
    """
    # Get the current state of all keys
    keys = pygame.key.get_pressed()
    
    # Handle arrow keys and other special keys
    if isinstance(key, str):
        # Convert the input character to its corresponding pygame key code
        if key.lower() in ['left', 'right', 'up', 'down']:
            # Map arrow key names to Pygame constants
            arrow_keys = {
                'left': pygame.K_LEFT,
                'right': pygame.K_RIGHT,
                'up': pygame.K_UP,
                'down': pygame.K_DOWN
            }
            key_code = arrow_keys.get(key.lower())
        else:
            # Handle regular alphanumeric keys
            key_code = getattr(pygame, f'K_{key.lower()}', None)
    elif isinstance(key, int):
        # Assume the input is already a Pygame key constant
        key_code = key
    else:
        raise ValueError(f"Invalid key type: {type(key)}. Expected str or int.")
    
    if key_code is None:
        raise ValueError(f"The key '{key}' is not a valid key.")

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
            # grid = 1
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

    # Vertical lines
    start_x = -240 + (x % grid_size)
    for i in range((NATIVE_WIDTH // grid_size) + 2):
        current_x = start_x + i * grid_size
        pen.goto(current_x, -180)
        pen.pen_down()
        pen.goto(current_x, 180)
        pen.pen_up()

    # Horizontal lines
    start_y = -180 + (y % grid_size)
    for i in range((NATIVE_HEIGHT // grid_size) + 2):
        current_y = start_y + i * grid_size
        pen.goto(-240, current_y)
        pen.pen_down()
        pen.goto(240, current_y)
        pen.pen_up()

# Death
def death():
    global x, y
    if enter_exit == 1:
        y = 0
        x = 0
    else:
        x = goal_x[level - 1]
        y = goal_y[level - 1]

# Falling
# This is the function that handles the character falling
def fall():
    print("Falling function called")
    # USE ROUND HITBOX FOR ENTIRE FUNCTION
    global falling, remember, time_global, y, jump, last_jump_time
    if pen.touching_color(LEVEL_COLOR, HITBOX_ROUND):
        falling = False
        time_global = 0
        pen.pen_up()
        remember = 0
        while pen.touching_color(LEVEL_COLOR, HITBOX_ROUND) and pen.y <= 170:
            y -= 1
            pen.change_y_by(1)
            remember -= 1
        pen.change_y_by(remember)
        y += 4
        pen.pen_down()
        if check_key_pressed("up") and (time.time() - last_jump_time) >= 0.25:
            last_jump_time = time.time()
            jump = JUMP_HEIGHT
            y -= JUMP_HEIGHT
    else:
        if not falling:
            time_global = 0
            if check_key_pressed("up"):
                jump = JUMP_HEIGHT
            else:
                jump = 0
        falling = True
        accel = (GRAVITY_COEFF * (time_global * time_global)) - jump
        if accel > GRAVITY_MAX_STEP:
            accel = GRAVITY_MAX_STEP
        y += accel

# Sensing
def sensing():
    # USE ROUND HITBOX HERE
    global y, jump, enter_exit, level, x, time_global, xvel
    
    # Collision with lava
    if pen.touching_color(LAVA_COLOR, HITBOX_ROUND):
        death()

    print(f"Current pen direction: {pen.direction}")
    # Collision with level (ground)
    if pen.direction == DIR_GROUND_CHECK:
        if pen.touching_color(LEVEL_COLOR, HITBOX_ROUND):
            jump = 0
            y += 5
    else:
        if pen.direction == DIR_FALL_CHECK:
            # USE ROUND HITBOX HERE
            fall()

            # Collision with goal
            if pen.touching_color(GOAL_COLOR, HITBOX_ROUND):
                if abs(x) > 200:
                    enter_exit = 1
                    level += 1
                    x = 0
                    y = 0
                else:
                    enter_exit = 2
                    level -= 1
                    x = goal_x[level - 1]
                    y = goal_y[level - 1]
        else:
            if pen.direction == DIR_RIGHT_CHECK:
                # USE HORIZONTAL HITBOX HERE
                print(f"Result of checking right key and touching color: {check_key_pressed('right')}, {not pen.touching_color(LEVEL_COLOR, HITBOX_HORIZONTAL)}")
                if check_key_pressed("right") and not (pen.touching_color(LEVEL_COLOR, HITBOX_HORIZONTAL) and xvel < 0):
                    xvel -= HORIZ_SPEED
                if pen.touching_color(LEVEL_COLOR, HITBOX_HORIZONTAL):
                    if xvel < 0:
                        xvel = 0
                    if check_key_pressed("up") and check_key_pressed("left"):
                        time_global = 0.1
                        xvel = HORIZ_SPEED
            else:
                if pen.direction == DIR_LEFT_CHECK:
                    print(f"Result of checking left key and touching color: {check_key_pressed('left')}, {not pen.touching_color(LEVEL_COLOR, HITBOX_HORIZONTAL)}")
                    # USE HORIZONTAL HITBOX HERE
                    if check_key_pressed("left") and not (pen.touching_color(LEVEL_COLOR, HITBOX_HORIZONTAL) and xvel > 0):
                        xvel += HORIZ_SPEED
                    if pen.touching_color(LEVEL_COLOR, HITBOX_HORIZONTAL):
                        if xvel > 0:
                            xvel = 0
                        if check_key_pressed("up") and check_key_pressed("right"):
                            time_global = 0.1
                            xvel = -HORIZ_SPEED

# Debug flying mode
def debug_fly():
    global x, y
    # Use W, A, S, D keys to move the character in debug mode
    if check_key_pressed('w'):
        y -= 1
    if check_key_pressed('s'):
        y += 1
    if check_key_pressed('a'):
        x += 1
    if check_key_pressed('d'):
        x -= 1

# Function that draws the character in the game
# Originally just titled "C"
def draw_character_with_sensing():
    global doods
    pen.point_in_direction(112)
    doods = 0
    pen.set_pen_size(3)
    pen.set_pen_color(CHARACTER_COLOR)
    pen.pen_up()
    pen.goto(0, 15)
    pen.pen_down()
    for i in range(8):
        sensing()
        if DEBUG:
            debug_fly()
        pen.move(8)
        pen.turn_right(45)
    pen.pen_up()
    pen.goto(-0.2 * xvel - 3, 10)
    pen.pen_down()
    pen.change_y_by(-5)
    pen.pen_up()
    pen.goto(-0.2 * xvel + 3, 10)
    pen.pen_down()
    pen.change_y_by(-5)

# Game timeout timer
def timeout_tick():
    global time_global, y, move
    time_global += 0.05
    move += 1
    # Check if time up or 'r' key is pressed
    if y > 500 or check_key_pressed('r'):
        death()

# Game screen
def game_screen():
    global x, y, xvel, level, grid, t_pressed, q_pressed, enter_exit, falling, start, grid_size
    pen.erase_all()
    if grid:
        draw_grid()
    load_level(level, x, y, pen, move)
    draw_character_with_sensing()

    # Debug prints to verify xvel and y
    # debug_print(f"xvel: {xvel}, y: {y}")

    # Apply xvel to x
    x += xvel
    xvel /= 1.5  # Apply friction to xvel

    # Handle grid size toggle
    if check_key_pressed('t'):
        if not t_pressed:
            t_pressed = True
            if grid_size > 150:
                grid_size = 10
            else:
                grid_size += 10
    else:
        t_pressed = False

    # Handle emergency quit
    if check_key_pressed('q'):
        q_pressed += 1
        if q_pressed >= 40:
            enter_exit = 1
            level = 1
            falling = False
            y = 0
            x = 0
            xvel = 0
            start = STATE_MENU_SCREEN
            q_pressed = 0
    else:
        q_pressed = 0

    timeout_tick()
    
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
        elif event.type == pygame.KEYDOWN:
            debug_print(f"Key down: {pygame.key.name(event.key)}")
        elif event.type == pygame.KEYUP:
            debug_print(f"Key up: {pygame.key.name(event.key)}")
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
        game_screen()
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
    if DEBUG:
        draw_debug_overlay(fps)
    
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()