"""audio.py — звук: фоновая музыка, win/fall, процедурные SFX."""
import pygame
import os
import math
import random
import struct

SAMPLE_RATE      = 22050
SOUNDS_DIR       = "sounds"           # фоновая музыка (loop, тихо)
SOUNDS_EVENT_DIR = "sounds_event"     # события win/fall
MUSIC_VOLUME     = 0.85
WIN_FILE_NAME    = "win.mp3"
FALL_FILE_NAME   = "fall.mp3"
REBELS_FILE_NAME = "rebels.mp3" 
AUDIO_EXTS       = (".mp3", ".ogg", ".wav", ".flac", ".opus")


# ==================== WAV-ГЕНЕРАЦИЯ ====================
def _wav_from_samples(samples, sample_rate=SAMPLE_RATE):
    pcm = bytearray()
    for v in samples:
        v = max(-1.0, min(1.0, v))
        pcm += struct.pack("<h", int(v * 32767))
    header = b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVE"
    header += b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, sample_rate,
                                     sample_rate * 2, 2, 16)
    header += b"data" + struct.pack("<I", len(pcm))
    return bytes(header) + bytes(pcm)


def _sound_from_samples(samples, sample_rate=SAMPLE_RATE):
    if not pygame.mixer.get_init():
        return None
    try:
        return pygame.mixer.Sound(buffer=_wav_from_samples(samples, sample_rate))
    except Exception:
        return None


# ==================== ПРОЦЕДУРНЫЕ ЭФФЕКТЫ ====================
def gen_step_sound():
    n = int(SAMPLE_RATE * 0.05)
    return _sound_from_samples([random.uniform(-0.3, 0.3) *
                                math.exp(-(i/SAMPLE_RATE) * 60)
                                for i in range(n)])


def gen_pickup_sound():
    n = int(SAMPLE_RATE * 0.25)
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        f = 660 + 330 * min(t / 0.1, 1.0)
        out.append(math.sin(2 * math.pi * f * t) * math.exp(-t * 6) * 0.5)
    return _sound_from_samples(out)


def gen_blaster_sound():
    n = int(SAMPLE_RATE * 0.18)
    out, phase = [], 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        f = 1200 * math.exp(-t * 12) + 120
        phase += 2 * math.pi * f / SAMPLE_RATE
        env = math.exp(-t * 10)
        noise = random.uniform(-0.1, 0.1) * env
        out.append((math.sin(phase) * 0.6 + noise) * env)
    return _sound_from_samples(out)


def gen_saber_swing_sound():
    n = int(SAMPLE_RATE * 0.4)
    out, phase = [], 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        f = 180 + 60 * math.sin(2 * math.pi * 8 * t) + 80 * math.sin(2 * math.pi * 3 * t)
        phase += 2 * math.pi * f / SAMPLE_RATE
        env = math.sin(math.pi * t / 0.4)
        saw = 2 * ((phase / (2 * math.pi)) % 1.0) - 1
        out.append((math.sin(phase) * 0.5 + saw * 0.3) * env * 0.6)
    return _sound_from_samples(out)


def gen_vader_breath_sound(duration=0.8):
    n = int(SAMPLE_RATE * duration)
    out, prev = [], 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        prev = prev * 0.92 + random.uniform(-1, 1) * 0.08
        out.append(prev * math.sin(math.pi * t / duration) ** 2 * 0.5)
    return _sound_from_samples(out)


def gen_vader_laugh_sound():
    out = []
    for base in (110, 98, 88):
        dur = 0.22
        n = int(SAMPLE_RATE * dur)
        for i in range(n):
            t = i / SAMPLE_RATE
            f = base * (1.0 - 0.3 * t / dur)
            mod = 1 + 0.15 * math.sin(2 * math.pi * 25 * t)
            phase = 2 * math.pi * f * t
            val = (math.sin(phase) * 0.5 +
                   math.sin(phase * 2) * 0.25 +
                   math.sin(phase * 3) * 0.15) * mod
            env = math.sin(math.pi * i / n) ** 1.5
            out.append((val + random.uniform(-0.05, 0.05)) * env * 0.6)
        out.extend([0.0] * int(SAMPLE_RATE * 0.05))
    return _sound_from_samples(out)


def gen_win_fanfare():
    out = []
    for f in (523.25, 659.25, 783.99, 1046.50):
        n = int(SAMPLE_RATE * 0.12)
        for j in range(n):
            env = math.sin(math.pi * j / n)
            out.append(math.sin(2 * math.pi * f * j / SAMPLE_RATE) * env * 0.35)
    n = int(SAMPLE_RATE * 0.9)
    for j in range(n):
        t = j / SAMPLE_RATE
        env = math.exp(-t * 2.5)
        val = sum(math.sin(2 * math.pi * f * t)
                  for f in (523.25, 659.25, 783.99, 1046.50)) / 4
        out.append(val * env * 0.5)
    return _sound_from_samples(out)


def gen_fall_sting():
    n = int(SAMPLE_RATE * 0.5)
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        f = 200 * math.exp(-t * 3) + 40
        out.append(math.sin(2 * math.pi * f * t) * math.exp(-t * 2) * 0.6)
    return _sound_from_samples(out)


def gen_ambient_loop(duration=12.0):
    n = int(SAMPLE_RATE * duration)
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        drone = (math.sin(2 * math.pi * 55 * t) * 0.08 +
                 math.sin(2 * math.pi * 82.5 * t) * 0.05)
        drone *= 0.6 + 0.4 * math.sin(2 * math.pi * 0.1 * t)
        out.append(drone)
    fade = int(SAMPLE_RATE * 0.5)
    for i in range(fade):
        k = i / fade
        out[i] *= k
        out[-i - 1] *= k
    return _sound_from_samples(out)


# ==================== МЕНЕДЖЕР ====================
def _list_audio_files(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(os.path.join(folder, f) for f in os.listdir(folder)
                  if f.lower().endswith(AUDIO_EXTS))


class SoundManager:
    def __init__(self):
        self.enabled = pygame.mixer.get_init() is not None
        self.music_channel = None
        self.current_music_idx = 0
        self.music_playlist = []
        self.proc_ambient = None
        self.event_win = None
        self.event_fall = None
        self.event_rebels = None

        if not self.enabled:
            self.step = self.pickup = self.blaster = None
            self.swing = self.breath = self.laugh = None
            return

        print("🔊 Инициализация звуков...")
        self.step    = gen_step_sound()
        self.pickup  = gen_pickup_sound()
        self.blaster = gen_blaster_sound()
        self.swing   = gen_saber_swing_sound()
        self.breath  = gen_vader_breath_sound()
        self.laugh   = gen_vader_laugh_sound()
        for snd, vol in [(self.step, 0.10), (self.pickup, 0.35),
                         (self.blaster, 0.30), (self.swing, 0.45),
                         (self.breath, 0.35), (self.laugh, 0.55)]:
            if snd:
                snd.set_volume(vol)

        self._load_event_sounds()
        self._setup_background_music()

        try:
            pygame.mixer.set_num_channels(16)
            self.music_channel = pygame.mixer.Channel(0)
            self.music_channel.set_volume(MUSIC_VOLUME)
        except Exception:
            self.music_channel = None

        # Если музыка не запустилась до создания канала — запустим сейчас
        if self.music_playlist and self.music_channel:
            self._play_next_music()
        elif self.proc_ambient and self.music_channel:
            self.music_channel.play(self.proc_ambient, loops=-1)

        print("✅ Звуки готовы.")

    def _load_event_sounds(self):
        win_path  = os.path.join(SOUNDS_EVENT_DIR, WIN_FILE_NAME)
        fall_path = os.path.join(SOUNDS_EVENT_DIR, FALL_FILE_NAME)

        if os.path.isfile(win_path):
            try:
                self.event_win = pygame.mixer.Sound(win_path)
                self.event_win.set_volume(0.8)
                print(f"🎵 win: {win_path}")
            except Exception as e:
                print(f"⚠️  win.mp3: {e}")
        else:
            print(f"ℹ️  Нет {win_path} — процедурные фанфары.")
            self.event_win = gen_win_fanfare()
            if self.event_win: self.event_win.set_volume(0.6)

        if os.path.isfile(fall_path):
            try:
                self.event_fall = pygame.mixer.Sound(fall_path)
                self.event_fall.set_volume(0.8)
                print(f"🎵 fall: {fall_path}")
            except Exception as e:
                print(f"⚠️  fall.mp3: {e}")
        else:
            print(f"ℹ️  Нет {fall_path} — процедурный fall-стинг.")
            self.event_fall = gen_fall_sting()
            if self.event_fall: self.event_fall.set_volume(0.6)

        # rebels.mp3 — когда все повстанцы уничтожены
        self.event_rebels = None
        rebels_path = os.path.join(SOUNDS_EVENT_DIR, REBELS_FILE_NAME)
        if os.path.isfile(rebels_path):
            try:
                self.event_rebels = pygame.mixer.Sound(rebels_path)
                self.event_rebels.set_volume(0.8)
                print(f"🎵 rebels: {rebels_path}")
            except Exception as e:
                print(f"⚠️  rebels.mp3: {e}")
        else:
            print(f"ℹ️  Нет {rebels_path} — звук будет пропущен.")

    def _setup_background_music(self):
        self.music_playlist = _list_audio_files(SOUNDS_DIR)
        if self.music_playlist:
            print(f"🎶 Фоновая музыка: {len(self.music_playlist)} файл(ов)")
            for p in self.music_playlist:
                print(f"   • {os.path.basename(p)}")
        else:
            print(f"ℹ️  '{SOUNDS_DIR}/' пуста — процедурный эмбиент.")
            self.proc_ambient = gen_ambient_loop(12.0)

    def _play_next_music(self):
        if not self.music_playlist or not self.music_channel:
            return
        path = self.music_playlist[self.current_music_idx % len(self.music_playlist)]
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(MUSIC_VOLUME)
            self.music_channel.play(snd)
            print(f"▶️  {os.path.basename(path)}")
        except Exception as e:
            print(f"⚠️  {path}: {e}")
        self.current_music_idx += 1

    def update_music(self):
        if not self.music_playlist or not self.music_channel:
            return
        if not self.music_channel.get_busy():
            self._play_next_music()

    def play(self, name):
        if not self.enabled:
            return
        snd = getattr(self, name, None)
        if snd is not None:
            try: snd.play()
            except Exception: pass

    def stop_music(self):
        if self.music_channel:
            self.music_channel.stop()

    def play_win(self):
        self.stop_music()
        if self.event_win:
            try: self.event_win.play()
            except Exception: pass

    def play_fall(self):
        """Проигрывает fall.mp3 СРАЗУ + меч/дыхание/смех параллельно."""
        self.stop_music()

        # fall.mp3 — сразу и гарантированно
        if self.event_fall:
            try:
                self.event_fall.play()
            except Exception:
                pass

        # Меч — сразу
        if self.swing:
            try:
                self.swing.play()
            except Exception:
                pass

        # Дыхание и смех — с задержкой через отдельный поток-таймер
        # (pygame.time.set_timer здесь ненадёжен, поэтому используем
        #  threading.Timer — он не зависит от главного цикла игры)
        import threading
        if self.breath:
            threading.Timer(0.4, self._safe_play, args=(self.breath,)).start()
        if self.laugh:
            threading.Timer(0.9, self._safe_play, args=(self.laugh,)).start()

    def play_rebels(self):
        """Проигрывает rebels.mp3, если он загружен."""
        if self.event_rebels:
            try:
                self.event_rebels.play()
            except Exception:
                pass

    def _safe_play(self, snd):
        try:
            snd.play()
        except Exception:
            pass

    def stop_all(self):
        """Останавливает ВСЁ: музыку, win/fall, меч, смех."""
        if self.music_channel:
            try:
                self.music_channel.stop()
            except Exception:
                pass

        # Отложенные таймеры больше не нужны — гасим на всякий случай
        for evt in (pygame.USEREVENT + 1,
                    pygame.USEREVENT + 2,
                    pygame.USEREVENT + 3):
            try:
                pygame.time.set_timer(evt, 0)
            except Exception:
                pass

        # Явно остановить все event/SFX-звуки
        for snd in (self.event_win, self.event_fall, self.event_rebels,
                    self.swing, self.breath, self.laugh):
            if snd is not None:
                try:
                    snd.stop()
                except Exception:
                    pass

    def resume_music(self):
        if self.music_playlist:
            if self.music_channel and not self.music_channel.get_busy():
                self._play_next_music()
        elif self.proc_ambient and self.music_channel:
            if not self.music_channel.get_busy():
                self.music_channel.play(self.proc_ambient, loops=-1)

