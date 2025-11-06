# main.py

import pygame
import sys
import argparse
from spear_game.controller import GameController
from spear_game.level_editor import LevelEditor

def main():
    parser = argparse.ArgumentParser(description='Spear Game')
    parser.add_argument('--editor', action='store_true', help='Start in level editor mode')
    args = parser.parse_args()

    pygame.init()
    
    if args.editor:
        editor = LevelEditor()
        editor.run()
    else:
        game = GameController()
        game.game_loop()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()