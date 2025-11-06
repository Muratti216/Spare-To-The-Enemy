# spear_game/game_states.py

import pygame
import sys
import random
import json

# Proje içi modüllerden importlar
from .settings import (
    WIDTH, HEIGHT, TILE_SIZE, ASSET_BASE_PATH,
    BLACK, WHITE, GRAY, LIGHT_GRAY, DARK_GRAY, RED, GREEN, BLUE, YELLOW,
    HIGHLIGHT_COLOR, TITLE_FONT_SIZE, BUTTON_FONT_SIZE, SAVE_SLOT_FONT_SIZE,
    DEFAULT_ENEMY_SPEED, DEFAULT_PLAYER_SPEED,
    MIN_ENEMY_SPEED, MAX_ENEMY_SPEED,
    MIN_PLAYER_SPEED, MAX_PLAYER_SPEED
)
from .utils import load_image, draw_text
from . import save_system
from .sprites import Player, Spear, Walls, Enemy, Money
from .ui_manager import UIManager

class GameState:
    """Base state class for game states.
    
    This class provides common functionality used by all game states, including:
    - Font management and caching
    - State transitions
    - Mouse position handling
    - Basic UI functionality
    
    All game states (menus, game screens, etc.) should inherit from this class.
    """
    
    # Ensure pygame is initialized
    pygame.init()
    pygame.font.init()
    
    # Class-level caches and settings
    _font_cache = {}
    _image_cache = {}
    _state_transition_delay = 150  # Minimum state transition delay (ms)
    
    def __init__(self, controller):
        """Initialize a new game state.

        Args:
            controller: The game controller instance that manages game states
        """
        self.controller = controller
        self._init_time = pygame.time.get_ticks()
        
        # Ensure pygame is initialized
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
            
        # Initialize UI manager
        self.ui_manager = UIManager()
        fonts = self.ui_manager.fonts
        
        # Initialize fonts with fallbacks
        self.TITLE_FONT = fonts.get('title') or pygame.font.Font(None, TITLE_FONT_SIZE)
        self.BUTTON_FONT = fonts.get('button') or pygame.font.Font(None, BUTTON_FONT_SIZE)
        self.SAVE_SLOT_FONT = fonts.get('save_slot') or pygame.font.Font(None, SAVE_SLOT_FONT_SIZE)
        self.CREDITS_FONT = pygame.font.Font(None, 40)  # Credits font always uses system font
        
        # Validate fonts after initialization
        if not self.TITLE_FONT or not hasattr(self.TITLE_FONT, 'render'):
            self.TITLE_FONT = pygame.font.Font(None, TITLE_FONT_SIZE)
        if not self.BUTTON_FONT or not hasattr(self.BUTTON_FONT, 'render'):
            self.BUTTON_FONT = pygame.font.Font(None, BUTTON_FONT_SIZE)
        if not self.SAVE_SLOT_FONT or not hasattr(self.SAVE_SLOT_FONT, 'render'):
            self.SAVE_SLOT_FONT = pygame.font.Font(None, SAVE_SLOT_FONT_SIZE)
    
    def handle_events(self, events):
        """Process and handle pygame events.

        Args:
            events: List of pygame events to process
        """
        pass
    
    def update(self, dt):
        """Update the state's logic.

        Args:
            dt: Time elapsed since last update in seconds
        """
        pass
    
    def draw(self, screen):
        """Draw the state's content to the screen.

        Args:
            screen: The pygame surface to draw on
        """
        pass
    
    def can_transition(self):
        """Check if enough time has passed for state transition.

        This prevents rapid state changes that could confuse the user or
        cause input issues. States can only transition after a minimum delay.

        Returns:
            bool: True if enough time has passed for state transition
        """
        return pygame.time.get_ticks() - self._init_time >= self._state_transition_delay
        
    def get_mouse_pos(self):
        """Get the adjusted mouse position for fullscreen mode.

        Returns:
            tuple: (x, y) coordinates adjusted for fullscreen scaling if needed
        """
        raw_pos = pygame.mouse.get_pos()
        if hasattr(self.controller, 'fullscreen') and self.controller.fullscreen:
            return self.controller.get_scaled_position(raw_pos)
        return raw_pos

    def on_enter(self):
        """Called when entering this state."""
        pass

    def on_exit(self):
        """Called when exiting this state."""
        pass

    def on_pause(self):
        """Called when this state is paused (e.g. when opening pause menu)."""
        pass

    def on_resume(self):
        """Called when this state is resumed (e.g. when closing pause menu)."""
        pass
    






# --- HighScoreEntry State ---
class HighScoreEntry(GameState):
    def __init__(self, controller, score=None):
        super().__init__(controller)
        self.score = score if score is not None else self.ui_manager.get_score()
        self.input_active = True
        self.input_text = ""
        self.max_name_chars = 12
        self.saved = False
        self.info_text = "Enter your name to save your score!"

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.controller.quit_game()
            elif event.type == pygame.KEYDOWN and self.input_active:
                if event.key == pygame.K_RETURN:
                    name = self.input_text.strip() or "PLAYER"
                    from . import save_system
                    save_system.save_player_score(name[:self.max_name_chars], self.score)
                    self.saved = True
                    self.input_active = False
                    self.info_text = f"Score saved! Press ENTER to return."
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif len(self.input_text) < self.max_name_chars and event.unicode.isprintable():
                    self.input_text += event.unicode
                elif event.key == pygame.K_RETURN and self.saved:
                    self.controller.back_to_menu()
            elif event.type == pygame.KEYDOWN and self.saved:
                if event.key == pygame.K_RETURN:
                    self.controller.back_to_menu()

    def draw(self, screen):
        screen.fill(BLACK)
        draw_text("NEW HIGH SCORE!", self.TITLE_FONT, YELLOW, screen, WIDTH // 2, 200)
        draw_text(f"Your Score: {self.score}", self.BUTTON_FONT, WHITE, screen, WIDTH // 2, 300)
        draw_text(self.info_text, self.BUTTON_FONT, WHITE, screen, WIDTH // 2, 400)
        # İsim girişi kutusu
        box_rect = pygame.Rect(WIDTH//2 - 180, 480, 360, 60)
        pygame.draw.rect(screen, BLUE, box_rect, 3, border_radius=10)
        display_text = self.input_text if self.input_text or self.input_active else "Name here..."
        color = (255,255,255) if self.input_text else (180,180,180)
        text_surface = self.BUTTON_FONT.render(display_text, True, color)
        text_rect = text_surface.get_rect(center=box_rect.center)
        screen.blit(text_surface, text_rect)

# --- PauseMenu State ---
class PauseMenu(GameState):
    def __init__(self, controller):
        super().__init__(controller)
        self.audio_manager = controller.audio_manager
        self.options = ["Continue", "Settings", "Main Menu"]
        self.button_rects = []
        self.SMALL_BUTTON_FONT = pygame.font.Font(None, 47)  # Özel küçük font
        self.ui_manager = UIManager()  # UI Manager'ı başlat
        self._update_button_rects()

    def _update_button_rects(self):
        self.button_rects = []
        button_width = 350
        button_height = 70
        spacing = 20  # Butonlar arası boşluk
        
        # Tüm butonların toplam yüksekliği
        total_height = (button_height * len(self.options)) + (spacing * (len(self.options) - 1))
        
        # Başlangıç y pozisyonu (ekranın ortası - toplam yüksekliğin yarısı)
        start_y = (HEIGHT - total_height) // 2
        
        x = WIDTH // 2 - button_width // 2
        for i, opt in enumerate(self.options):
            y = start_y + (button_height + spacing) * i
            rect = pygame.Rect(x, y, button_width, button_height)
            self.button_rects.append(rect)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.controller.quit_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.controller.resume_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = self.get_mouse_pos()
                for i, rect in enumerate(self.button_rects):
                    if rect.collidepoint(mouse_pos):
                        if i == 0:  # Continue
                            self.controller.resume_game()
                        elif i == 1:  # Settings
                            self.controller.show_options_menu(return_to_pause=True)
                        elif i == 2:  # Back to Main Menu
                            self.controller.back_to_menu()

    def draw(self, screen):
        # Önce alttaki Playing state'ini çiz (pause edilmiş hali)
        playing_state = self.controller.states.get('playing')
        if playing_state and hasattr(playing_state, 'draw'):
            playing_state.draw(screen)
            
            # Blur efekti uygula: küçült-büyüt yöntemiyle hızlı blur
            blur_factor = 8  # Ne kadar küçültüleceği (yüksek = daha bulanık)
            small_size = (WIDTH // blur_factor, HEIGHT // blur_factor)
            
            # Ekranı küçült
            small_surface = pygame.transform.smoothscale(screen, small_size)
            # Tekrar büyüt (blur efekti)
            blurred = pygame.transform.smoothscale(small_surface, (WIDTH, HEIGHT))
            screen.blit(blurred, (0, 0))
        
        # Yarı şeffaf siyah arka plan - daha düşük alpha ile oyun net görünsün
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(120)  # 120/255 opaklık - daha şeffaf, oyun daha net görünür
        screen.blit(overlay, (0, 0))
        
        # PAUSE yazısını ekranın üst kısmına çiz
        title_y = self.button_rects[0].top - 100 if self.button_rects else 200
        draw_text("PAUSE", self.TITLE_FONT, WHITE, screen, WIDTH // 2, title_y)
        
        # Butonları çiz
        self._update_button_rects()
        mouse_pos = self.get_mouse_pos()
        for i, (opt, rect) in enumerate(zip(self.options, self.button_rects)):
            # Buton arka planı (yarı şeffaf)
            button_bg = pygame.Surface((rect.width, rect.height))
            button_bg.fill((60, 60, 60))
            button_bg.set_alpha(200)  # Butonlar biraz daha opak
            screen.blit(button_bg, rect)
            
            # Buton çerçevesi
            color = YELLOW if rect.collidepoint(mouse_pos) else WHITE
            pygame.draw.rect(screen, color, rect, 3, border_radius=18)
            
            # Buton yazısı
            if hasattr(self.ui_manager, 'BUTTON_FONT'):
                font = self.ui_manager.BUTTON_FONT
            else:
                font = self.BUTTON_FONT if i != 2 else self.SMALL_BUTTON_FONT
            
            draw_text(opt, font, color, screen, rect.centerx, rect.centery)

class MainMenu(GameState):
    def __init__(self, controller):
        super().__init__(controller)
        self.audio_manager = controller.audio_manager
        self.audio_manager.stop_music()  # Önceki müziği durdur
        self.audio_manager.load_settings()  # Ayar dosyasını tekrar yükle
        self.audio_manager.apply_all_volumes()  # En güncel ayarları uygula
        self.button_y_start = HEIGHT // 1.68
        self.button_spacing = 100
        self.play_button_rect = pygame.Rect(0, 0, 1, 1)
        self.options_button_rect = pygame.Rect(0, 0, 1, 1)
        self.credits_button_rect = pygame.Rect(0, 0, 1, 1)
        self.exit_button_rect = pygame.Rect(0, 0, 1, 1)
        self.music_loaded = False
        self.TITLE_FONT = pygame.font.Font(None, 100)
        self.BUTTON_FONT = pygame.font.Font(None, 60)
        self.CREDITS_FONT = pygame.font.Font(None, 40)
        self.menu_background_image = load_image("background0.png", (WIDTH, HEIGHT))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.controller.quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.can_transition():  # Geçiş için yeterli süre geçmediyse işleme
                    return
                    
                mouse_pos = self.get_mouse_pos()
                if self.play_button_rect.collidepoint(mouse_pos):
                    self.controller.start_game()
                elif self.options_button_rect.collidepoint(mouse_pos):
                    if 'options' not in self.controller.states:  # State'i önbellekle
                        self.controller.states['options'] = OptionsMenu(self.controller)
                    self.controller.current_state = self.controller.states['options']
                elif self.credits_button_rect.collidepoint(mouse_pos):
                    if 'credits' not in self.controller.states:  # State'i önbellekle
                        self.controller.states['credits'] = Credits(self.controller)
                    self.controller.current_state = self.controller.states['credits']
                elif self.exit_button_rect.collidepoint(mouse_pos):
                    self.controller.quit_game()

    def update(self, dt):
        if not self.music_loaded:
            self.audio_manager.play_music('menu')
            self.music_loaded = True

    def draw(self, screen):
        error_message = None
        # Arka planı yükleyemediysek hata mesajı hazırla
        if self.menu_background_image:
            screen.blit(self.menu_background_image, (0, 0))
        else:
            screen.fill(DARK_GRAY)
            error_message = "Arka plan resmi yüklenemedi: assets/background0.png"

        # Fontlar yüklenmedi mi kontrolü
        try:
            mouse_pos = self.get_mouse_pos()
            # Font boyutuna göre letter spacing ayarla
            letter_spacing = int(self.BUTTON_FONT.get_height() * 0.1)  # Font yüksekliğinin %10'u kadar spacing
            
            play_color = HIGHLIGHT_COLOR if self.play_button_rect.collidepoint(mouse_pos) else WHITE
            self.play_button_rect = draw_text("Play", self.BUTTON_FONT, play_color, screen, WIDTH // 2, 
                                            self.button_y_start, letter_spacing=letter_spacing)

            options_color = HIGHLIGHT_COLOR if self.options_button_rect.collidepoint(mouse_pos) else WHITE
            self.options_button_rect = draw_text("Options", self.BUTTON_FONT, options_color, screen, WIDTH // 2, 
                                               self.button_y_start + self.button_spacing, letter_spacing=letter_spacing)

            credits_color = HIGHLIGHT_COLOR if self.credits_button_rect.collidepoint(mouse_pos) else WHITE
            self.credits_button_rect = draw_text("Credits", self.BUTTON_FONT, credits_color, screen, WIDTH // 2, 
                                               self.button_y_start + self.button_spacing * 2, letter_spacing=letter_spacing)

            exit_color = HIGHLIGHT_COLOR if self.exit_button_rect.collidepoint(mouse_pos) else WHITE
            self.exit_button_rect = draw_text("Exit", self.BUTTON_FONT, exit_color, screen, WIDTH // 2, 
                                            self.button_y_start + self.button_spacing * 3, letter_spacing=letter_spacing)
        except Exception as e:
            error_message = f"Font veya buton çizimi hatası: {e}"

        # Hata varsa ekrana kırmızı yazı ile göster
        if error_message:
            font = pygame.font.Font(None, 36)
            draw_text(error_message, font, (255,0,0), screen, WIDTH//2, HEIGHT//2)

class OptionsMenu(GameState):
    def update(self, dt):
        pass
    def __init__(self, controller, return_to_pause=False):
        super().__init__(controller)
        self.audio_manager = controller.audio_manager
        self.audio_manager.stop_music()  # Önceki müziği durdur
        self.audio_manager.load_settings()  # Ayar dosyasını tekrar yükle
        self.audio_manager.apply_all_volumes()  # En güncel ayarları uygula
        self.ui_manager = UIManager()
        self.audio_manager.play_music('menu')

        # Ses kontrol butonları
        self.music_minus_rect = None
        self.music_plus_rect = None
        self.sfx_minus_rect = None
        self.sfx_plus_rect = None
        self.mute_rect = None

        # Düşman kontrol butonları
        self.enemy_speed_minus_rect = None
        self.enemy_speed_plus_rect = None
        self.enemy_toggle_rect = None

        # Oyuncu hız kontrol butonları
        self.player_speed_minus_rect = None
        self.player_speed_plus_rect = None

        # Gizli kod sistemi için değişkenler
        self.arrows_sequence = []
        self.wasd_sequence = []
        self.show_speed_settings = False
        self.last_key_time = pygame.time.get_ticks()
        self.key_timeout = 1000  # 1 saniye içinde girilen tuşları kabul et
        
        # Doğru kod sekansları
        self.correct_arrows = [
            pygame.K_UP, pygame.K_DOWN, pygame.K_UP, pygame.K_DOWN,
            pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT
        ]
        self.correct_wasd = [
            pygame.K_w, pygame.K_s, pygame.K_w, pygame.K_s,
            pygame.K_a, pygame.K_d, pygame.K_a, pygame.K_d
        ]

        # Ayarları yükle
        self.load_game_settings()
        self.return_to_pause = return_to_pause
        
    def load_game_settings(self):
        """Oyun ayarlarını dosyadan yükler"""
        try:
            with open('game_settings.json', 'r') as f:
                settings = json.load(f)
                self.enemy_speed = settings.get('enemy_speed', DEFAULT_ENEMY_SPEED)
                self.enemy_spawn_enabled = settings.get('enemy_spawn_enabled', True)
                self.player_speed = settings.get('player_speed', DEFAULT_PLAYER_SPEED)
                self.show_speed_settings = settings.get('show_speed_settings', False)
        except (FileNotFoundError, json.JSONDecodeError):
            self.enemy_speed = DEFAULT_ENEMY_SPEED
            self.enemy_spawn_enabled = True
            self.player_speed = DEFAULT_PLAYER_SPEED
            self.show_speed_settings = False
            self.save_game_settings()
            
    def save_game_settings(self):
        """Oyun ayarlarını dosyaya kaydeder"""
        settings = {
            'enemy_speed': self.enemy_speed,
            'enemy_spawn_enabled': self.enemy_spawn_enabled,
            'player_speed': self.player_speed,
            'show_speed_settings': self.show_speed_settings
        }
        with open('game_settings.json', 'w') as f:
            json.dump(settings, f)
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.controller.quit_game()
            elif event.type == pygame.KEYDOWN:
                # Gizli kod sekanslarını kontrol et
                current_time = pygame.time.get_ticks()
                
                # Zaman aşımını kontrol et
                if current_time - self.last_key_time > self.key_timeout:
                    self.arrows_sequence.clear()
                    self.wasd_sequence.clear()
                
                self.last_key_time = current_time
                
                # Ok tuşları sekansı
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    self.arrows_sequence.append(event.key)
                    if len(self.arrows_sequence) > 8:
                        self.arrows_sequence.pop(0)
                    if self.arrows_sequence == self.correct_arrows:
                        self.show_speed_settings = True
                        self.save_game_settings()
                
                # WASD sekansı
                if event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                    self.wasd_sequence.append(event.key)
                    if len(self.wasd_sequence) > 8:
                        self.wasd_sequence.pop(0)
                    if self.wasd_sequence == self.correct_wasd:
                        self.show_speed_settings = True
                        self.save_game_settings()
                
                if event.key == pygame.K_ESCAPE:
                    # Tüm ayarları kaydet ve uygula
                    self.audio_manager.save_settings()
                    self.audio_manager.apply_all_volumes()
                    self.save_game_settings()
                    # Önceki ekrana dön
                    if getattr(self, 'return_to_pause', False):
                        new_pause = PauseMenu(self.controller)
                        self.controller.states['pause'] = new_pause
                        self.controller.current_state = new_pause
                        # Pause menüde müzik çalınmayacak
                        self.audio_manager.stop_music()
                    else:
                        self.controller.back_to_menu()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = self.get_mouse_pos()

                # Müzik kontrolleri
                if self.music_minus_rect and self.music_minus_rect.collidepoint(mouse_pos):
                    new_vol = max(0.0, self.audio_manager.music_volume - 0.1)
                    self.audio_manager.set_music_volume(new_vol)
                elif self.music_plus_rect and self.music_plus_rect.collidepoint(mouse_pos):
                    new_vol = min(1.0, self.audio_manager.music_volume + 0.1)
                    self.audio_manager.set_music_volume(new_vol)

                # SFX kontrolleri
                elif self.sfx_minus_rect and self.sfx_minus_rect.collidepoint(mouse_pos):
                    new_vol = max(0.0, self.audio_manager.sfx_volume - 0.1)
                    self.audio_manager.set_sfx_volume(new_vol)
                elif self.sfx_plus_rect and self.sfx_plus_rect.collidepoint(mouse_pos):
                    new_vol = min(1.0, self.audio_manager.sfx_volume + 0.1)
                    self.audio_manager.set_sfx_volume(new_vol)

                # Mute kontrolü
                elif self.mute_rect and self.mute_rect.collidepoint(mouse_pos):
                    self.audio_manager.toggle_mute()

                # Oyuncu hızı kontrolleri
                elif self.player_speed_minus_rect and self.player_speed_minus_rect.collidepoint(mouse_pos):
                    self.player_speed = max(10, self.player_speed - 10)  # Minimum 10 hız
                    self.save_game_settings()
                elif self.player_speed_plus_rect and self.player_speed_plus_rect.collidepoint(mouse_pos):
                    self.player_speed += 10  # Sınırsız artış
                    self.save_game_settings()

                # Düşman kontrolleri
                elif self.enemy_speed_minus_rect and self.enemy_speed_minus_rect.collidepoint(mouse_pos):
                    self.enemy_speed = max(MIN_ENEMY_SPEED, self.enemy_speed - 10)
                    self.save_game_settings()
                elif self.enemy_speed_plus_rect and self.enemy_speed_plus_rect.collidepoint(mouse_pos):
                    self.enemy_speed = min(MAX_ENEMY_SPEED, self.enemy_speed + 10)
                    self.save_game_settings()
                elif self.enemy_toggle_rect and self.enemy_toggle_rect.collidepoint(mouse_pos):
                    self.enemy_spawn_enabled = not self.enemy_spawn_enabled
                    self.save_game_settings()

                # Her değişiklikten sonra ayarları uygula ve kaydet
                self.audio_manager.apply_all_volumes()
                self.audio_manager.save_settings()

    def draw_volume_slider(self, screen, y_pos, label, volume):
        """Ses ayarını ve görsel barını çizen yardımcı fonksiyon. Buton rect'lerini döndürür."""
        draw_text(label, self.ui_manager.BUTTON_FONT, WHITE, screen, WIDTH // 5, y_pos, center_align=False)
        
        # Butonların x koordinatları
        minus_x = WIDTH * 0.65
        plus_x = WIDTH * 0.9
        
        # Butonları yerleştir
        minus_rect = pygame.Rect(minus_x-20, y_pos-20, 40, 40)
        plus_rect = pygame.Rect(plus_x-20, y_pos-20, 40, 40)
        
        # Eksi Butonu
        pygame.draw.rect(screen, DARK_GRAY, minus_rect, border_radius=10)
        draw_text("-", self.ui_manager.BUTTON_FONT, WHITE, screen, minus_rect.centerx, minus_rect.centery)
        
        # Bar için kullanılabilir alanı hesapla
        bar_width = 160  # Barın genişliği
        bar_start_x = minus_x + 30  # Eksi butonunun sağından başla
        
        # Ses Barı
        bar_bg_rect = pygame.Rect(bar_start_x, y_pos - 15, bar_width, 30)
        bar_fill_rect = pygame.Rect(bar_start_x, y_pos - 15, bar_width * volume, 30)
        pygame.draw.rect(screen, DARK_GRAY, bar_bg_rect)
        pygame.draw.rect(screen, GREEN, bar_fill_rect)
        # Artı Butonu
        pygame.draw.rect(screen, DARK_GRAY, plus_rect, border_radius=10)
        draw_text("+", self.ui_manager.BUTTON_FONT, WHITE, screen, plus_rect.centerx, plus_rect.centery)
        return minus_rect, plus_rect


    def draw_enemy_speed_controls(self, screen, y_pos):
        """Düşman hızı kontrollerini çizer"""
        draw_text("Enemy Speed", self.ui_manager.BUTTON_FONT, WHITE, screen, WIDTH // 5, y_pos, center_align=False)
        minus_rect = pygame.Rect(WIDTH*0.65-20, y_pos-20, 40, 40)  # Moved more right
        plus_rect = pygame.Rect(WIDTH*0.9-20, y_pos-20, 40, 40)  # Moved more right
        
        # Eksi/Artı Butonları
        pygame.draw.rect(screen, DARK_GRAY, minus_rect, border_radius=10)
        pygame.draw.rect(screen, DARK_GRAY, plus_rect, border_radius=10)
        draw_text("-", self.ui_manager.BUTTON_FONT, WHITE, screen, minus_rect.centerx, minus_rect.centery)
        draw_text("+", self.ui_manager.BUTTON_FONT, WHITE, screen, plus_rect.centerx, plus_rect.centery)
        
        # Hız Göstergesi
        speed_text = f"{self.enemy_speed}"
        draw_text(speed_text, self.ui_manager.BUTTON_FONT, WHITE, screen, WIDTH*0.775, y_pos)  # Moved more right
        
        return minus_rect, plus_rect

    def draw_speed_controls(self, screen, y_pos, label, current_speed, min_speed, max_speed):
        """Hız kontrolleri için yardımcı fonksiyon"""
        draw_text(label, self.ui_manager.BUTTON_FONT, WHITE, screen, WIDTH // 5, y_pos, center_align=False)
        
        # Butonların x koordinatları
        minus_x = WIDTH * 0.65
        plus_x = WIDTH * 0.9
        
        # Butonları yerleştir
        minus_rect = pygame.Rect(minus_x-20, y_pos-20, 40, 40)
        plus_rect = pygame.Rect(plus_x-20, y_pos-20, 40, 40)
        
        # Eksi/Artı Butonları
        pygame.draw.rect(screen, DARK_GRAY, minus_rect, border_radius=10)
        pygame.draw.rect(screen, DARK_GRAY, plus_rect, border_radius=10)
        draw_text("-", self.ui_manager.BUTTON_FONT, WHITE, screen, minus_rect.centerx, minus_rect.centery)
        draw_text("+", self.ui_manager.BUTTON_FONT, WHITE, screen, plus_rect.centerx, plus_rect.centery)
        
        # Hız Göstergesi
        # Hız değerini göster (- ve + butonları arasında ortalı)
        current_text = f"{current_speed}"
        text_x = minus_x + (plus_x - minus_x) / 2  # İki buton arasının ortası
        draw_text(current_text, self.ui_manager.BUTTON_FONT, WHITE, screen, text_x, y_pos)  # Moved more right
        
        return minus_rect, plus_rect

    def draw(self, screen):
        screen.fill(BLACK)
        draw_text("Options", self.ui_manager.TITLE_FONT, WHITE, screen, WIDTH // 2, 150)  # Title moved down
        
        # Müzik ve SFX ayar çubukları
        self.music_minus_rect, self.music_plus_rect = self.draw_volume_slider(screen, 250, "Music", self.audio_manager.music_volume)
        self.sfx_minus_rect, self.sfx_plus_rect = self.draw_volume_slider(screen, 340, "SFX", self.audio_manager.sfx_volume)
        
        if self.show_speed_settings:
            # Oyuncu hızı ayarları
            self.player_speed_minus_rect, self.player_speed_plus_rect = self.draw_speed_controls(
                screen, 430, "Player Speed", self.player_speed, MIN_PLAYER_SPEED, MAX_PLAYER_SPEED)
            
            # Düşman hızı ayarları
            self.enemy_speed_minus_rect, self.enemy_speed_plus_rect = self.draw_speed_controls(
                screen, 520, "Enemy Speed", self.enemy_speed, MIN_ENEMY_SPEED, MAX_ENEMY_SPEED)
        else:
            self.player_speed_minus_rect = None
            self.player_speed_plus_rect = None
            self.enemy_speed_minus_rect = None
            self.enemy_speed_plus_rect = None
        
        # Düşman spawn toggle
        spawn_text = "Enemies: ON" if self.enemy_spawn_enabled else "Enemies: OFF"
        spawn_rect = pygame.Rect(WIDTH//2-100, 610-30, 200, 60)  # Adjusted vertical position
        self.enemy_toggle_rect = spawn_rect
        draw_text(spawn_text, self.ui_manager.BUTTON_FONT, GREEN if self.enemy_spawn_enabled else RED, screen, WIDTH // 2, 610)
        
        # Mute seçeneği
        mute_text = "Mute (X)" if self.audio_manager.is_muted else "Mute ( )"
        mute_rect = pygame.Rect(WIDTH//2-80, 685-30, 160, 60)  # Adjusted vertical position
        self.mute_rect = mute_rect
        draw_text(mute_text, self.ui_manager.BUTTON_FONT, WHITE, screen, WIDTH // 2, 685)
        
        draw_text("Press ESC to go back", self.ui_manager.SAVE_SLOT_FONT, GRAY, screen, WIDTH // 2, HEIGHT - 100)


class Playing(GameState):
    def __init__(self, controller, start_music=True):
        super().__init__(controller)
        self.audio_manager = controller.audio_manager
        self.ui_manager = UIManager()
        
        # Font'ları yükle
        self.TITLE_FONT = pygame.font.Font(None, 100)
        self.BUTTON_FONT = pygame.font.Font(None, 60)
        self.SCORE_FONT = pygame.font.Font(None, 36)
        
        # Yüksek skorları yükle
        from .save_system import get_sorted_high_scores
        high_scores = get_sorted_high_scores(limit=1)
        self.high_score = high_scores[0][1] if high_scores else 0
        
        # Ayarları yükle
        try:
            with open('game_settings.json', 'r') as f:
                settings = json.load(f)
                player_speed = settings.get('player_speed', DEFAULT_PLAYER_SPEED)
        except (FileNotFoundError, json.JSONDecodeError):
            player_speed = DEFAULT_PLAYER_SPEED
        
        # Oyun bileşenlerini başlat
        self.walls = Walls()
        start_pos = self.walls.find_player_start()
        self.player = Player(start_pos, player_speed)
        self.spear = Spear()
        
        # Düşman yönetimi
        self.enemies = []
        self.num_enemies = 8
        self.enemy_speed_default = 120
        self.init_enemies()
        self.spawn_timer = 0
        self.spawn_interval = 5
        
        # Oyun durumu
        self.game_time = 0
        self.last_spawn_interval_update = 0
        self.money_objects = []
        self.spawn_money_objects()
        self.pending_game_over = False
        self.game_over_timer = 0
        self.pending_you_win = False
        
        # Ses ve görüntü ayarları
        self._last_muted = self.audio_manager.is_muted
        self.music_loaded = False
        self.game_background_image = load_image("black.jpg", (WIDTH, HEIGHT))
        self.start_music = start_music
        self.you_win_timer = 0
        
        # Pause/Resume için gerekli değişkenler
        self._paused_time = 0
        self._paused_spawn_timer = 0
        
        # Başlangıçta müziği başlat
        if start_music:
            self.init_music()
    
    def init_music(self):
        """Oyun müziğini başlat"""
        if not self.audio_manager.is_muted:
            self.audio_manager.play_music('playing')
            self.music_loaded = True
        self._last_muted = self.audio_manager.is_muted

    def on_pause(self):
        """Oyun duraklatıldığında çağrılır"""
        # Müziği duraklat
        self.audio_manager.stop_music()
        # Zamanlayıcıları kaydet
        self._paused_time = pygame.time.get_ticks()
        self._paused_spawn_timer = self.spawn_timer

    def on_resume(self):
        """Oyun devam ettirildiğinde çağrılır"""
        # Müziği devam ettir
        if not self.audio_manager.is_muted:
            self.audio_manager.play_music('playing')
            
        # Eğer daha önce pause edilmediyse, zamanlayıcıları güncelleme
        if hasattr(self, '_paused_time') and self._paused_time > 0:
            try:
                paused_duration = pygame.time.get_ticks() - self._paused_time
                if hasattr(self, '_paused_spawn_timer'):
                    self.spawn_timer = self._paused_spawn_timer
                # Enemy'lerin son pozisyonlarını güncelle
                for enemy in self.enemies:
                    if hasattr(enemy, 'last_update_time'):
                        enemy.last_update_time += paused_duration
            except Exception as e:
                print(f"[WARNING] Resume sırasında hata: {e}")
            
        # Pause değişkenlerini sıfırla
        self._paused_time = 0
        self._paused_spawn_timer = 0
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.controller.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.controller.states['pause'] = PauseMenu(self.controller)
                    self.controller.current_state = self.controller.states['pause']
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sol tık
                    mouse_pos = self.get_mouse_pos()
                    self.spear.throw(self.player.pos, mouse_pos)

        if not hasattr(self, 'BUTTON_FONT'):
            self.BUTTON_FONT = pygame.font.Font(None, 60)
            self.CREDITS_FONT = pygame.font.Font(None, 40)
            self.game_background_image = load_image("black.jpg", (WIDTH, HEIGHT))
            self._last_muted = self.audio_manager.is_muted

            # Önceki müziği durdur ve yeni ayarları yükle
            self.audio_manager.stop_music()
            self.audio_manager.load_settings()
            self.audio_manager.apply_all_volumes()

            # Eğer ses kapalı değilse ve başlangıçta müzik istendiyse müziği başlat
            if self.start_music and not self.audio_manager.is_muted:
                self.audio_manager.play_music('playing')
                self.music_loaded = True
            else:
                self.music_loaded = False
    def init_enemies(self):
        self.enemies.clear()
        
        # Oyun ayarlarını yükle
        try:
            with open('game_settings.json', 'r') as f:
                settings = json.load(f)
                base_speed = settings.get('enemy_speed', DEFAULT_ENEMY_SPEED)
                spawn_enabled = settings.get('enemy_spawn_enabled', True)
        except (FileNotFoundError, json.JSONDecodeError):
            base_speed = DEFAULT_ENEMY_SPEED
            spawn_enabled = True
            
        # Eğer düşman oluşturma kapalıysa, hiç düşman oluşturma
        if not spawn_enabled:
            return
            
        half = self.num_enemies // 2
        for _ in range(half):
            spawn_point = (512, 450)
            speed = base_speed + random.randint(-10, 10)
            self.enemies.append(Enemy(spawn_point, speed, color_type="red"))
        for _ in range(self.num_enemies - half):
            spawn_point = (512, 50)
            speed = base_speed + random.randint(-10, 10)
            self.enemies.append(Enemy(spawn_point, speed, color_type="blue"))

    def get_mouse_pos(self):
        """Mouse pozisyonunu tam ekran için düzeltilmiş şekilde döndür"""
        raw_pos = pygame.mouse.get_pos()
        if self.controller.fullscreen:
            offset_x, offset_y = self.controller.current_offset
            scale = self.controller.scale_factor
            
            # Tam ekrandaki pozisyonu oyun koordinatlarına dönüştür
            game_x = (raw_pos[0] - offset_x) / scale
            game_y = (raw_pos[1] - offset_y) / scale
            
            return (int(game_x), int(game_y))
        else:
            return raw_pos

    def update(self, dt):
        # Ses durumunu kontrol et
        if self.audio_manager.is_muted != self._last_muted:
            if self.audio_manager.is_muted:
                self.audio_manager.stop_music()
                self.music_loaded = False
            else:
                self.audio_manager.play_music('playing')
                self.music_loaded = True
            self._last_muted = self.audio_manager.is_muted
        
        # Yüksek skoru güncelle
        current_score = self.ui_manager.get_score()
        if current_score > self.high_score:
            self.high_score = current_score

        # Game over ve kazanma durumlarını kontrol et
        if self.pending_game_over and pygame.time.get_ticks() >= self.game_over_timer:
            score = self.ui_manager.get_score() if hasattr(self, 'ui_manager') else 0
            game_over_state = GameOver(self.controller, score)
            self.controller.states['game_over'] = game_over_state
            self.controller.current_state = game_over_state
            self.pending_game_over = False
            return
        if self.pending_you_win and pygame.time.get_ticks() >= self.you_win_timer:
            score = self.ui_manager.get_score() if hasattr(self, 'ui_manager') else 0
            you_win_state = YouWin(self.controller, score)
            self.controller.states['you_win'] = you_win_state
            self.controller.current_state = you_win_state
            self.pending_you_win = False
            return
        if self.pending_game_over or self.pending_you_win:
            return

        # Oyun mantığını güncelle
        mouse_pos = self.get_mouse_pos()
        self.game_time += dt
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, self.walls.wall_rects)
        self.check_money_collisions()
        self.spear.update(dt, self.player.pos, mouse_pos)

        # Düşmanlarla çarpışma kontrolü
        for enemy in self.enemies[:]:  # Liste kopyası üzerinden işlem yap
            enemy.update(self.player.pos, self.player.rect, dt, self.walls)
            if self.player.rect.colliderect(enemy.rect):
                self.pending_game_over = True
                self.game_over_timer = pygame.time.get_ticks() + 1000
                break

        # Mızrak kontrolü ve düşman öldürme
        if self.spear and self.spear.thrown:
            spear_pos = self.spear.pos
            enemies_to_remove = []
            for enemy in self.enemies:
                if enemy.rect.collidepoint(spear_pos.x, spear_pos.y):
                    enemies_to_remove.append(enemy)
            
            for enemy in enemies_to_remove:
                self.enemies.remove(enemy)
                self.ui_manager.add_score(100)
                self.audio_manager.play_sfx('enemy_hit')

        # Tüm paralar toplandı mı kontrolü
        if not self.money_objects:
            self.pending_you_win = True
            self.you_win_timer = pygame.time.get_ticks() + 1000
            return

        # Düşman spawn zamanlaması
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = 0

        # Spawn interval güncelleme
        if self.game_time - self.last_spawn_interval_update >= 30 and self.spawn_interval > 1:
            self.spawn_interval -= 1
            self.last_spawn_interval_update = self.game_time

    def spawn_money_objects(self):
        self.money_objects.clear()
        tile_size = TILE_SIZE
        for row_index, row in enumerate(self.walls.level_map):
            for col_index, value in enumerate(row):
                if value in (6, 7, 8, 9):
                    x = col_index * tile_size
                    y = row_index * tile_size
                    money = Money((x, y))
                    self.money_objects.append(money)

    def draw_money_objects(self, screen):
        for money in self.money_objects:
            money.draw(screen)

    def draw_score(self, screen):
        # Mevcut skoru göster
        current_score = self.ui_manager.get_score()
        score_text = f"Score: {current_score}"
        draw_text(score_text, self.SCORE_FONT, WHITE, screen, 20, 20, center_align=False)
        
        # Yüksek skoru göster (eğer mevcut skordan yüksekse sarı, değilse beyaz renkte)
        high_score_color = YELLOW if self.high_score > current_score else WHITE
        high_score_text = f"Best: {self.high_score}"
        draw_text(high_score_text, self.SCORE_FONT, high_score_color, screen, 20, 60, center_align=False)

    def spawn_enemy(self):
        """Yeni düşman oluştur"""
        # Oyun ayarlarını kontrol et
        try:
            with open('game_settings.json', 'r') as f:
                settings = json.load(f)
                spawn_enabled = settings.get('enemy_spawn_enabled', True)
                base_speed = settings.get('enemy_speed', DEFAULT_ENEMY_SPEED)
        except (FileNotFoundError, json.JSONDecodeError):
            spawn_enabled = True
            base_speed = DEFAULT_ENEMY_SPEED

        # Düşman oluşturma kapalıysa veya çok fazla düşman varsa oluşturma
        if not spawn_enabled or len(self.enemies) >= self.num_enemies * 2:
            return

        # Rastgele spawn noktası seç
        if random.choice([True, False]):
            spawn_point = (512, 450)  # Alt spawn noktası
            enemy_type = "red"
        else:
            spawn_point = (512, 50)   # Üst spawn noktası
            enemy_type = "blue"

        # Hızı ayarla ve düşmanı oluştur
        speed = base_speed + random.randint(-10, 10)
        self.enemies.append(Enemy(spawn_point, speed, color_type=enemy_type))

    def draw(self, screen):
        if self.game_background_image:
            screen.blit(self.game_background_image, (0, 0))
        else:   
            screen.fill(LIGHT_GRAY)

        self.walls.draw(screen)
        # Önce paraları çiz, sonra enemy'leri çiz ki enemy'ler paraların üstünde gözüksün
        self.draw_money_objects(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
        self.player.draw(screen)
        self.spear.draw(screen, self.player.pos)
        self.draw_score(screen)

    def check_money_collisions(self):
        for money in self.money_objects[:]:
            if self.player.rect.colliderect(money.rect):
                self.money_objects.remove(money)
                self.ui_manager.add_score(25)
                self.audio_manager.play_sfx('collect_money')


# ... Credits, GameOver, YouWin ve Playing sınıflarının tamamı buraya gelecek ...
# Dikkat: Bu sınıfların içindeki tüm load_image, load_music, draw_text çağrıları
# ve WIDTH, HEIGHT gibi sabitler artık bu dosyanın başındaki importlar sayesinde çalışacaktır.

class Credits(GameState):
    def __init__(self, controller):
        super().__init__(controller)
        self.back_button_rect = pygame.Rect(0, 0, 1, 1)
        self.TITLE_FONT = pygame.font.Font(None, 100)
        self.BUTTON_FONT = pygame.font.Font(None, 60)
        self.CREDITS_FONT = pygame.font.Font(None, 40)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.controller.quit_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.controller.back_to_menu()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = self.get_mouse_pos()
                event_pos = mouse_pos  # In full-screen mode, use the corrected mouse position
                if self.back_button_rect.collidepoint(event_pos):
                    self.controller.back_to_menu()

    def update(self, dt):
        pygame.mixer.music.stop()
        #pass

    def draw(self, screen):
        screen.fill(DARK_GRAY)
        title_y = HEIGHT // 4
        line_height = self.CREDITS_FONT.get_linesize() + 10
        draw_text("Credits", self.TITLE_FONT, WHITE, screen, WIDTH // 2, title_y)

        current_y = HEIGHT // 2 - line_height * 1.5
        draw_text("Developers: Kerem Kekulluoglu, Muratcan Sariyildiz", self.CREDITS_FONT, WHITE, screen, WIDTH // 2, current_y)
        current_y += line_height
        draw_text("Designer: Ege Alpogan", self.CREDITS_FONT, WHITE, screen, WIDTH // 2, current_y)
        current_y += line_height
        draw_text("Theme: Medieval", self.CREDITS_FONT, WHITE, screen, WIDTH // 2, current_y)

        mouse_pos = self.get_mouse_pos()
        back_color = HIGHLIGHT_COLOR if self.back_button_rect.collidepoint(mouse_pos) else WHITE
        self.back_button_rect = draw_text("Back to Main Menu (ESC)", self.BUTTON_FONT, back_color, screen, WIDTH // 2, HEIGHT * 3 // 4 + 50)





# --- Consolidated GameOver State ---
class GameOver(GameState):
    """Game Over screen state.
    
    Displayed when the player loses the game. Provides options to:
    - Try again
    - Return to main menu
    - Save the current score
    """
    
    def __init__(self, controller, score):
        """Initialize the game over screen.

        Args:
            controller: The game controller instance
            score: The player's final score
        """
        super().__init__(controller)
        self.score = score
        self.background = load_image("game_over_bg.png", (WIDTH, HEIGHT))
        
        # Initialize UI manager for fonts
        self.ui_manager = UIManager()
        
        # Initialize button rectangles for collision detection
        self.retry_button_rect = pygame.Rect(0, 0, 1, 1)
        self.menu_button_rect = pygame.Rect(0, 0, 1, 1)
        self.save_score_button_rect = pygame.Rect(0, 0, 1, 1)
        self.save_score_entered = False

    def handle_events(self, events):
        """Process events for the game over screen.

        Handles:
        - Mouse clicks on buttons (retry, menu, save score)
        - Escape key for returning to menu
        - Quit event

        Args:
            events: List of pygame events to process
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.controller.quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Handle button clicks
                mouse_pos = self.get_mouse_pos()
                if self.retry_button_rect.collidepoint(mouse_pos):
                    self.controller.start_game()
                    self.ui_manager.reset_score()
                elif self.menu_button_rect.collidepoint(mouse_pos):
                    self.controller.back_to_menu()
                    self.ui_manager.reset_score()
                elif self.save_score_button_rect.collidepoint(mouse_pos) and not self.save_score_entered:
                    # Start high score entry process
                    self.controller.states['highscore_entry'] = HighScoreEntry(self.controller, self.score)
                    self.controller.current_state = self.controller.states['highscore_entry']
                    self.save_score_entered = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.controller.back_to_menu()
                self.ui_manager.reset_score()

    def update(self, dt):
        pass

    def draw(self, screen):
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(DARK_GRAY)

        # Use the local TITLE_FONT and BUTTON_FONT defined on this state
        draw_text("GAME OVER", self.TITLE_FONT, RED, screen, WIDTH // 2, 200)
        draw_text(f"Your Score: {self.score}", self.BUTTON_FONT, WHITE, screen, WIDTH // 2, 300)

        score_text = f"Score: {self.ui_manager.get_score()}"
        draw_text(score_text, self.BUTTON_FONT, WHITE, screen, 375, 475, center_align=False)

        mouse_pos = self.get_mouse_pos()
        color = HIGHLIGHT_COLOR if self.retry_button_rect.collidepoint(mouse_pos) else WHITE
        self.retry_button_rect = draw_text("Try Again", self.ui_manager.BUTTON_FONT, color, screen, WIDTH // 2, HEIGHT // 2 + 75)

        color = HIGHLIGHT_COLOR if self.menu_button_rect.collidepoint(mouse_pos) else WHITE
        self.menu_button_rect = draw_text("Main Menu", self.ui_manager.BUTTON_FONT, color, screen, WIDTH // 2, HEIGHT // 2 + 200)

        color = HIGHLIGHT_COLOR if self.save_score_button_rect.collidepoint(mouse_pos) else WHITE
        self.save_score_button_rect = draw_text("Save Score", self.ui_manager.BUTTON_FONT, color, screen, WIDTH // 2, HEIGHT // 2 + 325)

        hint_text = "Increasing my score fills me with determination"
        hint_img_path = f"{ASSET_BASE_PATH}/tip_icon.png"

        try:
            hint_image = load_image(hint_img_path, (74, 74))
            img_x = WIDTH // 2 - 342
            img_y = HEIGHT // 2 + 400  # Move lower
            screen.blit(hint_image, (img_x, img_y))
            text_x = img_x + 74 + 10
            text_y = img_y + 32
            draw_text(hint_text, self.CREDITS_FONT, WHITE, screen, text_x, text_y, center_align=False)
        except Exception:
            draw_text(hint_text, self.CREDITS_FONT, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 400)

class YouWin(GameState):
    def __init__(self, controller, score):
        super().__init__(controller)
        self.ui_manager = UIManager()
        self.score = score
        self.background = load_image("you_win_bg.png", (WIDTH, HEIGHT))
        self.menu_button_rect = pygame.Rect(0, 0, 1, 1)
        self.save_score_button_rect = pygame.Rect(0, 0, 1, 1)
        # Provide a local TITLE_FONT to avoid relying on UIManager implementation
        self.TITLE_FONT = pygame.font.Font(None, 100)
        self.BUTTON_FONT = pygame.font.Font(None, 60)
        self.CREDITS_FONT = pygame.font.Font(None, 40)
        self.save_score_entered = False

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.controller.quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = self.get_mouse_pos()
                if self.menu_button_rect.collidepoint(mouse_pos):
                    self.controller.back_to_menu()
                    self.ui_manager.reset_score()
                elif self.save_score_button_rect.collidepoint(mouse_pos) and not self.save_score_entered:
                    self.controller.states['highscore_entry'] = HighScoreEntry(self.controller, self.score)
                    self.controller.current_state = self.controller.states['highscore_entry']
                    self.save_score_entered = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.controller.back_to_menu()
    def draw(self, screen):
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(DARK_GRAY)

        # Use local TITLE_FONT and BUTTON_FONT instead of assuming UIManager owns them
        draw_text("YOU WIN!", self.TITLE_FONT, YELLOW, screen, WIDTH // 2, 200)
        draw_text(f"Your Score: {self.score}", self.BUTTON_FONT, WHITE, screen, WIDTH // 2, 300)

        score_text = f"Score: {self.ui_manager.get_score()}"
        draw_text(score_text, self.BUTTON_FONT, WHITE, screen, 375, 475, center_align=False)

        mouse_pos = self.get_mouse_pos()
        color = HIGHLIGHT_COLOR if self.menu_button_rect.collidepoint(mouse_pos) else WHITE
        self.menu_button_rect = draw_text("Main Menu", self.ui_manager.BUTTON_FONT, color, screen, WIDTH // 2, HEIGHT // 2 + 200)

        color = HIGHLIGHT_COLOR if self.save_score_button_rect.collidepoint(mouse_pos) else WHITE
        self.save_score_button_rect = draw_text("Save Score", self.ui_manager.BUTTON_FONT, color, screen, WIDTH // 2, HEIGHT // 2 + 325)

        hint_text = "Winning the game fills me with determination"
        hint_img_path = f"{ASSET_BASE_PATH}/tip_icon.png"

        try:
            hint_image = load_image(hint_img_path, (74, 74))
            img_x = WIDTH // 2 - 342
            img_y = HEIGHT // 2 + 400  # Move lower
            screen.blit(hint_image, (img_x, img_y))
            text_x = img_x + 74 + 10
            text_y = img_y + 32
            draw_text(hint_text, self.CREDITS_FONT, WHITE, screen, text_x, text_y, center_align=False)

            # Draw congratulations text below the hint
            congratulations_text = "CONGRATULATIONS!! Murat Can will treat you to any coffee you want."
            draw_text(congratulations_text, self.CREDITS_FONT, YELLOW, screen, WIDTH // 2, img_y + 100, center_align=True)
        except Exception:
            # Fallback if image loading fails
            draw_text(hint_text, self.CREDITS_FONT, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 400)
            draw_text(congratulations_text, self.CREDITS_FONT, YELLOW, screen, WIDTH // 2, HEIGHT // 2 + 500, center_align=True)




# SaveLoadMenu ve slot sistemi kaldırıldı. Yüksek skor sistemi için yeni ekran eklenecek.


# ============================================================================
# STATE REGISTRY for Open/Closed Principle
# ============================================================================
# To add a new state, simply register it here. Controller can auto-discover.
STATE_REGISTRY = {
    'main_menu': MainMenu,
    'credits': Credits,
    'pause': PauseMenu,
    'options': OptionsMenu,
    'game_over': GameOver,
    'you_win': YouWin,
    'highscore_entry': HighScoreEntry,
    # 'playing' is special (created on-demand with music flag)
}
