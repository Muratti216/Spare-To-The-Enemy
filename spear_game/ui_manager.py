
import os
import pygame
from .settings import TITLE_FONT_SIZE, BUTTON_FONT_SIZE, SAVE_SLOT_FONT_SIZE, ZELDA_FONT_PATH

class UIManager:
    # Class level font declarations
    TITLE_FONT = None
    BUTTON_FONT = None
    SAVE_SLOT_FONT = None
    font_loaded = False
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            instance = super(UIManager, cls).__new__(cls)
            # Initialize score
            instance.score = 0
            
            # Always initialize system fonts first as fallback
            cls.TITLE_FONT = pygame.font.Font(None, TITLE_FONT_SIZE)
            cls.BUTTON_FONT = pygame.font.Font(None, BUTTON_FONT_SIZE)
            cls.SAVE_SLOT_FONT = pygame.font.Font(None, SAVE_SLOT_FONT_SIZE)
            cls.font_loaded = False
            
            # Try to load custom Zelda font
            try:
                if os.path.exists(ZELDA_FONT_PATH):
                    zelda_font = pygame.font.Font(ZELDA_FONT_PATH, BUTTON_FONT_SIZE)
                    cls.TITLE_FONT = pygame.font.Font(ZELDA_FONT_PATH, TITLE_FONT_SIZE)
                    cls.BUTTON_FONT = zelda_font  # Reuse the same font object
                    cls.SAVE_SLOT_FONT = pygame.font.Font(ZELDA_FONT_PATH, SAVE_SLOT_FONT_SIZE)
                    cls.font_loaded = True
                else:
                    print(f"Warning: Font file not found: {ZELDA_FONT_PATH}. Using system fonts.")
            except Exception as e:
                print(f"Warning: Failed to load custom font: {e}. Using system fonts.")
            
            cls._instance = instance
        return cls._instance

    def add_score(self, amount):
        self.score += amount

    def get_score(self):
        return self.score

    def reset_score(self):
        self.score = 0
        
    @property
    def fonts(self):
        """Return available fonts as a dictionary"""
        # Ensure pygame is initialized
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
            
        # Validate fonts and reinitialize if needed
        for font_name, font_obj in [('title', self.TITLE_FONT), 
                                  ('button', self.BUTTON_FONT), 
                                  ('save_slot', self.SAVE_SLOT_FONT)]:
            if not font_obj or not hasattr(font_obj, 'render'):
                print(f"Warning: {font_name} font is invalid. Reinitializing with system font.")
                if font_name == 'title':
                    self.__class__.TITLE_FONT = pygame.font.Font(None, TITLE_FONT_SIZE)
                elif font_name == 'button':
                    self.__class__.BUTTON_FONT = pygame.font.Font(None, BUTTON_FONT_SIZE)
                elif font_name == 'save_slot':
                    self.__class__.SAVE_SLOT_FONT = pygame.font.Font(None, SAVE_SLOT_FONT_SIZE)
                    
        return {
            'title': self.TITLE_FONT,
            'button': self.BUTTON_FONT,
            'save_slot': self.SAVE_SLOT_FONT
        }