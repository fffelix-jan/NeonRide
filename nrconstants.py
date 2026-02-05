# Display and Scaling Constants
NATIVE_WIDTH = 960
NATIVE_HEIGHT = 720
SCALE_FACTOR = 2
ASPECT_RATIO = NATIVE_WIDTH / NATIVE_HEIGHT

# Colors
BACKGROUND_COLOR = (0, 0, 0)
OVERLAY_COLOR = (255, 255, 255)
CHARACTER_COLOR = "#EE7D16"
ZERO_POINT_ONE_COLOR = "#202020"
ZERO_POINT_FIVE_COLOR = "#9C9EA2"
LEVEL_COLOR = "#4A6CD4"
GOAL_COLOR = "#5DB713"
LAVA_COLOR = "#F50E02"

# Hitbox dimensions (width x height)
HITBOX_ROUND = (15, 15)
HITBOX_VERTICAL = (15, 18)
HITBOX_HORIZONTAL = (23, 15)

# Physics and Direction Constants (magic numbers in the original game)
DIR_GROUND_CHECK = 112     # Direction for checking ground collisions
DIR_FALL_CHECK = 292       # Direction for checking fall/vertical collisions (equivalent to -68 mod 360)
DIR_RIGHT_CHECK = 202     # Direction for checking right-side collisions (equivalent to -158 mod 360)
DIR_LEFT_CHECK = 22        # Direction for checking left-side collisions

# Game States
STATE_ANIMATION = 0
STATE_WAITING_FOR_INPUT = 1
STATE_GAME_SCREEN = 2   # 't' in the original game
STATE_INSTRUCTION_SCREEN = 3    # 'i' in the original game
STATE_EMERGENCY = 4 # 'e' in the original game
STATE_MENU_SCREEN = 5

# Grid Settings
GRID_SIZE = 100

# Debug Settings
DEBUG = True
FLYING_ENABLED = False

JUMP_HEIGHT = 8           # Upward impulse applied when jumping
HORIZ_SPEED = 2           # Horizontal acceleration applied per sensing tick
GRAVITY_COEFF = 8         # Quadratic gravity coefficient (position uses t^2 style)
GRAVITY_MAX_STEP = 7      # Per-tick clamp on downward acceleration

SKIP_START_ANIMATION = False