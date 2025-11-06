# spear_game/controller.py

import os
import sys
import json
import pygame

# Local imports
from .settings import FPS, WIDTH, HEIGHT
from .game_states import (
    MainMenu, Playing, Credits,
    GameOver, YouWin, PauseMenu, OptionsMenu
)
from .ui_manager import UIManager
from .audio_manager import AudioManager
from .save_system import load_high_scores, save_player_score  # High score system


class GameController:
    def init_states(self):
        """Game states'leri başlat"""
        self.states = {
            'main_menu': MainMenu(self),
            'playing': None,
            'credits': Credits(self),
            'game_over': None,  # Skor ile oluşturulacak
            'you_win': None,    # Skor ile oluşturulacak
            'save_load': None
        }
        self.current_state = self.states['main_menu']
    def __init__(self):
        pygame.init()
        self.base_resolution = (WIDTH, HEIGHT)
        self.last_screen_size = self.base_resolution
        self.scale_factor = 1.0
        self.current_offset = (0, 0)
        self.fullscreen = False
        self.scaled_surface = None
        
        # Ana yüzeyleri oluştur
        self.screen = pygame.display.set_mode(self.base_resolution, pygame.SCALED | pygame.RESIZABLE)
        self.game_surface = pygame.Surface(self.base_resolution)
        
        self.states = {}
        self.current_state = None
        self.running = True
        self.clock = pygame.time.Clock()
        self.ui_manager = UIManager()
        self.audio_manager = AudioManager()
        
        # States'leri başlat
        self.init_states()

    def get_scaled_position(self, position):
        """Tam ekran modunda koordinatları oyun koordinat sistemine dönüştür"""
        if not self.fullscreen:
            return position

        return (
            (position[0] - self.current_offset[0]) / self.scale_factor,
            (position[1] - self.current_offset[1]) / self.scale_factor
        )

    def _calculate_scale_dimensions(self, screen_size):
        """Ölçeklendirme boyutlarını hesapla"""
        screen_width, screen_height = screen_size
        target_ratio = self.base_resolution[0] / self.base_resolution[1]
        screen_ratio = screen_width / screen_height

        if screen_ratio > target_ratio:
            # Ekran daha geniş
            scaled_height = screen_height
            scaled_width = int(scaled_height * target_ratio)
            scale_factor = scaled_height / self.base_resolution[1]
        else:
            # Ekran daha dar
            scaled_width = screen_width
            scaled_height = int(scaled_width / target_ratio)
            scale_factor = scaled_width / self.base_resolution[0]

        return scaled_width, scaled_height, scale_factor

    def update_screen_scaling(self, current_size):
        """Ekran ölçekleme hesaplamalarını güncelle ve önbellekle"""
        if not self.fullscreen:
            if self.scaled_surface is not None:
                self.scaled_surface = None
            self.last_screen_size = current_size
            self.scale_factor = 1.0
            self.current_offset = (0, 0)
            return

        scaled_width, scaled_height, scale_factor = self._calculate_scale_dimensions(current_size)
        screen_width, screen_height = current_size

        # Sadece gerekli olduğunda yeni scaled_surface oluştur
        need_new_surface = (
            self.scaled_surface is None or
            self.scale_factor != scale_factor or
            self.scaled_surface.get_size() != (scaled_width, scaled_height)
        )

        if need_new_surface:
            self.scale_factor = scale_factor
            
            # Hardware-accelerated scaling kullan
            try:
                if hasattr(pygame.transform, 'scale_by'):
                    # Önceki surface'i temizle
                    if self.scaled_surface:
                        self.scaled_surface = None
                    # Yeni surface oluştur
                    self.scaled_surface = pygame.Surface((scaled_width, scaled_height)).convert_alpha()
                    pygame.transform.scale_by(self.game_surface, self.scale_factor, self.scaled_surface)
                else:
                    # smoothscale kullan
                    self.scaled_surface = pygame.transform.smoothscale(
                        self.game_surface, (scaled_width, scaled_height)
                    )
            except pygame.error:
                # Fallback: normal scale
                if self.scaled_surface is None or self.scaled_surface.get_size() != (scaled_width, scaled_height):
                    self.scaled_surface = pygame.Surface((scaled_width, scaled_height)).convert_alpha()
                pygame.transform.scale(self.game_surface, (scaled_width, scaled_height), self.scaled_surface)

        # Offset'leri güncelle
        self.current_offset = (
            (screen_width - scaled_width) // 2,
            (screen_height - scaled_height) // 2
        )
        self.last_screen_size = current_size

    def get_surface_offset(self):
        """Mevcut offset değerlerini döndür"""
        return self.current_offset if hasattr(self, 'current_offset') else (0, 0)

    def show_options_menu(self, return_to_pause=False):
        # Oyun durumunda mıyız kontrol et
        is_in_game = isinstance(self.current_state, Playing)
        # Önceki müziği kaydet
        previous_music = self.audio_manager.current_music
        # Yeni options menüsü oluştur
        new_options = OptionsMenu(self, return_to_pause=return_to_pause)
        # Eğer oyundaysak, options menüsü kapatıldığında oyun müziğine dönmek için kaydet
        if is_in_game or return_to_pause:
            # Attach dynamically to avoid static attribute errors from type checkers
            setattr(new_options, 'previous_music', previous_music)
        self.states['options'] = new_options
        self.current_state = new_options
        

    def toggle_fullscreen(self):
        """Tam ekran ve pencere modu arasında geçiş yap"""
        self.fullscreen = not self.fullscreen
        current_flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED
        
        try:
            if self.fullscreen:
                # Tam ekran modu - mevcut ekran boyutlarını al
                current_w = pygame.display.Info().current_w
                current_h = pygame.display.Info().current_h
                window_size = (current_w, current_h)
                
                # VSync ve GPU hızlandırma ile tam ekran
                self.screen = pygame.display.set_mode(
                    window_size,
                    current_flags | pygame.FULLSCREEN,
                    vsync=1,
                    depth=32
                )
                
                # Ölçekleme faktörünü güncelle
                self.update_screen_scaling(window_size)
                
                # Ölçeklenmiş yüzeyi oluştur
                scaled_width = int(self.base_resolution[0] * self.scale_factor)
                scaled_height = int(self.base_resolution[1] * self.scale_factor)
                self.scaled_surface = pygame.Surface((scaled_width, scaled_height))
                
            else:
                # Pencere modu - temel çözünürlük ile
                self.screen = pygame.display.set_mode(
                    self.base_resolution,
                    current_flags,
                    vsync=1
                )
                
                # Pencere modu için ayarları sıfırla
                self.scale_factor = 1.0
                self.current_offset = (0, 0)
                self.scaled_surface = None
                
            # Son ekran boyutunu güncelle
            self.last_screen_size = self.screen.get_size()
            # Ekran güncellemesini bekle
            pygame.display.flip()
            
        except pygame.error as e:
            print(f"Ekran modu değiştirilemedi: {e}")
            # Hata durumunda güvenli moda geri dön
            self.fullscreen = False
            self.screen = pygame.display.set_mode(
                self.base_resolution,
                pygame.HWSURFACE | pygame.DOUBLEBUF
            )
        
        # Event kuyruğunu ve önbelleği temizle
        pygame.event.clear()
        self.screen.fill((0, 0, 0))
        pygame.display.flip()

    def start_game(self):
        self.states['playing'] = Playing(self)
        self.current_state = self.states['playing']
    

    def show_credits(self):
        self.current_state = self.states['credits']

    def back_to_menu(self):
        # Ana menü müziğini çal
        self.audio_manager.play_music('menu')
        self.current_state = self.states['main_menu']
        if hasattr(self.current_state, "init_music"):
            self.current_state.init_music()

    def reset_game_settings(self):
        """Oyun ayarlarını yükle ve hız ayarlarını gizle"""
        try:
            with open('game_settings.json', 'r') as f:
                settings = json.load(f)
                settings['show_speed_settings'] = False  # Hız ayarlarını gizle
            with open('game_settings.json', 'w') as f:
                json.dump(settings, f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def quit_game(self):
        self.audio_manager.save_settings()  # Ses ayarlarını kaydet
        self.reset_game_settings()  # Hız ayarlarını sıfırla
        self.running = False
    
    def resume_game(self):
        """Resume the playing state after pausing.

        If a playing state already exists it will be restored. Otherwise a new
        Playing state will be created. Attempt to (re)start game music if
        the playing state provides an init_music method.
        """
        # Prefer existing playing state so we don't reset game progress
        playing_state = self.states.get('playing')
        if playing_state is None:
            # Create a new playing state if one doesn't exist
            self.states['playing'] = Playing(self)
            playing_state = self.states['playing']

        # Call lifecycle hooks
        if hasattr(playing_state, 'on_resume'):
            playing_state.on_resume()

        self.current_state = playing_state

        # Try to resume music for the playing state
        try:
            if hasattr(playing_state, 'init_music'):
                playing_state.init_music()
            else:
                # Fallback: request audio manager to play the playing track
                self.audio_manager.play_music('playing')
            # Play a small resume sfx if available to provide feedback
            try:
                self.audio_manager.play_sfx('collect_money')
            except Exception:
                pass
        except Exception:
            # Don't let audio issues break resume
            pass
    # Remove the duplicate game_loop definition above

    def _handle_system_events(self, event):
        """Sistem seviyesi eventleri işle (fullscreen, quit)"""
        if event.type == pygame.QUIT:
            self.running = False
            return True
        elif event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_F11 or 
                (event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT)):
                self.toggle_fullscreen()
                return True
        return False

    def game_loop(self):
        # Event tipleri önbelleğe alınıyor
        TRACKED_EVENTS = {
            pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP,
            pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION
        }
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Event yönetimi optimizasyonu
            events = []
            for event in pygame.event.get():
                # Sadece takip edilen event tiplerini işle
                if event.type in TRACKED_EVENTS:
                    # Sistem eventlerini ayrı işle
                    if not self._handle_system_events(event):
                        events.append(event)

            if not self.running:
                break

            # State güncellemeleri
            if self.current_state is None:
                self.current_state = self.states.get('main_menu')
                if self.current_state is None:
                    continue
            self.current_state.handle_events(events)
            if hasattr(self.current_state, 'update'):
                self.current_state.update(dt)
            # Ekran boyutu kontrolü ve ölçekleme
            current_size = self.screen.get_size()
            if current_size != self.last_screen_size:
                self.update_screen_scaling(current_size)
                self.last_screen_size = current_size
            # Oyun mantığı güncellemesi
            if self.current_state is not None and hasattr(self.current_state, 'draw'):
                self.current_state.draw(self.game_surface)
            
            # Çizim optimizasyonu
            self.screen.fill((0, 0, 0))
            
            if self.fullscreen:
                if not self.scaled_surface:
                    scaled_size = (
                        int(self.base_resolution[0] * self.scale_factor),
                        int(self.base_resolution[1] * self.scale_factor)
                    )
                    self.scaled_surface = pygame.Surface(scaled_size).convert()
                
                # Direkt ve basit ölçekleme kullan
                pygame.transform.scale(self.game_surface, self.scaled_surface.get_size(), self.scaled_surface)
                self.screen.blit(self.scaled_surface, self.current_offset)
            else:
                # Pencere modunda direkt çizim
                self.screen.blit(self.game_surface, (0, 0))
            
            # Ekranı güncelle (VSync ile)
            pygame.display.flip()


    def trigger_load_game(self, slot_index=None):
        """Start a new game instead of loading from slot.
        
        The slot_index parameter is kept for backward compatibility but is ignored.
        The game now uses a high score system instead of save slots.
        """
        self.states['playing'] = Playing(self)
        self.current_state = self.states['playing']
        
        # Start the game music
        if hasattr(self.current_state, 'init_music'):
            self.current_state.init_music()
        
        pygame.display.update()


