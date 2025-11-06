import os
import pygame

# Try to run headless to avoid opening a window during smoke test
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

from spear_game.controller import GameController

def main():
    print('Initializing pygame (headless)')
    pygame.init()
    try:
        gc = GameController()
        print('Created GameController')
        try:
            gc.resume_game()
            print('resume_game() called successfully')
        except Exception as e:
            print('resume_game() raised:', e)
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()
