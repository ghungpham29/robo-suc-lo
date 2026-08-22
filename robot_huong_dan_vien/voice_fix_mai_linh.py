# coding: utf-8
"""
=============================================================================
=== BỘ TỐI ƯU HÓA & FIX LỖI GIỌNG ĐỌC MAI LINH (KOKORO-TTS VIETNAMESE) ===
=============================================================================
Vấn đề giải quyết:
1. KHẮC PHỤC KHOẢNG LẶNG QUÁ DÀI GIỮA CÁC CÂU (DẤU CHẤM "."):
   - Nguyên nhân: Mô hình Kokoro ONNX sinh ra ~1000ms khoảng lặng đuôi (trail silence)
     và ~200ms khoảng lặng đầu (lead silence) cho mỗi phân đoạn câu sau dấu chấm ".".
     Khi nối câu, khoảng lặng chết (dead pause) lên tới 1.2s - 1.5s làm giọng bị ngắt quãng.
   - Giải pháp: Cắt tỉa chính xác khoảng lặng thừa (Adaptive Silence Trimming) ở từng câu,
     sau đó ghép nối với khoảng nghỉ đệm tự nhiên như con người thở (150ms - 180ms).

2. ĐIỀU CHỈNH TỐC ĐỘ PHÙ HỢP VỚI NGÔN NGỮ NÓI TỰ NHIÊN CỦA CON NGƯỜI:
   - Nguyên nhân: Tốc độ mặc định 1.0x của Mai Linh bị rề rà, kéo dài âm tiết.
   - Giải pháp: Thiết lập tốc độ tối ưu 1.20x (Calibrated Conversational Speed),
     giúp giọng đọc Mai Linh trẻ trung, hoạt bát, dứt khoát và dễ nghe như hướng dẫn viên thực thụ.

3. XỬ LÝ 100% TRÊN RAM (IN-MEMORY BUFFER, ZERO DISK I/O LATENCY).
=============================================================================
"""

import os
import re
import sys
import io
import time
import threading
from typing import Optional, Tuple, List, Dict
import numpy as np

# Fix UTF-8 console output trên Windows
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    if hasattr(sys.stdout, "reconfigure"):
        getattr(sys.stdout, "reconfigure")(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        getattr(sys.stderr, "reconfigure")(encoding="utf-8", errors="replace")
except Exception:
    pass

# Cấu hình đường dẫn module
_this_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = _this_dir if not os.path.exists(os.path.join(_this_dir, "core")) else os.path.dirname(_this_dir)
_robot_dir = os.path.join(_root_dir, "robot_huong_dan_vien")
_kokoro_src = os.path.join(_robot_dir, "Kokoro-Vietnamese-src", "Kokoro-Vietnamese-main", "src")

for p in [_root_dir, _robot_dir, _kokoro_src, _this_dir]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

# Import bộ phiên âm ngầm tiếng Việt
try:
    from core.phonetics import to_speech_phonetics
except Exception:
    try:
        from robot_huong_dan_vien.core.phonetics import to_speech_phonetics
    except Exception:
        def to_speech_phonetics(t: str) -> str:
            return t

# Kiểm tra thư viện âm thanh
try:
    import soundfile as sf
    _SOUNDFILE_AVAILABLE = True
except ImportError:
    _SOUNDFILE_AVAILABLE = False

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False

# Kiểm tra Kokoro ONNX
_KOKORO_AVAILABLE = False
try:
    from kokoro_vietnamese.onnx_cli import KokoroVietnameseONNX
    from kokoro_vietnamese.core import split_text, phonemize
    from kokoro_vietnamese.onnx_utils import phonemes_to_input_ids, select_voice_style, speed_input
    _KOKORO_AVAILABLE = True
except Exception:
    _KOKORO_AVAILABLE = False

# Kiểm tra Edge-TTS dự phòng
_EDGE_TTS_AVAILABLE = False
try:
    import edge_tts
    import asyncio
    _EDGE_TTS_AVAILABLE = True
except Exception:
    _EDGE_TTS_AVAILABLE = False


# =============================================================================
# THÔNG SỐ CẤU HÌNH CHUẨN CHO GIỌNG MAI LINH ĐÃ FIX
# =============================================================================
DEFAULT_MAI_LINH_SPEED: float = 1.20       # Tốc độ đọc tự nhiên chuẩn con người (1.18x - 1.22x)
DEFAULT_PAUSE_PERIOD_MS: int = 160         # Khoảng nghỉ sau dấu chấm "." (160ms thay vì 1400ms)
DEFAULT_PAUSE_COMMA_MS: int = 90           # Khoảng nghỉ sau dấu phẩy "," (90ms)
DEFAULT_PAUSE_PARAGRAPH_MS: int = 260      # Khoảng nghỉ sau ngắt đoạn (260ms)
SAMPLE_RATE: int = 24000                   # Tần số lấy mẫu âm thanh Kokoro
SILENCE_THRESHOLD: float = 0.008           # Ngưỡng phát hiện âm thanh/khoảng lặng
EDGE_FALLBACK_VOICE: str = "vi-VN-HoaiMyNeural"


def _ensure_mixer():
    """Khởi tạo mixer với buffer nhỏ để phát tức thì."""
    if _PYGAME_AVAILABLE and not pygame.mixer.get_init():
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=1024)
        except Exception:
            try:
                pygame.mixer.init()
            except Exception:
                pass


class MaiLinhVoiceOptimizer:
    """
    Bộ tối ưu hóa âm thanh chuyên dụng cho Giọng Mai Linh (Kokoro TTS):
    - Khắc phục triệt để khoảng lặng kéo dài sau dấu chấm câu ".".
    - Đồng bộ tốc độ tự nhiên, rõ ràng, giàu sức sống.
    - Cắt tỉa khoảng lặng thừa và điều tiết nhịp thở tự nhiên.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MaiLinhVoiceOptimizer, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, device: str = "cpu"):
        if getattr(self, "_initialized", False):
            return
        self.device = device
        self.kokoro_model: Optional[KokoroVietnameseONNX] = None
        self._load_model()
        _ensure_mixer()
        self._initialized = True

    def _load_model(self):
        """Khởi tạo Singleton Kokoro ONNX cho giọng Mai Linh."""
        if not _KOKORO_AVAILABLE:
            print("[MaiLinh Optimizer] Kokoro-Vietnamese chưa sẵn sàng -> Sẽ dùng Edge-TTS tối ưu.")
            return

        try:
            self.kokoro_model = KokoroVietnameseONNX(
                voice="mai_linh",
                device=self.device,
            )
            print("[MaiLinh Optimizer] ✅ Đã nạp thành công mô hình Kokoro ONNX - Giọng Mai Linh!")
        except Exception as e:
            print(f"[MaiLinh Optimizer] ⚠️ Lỗi nạp Kokoro ONNX ({e}) -> Fallback Edge-TTS.")
            self.kokoro_model = None

    @staticmethod
    def trim_silence(
        audio: np.ndarray,
        threshold: float = SILENCE_THRESHOLD,
        pad_ms: int = 15,
        sr: int = SAMPLE_RATE,
    ) -> np.ndarray:
        """
        Cắt tỉa toàn bộ khoảng lặng chết ở đầu và đuôi phân đoạn âm thanh.
        Giữ lại đệm nhỏ 15ms và áp dụng fade in/out nhẹ để chống tiếng nổ (anti-pop).
        """
        if len(audio) == 0:
            return audio

        pad_samples = int(sr * (pad_ms / 1000.0))
        mask = np.abs(audio) > threshold

        if not np.any(mask):
            return np.array([], dtype=np.float32)

        start_idx = max(0, int(np.argmax(mask)) - pad_samples)
        end_idx = min(len(audio), len(audio) - int(np.argmax(mask[::-1])) + pad_samples)

        trimmed = audio[start_idx:end_idx].copy()
        if len(trimmed) < 64:
            return trimmed

        # Áp dụng Micro Fade-In và Fade-Out (3ms) để âm thanh êm ái
        fade_len = min(int(sr * 0.003), len(trimmed) // 4)
        if fade_len > 1:
            fade_in = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
            fade_out = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
            trimmed[:fade_len] *= fade_in
            trimmed[-fade_len:] *= fade_out

        return trimmed.astype(np.float32, copy=False)

    def _split_into_smart_chunks(self, text: str) -> List[Tuple[str, str]]:
        """
        Tách văn bản thành các phân đoạn đi kèm dấu ngắt câu để chèn khoảng nghỉ chuẩn:
        Trả về danh sách tuple: (nội dung câu, loại dấu ngắt: 'period' | 'comma' | 'paragraph' | 'end')
        """
        cleaned = text.strip()
        if not cleaned:
            return []

        # Tách trước theo đoạn văn bản
        paragraphs = [p.strip() for p in cleaned.split("\n") if p.strip()]
        chunks_with_type: List[Tuple[str, str]] = []

        for p_idx, paragraph in enumerate(paragraphs):
            # Tách câu theo dấu kết thúc câu: . ! ? …
            raw_sentences = re.split(r"(?<=[.!?…])\s+", paragraph)
            for s_idx, s in enumerate(raw_sentences):
                s_clean = s.strip()
                if not s_clean:
                    continue

                is_last_in_paragraph = (s_idx == len(raw_sentences) - 1)
                is_last_overall = is_last_in_paragraph and (p_idx == len(paragraphs) - 1)

                if is_last_overall:
                    p_type = "end"
                elif is_last_in_paragraph:
                    p_type = "paragraph"
                else:
                    p_type = "period"

                chunks_with_type.append((s_clean, p_type))

        return chunks_with_type

    def synthesize(
        self,
        text: str,
        speed: float = DEFAULT_MAI_LINH_SPEED,
        pause_period_ms: int = DEFAULT_PAUSE_PERIOD_MS,
        pause_comma_ms: int = DEFAULT_PAUSE_COMMA_MS,
        pause_paragraph_ms: int = DEFAULT_PAUSE_PARAGRAPH_MS,
    ) -> Tuple[np.ndarray, int]:
        """
        Tổng hợp âm thanh giọng Mai Linh ĐÃ FIX KHOẢNG LẶNG & TỐC ĐỘ:
        1. Phiên âm chuẩn hóa ngữ âm tiếng Việt.
        2. Tách câu thông minh.
        3. Tổng hợp từng câu qua ONNX.
        4. Cắt tỉa sạch khoảng lặng thừa ~1.1s ở đuôi mỗi câu.
        5. Nối các câu với khoảng nghỉ chuẩn tự nhiên (160ms).
        """
        if not text or not text.strip():
            return np.array([], dtype=np.float32), SAMPLE_RATE

        # Chuẩn hóa ngữ âm
        phonetic_text = to_speech_phonetics(text.strip())

        # Fallback sang Edge-TTS nếu không có Kokoro
        if self.kokoro_model is None:
            return self._synthesize_edge_fallback(phonetic_text, speed=speed)

        chunks_info = self._split_into_smart_chunks(phonetic_text)
        if not chunks_info:
            return np.array([], dtype=np.float32), SAMPLE_RATE

        speed_val = speed_input(speed)
        audio_segments: List[np.ndarray] = []

        # Các mảng khoảng lặng đệm được tính toán trước
        pause_period_arr = np.zeros(int(SAMPLE_RATE * (pause_period_ms / 1000.0)), dtype=np.float32)
        pause_paragraph_arr = np.zeros(int(SAMPLE_RATE * (pause_paragraph_ms / 1000.0)), dtype=np.float32)

        for chunk_text, pause_type in chunks_info:
            # Lấy phonemes cho từng đoạn
            ps = phonemize(chunk_text)
            if not ps:
                continue

            try:
                input_ids = phonemes_to_input_ids(
                    ps,
                    self.kokoro_model.config["vocab"],
                    context_length=self.kokoro_model.context_length,
                )
                ref_s = select_voice_style(self.kokoro_model.voicepack, len(ps))

                waveform, _ = self.kokoro_model.session.run(
                    None,
                    {
                        "input_ids": input_ids,
                        "ref_s": ref_s,
                        "speed": speed_val,
                    },
                )
                raw_chunk_audio = np.asarray(waveform, dtype=np.float32).reshape(-1)

                # FIX CỐT LÕI: Cắt tỉa khoảng lặng thừa 1000ms+ ở đuôi và 200ms ở đầu
                trimmed_chunk = self.trim_silence(raw_chunk_audio, threshold=SILENCE_THRESHOLD, pad_ms=15)
                if len(trimmed_chunk) == 0:
                    continue

                audio_segments.append(trimmed_chunk)

                # Chèn khoảng nghỉ nhịp thở chuẩn theo loại dấu câu
                if pause_type == "period":
                    audio_segments.append(pause_period_arr)
                elif pause_type == "paragraph":
                    audio_segments.append(pause_paragraph_arr)

            except Exception as e:
                print(f"[MaiLinh Optimizer] Lỗi tổng hợp câu '{chunk_text}': {e}")
                continue

        if not audio_segments:
            return np.array([], dtype=np.float32), SAMPLE_RATE

        final_audio = np.concatenate(audio_segments).astype(np.float32, copy=False)
        return final_audio, SAMPLE_RATE

    def _synthesize_edge_fallback(self, text: str, speed: float = DEFAULT_MAI_LINH_SPEED) -> Tuple[np.ndarray, int]:
        """Tổng hợp âm thanh dự phòng qua Edge-TTS nếu không có ONNX."""
        if not _EDGE_TTS_AVAILABLE or not _SOUNDFILE_AVAILABLE:
            return np.array([], dtype=np.float32), SAMPLE_RATE

        try:
            rate_str = f"{int((speed - 1.0) * 100):+d}%" if speed != 1.0 else "+15%"
            comm = edge_tts.Communicate(text, EDGE_FALLBACK_VOICE, rate=rate_str)

            async def _fetch():
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

            bio = loop.run_until_complete(_fetch())
            if bio.getbuffer().nbytes > 0:
                data, sr = sf.read(bio, dtype="float32")
                if len(data.shape) > 1:
                    data = data[:, 0]
                return data, sr
        except Exception as e:
            print(f"[MaiLinh Optimizer] Fallback Edge-TTS thất bại: {e}")

        return np.array([], dtype=np.float32), SAMPLE_RATE

    def speak(
        self,
        text: str,
        speed: float = DEFAULT_MAI_LINH_SPEED,
        pause_period_ms: int = DEFAULT_PAUSE_PERIOD_MS,
        is_async: bool = False,
    ) -> None:
        """
        Phát âm thanh giọng Mai Linh trực tiếp ra Loa trên RAM (Không ghi đĩa):
        - Liền mạch không khoảng lặng chết sau dấu chấm ".".
        - Tốc độ đọc 1.20x chuẩn tiếng Việt đàm thoại.
        """
        if not text or not text.strip():
            return

        if is_async:
            t = threading.Thread(
                target=self.speak,
                args=(text, speed, pause_period_ms, False),
                daemon=True,
            )
            t.start()
            return

        audio_array, sr = self.synthesize(text, speed=speed, pause_period_ms=pause_period_ms)
        if len(audio_array) == 0:
            return

        if not _PYGAME_AVAILABLE or not _SOUNDFILE_AVAILABLE:
            return

        try:
            _ensure_mixer()
            bio = io.BytesIO()
            sf.write(bio, audio_array, sr, format="WAV", subtype="PCM_16")
            bio.seek(0)

            sound = pygame.mixer.Sound(bio)
            channel = sound.play()
            clock = pygame.time.Clock()
            sound_dur = len(audio_array) / float(sr)
            t_start = time.time()

            while channel and channel.get_busy():
                if time.time() - t_start > sound_dur + 0.5:
                    break
                clock.tick(100)
        except Exception as e:
            print(f"[MaiLinh Optimizer] Lỗi phát âm thanh: {e}")

    def save_wav(self, text: str, output_path: str, speed: float = DEFAULT_MAI_LINH_SPEED, pause_period_ms: int = DEFAULT_PAUSE_PERIOD_MS) -> bool:
        """Tổng hợp và lưu thành file WAV chất lượng cao."""
        if not _SOUNDFILE_AVAILABLE:
            print("[Lỗi] soundfile chưa được cài đặt.")
            return False

        audio_array, sr = self.synthesize(text, speed=speed, pause_period_ms=pause_period_ms)
        if len(audio_array) == 0:
            return False

        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            sf.write(output_path, audio_array, sr)
            print(f"✅ Đã xuất file audio: {output_path} (Thời lượng: {len(audio_array)/sr:.2f}s)")
            return True
        except Exception as e:
            print(f"❌ Lỗi ghi file audio: {e}")
            return False


# =============================================================================
# HÀM TIỆN ÍCH DÙNG TRỰC TIẾP TRONG TOÀN BỘ PROJECT (CONVENIENCE APIS)
# =============================================================================

_global_optimizer: Optional[MaiLinhVoiceOptimizer] = None


def get_mai_linh_optimizer() -> MaiLinhVoiceOptimizer:
    """Lấy Singleton Optimizer cho giọng Mai Linh."""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = MaiLinhVoiceOptimizer()
    return _global_optimizer


def speak_mai_linh(
    text: str,
    speed: float = DEFAULT_MAI_LINH_SPEED,
    pause_period_ms: int = DEFAULT_PAUSE_PERIOD_MS,
    is_async: bool = False,
) -> None:
    """
    Hàm phát âm thanh giọng Mai Linh ĐÃ FIX:
    - Tự động triệt tiêu khoảng lặng chết 1.4s ở dấu chấm ".".
    - Tốc độ đọc 1.20x chuẩn đàm thoại tự nhiên.
    """
    optimizer = get_mai_linh_optimizer()
    optimizer.speak(text, speed=speed, pause_period_ms=pause_period_ms, is_async=is_async)


def synthesize_mai_linh(
    text: str,
    speed: float = DEFAULT_MAI_LINH_SPEED,
    pause_period_ms: int = DEFAULT_PAUSE_PERIOD_MS,
    save_path: Optional[str] = None,
) -> Tuple[np.ndarray, int]:
    """
    Hàm tổng hợp âm thanh giọng Mai Linh đã fix thành mảng NumPy (PCM 24kHz).
    """
    optimizer = get_mai_linh_optimizer()
    audio, sr = optimizer.synthesize(text, speed=speed, pause_period_ms=pause_period_ms)
    if save_path:
        optimizer.save_wav(text, save_path, speed=speed, pause_period_ms=pause_period_ms)
    return audio, sr


# =============================================================================
# GIAO DIỆN KIỂM THỬ TƯƠNG TÁC DÒNG LỆNH (INTERACTIVE CLI TEST STUDIO)
# =============================================================================

SAMPLE_STATUE_TEXT = (
    "Kính chào quý khách đến với Triển lãm Văn hóa Chăm Pa. "
    "Đây là điểm khởi đầu của hành trình chiêm ngưỡng 11 kiệt tác điêu khắc sa thạch cổ đại. "
    "Nơi hội tụ tinh hoa nghệ thuật Ấn Độ giáo và bản sắc độc đáo của vương triều Chăm Pa qua các thời kỳ lịch sử."
)

SAMPLE_SHIVA_TEXT = (
    "Đại thần Shiva được tôn là vị thần bảo hộ tối cao. "
    "Phù điêu thần ngồi thiền định tạc nổi trên khối đá hình lá đề tại trán cửa tháp nhằm trấn giữ và khẳng định uy quyền vương triều. "
    "Hình tượng tiến hóa từ vẻ đẹp thời sơ kỳ sang nét uy nghiêm ở thời Tháp Mẫm."
)


def _synthesize_original_unfixed(text: str) -> Tuple[np.ndarray, int]:
    """Tổng hợp giọng Mai Linh GỐC (Chưa fix) để người dùng nghe đối chứng so sánh."""
    if not _KOKORO_AVAILABLE:
        return np.array([], dtype=np.float32), SAMPLE_RATE
    try:
        from kokoro_vietnamese.onnx_cli import KokoroVietnameseONNX
        tts = KokoroVietnameseONNX(voice="mai_linh")
        audio, _ = tts.synthesize(text, speed=1.0, crossfade_ms=50)
        return audio, SAMPLE_RATE
    except Exception:
        return np.array([], dtype=np.float32), SAMPLE_RATE


def run_interactive_studio():
    """Studio thử nghiệm và so sánh chất lượng giọng Mai Linh trước & sau khi fix."""
    print("\n" + "=" * 78)
    print("      🎙️  STUDIO KIỂM THỬ & ĐỐI CHỨNG GIỌNG MAI LINH (KOKORO-TTS FIX)  🎙️")
    print("=" * 78)
    print("  Các cải tiến đã áp dụng:")
    print("   1. Cắt tỉa triệt để ~1.1s khoảng lặng chết (trail silence) sau dấu chấm '.'")
    print("   2. Thiết lập khoảng nghỉ tự nhiên như nhịp thở con người (160ms)")
    print("   3. Tốc độ đọc tối ưu 1.20x chuẩn hướng dẫn viên đàm thoại")
    print("=" * 78)

    optimizer = get_mai_linh_optimizer()

    while True:
        print("\n  👉 MENU CHỌN TÍNH NĂNG:")
        print("   [1] 🔊 Nghe mẫu thuyết minh tượng bằng giọng Mai Linh ĐÃ FIX (Mượt mà, tốc độ 1.2x)")
        print("   [2] ⚠️  Nghe mẫu thuyết minh bằng giọng Mai Linh GỐC (Tốc độ 1.0x, khoảng lặng 1.4s ở '.') để so sánh")
        print("   [3] 🔊 Nghe bài thuyết minh Thần Shiva ĐÃ FIX (Nhiều câu liên tiếp)")
        print("   [4] ✍️  Tự nhập văn bản bất kỳ có nhiều dấu chấm '.' để test độ mượt")
        print("   [5] ⚙️  Tùy chỉnh Tốc độ (Speed) và Thời gian dừng (Pause ms)")
        print("   [6] 💾 Xuất file âm thanh (.wav) đã fix vào thư mục 'outputs/'")
        print("   [0] 🚪 Thoát")
        print("-" * 78)

        choice = input("Xin mời nhập lựa chọn (0-6): ").strip()

        if choice in ["0", "exit", "quit", "q"]:
            print("\n👋 Đã thoát Studio kiểm thử giọng Mai Linh. Hẹn gặp lại!\n")
            break

        elif choice == "1":
            print("\n[ĐANG PHÁT - ĐÃ FIX]: Đọc bài thuyết minh tượng (Speed: 1.20x, Pause: 160ms)...")
            optimizer.speak(SAMPLE_STATUE_TEXT, speed=DEFAULT_MAI_LINH_SPEED, pause_period_ms=DEFAULT_PAUSE_PERIOD_MS)

        elif choice == "2":
            print("\n[ĐANG PHÁT - GỐC CHƯA FIX]: Đọc bài thuyết minh gốc (Speed: 1.0x, khoảng lặng dài ở dấu chấm)...")
            orig_audio, sr = _synthesize_original_unfixed(SAMPLE_STATUE_TEXT)
            if len(orig_audio) > 0 and _PYGAME_AVAILABLE and _SOUNDFILE_AVAILABLE:
                _ensure_mixer()
                bio = io.BytesIO()
                sf.write(bio, orig_audio, sr, format="WAV", subtype="PCM_16")
                bio.seek(0)
                snd = pygame.mixer.Sound(bio)
                chan = snd.play()
                while chan and chan.get_busy():
                    pygame.time.Clock().tick(100)

        elif choice == "3":
            print("\n[ĐANG PHÁT - ĐÃ FIX]: Bài thuyết minh Thần Shiva...")
            optimizer.speak(SAMPLE_SHIVA_TEXT, speed=DEFAULT_MAI_LINH_SPEED, pause_period_ms=DEFAULT_PAUSE_PERIOD_MS)

        elif choice == "4":
            user_text = input("\n👉 Nhập văn bản cần đọc: ").strip()
            if user_text:
                print("\n[ĐANG PHÁT - ĐÃ FIX]:...")
                optimizer.speak(user_text, speed=DEFAULT_MAI_LINH_SPEED, pause_period_ms=DEFAULT_PAUSE_PERIOD_MS)

        elif choice == "5":
            try:
                s_in = input(f"Nhập tốc độ mong muốn (mặc định {DEFAULT_MAI_LINH_SPEED}, vd 1.15, 1.20, 1.25): ").strip()
                p_in = input(f"Nhập khoảng dừng sau dấu chấm ms (mặc định {DEFAULT_PAUSE_PERIOD_MS}ms, vd 140, 160, 200): ").strip()
                custom_speed = float(s_in) if s_in else DEFAULT_MAI_LINH_SPEED
                custom_pause = int(p_in) if p_in else DEFAULT_PAUSE_PERIOD_MS
                print(f"\n[ĐANG PHÁT THỬ NGHIỆM]: Speed={custom_speed}x, Pause={custom_pause}ms...")
                optimizer.speak(SAMPLE_STATUE_TEXT, speed=custom_speed, pause_period_ms=custom_pause)
            except Exception as e:
                print(f"[!] Giá trị không hợp lệ: {e}")

        elif choice == "6":
            out_file = os.path.join(_root_dir, "outputs", "mai_linh_fixed_export.wav")
            optimizer.save_wav(SAMPLE_STATUE_TEXT, out_file, speed=DEFAULT_MAI_LINH_SPEED, pause_period_ms=DEFAULT_PAUSE_PERIOD_MS)


if __name__ == "__main__":
    run_interactive_studio()
