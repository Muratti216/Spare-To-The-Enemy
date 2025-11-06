# spear_game/utils.py

import sys
import os
import pygame
from .settings import ASSET_BASE_PATH # Ayarlardan yolu alıyoruz

def resource_path(relative_path):
    """PyInstaller ile uyumlu dosya yolu döndürür."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

_image_cache = {}

def load_image(filename, size=None):
    """Optimize edilmiş görsel yükleme fonksiyonu."""
    from .settings import ASSET_BASE_PATH
    import traceback
    
    # Önbellek anahtarını oluştur
    cache_key = f"{filename}_{size if size else 'original'}"
    
    # Önbellekte varsa direkt dön
    if cache_key in _image_cache:
        return _image_cache[cache_key]
    
    # Yoksa yükle ve önbelleğe al
    full_path = resource_path(os.path.join(ASSET_BASE_PATH, filename))
    try:
        image = pygame.image.load(full_path).convert_alpha()  # convert_alpha() eklendi
        if size:
            image = pygame.transform.scale(image, size)
        _image_cache[cache_key] = image
        return image
    except Exception as e:
        print(f"[ASSET ERROR] Görsel yüklenemedi: {full_path}\nHata: {e}")
        traceback.print_exc()
        return None

def draw_text(text, font, color, surface, x, y, center_align=True, letter_spacing=0):
    """Metni çiz ve letter spacing uygula"""
    if not text:  # Boş metin kontrolü
        return pygame.Rect(x, y, 0, 0)

    # Font yüksekliği ve toplam genişliği hesapla
    font_height = font.get_height()
    total_width = 0
    char_widths = []

    # Her karakter için genişliği hesapla
    for char in text:
        char_width = font.size(char)[0]
        char_widths.append(char_width)
        total_width += char_width

    # Letter spacing ekle
    if len(text) > 1:
        total_width += letter_spacing * (len(text) - 1)

    # Metin surface'ini oluştur
    text_surface = pygame.Surface((total_width, font_height), pygame.SRCALPHA)
    
    # Her karakteri ayrı ayrı render et
    x_offset = 0
    for i, char in enumerate(text):
        char_surface = font.render(char, True, color)
        text_surface.blit(char_surface, (x_offset, 0))
        x_offset += char_widths[i] + letter_spacing

    # Pozisyonlamayı ayarla
    text_rect = text_surface.get_rect()
    if center_align:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)

    # Surface'e çiz
    surface.blit(text_surface, text_rect)
    return text_rect