#Game options/settings


TITLE = "Jumping to the stars..."
WIDTH = 600
HEIGHT = 800
FPS = 60
SPRITESHEET = "spritesheet_jumper.png"
FONT_NAME = 'arial'
HS_FILE = "Highscore.txt"

resolution = (WIDTH, HEIGHT)

# Player properties
PLAYER_ACC = 0.6
PLAYER_FRICTION = -0.10
PLAYER_GRAV = 0.80
PLAYER_JUMP = 20
ANIMATED_SPEED = 7

#Game properties
MAX_SPEED_UP = -120
MAX_SPEED_DOWN = 25

MAX_FUEL = 60 * 3
JET_SPEED = -30
FUELBAR_HEIGHT = 20
FUELBAR_WIDTH = 200

BOOST_POWER = 60

JET_SPAWN_PCT = 2
POW_SPAWN_PCT = 5
SPIKE_SPAWN_PCT = 0

# Layers
CLOUD_LAYER = 0
PLAYER_LAYER = 3
PLATFORM_LAYER = 1
POW_LAYER = 2
MOB_LAYER = 3

# Starting plateforms
PLATFORM_LIST = [(WIDTH *0.7, HEIGHT * 0.95),
				(WIDTH * 0.2, HEIGHT * 0.95), 
				(WIDTH * 0.8, HEIGHT *0.75),
				(WIDTH /2, HEIGHT /2),
				(WIDTH * 0.1, HEIGHT * 0.2),
				(WIDTH * 0.75, HEIGHT * 0.3),
				(WIDTH * 0.9, HEIGHT * 0.1),
				(WIDTH /2, -HEIGHT *0.1)]

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PINK = (255, 0, 255)
CYAN = (0, 255, 255)

GRAY = (170, 170, 170)
SKY_BLUE = (100, 100, 255)
NIGHT_PURPLE = (20, 0, 40)

WINDOW_COLOR = (200, 200, 40)