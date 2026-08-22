"""
Module Xử lý Âm thanh & Quản lý Giọng đọc Tối ưu (Voice Engine 6.0 Real-time Streaming)
Tối ưu hóa:
- Token-to-Speech Real-time Streaming Pipeline: Phát âm thanh ngay trên RAM khi Gemini đang sinh từng từ.
- Xử lý âm thanh 100% trên bộ nhớ RAM (In-Memory Buffer, Zero Disk I/O).
- Hỗ trợ đa động cơ: Edge-TTS (siêu nhanh <300ms), Kokoro-TTS (AI Tiếng Việt), gTTS.
- Luồng phát âm thanh Double-Buffering Queue liền mạch không khoảng lặng.
"""

import os
import re
import sys
import io
import time
import queue
import threading
import asyncio
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

# Import bộ phiên âm ngầm chuyên dụng
from core.phonetics import to_speech_phonetics

load_dotenv()

# Danh mục các Giọng đọc AI Tiếng Việt Kokoro
KOKORO_VOICES: Dict[str, str] = {
    "diem_trinh": "Nữ - Truyền cảm, ấm áp, trang trọng (Tiêu chuẩn Hướng dẫn viên)",
    "mai_linh": "Nữ - Trẻ trung, trong trẻo, tự nhiên (Mặc định)",
    "thanh_dat": "Nam - Phóng khoáng, tự tin, rõ ràng (Giọng Nam tiêu chuẩn)",
}

# Cấu hình từ .env
TTS_ENGINE = os.getenv("TTS_ENGINE", "edge-tts").lower().strip()
CURRENT_VOICE = os.getenv("KOKORO_VOICE", "mai_linh").lower().strip()
KOKORO_DEVICE = os.getenv("KOKORO_DEVICE", "cpu").lower().strip()
VOICE_SPEED = float(os.getenv("VOICE_SPEED", "1.05"))
EDGE_VOICE = os.getenv("VOICE_NAME", "vi-VN-HoaiMyNeural")

# Kiểm tra Kokoro Vietnamese
_KOKORO_AVAILABLE = False
_kokoro_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Kokoro-Vietnamese-src", "Kokoro-Vietnamese-main", "src"))
if os.path.exists(_kokoro_src) and _kokoro_src not in sys.path:
    sys.path.insert(0, _kokoro_src)

try:
    from kokoro_vietnamese.onnx_cli import KokoroVietnameseONNX
    import soundfile as sf
    _KOKORO_AVAILABLE = True
except ImportError:
    _KOKORO_AVAILABLE = False

# Kiểm tra edge-tts
try:
    import edge_tts
    _EDGE_TTS_AVAILABLE = True
except ImportError:
    _EDGE_TTS_AVAILABLE = False

# Kiểm tra gTTS
try:
    from gtts import gTTS
    _GTTS_AVAILABLE = True
except ImportError:
    _GTTS_AVAILABLE = False

# Kiểm tra pygame
try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False

# Bộ nhớ đệm lưu trữ các Instance Kokoro theo từng giọng (Singleton Caching)
_kokoro_instances: Dict[str, any] = {}
_audio_lock = threading.Lock()
_active_pipelines: List[any] = []
_is_speaking_active: bool = False


def _ensure_mixer_init():
    """Khởi tạo Pygame Mixer với bộ đệm nhỏ (1024) để giảm độ trễ tối đa (<25ms)."""
    if _PYGAME_AVAILABLE and not pygame.mixer.get_init():
        try:
            pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=1024)
        except Exception:
            try:
                pygame.mixer.init()
            except Exception:
                pass


def is_speaking() -> bool:
    """Kiểm tra xem Robot có đang phát âm thanh ra loa hay đang tổng hợp hay không."""
    global _is_speaking_active
    if _is_speaking_active:
        return True
    for p in list(_active_pipelines):
        if p.is_active():
            return True
    if _PYGAME_AVAILABLE and pygame.mixer.get_init():
        return pygame.mixer.get_busy()
    return False


def wait_until_speaking_done(timeout: float = 30.0) -> None:
    """Chờ cho đến khi Robot nói xong hoàn toàn và loa tắt hẳn trước khi bật Micro."""
    start_time = time.time()
    time.sleep(0.08)
    for p in list(_active_pipelines):
        p.wait_until_done(timeout=max(1.0, timeout - (time.time() - start_time)))

    while is_speaking():
        if time.time() - start_time > timeout:
            break
        time.sleep(0.06)
    # Khoảng nghỉ đệm 0.25s để âm thanh phòng tiêu tán hoàn toàn, tránh micro thu lại tiếng loa
    time.sleep(0.25)


def get_available_voices() -> Dict[str, str]:
    """Trả về danh sách giọng đọc Kokoro khả dụng cùng mô tả."""
    return KOKORO_VOICES.copy()


def get_current_voice() -> str:
    """Trả về tên giọng đọc hiện tại đang được áp dụng."""
    global CURRENT_VOICE
    return CURRENT_VOICE


def set_voice(voice_name: str) -> bool:
    """Thay đổi giọng đọc của Robot trong Runtime."""
    global CURRENT_VOICE
    clean_name = voice_name.lower().strip()
    if clean_name in KOKORO_VOICES:
        CURRENT_VOICE = clean_name
        print(f"[Voice Engine] Đã chuyển sang giọng đọc: '{CURRENT_VOICE}' ({KOKORO_VOICES[CURRENT_VOICE]}).")
        return True
    else:
        print(f"[Voice Engine] Không tìm thấy giọng '{voice_name}'. Các giọng khả dụng: {list(KOKORO_VOICES.keys())}")
        return False


def _trim_silence_numpy(audio: "np.ndarray", threshold: float = 0.008, pad_ms: int = 40, sr: int = 24000) -> "np.ndarray":
    """Cắt tỉa khoảng lặng thừa ở đầu và cuối mảng âm thanh để nối câu liền mạch."""
    try:
        import numpy as np
        pad_samples = int(sr * (pad_ms / 1000.0))
        mask = np.abs(audio) > threshold
        if not np.any(mask):
            return audio
        start = max(0, int(np.argmax(mask)) - pad_samples)
        end = min(len(audio), len(audio) - int(np.argmax(mask[::-1])) + pad_samples)
        return audio[start:end]
    except Exception:
        return audio


def _get_kokoro_model(voice_name: str = None):
    """Lấy hoặc khởi tạo instance Kokoro ONNX cho giọng đọc chỉ định (Singleton Caching)."""
    global _kokoro_instances
    if not _KOKORO_AVAILABLE:
        return None

    target_voice = (voice_name or CURRENT_VOICE).lower().strip()
    if target_voice not in KOKORO_VOICES:
        target_voice = "mai_linh"

    if target_voice in _kokoro_instances:
        return _kokoro_instances[target_voice]

    try:
        instance = KokoroVietnameseONNX(
            voice=target_voice,
            device=KOKORO_DEVICE,
        )
        _kokoro_instances[target_voice] = instance
        return instance
    except Exception as e:
        print(f"[Kokoro TTS] Không thể nạp giọng '{target_voice}' ({e}) -> Fallback sang Edge-TTS.")
        return None


def warmup_voice_engine() -> None:
    """Tự động khởi động trước mixer và làm nóng kết nối ở luồng nền (Zero Startup Lag)."""
    def _warmup_worker():
        try:
            _ensure_mixer_init()
            if _KOKORO_AVAILABLE:
                _get_kokoro_model(CURRENT_VOICE)
        except Exception:
            pass

    t = threading.Thread(target=_warmup_worker, daemon=True)
    t.start()


# Khởi động làm nóng ngầm khi nạp module
warmup_voice_engine()


def play_chime(sound_file: str = "assets/sounds/chime.wav") -> None:
    """Phát âm thanh thông báo nhẹ trước khi robot trả lời."""
    if not _PYGAME_AVAILABLE or not os.path.exists(sound_file):
        return
    try:
        _ensure_mixer_init()
        sound = pygame.mixer.Sound(sound_file)
        sound.set_volume(0.25)
        sound.play()
    except Exception:
        pass


def _split_into_sentences(text: str) -> List[str]:
    """Chia văn bản thành các đoạn hợp lý để phát liên tục không bị ngắt vụn."""
    if not text:
        return []
    # Tách theo các dấu kết thúc câu [.!?\n]
    raw_sentences = re.split(r"(?<=[.!?\n])\s+", text.strip())
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    
    # Gộp các câu quá ngắn (< 35 ký tự) vào câu kế tiếp để tránh trễ mạng / ngắt ngứ
    merged: List[str] = []
    buf = ""
    for s in sentences:
        if buf:
            buf = f"{buf} {s}"
        else:
            buf = s
        if len(buf) >= 40 or s == sentences[-1]:
            merged.append(buf)
            buf = ""
    if buf:
        merged.append(buf)
    return merged if merged else [text.strip()]


# =============================================================================
# TẦNG TỔNG HỢP ÂM THANH TRỰC TIẾP TRÊN RAM (IN-MEMORY AUDIO SYNTHESIS)
# =============================================================================

def _synthesize_edge_tts_in_memory(text: str, voice: str = None, rate: str = "+8%") -> Optional["pygame.mixer.Sound"]:
    """Tổng hợp âm thanh bằng Edge-TTS nạp trực tiếp vào RAM (không ghi file ổ đĩa)."""
    if not _EDGE_TTS_AVAILABLE or not text.strip():
        return None
    try:
        v = voice or EDGE_VOICE
        comm = edge_tts.Communicate(text, v, rate=rate)
        
        async def _fetch_audio():
            bio = io.BytesIO()
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    bio.write(chunk["data"])
            bio.seek(0)
            return bio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        bio = loop.run_until_complete(_fetch_audio())
        if bio.getbuffer().nbytes > 0:
            _ensure_mixer_init()
            return pygame.mixer.Sound(bio)
    except Exception:
        pass
    return None


def _synthesize_kokoro_in_memory(text: str, voice: str = None, speed: float = 1.05) -> Optional["pygame.mixer.Sound"]:
    """Tổng hợp âm thanh bằng Kokoro ONNX nạp trực tiếp vào RAM với cắt tỉa khoảng lặng."""
    if not _KOKORO_AVAILABLE or not text.strip():
        return None
    try:
        model = _get_kokoro_model(voice or CURRENT_VOICE)
        if model is None:
            return None
        audio_array, _ = model.synthesize(text, speed=speed)
        if len(audio_array) > 0:
            # Cắt tỉa khoảng lặng thừa ở đầu và cuối để nối mượt mà sau dấu câu
            trimmed_audio = _trim_silence_numpy(audio_array, threshold=0.008, pad_ms=35, sr=24000)
            bio = io.BytesIO()
            sf.write(bio, trimmed_audio, 24000, format="WAV", subtype="PCM_16")
            bio.seek(0)
            _ensure_mixer_init()
            return pygame.mixer.Sound(bio)
    except Exception:
        pass
    return None


def _synthesize_gtts_in_memory(text: str) -> Optional["pygame.mixer.Sound"]:
    """Tổng hợp âm thanh bằng gTTS dự phòng nạp trực tiếp vào RAM."""
    if not _GTTS_AVAILABLE or not text.strip():
        return None
    try:
        tts = gTTS(text=text, lang="vi", slow=False)
        bio = io.BytesIO()
        tts.write_to_fp(bio)
        bio.seek(0)
        _ensure_mixer_init()
        return pygame.mixer.Sound(bio)
    except Exception:
        return None


def _synthesize_sentence_sound(
    sentence: str,
    engine: str = None,
    voice: str = None,
    speed: float = None,
) -> Optional["pygame.mixer.Sound"]:
    """
    Tổng hợp văn bản thành đối tượng Pygame Sound trên RAM:
    Ưu tiên 1: Edge-TTS Neural Voice (mượt mà, tự nhiên, không ngắt quãng)
    Ưu tiên 2: Kokoro ONNX
    Ưu tiên 3: gTTS
    """
    if not sentence or not sentence.strip():
        return None

    # Áp dụng chuẩn hóa ngữ âm ngầm
    phonetic_text = to_speech_phonetics(sentence)
    sel_engine = (engine or TTS_ENGINE or "edge-tts").lower().strip()
    target_voice = voice or CURRENT_VOICE
    actual_speed = speed or VOICE_SPEED

    sound = None

    # 1. Ưu tiên Edge-TTS nếu engine yêu cầu hoặc mặc định
    if _EDGE_TTS_AVAILABLE and sel_engine in ["edge-tts", "edge", "neural"]:
        edge_v = target_voice if "Neural" in target_voice else EDGE_VOICE
        rate_str = f"{int((actual_speed - 1.0) * 100):+d}%" if actual_speed != 1.0 else "+8%"
        sound = _synthesize_edge_tts_in_memory(phonetic_text, voice=edge_v, rate=rate_str)

    # 2. Thử Kokoro nếu được chỉ định
    if sound is None and sel_engine == "kokoro" and _KOKORO_AVAILABLE:
        sound = _synthesize_kokoro_in_memory(phonetic_text, voice=target_voice, speed=actual_speed)

    # 3. Fallback sang Edge-TTS
    if sound is None and _EDGE_TTS_AVAILABLE:
        edge_v = target_voice if "Neural" in target_voice else EDGE_VOICE
        rate_str = f"{int((actual_speed - 1.0) * 100):+d}%" if actual_speed != 1.0 else "+8%"
        sound = _synthesize_edge_tts_in_memory(phonetic_text, voice=edge_v, rate=rate_str)

    # 4. Fallback sang Kokoro
    if sound is None and _KOKORO_AVAILABLE:
        sound = _synthesize_kokoro_in_memory(phonetic_text, voice=target_voice, speed=actual_speed)

    # 5. Fallback sang gTTS
    if sound is None and _GTTS_AVAILABLE:
        sound = _synthesize_gtts_in_memory(phonetic_text)

    return sound


# =============================================================================
# PIPELINE PHÁT ÂM THANH THỜI GIAN THỰC (TOKEN-TO-SPEECH STREAMING PIPELINE)
# =============================================================================

class SpeechStreamPipeline:
    """
    Pipeline phát âm thanh theo thời gian thực (Token-to-Speech Streaming):
    - Nhận từng token từ Gemini stream qua feed_token().
    - Tự động nhận diện điểm ngắt câu [.!?\n] hợp lý để tổng hợp ngay.
    - Luồng Synthesizer tổng hợp trên RAM và đẩy vào _audio_queue.
    - Luồng Player phát âm thanh ra Loa liền mạch, triệt tiêu khoảng lặng sau dấu câu.
    """

    def __init__(self, voice: str = None, engine: str = None, speed: float = None):
        self.voice = voice or CURRENT_VOICE
        self.engine = (engine or TTS_ENGINE or "edge-tts").lower()
        self.speed = speed or VOICE_SPEED
        
        self._text_buffer = ""
        self._sentence_queue = queue.Queue()
        self._audio_queue = queue.Queue()
        self._first_chunk_sent = False
        
        self._stop_event = threading.Event()
        self._input_finished = threading.Event()
        self._is_playing_sound = False
        
        _ensure_mixer_init()
        
        # Khởi chạy luồng Synthesizer và Player nền
        self._synth_thread = threading.Thread(target=self._synthesizer_worker, daemon=True)
        self._player_thread = threading.Thread(target=self._player_worker, daemon=True)
        
        self._synth_thread.start()
        self._player_thread.start()
        
        with _audio_lock:
            _active_pipelines.append(self)

    def is_active(self) -> bool:
        """Kiểm tra xem pipeline còn đang tổng hợp hoặc phát âm thanh hay không."""
        if self._stop_event.is_set():
            return False
        if not self._input_finished.is_set():
            return True
        if not self._sentence_queue.empty() or not self._audio_queue.empty():
            return True
        if self._is_playing_sound:
            return True
        if self._synth_thread.is_alive() and not self._input_finished.is_set():
            return True
        return False

    def feed_token(self, token: str) -> None:
        """Nhận từng token từ luồng LLM stream."""
        if self._stop_event.is_set() or not token:
            return

        self._text_buffer += token

        if not self._first_chunk_sent:
            words = self._text_buffer.split()
            punct_match = re.search(r"([.!?,\n;:]+)\s+", self._text_buffer)
            if punct_match and len(words) >= 2:
                split_idx = punct_match.end()
                candidate = self._text_buffer[:split_idx].strip()
                self._text_buffer = self._text_buffer[split_idx:]
                self._first_chunk_sent = True
                self._sentence_queue.put(candidate)
                return
            elif len(words) >= 4:
                split_idx = self._text_buffer.find(words[2]) + len(words[2])
                candidate = self._text_buffer[:split_idx].strip()
                self._text_buffer = self._text_buffer[split_idx:].lstrip()
                self._first_chunk_sent = True
                self._sentence_queue.put(candidate)
                return

        match = re.search(r"([.!?\n]+)\s+", self._text_buffer)
        if match:
            split_idx = match.end()
            candidate = self._text_buffer[:split_idx].strip()
            self._text_buffer = self._text_buffer[split_idx:]
            if candidate:
                self._sentence_queue.put(candidate)

    def feed_sentence(self, sentence: str) -> None:
        if self._stop_event.is_set() or not sentence.strip():
            return
        self._sentence_queue.put(sentence.strip())

    def finish(self) -> None:
        if self._text_buffer.strip() and not self._stop_event.is_set():
            self._sentence_queue.put(self._text_buffer.strip())
            self._text_buffer = ""
        self._input_finished.set()

    def stop(self) -> None:
        self._stop_event.set()
        self._input_finished.set()
        if _PYGAME_AVAILABLE and pygame.mixer.get_init():
            try:
                pygame.mixer.stop()
            except Exception:
                pass
        while not self._sentence_queue.empty():
            try:
                self._sentence_queue.get_nowait()
                self._sentence_queue.task_done()
            except Exception:
                break
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
                self._audio_queue.task_done()
            except Exception:
                break

    def wait_until_done(self, timeout: float = 120.0) -> None:
        start_t = time.time()
        while self.is_active() and not self._stop_event.is_set():
            if time.time() - start_t > timeout:
                self.stop()
                break
            time.sleep(0.05)

    def _synthesizer_worker(self) -> None:
        while not self._stop_event.is_set():
            try:
                sentence = self._sentence_queue.get(timeout=0.05)
            except queue.Empty:
                if self._input_finished.is_set() and self._sentence_queue.empty():
                    self._audio_queue.put(None)
                    break
                continue

            if sentence is None:
                self._sentence_queue.task_done()
                self._audio_queue.put(None)
                break

            try:
                sound = _synthesize_sentence_sound(
                    sentence=sentence,
                    engine=self.engine,
                    voice=self.voice,
                    speed=self.speed,
                )
                if sound is not None and not self._stop_event.is_set():
                    self._audio_queue.put(sound)
            except Exception:
                pass
            finally:
                self._sentence_queue.task_done()

    def _player_worker(self) -> None:
        """Luồng phát âm thanh: lấy từng Sound trên RAM -> phát mượt mà, không khoảng lặng ngắt ngứ."""
        while not self._stop_event.is_set():
            try:
                sound = self._audio_queue.get(timeout=0.05)
            except queue.Empty:
                if self._input_finished.is_set() and self._sentence_queue.empty() and self._audio_queue.empty():
                    break
                continue

            if sound is None:
                self._audio_queue.task_done()
                break

            try:
                if _PYGAME_AVAILABLE and not self._stop_event.is_set():
                    _ensure_mixer_init()
                    self._is_playing_sound = True
                    channel = sound.play()
                    play_start = time.time()
                    sound_dur = sound.get_length() if hasattr(sound, "get_length") else 8.0
                    clock = pygame.time.Clock()
                    while channel and channel.get_busy() and not self._stop_event.is_set():
                        if time.time() - play_start > sound_dur + 0.4:
                            break
                        clock.tick(100)
            except Exception:
                pass
            finally:
                self._is_playing_sound = False
                self._audio_queue.task_done()

        with _audio_lock:
            if self in _active_pipelines:
                _active_pipelines.remove(self)


def create_speech_pipeline(voice: str = None, engine: str = None, speed: float = None) -> SpeechStreamPipeline:
    return SpeechStreamPipeline(voice=voice, engine=engine, speed=speed)


# =============================================================================
# HÀM PHÁT ÂM THANH CHUẨN SPEAK (TỰ ĐỘNG PHÁT LIỀN MẠCH KHÔNG NGẮT QUÃNG)
# =============================================================================

def speak(
    text: str,
    play_alert: bool = False,
    voice: str = None,
    engine: str = None,
    speed: float = None,
    is_async: bool = False,
) -> None:
    """Chuyển văn bản thành giọng nói tiếng Việt mượt mà, không ngắt quãng sau dấu câu."""
    if not text or not text.strip():
        return

    if is_async:
        t = threading.Thread(
            target=speak,
            args=(text, play_alert, voice, engine, speed, False),
            daemon=True,
        )
        t.start()
        return

    global _is_speaking_active
    _is_speaking_active = True

    try:
        if play_alert:
            play_chime()

        sentences = _split_into_sentences(text)
        if not sentences:
            return

        pipeline = create_speech_pipeline(voice=voice, engine=engine, speed=speed)
        for s in sentences:
            pipeline.feed_sentence(s)
        pipeline.finish()
        pipeline.wait_until_done()
    finally:
        _is_speaking_active = False
