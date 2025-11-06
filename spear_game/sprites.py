# spear_game/sprites.py

import pygame
import sys
import heapq
import os
from .settings import *
from .utils import load_image

class Walls:
    def __init__(self):
        self.wall_rects = []
        self.level_map = []
        self.start_pos = None  # Oyuncu başlangıç pozisyonu
        # Sprite bilgileri artık doğrudan dosya adlarını kullanıyor
        paris_sprite_info = {
            0: (None, 1),  # Boş tile
            1: (None, 1),  # Oyuncu başlangıç pozisyonu
            2: ("Wall1.png", 1),
            3: ("Wall1_Dik.png", 1),
            4: ("Wall2.png", 1),
            5: ("Wall3.png", 1),
            6: ("Mermer.png", 1),
            7: ("Mermer2.png", 1),
            8: ("Mermer3.png", 1),
            9: ("Mermer4.png", 1),
            10: ("Mermer_Red.png", 1),
            11: ("Mermer_Red_2.png", 1),
            12: ("Mermer_Red_4.png", 1),
            13: ("Mermer_Blue.png", 1),
            14: ("Mermer_Blue_2.png", 1),
        }
        self.paris_tiles = {}
        for code, (filename, width) in paris_sprite_info.items():
            if filename is None:
                if code == 1:  # Oyuncu başlangıç pozisyonu için özel görünüm
                    # Başlangıç noktası için hafif mavi, yarı saydam bir gösterge
                    empty_surface = pygame.Surface((TILE_SIZE * width, TILE_SIZE), pygame.SRCALPHA)
                    indicator_color = (0, 150, 255, 100)  # Açık mavi, yarı saydam
                    empty_surface.fill(indicator_color)
                    pygame.draw.circle(empty_surface, (0, 200, 255, 150), 
                                    (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//4)
                else:  # Boş tile (kod 0) için tamamen saydam
                    empty_surface = pygame.Surface((TILE_SIZE * width, TILE_SIZE), pygame.SRCALPHA)
                    empty_surface.fill((0, 0, 0, 0))  # Tamamen saydam
                self.paris_tiles[code] = {"image": empty_surface, "width": width}
                continue
                
            try:
                # utils.load_image kullanılıyor
                image = load_image(filename, (TILE_SIZE * width, TILE_SIZE))
                self.paris_tiles[code] = {"image": image, "width": width}
            except pygame.error as e:
                print(f"Hata: Duvar resmi yuklenemedi - {filename}\n{e}")
                fallback_image = pygame.Surface((TILE_SIZE * width, TILE_SIZE))
                fallback_image.fill(BLACK)
                self.paris_tiles[code] = {"image": fallback_image, "width": width}
        
        self.load_map_from_file(MAP_PATH) # Haritayı dosyadan yükle
        
        self.create_colliders()

    def load_map_from_file(self, file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue  # boş satırları atla
                self.level_map.append([int(i) for i in line.split(',') if i.strip() != ''])
    
    def create_colliders(self):
        self.wall_rects.clear()
        collider_tile_codes = {2, 3, 4, 5}
        for row_index, row in enumerate(self.level_map):
            for col_index, tile_code in enumerate(row):
                if tile_code in collider_tile_codes:
                    width = self.paris_tiles[tile_code]["width"]
                    rect = pygame.Rect(
                        col_index * TILE_SIZE,
                        row_index * TILE_SIZE,
                        TILE_SIZE * width,
                        TILE_SIZE
                    )
                    self.wall_rects.append(rect)

    def draw(self, surface):
        for row_index, row in enumerate(self.level_map):
            for col_index, tile_code in enumerate(row):
                tile = self.paris_tiles.get(tile_code)
                if tile:
                    surface.blit(tile["image"], (col_index * TILE_SIZE, row_index * TILE_SIZE))
        self.wall_rects.clear()
        collider_tile_codes = {2, 3, 4, 5}
        for row_index, row in enumerate(self.level_map):
            for col_index, tile_code in enumerate(row):
                if tile_code in collider_tile_codes:
                    width = self.paris_tiles[tile_code]["width"]
                    rect = pygame.Rect(
                        col_index * TILE_SIZE,
                        row_index * TILE_SIZE,
                        TILE_SIZE * width,
                        TILE_SIZE
                    )
                    self.wall_rects.append(rect)

    def draw(self, surface):
        for row_index, row in enumerate(self.level_map):
            for col_index, tile_code in enumerate(row):
                tile = self.paris_tiles.get(tile_code)
                if tile and tile["image"]:  # None olmayan image'ları çiz
                    surface.blit(tile["image"], (col_index * TILE_SIZE, row_index * TILE_SIZE))

    def find_player_start(self):
        """Haritadan oyuncu başlangıç pozisyonunu bulur ve tile'ı Mermer (6) ile değiştirir"""
        default_pos = (WIDTH // 2, HEIGHT // 2)
        for row_index, row in enumerate(self.level_map):
            for col_index, tile_code in enumerate(row):
                if tile_code == 1:  # Oyuncu başlangıç noktası
                    # Başlangıç noktasını Mermer (6) ile değiştir
                    self.level_map[row_index][col_index] = 6
                    return (col_index * TILE_SIZE + TILE_SIZE // 2, 
                           row_index * TILE_SIZE + TILE_SIZE // 2)
        return default_pos

# --- Player Sınıfı ---
class Player:
    def __init__(self, pos=None, speed=None):
        self.image_right = load_image("Character_right.png", (30, 54))
        if pos is None:
            pos = (WIDTH // 2, HEIGHT // 1.15)
        self.pos = pygame.Vector2(pos)
        self.speed = speed if speed is not None else DEFAULT_PLAYER_SPEED
        self.facing_left = False
        self.rect = self.image_right.get_rect(center=self.pos)
        self.surface = self.image_right

    def update(self, dt, keys, wall_rects):
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()
            # Tam ekranda pozisyonu ölçekle
            move_speed = self.speed * dt
            
            # X ekseninde hareket
            new_x = self.pos.x + direction.x * move_speed
            self.rect.centerx = int(new_x)
            collision_x = False
            for wall in wall_rects:
                if self.rect.colliderect(wall):
                    collision_x = True
                    if direction.x > 0:
                        self.rect.right = wall.left
                    elif direction.x < 0:
                        self.rect.left = wall.right
            if not collision_x:
                self.pos.x = new_x
            else:
                self.pos.x = self.rect.centerx

            # Y ekseninde hareket
            new_y = self.pos.y + direction.y * move_speed
            self.rect.centery = int(new_y)
            collision_y = False
            for wall in wall_rects:
                if self.rect.colliderect(wall):
                    collision_y = True
                    if direction.y > 0:
                        self.rect.bottom = wall.top
                    elif direction.y < 0:
                        self.rect.top = wall.bottom
            if not collision_y:
                self.pos.y = new_y
            else:
                self.pos.y = self.rect.centery

            # Yön güncelleme
            if direction.x < 0:
                self.facing_left = True
            elif direction.x > 0:
                self.facing_left = False

        self.surface = pygame.transform.flip(self.image_right, True, False) if self.facing_left else self.image_right
        self.rect.center = self.pos

    def draw(self, screen):
        screen.blit(self.surface, self.rect.topleft)

# --- Money Sınıfı ---
class Money:
    def __init__(self, position):
        self.image = load_image("Money.png", (12, 12))
        self.rect = pygame.Rect(position[0], position[1], 24, 24)

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)

# --- Spear Sınıfı ---
from typing import Tuple, Union

class Spear:
    def __init__(self):
        self.image_original = load_image("spear_c.png", (62, 30))
        self.image = self.image_original
        self.thrown = False
        self.timer = 0.0
        self.pos = pygame.Vector2(0, 0)
        self.movement_direction = pygame.Vector2(0, 0)
        self.speed = 400
        self.visual_angle = 0.0
        self.lifetime = 1.5
        self.rect = self.image.get_rect()

    def throw(self, start_pos: Union[Tuple[float, float], pygame.Vector2], 
             target_pos: Union[Tuple[float, float], pygame.Vector2]) -> None:
        if not self.thrown:  # Sadece mızrak havada değilse yeni atış yap
            self.pos = pygame.Vector2(start_pos)
            direction = pygame.Vector2(target_pos) - self.pos
            if direction.length() > 0:
                self.movement_direction = direction.normalize()
            else:
                self.movement_direction = pygame.Vector2(1, 0)
            
            # Mızrağın açısını hesapla
            angle = pygame.math.Vector2().angle_to(self.movement_direction)
            self.image = pygame.transform.rotate(self.image_original, -angle)
            self.rect = self.image.get_rect(center=self.pos)
            
            self.thrown = True
            self.timer = 0.0
            
    def update(self, dt: float, 
                player_pos: Union[Tuple[float, float], pygame.Vector2],
                mouse_pos: Union[Tuple[float, float], pygame.Vector2]) -> None:
        if self.thrown:
            self.timer += dt
            if self.timer >= self.lifetime:
                self.thrown = False
                return
            
            # Mızrağı hareket ettir
            self.pos += self.movement_direction * self.speed * dt
            self.rect.center = self.pos
            
        else:
            # Mızrak atılmamışsa, oyuncuyu takip et
            self.pos = pygame.Vector2(player_pos)
            # Fare pozisyonuna göre mızrağın açısını güncelle
            direction = pygame.Vector2(mouse_pos) - self.pos
            if direction.length() > 0:
                self.movement_direction = direction.normalize()
                angle = pygame.math.Vector2().angle_to(self.movement_direction)
                self.image = pygame.transform.rotate(self.image_original, -angle)
                self.rect = self.image.get_rect(center=self.pos)
                
    def draw(self, screen: pygame.Surface, player_pos: Union[Tuple[float, float], pygame.Vector2]) -> None:
        """Mızrağı ekrana çizer"""
        # Mızrak pozisyonunu belirle (atılmışsa kendi pozisyonu, atılmamışsa oyuncu pozisyonu)
        center_pos = self.pos if self.thrown else pygame.Vector2(player_pos)
        
        # Mızrağı çiz
        rect = self.image.get_rect(center=center_pos)
        screen.blit(self.image, rect.topleft)


# --- Enemy Sınıfı ---
class Enemy:
    def __init__(self, pos, speed, color_type="red"):
        self.pos = pygame.Vector2(pos)
        self.speed = speed
        self.color_type = color_type
        if color_type == "red":
            self.image_right = load_image("Enemy_Red_Image.png", (30, 54))
            self.image_left = load_image("Enemy_Red_Image2.png", (30, 54))
        else:
            self.image_right = load_image("Enemy_Blue_Image.png", (30, 54))
            self.image_left = load_image("Enemy_Blue_Image2.png", (30, 54))
        self.current_image = self.image_right
        self.rect = self.image_right.get_rect(center=self.pos)
        self.facing_right = True
        self.path = []
        self.path_index = 0
        self.repath_timer = 0

    def grid_pos(self):
        # Düşmanın bulunduğu tile koordinatları
        return (int(self.pos.x // TILE_SIZE), int(self.pos.y // TILE_SIZE))

    def find_path(self, target_pos, walls):
        # A* algoritması ile yol bulma (sadece duvarlar engel, paralar engel DEĞİL)
        start = self.grid_pos()
        end = (int(target_pos.x // TILE_SIZE), int(target_pos.y // TILE_SIZE))
        wall_set = set((rect.x // TILE_SIZE, rect.y // TILE_SIZE) for rect in walls.wall_rects)
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: abs(start[0] - end[0]) + abs(start[1] - end[1])}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                # Sadece duvarlar engel, para tile'ları engel DEĞİL
                if (0 <= neighbor[0] < WIDTH // TILE_SIZE and 0 <= neighbor[1] < HEIGHT // TILE_SIZE and neighbor not in wall_set):
                    tentative_g = g_score[current] + 1
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + abs(neighbor[0] - end[0]) + abs(neighbor[1] - end[1])
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []

    def update(self, player_pos, player_rect, dt, walls):
        # Yol güncelleme
        self.repath_timer += dt
        if self.repath_timer > 0.5 or not self.path:
            self.path = self.find_path(player_pos, walls)
            self.path_index = 0
            self.repath_timer = 0
        
        # Yolun sonraki noktasına hareket et
        if self.path and self.path_index < len(self.path):
            target_tile = self.path[self.path_index]
            target_pixel = pygame.Vector2(target_tile[0] * TILE_SIZE + TILE_SIZE//2, target_tile[1] * TILE_SIZE + TILE_SIZE//2)
            direction = target_pixel - self.pos
            if direction.length_squared() > 4:
                move = direction.normalize() * self.speed * dt
                if move.length_squared() > direction.length_squared():
                    self.pos = target_pixel
                else:
                    self.pos += move
            else:
                self.path_index += 1
        else:
            # Hedef oyuncu ise doğrudan hareket
            direction = player_pos - self.pos
            if direction.length_squared() > 4:
                self.pos += direction.normalize() * self.speed * dt

        # Yüzü hedefe dön
        if self.path and self.path_index < len(self.path):
            direction_check = pygame.Vector2(self.path[self.path_index][0] * TILE_SIZE, self.path[self.path_index][1] * TILE_SIZE) - self.pos
        else:
            direction_check = player_pos - self.pos

        if direction_check.x > 0:
            self.facing_right = True
            self.current_image = self.image_right
        else:
            self.facing_right = False
            self.current_image = self.image_left

        self.rect = self.current_image.get_rect(center=self.pos)

    def draw(self, screen):
        screen.blit(self.current_image, self.rect.topleft)

