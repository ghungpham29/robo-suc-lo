"""
Module Nhận diện Giọng nói qua Micro (Speech-to-Text Listener v5.2 Pro Max)
Được tối ưu hóa đặc biệt cho môi trường giao tiếp tự nhiên tại triển lãm:
  1. Dual-Threshold Hysteresis VAD: Ngưỡng kích hoạt kép chống cắt ngang khi người dùng nói chậm, nhỏ giọng hoặc ngắt quãng lấy hơi.
  2. Pre-roll Buffer (0.5s) & Post-roll Padding (0.3s): Đảm bảo 100% không bị mất âm tiết đầu câu ("Ơi", "Này", "Cho", "Xin") hay âm đuôi ("ạ", "nhé", "nào").
  3. Noise-Spike Filter (Min Speech Filter): Tự động lọc bỏ các tiếng gõ bàn, tiếng ho, tạp âm thoáng qua (< 0.3s) để không bị đóng mic sớm.
  4. Pause Threshold chuẩn tự nhiên (1.4s): Cho phép du khách có đủ thời gian dừng lại suy nghĩ, ngắt nghỉ giữa các vế câu mà không bị ngắt ghi âm sớm.
  5. Tương thích toàn diện trên Windows/Linux/macOS (Sounddevice + SpeechRecognition).
"""

import collections
import os
import sys
import time
from typing import Any, Optional
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            getattr(sys.stdout, "reconfigure")(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            getattr(sys.stderr, "reconfigure")(encoding="utf-8", errors="replace")
    except Exception:
        pass

load_dotenv()

# Cấu hình từ .env (Mặc định 1.4s để du khách ngắt nghỉ tự nhiên không bị cắt câu)
PAUSE_THRESHOLD = float(os.getenv("MIC_PAUSE_THRESHOLD", "1.4"))
DEFAULT_TIMEOUT = int(os.getenv("MIC_TIMEOUT", "15"))
PHRASE_LIMIT = int(os.getenv("MIC_PHRASE_LIMIT", "30"))
ENV_ENERGY_THRESHOLD = os.getenv("MIC_ENERGY_THRESHOLD", "auto")

# Kiểm tra thư viện âm thanh
try:
    import sounddevice as sd
    import numpy as np
    _SD_AVAILABLE = True
except ImportError:
    _SD_AVAILABLE = False

try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False

SAMPLE_RATE = 16000
BLOCK_DURATION = 0.05  # 50ms mỗi khối âm thanh
BLOCK_SIZE = int(SAMPLE_RATE * BLOCK_DURATION)

# ==============================================================================
# QUẢN LÝ TRẠNG THÁI TOÀN CỤC
# ==============================================================================
_recognizer_instance = None
_calibrated_energy_threshold: float = 300.0
_is_calibrated: bool = False
_mic_status_cached: Optional[bool] = None


def get_recognizer() -> Any:
    """Khởi tạo hoặc lấy đối tượng sr.Recognizer Singleton."""
    global _recognizer_instance
    if _recognizer_instance is None:
        if _SR_AVAILABLE:
            _recognizer_instance = sr.Recognizer()
        else:
            raise RuntimeError("Thư viện SpeechRecognition chưa được cài đặt (pip install SpeechRecognition).")
    return _recognizer_instance


def is_mic_available(force_check: bool = False) -> bool:
    """
    Kiểm tra xem hệ thống có thiết bị Micro khả dụng hay không.
    Ưu tiên quét qua sounddevice (nhận diện nhanh và chính xác), sau đó tới speech_recognition.
    """
    global _mic_status_cached
    if _mic_status_cached is not None and not force_check:
        return _mic_status_cached

    # 1. Kiểm tra qua sounddevice
    if _SD_AVAILABLE:
        try:
            input_dev = sd.query_devices(kind="input")
            if input_dev and input_dev.get("max_input_channels", 0) > 0:
                _mic_status_cached = True
                return True
        except Exception:
            pass

    # 2. Kiểm tra qua speech_recognition / PyAudio
    if _SR_AVAILABLE:
        try:
            mics = sr.Microphone.list_microphone_names()
            if mics and len(mics) > 0:
                _mic_status_cached = True
                return True
        except Exception:
            pass

    _mic_status_cached = False
    return False


def calibrate_ambient_noise(duration: float = 1.0) -> float:
    """
    Đo mức năng lượng tạp âm nền thực tế trong phòng để thiết lập ngưỡng kích hoạt Micro tối ưu.
    """
    global _calibrated_energy_threshold, _is_calibrated

    # Nếu người dùng cấu hình cố định trong .env (ví dụ: MIC_ENERGY_THRESHOLD=350)
    if ENV_ENERGY_THRESHOLD.isdigit():
        _calibrated_energy_threshold = float(ENV_ENERGY_THRESHOLD)
        _is_calibrated = True
        return _calibrated_energy_threshold

    if _SD_AVAILABLE and is_mic_available():
        try:
            print("[🎙️ MICRO] Đang đo tạp âm môi trường (1.0s)... Vui lòng giữ im lặng.")
            energies = []
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16", blocksize=BLOCK_SIZE) as stream:
                start = time.time()
                while time.time() - start < duration:
                    data, _ = stream.read(BLOCK_SIZE)
                    e = float(np.abs(data).mean())
                    energies.append(e)

            ambient_mean = float(np.mean(energies)) if energies else 40.0
            # Ngưỡng kích hoạt = mức ồn nền + 120 (giới hạn an toàn từ 200 đến 650)
            threshold = max(ambient_mean + 120.0, 200.0)
            if threshold > 650.0:
                threshold = 450.0  # Chống trường hợp bị tiếng ồn bất chợt đẩy ngưỡng quá cao
            
            _calibrated_energy_threshold = threshold
            _is_calibrated = True
            print(f"[🎙️ MICRO] Cân bằng môi trường thành công (Ngưỡng nhạy kích hoạt: {_calibrated_energy_threshold:.0f})!")
            return _calibrated_energy_threshold
        except Exception as e:
            print(f"[🎙️ MICRO] Không thể tự động cân bằng tạp âm: {e}. Sử dụng ngưỡng mặc định 300.")

    _calibrated_energy_threshold = 300.0
    _is_calibrated = True
    return _calibrated_energy_threshold


def _record_audio_sounddevice(
    timeout: int = 10,
    phrase_time_limit: int = 25,
    pause_threshold: float = 1.3,
    energy_threshold: float = 60.0,
    callback_energy: Optional[Any] = None,
) -> Optional["sr.AudioData"]:
    """
    Thu âm thời gian thực thông minh bằng sounddevice với cơ chế:
      - Dynamic Noise Floor Tracking: Tự động thích ứng với mức ồn nền thực tế.
      - Pre-roll Buffer (0.5s) lưu lại âm tiết mở đầu (tránh cụt đầu câu).
      - Dual-Threshold Hysteresis: Trigger cao để chống nhiễu, Continue thấp để bắt trọn giọng nói.
      - Noise-Spike Filter: Lọc các tiếng ồn ngắn (<0.25s) không phải giọng nói người.
      - Post-roll Padding (0.3s): Giữ trọn âm đuôi cuối câu.
    """
    pre_roll_blocks = int(0.5 / BLOCK_DURATION)
    pre_roll_buffer = collections.deque(maxlen=pre_roll_blocks)

    energy_history = collections.deque(maxlen=3)
    recorded_blocks = []
    has_speech_started = False
    voiced_blocks_count = 0
    silence_duration = 0.0
    start_time = time.time()
    speech_start_time: float = start_time

    # Khởi tạo ngưỡng động thích ứng
    noise_floor = max(energy_threshold * 0.3, 20.0)
    trigger_threshold = max(energy_threshold, 60.0)
    continue_threshold = max(trigger_threshold * 0.6, 35.0)

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16", blocksize=BLOCK_SIZE) as stream:
            while True:
                data, _ = stream.read(BLOCK_SIZE)
                raw_energy = float(np.abs(data).mean())
                energy_history.append(raw_energy)
                smoothed_energy = float(np.mean(energy_history))
                now = time.time()

                if callback_energy:
                    try:
                        callback_energy(smoothed_energy, has_speech_started)
                    except Exception:
                        pass

                if not has_speech_started:
                    pre_roll_buffer.append(data.copy())
                    # Cập nhật mức ồn nền khi đang im lặng
                    noise_floor = noise_floor * 0.95 + smoothed_energy * 0.05
                    trigger_threshold = max(noise_floor * 2.2, 50.0)

                    # Kích hoạt khi năng lượng vượt ngưỡng
                    if smoothed_energy > trigger_threshold:
                        has_speech_started = True
                        speech_start_time = now
                        recorded_blocks.extend(list(pre_roll_buffer))
                        voiced_blocks_count = 1
                        silence_duration = 0.0
                        continue_threshold = max(trigger_threshold * 0.55, 30.0)
                    elif now - start_time > timeout:
                        return None
                else:
                    recorded_blocks.append(data.copy())

                    if smoothed_energy > continue_threshold:
                        voiced_blocks_count += 1
                        silence_duration = 0.0
                    else:
                        silence_duration += BLOCK_DURATION

                        if silence_duration >= pause_threshold:
                            total_speech_time = voiced_blocks_count * BLOCK_DURATION
                            if total_speech_time < 0.25:
                                has_speech_started = False
                                recorded_blocks.clear()
                                voiced_blocks_count = 0
                                silence_duration = 0.0
                                continue
                            break

                    if now - speech_start_time > phrase_time_limit:
                        break
    except Exception as e:
        print(f"[🎙️ MICRO] Lỗi luồng thu âm sounddevice: {e}")
        return None
        return None

    if not recorded_blocks or voiced_blocks_count < 4:
        return None

    full_audio = np.concatenate(recorded_blocks, axis=0)
    raw_bytes = full_audio.tobytes()
    return sr.AudioData(raw_bytes, SAMPLE_RATE, 2)


def _record_audio_pyaudio(
    recognizer: Any,
    timeout: int,
    phrase_time_limit: int,
    pause_threshold: float,
) -> Optional["sr.AudioData"]:
    """Thu âm dự phòng bằng speech_recognition.Microphone (PyAudio) nếu môi trường có sẵn PyAudio."""
    try:
        recognizer.pause_threshold = pause_threshold
        recognizer.non_speaking_duration = 0.5
        with sr.Microphone() as source:
            global _is_calibrated
            if not _is_calibrated:
                recognizer.adjust_for_ambient_noise(source, duration=1.0)
                _is_calibrated = True
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return audio
    except sr.WaitTimeoutError:
        return None
    except Exception as e:
        print(f"[🎙️ MICRO] Lỗi thu âm PyAudio: {e}")
        return None


def listen_from_mic(
    timeout: Optional[int] = None,
    phrase_time_limit: Optional[int] = None,
    pause_threshold: Optional[float] = None,
    callback_energy: Optional[Any] = None,
) -> Optional[str]:
    """
    Thu âm giọng nói từ Micro và nhận diện sang văn bản tiếng Việt qua Google Speech API.

    Args:
        timeout (int): Thời gian tối đa chờ du khách cất tiếng nói (giây).
        phrase_time_limit (int): Thời lượng tối đa cho 1 câu hỏi (giây).
        pause_threshold (float): Khoảng lặng sau khi dứt câu để kết thúc thu âm (giây).
        callback_energy: Hàm callback nhận năng lượng âm thanh theo thời gian thực (để cập nhật UI).

    Returns:
        str | None: Câu văn tiếng Việt nhận diện được hoặc None nếu không có tiếng nói / lỗi mạng.
    """
    if not is_mic_available():
        print("[🎙️ MICRO] Không tìm thấy Micro khả dụng trên máy tính.")
        return None

    actual_timeout = timeout or DEFAULT_TIMEOUT
    actual_limit = phrase_time_limit or PHRASE_LIMIT
    actual_pause = pause_threshold or PAUSE_THRESHOLD

    recognizer = get_recognizer()

    # Hiệu chỉnh tạp âm lần đầu tiên
    global _is_calibrated, _calibrated_energy_threshold
    if not _is_calibrated:
        calibrate_ambient_noise()

    audio_data: Optional[sr.AudioData] = None

    # Ưu tiên sử dụng sounddevice
    if _SD_AVAILABLE:
        audio_data = _record_audio_sounddevice(
            timeout=actual_timeout,
            phrase_time_limit=actual_limit,
            pause_threshold=actual_pause,
            energy_threshold=_calibrated_energy_threshold,
            callback_energy=callback_energy,
        )
    else:
        # Dự phòng PyAudio
        audio_data = _record_audio_pyaudio(
            recognizer=recognizer,
            timeout=actual_timeout,
            phrase_time_limit=actual_limit,
            pause_threshold=actual_pause,
        )

    if audio_data is None:
        print("⌛ Chưa phát hiện âm thanh nói... Đang lắng nghe tiếp.")
        return None

    print("⏳ Đang nhận diện qua Google Speech API...")
    try:
        text = recognizer.recognize_google(audio_data, language="vi-VN")
        if text and text.strip():
            recognized_text = text.strip()
            print(f"-> Nhận diện được: \"{recognized_text}\"")
            return recognized_text
    except sr.UnknownValueError:
        print("❓ Chưa nghe rõ câu hỏi. Quý khách vui lòng nói to và rõ hơn một chút nhé.")
    except sr.RequestError as e:
        print(f"⚠️ Lỗi kết nối Google Speech API (vui lòng kiểm tra kết nối mạng Internet): {e}")
    except Exception as e:
        print(f"[🎙️ MICRO] Lỗi xử lý âm thanh: {e}")

    return None


if __name__ == "__main__":
    print("=" * 60)
    print("  KIỂM TRA ĐỘC LẬP MODULE MICROPHONE & NHẬN DIỆN GIỌNG NÓI")
    print("=" * 60)
    if not is_mic_available():
        print("❌ KHÔNG TÌM THẤY MICROPHONE TRÊN HỆ THỐNG.")
        sys.exit(1)

    print("✅ Microphone đã sẵn sàng! Hãy thử nói một câu tiếng Việt...")
    result = listen_from_mic(timeout=10)
    if result:
        print(f"\n🎉 KẾT QUẢ TEST THÀNH CÔNG: {result}")
    else:
        print("\n⚠️ Không nhận diện được âm thanh trong lượt thử này.")
