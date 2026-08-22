# coding: utf-8
"""
=== TASK 3: LOGIC NHẬN DIỆN GIỌNG NÓI TIẾNG VIỆT & TỪ KHÓA ĐỘNG TÁC ===
Hỗ trợ cả 2 backend thu âm:
  1. Sounddevice thông minh (Tương thích 100% Windows/macOS/Linux, không cần PyAudio).
  2. PyAudio tiêu chuẩn (nếu có cài đặt).
"""

import sys
import speech_recognition as sr

# Kiểm tra sounddevice
try:
    import sounddevice as sd
    import numpy as np
    _SD_AVAILABLE = True
except ImportError:
    _SD_AVAILABLE = False


class SoundDeviceSource(sr.AudioSource):
    """Nguồn thu âm chuẩn AudioSource sử dụng sounddevice khi máy không có PyAudio."""
    def __init__(self, sample_rate=16000, chunk_size=800):
        self.SAMPLE_RATE = sample_rate
        self.SAMPLE_WIDTH = 2  # 16-bit PCM
        self.CHUNK = chunk_size
        self.stream = None
        self.sd_stream = None

    def __enter__(self):
        self.sd_stream = sd.InputStream(samplerate=self.SAMPLE_RATE, channels=1, dtype="int16", blocksize=self.CHUNK)
        self.sd_stream.start()

        class StreamWrapper:
            def __init__(self, stream, chunk):
                self.stream = stream
                self.chunk = chunk

            def read(self, size):
                data, _ = self.stream.read(self.chunk)
                return data.tobytes()

        self.stream = StreamWrapper(self.sd_stream, self.CHUNK)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sd_stream:
            try:
                self.sd_stream.stop()
                self.sd_stream.close()
            except Exception:
                pass
            self.sd_stream = None


MOTION_MAP = {
    # ================== DI CHUYỂN ==================
    "Forward": {
        "tiến lên", "đi thẳng", "chạy tới", "bước tới", "đi tới", "tiến tới"
    },
    "Backward": {
        "lùi lại", "đi lùi", "thụt lùi", "lùi"
    },
    "TurnLeft": {
        "rẽ trái", "quay trái", "quẹo trái", "xoay trái"
    },
    "TurnRight": {
        "rẽ phải", "quay phải", "quẹo phải", "xoay phải"
    },
    "OneStepForward": {
        "bước tới một bước", "bước tới 1 bước", "tiến một bước", "tiến 1 bước"
    },
    "OneStepBackward": {
        "lùi lại một bước", "lùi lại 1 bước", "lùi một bước", "lùi 1 bước"
    },
    "OneStepTurnLeft": {
        "xoay trái một bước"
    },
    "OneStepTurnRight": {
        "xoay phải một bước"
    },
    "OneStepMoveLeft": {
        "qua trái"
    },
    "OneStepMoveRight": {
        "qua phải"
    },
    "Move_fast": {
        "đi nhanh", "nhanh lên"
    },
    "Stop": {
        "dừng", "dừng lại", "stop", "đứng yên"
    },
    "Reset": {
        "reset", "đứng thẳng"
    },
    # ================== NĂNG LƯỢNG ==================
    "EnterEnergySavingSquat": {
        "nghỉ", "nghỉ ngơi", "nghỉ ngơi đi", "tiết kiệm năng lượng", "vào chế độ tiết kiệm năng lượng"
    },
    "ExitEnergySavingReset": {
        "dừng nghỉ", "dừng nghỉ đi", "dừng nghỉ ngơi", "thoát tiết kiệm năng lượng", "thoát chế độ tiết kiệm năng lượng"
    },
    # ================== ÂM THANH / NHẠC ==================
    "WakaWaka": {
        "nhảy", "nhảy waka", "waka", "nhảy đi", "nhảy lên"
    },
    "MerryChristmas": {
        "giáng sinh", "giáng sinh vui vẻ", "merry christmas"
    },
    "HappyBirthday": {
        "sinh nhật", "chúc mừng sinh nhật", "happy birthday"
    },
    "WeAreTakingOff": {
        "cất cánh", "cất cánh thôi", "cất cánh đi", "cất cánh lên", "We Are Taking Off"
    },
    "Victory": {
        "xin chào", "ăn mừng", "chào", "hi", "hello", "hey", "hey robot"
    },
    "GetupFront": {
        "ngã sấp đứng dậy", "ngã sấp đứng lên", "ngã sấp đứng dậy đi", "ngã sấp đứng dậy lên", "nằm sấp đứng dậy", "nằm sấp đứng lên", "nằm sấp đứng dậy đi", "nằm sấp đứng dậy lên", "lật lại", "lật người"
    },
    "GetupRear": {
        "ngã ngửa đứng dậy", "ngã ngửa đứng lên", "ngã ngửa đứng dậy đi", "ngã ngửa đứng dậy lên", "nằm ngửa đứng dậy", "nằm ngửa đứng lên", "nằm ngửa đứng dậy đi", "nằm ngửa đứng dậy lên", "ngồi dậy", "đứng dậy", "đứng lên"
    },
    "PushUp": {
        "hít đất", "hít đất đi", "hít đất lên", "hít đất đi lên", "chống đẩy", "chống đẩy đi", "chống đẩy lên", "chống đẩy đi lên"
    },
    "GetUp": {
        "Tập thể dục", "tập thể dục đi", "tập thể dục lên", "tập thể dục đi lên"
    },
    # ================== BÓNG ĐÁ ==================
    "Football_LKick": {
        "sút trái", "đá trái", "sút chân trái", "đá chân trái"
    },
    "Football_RKick": {
        "sút phải", "đá phải", "sút chân phải", "đá chân phải"
    },
    "Football_LShoot": {
        "dứt điểm trái", "sút mạnh trái", "sút bóng trái", "sút banh trái", "sút banh"
    },
    "Football_RShoot": {
        "dứt điểm phải", "sút mạnh phải", "sút bóng phải", "sút bóng", "đá bóng", "đá banh", "sút banh phải"
    },
    "GoalKeeper1": {
        "bắt bóng", "thủ môn bắt bóng", "bảo vệ khung thành", "bắt banh"
    },
    "GoalKeeper2": {
        "bắt bóng trên", "chuẩn bị bắt bóng", "thủ môn", "bắt banh trên"
    },
    "Football_LKeep": {
        "bắt bóng trái", "đỡ người bên trái", "đỡ người trái", "bắt banh trái"
    },
    "Football_RKeep": {
        "bắt bóng phải", "đỡ người bên phải", "đỡ người phải", "bắt banh phải"
    },
    "LeftTackle": {
        "xoạc bóng trái", "cướp bóng trái", "xoạc banh trái"
    },
    "RightTackle": {
        "xoạc bóng phải", "cướp bóng phải", "xoạc bóng", "xoạc banh phải"
    },
    "Left slide tackle": {
        "chùi bóng trái", "trượt bóng trái", "xoạc banh trái"
    },
    # ================== CHIẾN ĐẤU ==================
    "LeftSidePunch": {
        "đấm ngang trái", "đánh ngang trái", "đấm tay trái", "đánh tay trái"
    },
    "RightSidePunch": {
        "đấm ngang phải", "đánh ngang phải", "đấm tay phải", "đánh tay phải"
    },
    "LeftHitForward": {
        "đấm thẳng trái", "đánh thẳng trái", "tấn công trái"
    },
    "RightHitForward": {
        "đấm thẳng phải", "đánh thẳng phải", "tấn công phải", "đấm thẳng", "tấn công"
    },
    "PlayMusic": {
        "phát nhạc", "bật nhạc", "mở nhạc", "play music"
    },
    "StopMusic": {
        "tắt nhạc", "dừng nhạc", "stop music"
    },
    "VolumeUp": {
        "tăng âm lượng", "to lên", "lớn lên"
    },
    "VolumeDown": {
        "giảm âm lượng", "nhỏ lại"
    },
    "Mute": {
        "tắt âm thanh", "im lặng", "mute", "tắt tiếng", "tắt tiếng đi", "tắt tiếng lên"
    },
    "Unmute": {
        "bật âm thanh", "mở tiếng"
    },
}


def init_recognizer():
    """Khởi tạo đối tượng nhận diện giọng nói (Recognizer)."""
    return sr.Recognizer()


def get_microphone():
    """
    Lấy đối tượng Microphone làm nguồn thu âm đầu vào.
    Tự động sử dụng SoundDeviceSource nếu máy tính chưa cài PyAudio.
    """
    try:
        return sr.Microphone()
    except Exception:
        return SoundDeviceSource()


def record_audio(recognizer, source):
    """Ghi âm dữ liệu giọng nói từ Microphone nguồn."""
    try:
        from core.listener import _record_audio_sounddevice
        audio = _record_audio_sounddevice(timeout=12, phrase_time_limit=25, pause_threshold=1.3, energy_threshold=50.0)
        if audio is not None:
            return audio
    except Exception:
        pass

    try:
        return recognizer.listen(source, timeout=6, phrase_time_limit=20)
    except Exception:
        return None


def recognize_speech_vietnamese(recognizer, audio):
    """Sử dụng dịch vụ Google Speech Recognition để dịch âm thanh sang tiếng Việt."""
    if audio is None:
        return None
    return recognizer.recognize_google(audio, language="vi-VN")


def get_action(text):
    """Kiểm tra xem câu nói của người dùng có chứa từ khóa nào trong MOTION_MAP hay không."""
    if not text:
        return None
    text_lower = text.lower().strip()

    for motion_name, phrases in MOTION_MAP.items():
        for phrase in phrases:
            if phrase.lower() in text_lower:
                return motion_name
    return None
