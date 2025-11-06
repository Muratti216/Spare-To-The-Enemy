# spear_game/settings.py

import os

# Ekran Ayarları
WIDTH, HEIGHT = 1024, 1024
TILE_SIZE = 32
FPS = 60

# Oyun Ayarları
ENEMY_SPAWN_ENABLED = True  # Düşman doğmasını kontrol eder
DEFAULT_ENEMY_SPEED = 120   # Varsayılan düşman hızı
MIN_ENEMY_SPEED = 0        # Minimum düşman hızı (0 = hareketsiz)
MAX_ENEMY_SPEED = 300      # Maximum düşman hızı

# Oyuncu Ayarları
DEFAULT_PLAYER_SPEED = 200  # Varsayılan oyuncu hızı
MIN_PLAYER_SPEED = 100     # Minimum oyuncu hızı
MAX_PLAYER_SPEED = 400     # Maximum oyuncu hızı

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
HIGHLIGHT_COLOR = (150, 150, 150)

# Varlık (Asset) Yolları
# Projenin ana dizinini bulur, böylece her bilgisayarda çalışır
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_BASE_PATH = os.path.join(BASE_DIR, 'assets')
MUSIC_PATH = os.path.join(BASE_DIR, 'Music')
MAP_PATH = os.path.join(os.path.dirname(__file__), "..", "levels", "level0.txt")
ZELDA_FONT_PATH = os.path.join(ASSET_BASE_PATH, 'zelda_font.ttf')
TITLE_FONT_SIZE = 52  # Slightly larger for better readability
BUTTON_FONT_SIZE = 36  # Increased for better visibility
SAVE_SLOT_FONT_SIZE = 42  # Adjusted for consistency


