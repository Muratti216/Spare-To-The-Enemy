import pygame
import json
import os
from .settings import *
from .utils import load_image
from .sprites import Walls

class LevelEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Spear Game - Level Editor")
        
        # Temel ayarlar
        self.TILE_SIZE = 32
        self.GRID_WIDTH = 32
        self.GRID_HEIGHT = 24
        self.PALETTE_WIDTH = 250
        self.EDITOR_BG = (40, 44, 52)
        self.GRID_COLOR = (70, 70, 70)
        self.HIGHLIGHT_COLOR = (100, 100, 255, 100)
        
        # Font
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Editör durumu
        self.selected_tile = 2
        self.show_grid = True
        self.tool_mode = "place"  # "place", "erase", "fill"
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_mouse_pos = None
        
        # Undo/Redo
        self.history = []
        self.future = []
        self.max_history = 50
        
        # Level verisi
        self.level_data = [[0 for _ in range(self.GRID_WIDTH)] 
                          for _ in range(self.GRID_HEIGHT)]
        
        # Tile paleti
        self.tiles = self.load_tiles()
        self.tile_categories = {
            "Terrain": [2, 3, 4, 5],  # Duvarlar
            "Collectibles": [6, 7, 8, 9],  # Paralar
            "Special": [1, 10, 11, 12, 13, 14]  # Oyuncu spawn, düşman spawn vs.
        }
        self.current_category = "Terrain"
        
        # UI elemanları
        self.buttons = self.create_buttons()
        
        self.running = True
        
    def load_tiles(self):
        tiles = {}
        tile_info = {
            0: (None, "Empty"),
            1: ("Character_right.png", "Player Spawn"),
            2: ("Wall1.png", "Wall 1"),
            3: ("Wall1_Dik.png", "Wall 1 Vertical"),
            4: ("Wall2.png", "Wall 2"),
            5: ("Wall3.png", "Wall 3"),
            6: ("Mermer.png", "Coin 1"),
            7: ("Mermer2.png", "Coin 2"),
            8: ("Mermer3.png", "Coin 3"),
            9: ("Mermer4.png", "Coin 4"),
            10: ("Mermer_Red.png", "Red Enemy Spawn"),
            11: ("Mermer_Blue.png", "Blue Enemy Spawn"),
            12: ("Mermer_Red_2.png", "Red Enemy Area"),
            13: ("Mermer_Blue_2.png", "Blue Enemy Area"),
            14: ("CornerWall.png", "Corner Wall")
        }
        
        for code, (filename, name) in tile_info.items():
            if filename is None:
                empty = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
                tiles[code] = {"image": empty, "name": name}
            else:
                try:
                    image = load_image(filename, (self.TILE_SIZE, self.TILE_SIZE))
                    tiles[code] = {"image": image, "name": name}
                except Exception as e:
                    print(f"Error loading tile {filename}: {e}")
                    fallback = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
                    fallback.fill((255, 0, 255))  # Magenta for missing textures
                    tiles[code] = {"image": fallback, "name": f"Missing: {name}"}
        
        return tiles
        
    def create_buttons(self):
        buttons = {
            "save": {"rect": pygame.Rect(10, 640, 100, 30), "text": "Save (Ctrl+S)"},
            "load": {"rect": pygame.Rect(120, 640, 100, 30), "text": "Load (Ctrl+L)"},
            "grid": {"rect": pygame.Rect(10, 580, 100, 30), "text": "Toggle Grid"},
            "place": {"rect": pygame.Rect(10, 520, 100, 30), "text": "Place Tool"},
            "erase": {"rect": pygame.Rect(120, 520, 100, 30), "text": "Erase Tool"},
            "undo": {"rect": pygame.Rect(10, 460, 100, 30), "text": "Undo (Ctrl+Z)"},
            "redo": {"rect": pygame.Rect(120, 460, 100, 30), "text": "Redo (Ctrl+Y)"}
        }
        
        # Kategori butonları
        y = 50
        for category in self.tile_categories:
            buttons[f"cat_{category}"] = {
                "rect": pygame.Rect(10, y, self.PALETTE_WIDTH - 20, 30),
                "text": category
            }
            y += 40
            
        return buttons
    
    def save_state(self):
        """Mevcut durumu history'ye kaydet"""
        current_state = [row[:] for row in self.level_data]
        self.history.append(current_state)
        self.future.clear()  # Yeni değişiklik yapıldığında future'ı temizle
        
        # History limiti
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def undo(self):
        """Son değişikliği geri al"""
        if not self.history:
            return
            
        current_state = [row[:] for row in self.level_data]
        self.future.append(current_state)
        
        previous_state = self.history.pop()
        self.level_data = [row[:] for row in previous_state]
    
    def redo(self):
        """Geri alınan değişikliği tekrar uygula"""
        if not self.future:
            return
            
        current_state = [row[:] for row in self.level_data]
        self.history.append(current_state)
        
        next_state = self.future.pop()
        self.level_data = [row[:] for row in next_state]
    
    def save_level(self):
        """Level'ı dosyaya kaydet"""
        try:
            level_path = os.path.join("levels", "custom_level.txt")
            with open(level_path, "w") as f:
                for row in self.level_data:
                    f.write("".join(str(tile) for tile in row) + "\n")
            print(f"Level saved to {level_path}")
        except Exception as e:
            print(f"Error saving level: {e}")
    
    def load_level(self):
        """Level'ı dosyadan yükle"""
        try:
            level_path = os.path.join("levels", "custom_level.txt")
            with open(level_path, "r") as f:
                lines = f.readlines()
                for y, line in enumerate(lines):
                    for x, char in enumerate(line.strip()):
                        if y < len(self.level_data) and x < len(self.level_data[0]):
                            self.level_data[y][x] = int(char)
            print(f"Level loaded from {level_path}")
        except Exception as e:
            print(f"Error loading level: {e}")
    
    def handle_mouse_input(self, event):
        """Mouse inputlarını işle"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Buton kontrolleri
            for name, button in self.buttons.items():
                if button["rect"].collidepoint(mouse_pos):
                    self.handle_button_click(name)
                    return
            
            # Palette kontrolü
            if mouse_pos[0] < self.PALETTE_WIDTH:
                # Tile seçimi
                tile_y = 150  # Palette başlangıç y pozisyonu
                for tile_id in self.tile_categories[self.current_category]:
                    tile_rect = pygame.Rect(10, tile_y, self.TILE_SIZE, self.TILE_SIZE)
                    if tile_rect.collidepoint(mouse_pos):
                        self.selected_tile = tile_id
                        return
                    tile_y += 50
            else:
                # Grid'e tile yerleştirme
                if event.button == 1:  # Sol tık
                    self.dragging = True
                    self.place_tile(mouse_pos)
                elif event.button == 3:  # Sağ tık
                    self.dragging = True
                    self.erase_tile(mouse_pos)
            
            self.last_mouse_pos = mouse_pos
            
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            self.last_mouse_pos = None
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_pos = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:  # Sol tık
                self.place_tile(mouse_pos)
            elif pygame.mouse.get_pressed()[2]:  # Sağ tık
                self.erase_tile(mouse_pos)
    
    def handle_button_click(self, button_name):
        """Buton tıklamalarını işle"""
        if button_name == "save":
            self.save_level()
        elif button_name == "load":
            self.load_level()
        elif button_name == "grid":
            self.show_grid = not self.show_grid
        elif button_name == "place":
            self.tool_mode = "place"
        elif button_name == "erase":
            self.tool_mode = "erase"
        elif button_name == "undo":
            self.undo()
        elif button_name == "redo":
            self.redo()
        elif button_name.startswith("cat_"):
            self.current_category = button_name[4:]
    
    def place_tile(self, mouse_pos):
        """Belirtilen pozisyona tile yerleştir"""
        grid_x = (mouse_pos[0] - self.PALETTE_WIDTH) // self.TILE_SIZE
        grid_y = mouse_pos[1] // self.TILE_SIZE
        
        if (0 <= grid_x < self.GRID_WIDTH and 
            0 <= grid_y < self.GRID_HEIGHT and 
            self.level_data[grid_y][grid_x] != self.selected_tile):
            # State'i kaydet
            self.save_state()
            self.level_data[grid_y][grid_x] = self.selected_tile
    
    def erase_tile(self, mouse_pos):
        """Belirtilen pozisyondaki tile'ı sil"""
        grid_x = (mouse_pos[0] - self.PALETTE_WIDTH) // self.TILE_SIZE
        grid_y = mouse_pos[1] // self.TILE_SIZE
        
        if (0 <= grid_x < self.GRID_WIDTH and 
            0 <= grid_y < self.GRID_HEIGHT and 
            self.level_data[grid_y][grid_x] != 0):
            # State'i kaydet
            self.save_state()
            self.level_data[grid_y][grid_x] = 0
    
    def handle_events(self):
        """Event'leri işle"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type in (pygame.MOUSEBUTTONDOWN, 
                              pygame.MOUSEBUTTONUP, 
                              pygame.MOUSEMOTION):
                self.handle_mouse_input(event)
                
            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                
                # Kısayollar
                if mods & pygame.KMOD_CTRL:
                    if event.key == pygame.K_s:
                        self.save_level()
                    elif event.key == pygame.K_l:
                        self.load_level()
                    elif event.key == pygame.K_z:
                        self.undo()
                    elif event.key == pygame.K_y:
                        self.redo()
                        
                # Grid toggle
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                
                # ESC tuşu kontrolü
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def draw_palette(self):
        """Sol taraftaki tile paletini çiz"""
        # Palette arkaplanı
        pygame.draw.rect(self.screen, (30, 33, 39), 
                        (0, 0, self.PALETTE_WIDTH, 720))
        
        # Başlık
        title = self.font.render("Tile Palette", True, (200, 200, 200))
        self.screen.blit(title, (10, 10))
        
        # Kategoriler
        for name, button in self.buttons.items():
            if name.startswith("cat_"):
                color = (100, 100, 255) if self.current_category == name[4:] else (70, 70, 70)
                pygame.draw.rect(self.screen, color, button["rect"])
                text = self.small_font.render(button["text"], True, (200, 200, 200))
                text_rect = text.get_rect(center=button["rect"].center)
                self.screen.blit(text, text_rect)
        
        # Seçili kategorideki tile'lar
        tile_y = 150
        for tile_id in self.tile_categories[self.current_category]:
            # Tile
            tile_rect = pygame.Rect(10, tile_y, self.TILE_SIZE, self.TILE_SIZE)
            if tile_id in self.tiles:
                self.screen.blit(self.tiles[tile_id]["image"], tile_rect)
                
                # Seçili tile highlight
                if tile_id == self.selected_tile:
                    pygame.draw.rect(self.screen, (255, 255, 0), tile_rect, 2)
                
                # Tile ismi
                name = self.small_font.render(self.tiles[tile_id]["name"], True, (200, 200, 200))
                self.screen.blit(name, (50, tile_y + 8))
            
            tile_y += 50
        
        # Alt butonlar
        for name, button in self.buttons.items():
            if not name.startswith("cat_"):
                color = (70, 70, 70)
                if (name == "place" and self.tool_mode == "place") or \
                   (name == "erase" and self.tool_mode == "erase"):
                    color = (100, 100, 255)
                
                pygame.draw.rect(self.screen, color, button["rect"])
                text = self.small_font.render(button["text"], True, (200, 200, 200))
                text_rect = text.get_rect(center=button["rect"].center)
                self.screen.blit(text, text_rect)
    
    def draw_grid(self):
        """Grid çizgilerini çiz"""
        if not self.show_grid:
            return
            
        for x in range(self.GRID_WIDTH + 1):
            pygame.draw.line(self.screen, self.GRID_COLOR,
                           (x * self.TILE_SIZE + self.PALETTE_WIDTH, 0),
                           (x * self.TILE_SIZE + self.PALETTE_WIDTH, 720))
        
        for y in range(self.GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, self.GRID_COLOR,
                           (self.PALETTE_WIDTH, y * self.TILE_SIZE),
                           (1280, y * self.TILE_SIZE))
    
    def draw_tiles(self):
        """Level'daki tile'ları çiz"""
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                tile_id = self.level_data[y][x]
                if tile_id != 0 and tile_id in self.tiles:
                    pos_x = x * self.TILE_SIZE + self.PALETTE_WIDTH
                    pos_y = y * self.TILE_SIZE
                    self.screen.blit(self.tiles[tile_id]["image"], (pos_x, pos_y))
    
    def draw_info(self):
        """Ekranın sağ üst köşesine bilgi yaz"""
        tool = "Place" if self.tool_mode == "place" else "Erase"
        if self.selected_tile in self.tiles:
            selected = self.tiles[self.selected_tile]["name"]
        else:
            selected = "None"
            
        info_text = f"Tool: {tool} | Selected: {selected}"
        info = self.small_font.render(info_text, True, (200, 200, 200))
        self.screen.blit(info, (self.PALETTE_WIDTH + 10, 10))
    
    def draw(self):
        """Ana çizim fonksiyonu"""
        # Arkaplan
        self.screen.fill(self.EDITOR_BG)
        
        # Level elemanları
        self.draw_grid()
        self.draw_tiles()
        
        # UI
        self.draw_palette()
        self.draw_info()
        
        # Ekranı güncelle
        pygame.display.flip()
        
    def run(self):
        """Ana döngü"""
        while self.running:
            self.handle_events()
            self.draw()