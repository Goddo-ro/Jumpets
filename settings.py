TITLE = "JumpCat!"
WIDTH = 480
HEIGHT = 600
FPS = 60
FONT_NAME = 'arial'
HS_FILE = "highscore.txt"

# Аудио файлы
START_SCREEN_MUSIC = "start.ogg"
BACKGROUND_MUSIC = "background.ogg"
GAME_OVER_MUSIC = "game_over.wav"

# Параметры игрока
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 24

# Параметры игры
BOOST_POWER = 60
ACCELERATOR_SPAWN_CHANGE = 5
ENEMIES_SPAWN_TIME = 5000

# Стартовые платформы
PLATFORM_LIST = [(0, HEIGHT - 40),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4),
                 (125, HEIGHT - 350),
                 (350, 200),
                 (175, 100)]

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHTBLUE = (0, 175, 255)
BGCOLOR = LIGHTBLUE