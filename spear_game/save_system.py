# In save_system.py


import json
import os
from datetime import datetime




# Yüksek skorlar dosya yolu
HIGH_SCORE_FILE = os.path.join(os.path.dirname(__file__), '..', 'high_scores.json')

def load_high_scores():
    """Yüksek skorları dosyadan yükler."""
    if not os.path.exists(HIGH_SCORE_FILE):
        return {}
    try:
        with open(HIGH_SCORE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_high_scores(scores):
    """Yüksek skorları dosyaya kaydeder."""
    with open(HIGH_SCORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, indent=4, ensure_ascii=False)

def add_or_update_high_score(player_name, score):
    """Oyuncunun skorunu ekler veya günceller. Daha yüksekse üzerine yazar."""
    scores = load_high_scores()
    prev_score = scores.get(player_name, 0)
    if score > prev_score:
        scores[player_name] = score
        save_high_scores(scores)
        return True
    return False

def get_sorted_high_scores(limit=10):
    """Yüksek skorları azalan şekilde sıralı döndürür."""
    scores = load_high_scores()
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_scores[:limit]


# Artık slot kaydı yerine yüksek skor sistemi kullanılacak.
# Eski slot fonksiyonları kaldırıldı.

def save_player_score(player_name, score):
    """Oyuncu öldüğünde veya kazandığında skorunu kaydeder."""
    updated = add_or_update_high_score(player_name, score)
    if updated:
        print(f"{player_name} için yeni yüksek skor kaydedildi: {score}")
    else:
        print(f"{player_name} için skor güncellenmedi (daha düşük veya eşit).")
    return updated


# Slot silme fonksiyonu kaldırıldı. Yüksek skorlar için silme fonksiyonu eklenebilir.
def delete_player_score(player_name):
    """Belirtilen oyuncunun skorunu siler."""
    scores = load_high_scores()
    if player_name in scores:
        del scores[player_name]
        save_high_scores(scores)
        print(f"{player_name} skoru silindi.")
        return True
    print(f"{player_name} için skor bulunamadı.")
    return False


# Oyun yükleme fonksiyonu kaldırıldı. Artık sadece yüksek skorlar yönetiliyor.