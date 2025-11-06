# In audio_manager.py

import pygame
import json

CONFIG_FILE = 'config.json'

class AudioManager:
    _instance = None
    music_tracks = {}
    sfx_sounds = {}
    
    def __new__(cls):
        if cls._instance is None:
            try:
                cls._instance = super().__new__(cls)
                pygame.mixer.pre_init(44100, -16, 2, 512)
                pygame.mixer.init()

                # Varsayılan değerler
                cls._instance.music_volume = 0.5
                cls._instance.sfx_volume = 0.7
                cls._instance.is_muted = False
                cls._instance.current_music = None
                cls._instance.last_music = None
                cls._instance.load_settings() # Kayıtlı ayarları yüklemeyi dene

                # Ses dosyalarını güvenli şekilde yükle
                cls._instance.music_tracks = {
                    'menu': 'music/menu-music.wav',
                    'playing': 'music/playing-music.mp3'
                }
                cls._instance.sfx_sounds = {}
                sfx_files = {
                    'spear_throw': 'assets/sfx/spear_throw.wav',
                    'enemy_hit': 'assets/sfx/enemy_hit.wav',
                    'collect_money': 'assets/sfx/collect.wav'
                }
                for key, path in sfx_files.items():
                    try:
                        cls._instance.sfx_sounds[key] = pygame.mixer.Sound(path)
                    except Exception as e:
                        print(f"[AUDIO WARNING] SFX dosyası yüklenemedi: {path} ({e})")
                        cls._instance.sfx_sounds[key] = None
                cls._instance.apply_all_volumes()
            except Exception as e:
                print(f"[AUDIO ERROR] AudioManager başlatılamadı: {e}")
                # En azından boş değerlerle instance dön
                cls._instance = super().__new__(cls)
                cls._instance.music_tracks = {}
                cls._instance.sfx_sounds = {}
                cls._instance.music_volume = 0.5
                cls._instance.sfx_volume = 0.7
                cls._instance.is_muted = False
        return cls._instance

    def check_audio_files(self):
        """Tüm ses dosyalarının yüklenip yüklenmediğini kontrol eder."""
        missing = []
        for key, path in self.music_tracks.items():
            try:
                with open(path, 'rb'):
                    pass
            except Exception:
                missing.append(path)
        for key, sound in self.sfx_sounds.items():
            if sound is None:
                missing.append(f"SFX: {key}")
        if missing:
            print("[AUDIO WARNING] Eksik veya yüklenemeyen ses dosyaları:")
            for m in missing:
                print("  -", m)
        else:
            print("Tüm ses dosyaları başarıyla yüklendi.")
        return self

    def load_settings(self):
        """Kayıtlı ses ayarlarını config.json dosyasından yükler."""
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.music_volume = float(config.get('music_volume', 0.5))
                self.sfx_volume = float(config.get('sfx_volume', 0.7))
                self.is_muted = bool(config.get('is_muted', False))
                print("Ses ayarları yüklendi.")
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            print("Kayıtlı ses ayarı bulunamadı. Varsayılanlar kullanılıyor.")
    
    def save_settings(self):
        """Mevcut ses ayarlarını dosyaya kaydeder."""
        config = {
            'music_volume': self.music_volume,
            'sfx_volume': self.sfx_volume,
            'is_muted': self.is_muted
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print("Ses ayarları kaydedildi.")

    def set_music_volume(self, volume):
        """Müzik ses seviyesini 0.0 ile 1.0 arasında ayarlar."""
        self.music_volume = max(0.0, min(1.0, volume))
        if not self.is_muted:
            pygame.mixer.music.set_volume(self.music_volume)

    def set_sfx_volume(self, volume):
        """Tüm ses efektlerinin ses seviyesini ayarlar."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        if not self.is_muted:
            for sound in self.sfx_sounds.values():
                if sound is not None:
                    sound.set_volume(self.sfx_volume)

    def apply_all_volumes(self):
        """Mevcut ses ayarlarını tüm kanallara uygular."""
        if self.is_muted:
            pygame.mixer.music.set_volume(0)
            for sound in self.sfx_sounds.values():
                if sound is not None:
                    sound.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.music_volume)
            for sound in self.sfx_sounds.values():
                if sound is not None:
                    sound.set_volume(self.sfx_volume)

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.apply_all_volumes()

    def play_music(self, track_key, loops=-1, fade_ms=1000):
        """Belirtilen müziği yavaşça başlatarak çalar."""
        # Aynı müziği tekrar başlatmamak için kontrol
        if track_key == self.current_music:
            return
            
        if self.is_muted:
            return
            
        track_path = self.music_tracks.get(track_key)
        try:
            if track_path:
                # Önceki müziği durdur
                self.stop_music(fade_ms)
                
                # Yeni müziği yükle ve çal
                pygame.mixer.music.unload()
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
                
                # Müzik durumunu güncelle
                self.last_music = self.current_music
                self.current_music = track_key
        except Exception as e:
            print(f"[AUDIO WARNING] Müzik dosyası yüklenemedi: {track_path} ({e})")
    def stop_music(self, fade_ms=1000):
        """Müziği yavaşça durdurur."""
        try:
            pygame.mixer.music.fadeout(fade_ms)
            self.current_music = None
        except Exception as e:
            print(f"[AUDIO WARNING] Müzik durdurulamadı: {e}")

    def play_sfx(self, sfx_key, fallback_key=None, ignore_errors=False):
        """Belirtilen ses efektini çalar.
        
        Args:
            sfx_key: Çalınacak ses efektinin anahtarı
            fallback_key: Ana ses bulunamazsa çalınacak yedek ses
            ignore_errors: True ise hataları görmezden gel
        """
        if self.is_muted:
            return

        def try_play_sound(key):
            sound = self.sfx_sounds.get(key)
            if sound:
                try:
                    sound.set_volume(self.sfx_volume)
                    sound.play()
                    return True
                except Exception as e:
                    if not ignore_errors:
                        print(f"[AUDIO WARNING] SFX oynatılamadı: {key} ({e})")
            return False

        # Ana sesi çalmayı dene
        if try_play_sound(sfx_key):
            return

        # Fallback sesi çalmayı dene
        if fallback_key and try_play_sound(fallback_key):
            return
        
        # Her iki ses de çalınamazsa ve hatalar görmezden gelinmiyorsa uyar
        if not ignore_errors:
            print(f"[AUDIO WARNING] SFX bulunamadı veya yüklenemedi: {sfx_key}"
                  f"{f' (fallback: {fallback_key})' if fallback_key else ''}")