"""
Gói mã nguồn lõi (Core Package v4.0 Pro) - Robot Hướng Dẫn Viên Triển Lãm Văn Hóa.
Cung cấp các module chuyên biệt:
- ai_brain: Tương tác Gemini Flash siêu tốc với trí nhớ đàm thoại đa lượt
- cache: Bộ đệm thông minh Smart Fuzzy & Dynamic LRU Cache (0ms)
- voice: Quản lý Giọng đọc AI Tiếng Việt Kokoro-TTS / Edge-TTS
- phonetics: Module phiên âm âm thầm chuẩn hóa địa danh, số La Mã, số đo cho AI TTS
- listener: Thu âm và nhận diện giọng nói tiếng Việt qua Micro (Voice-to-Voice)
- knowledge_base: Cơ sở tri thức số hóa các hiện vật triển lãm văn hóa
"""

from core.ai_brain import ask_gemini, reset_conversation
from core.cache import check_cache, add_to_dynamic_cache
from core.voice import speak, set_voice, get_current_voice, get_available_voices
from core.phonetics import to_speech_phonetics, number_to_words
from core.listener import listen_from_mic, is_mic_available
from core.knowledge_base import EXHIBITION_KNOWLEDGE

__all__ = [
    "ask_gemini",
    "reset_conversation",
    "check_cache",
    "add_to_dynamic_cache",
    "speak",
    "set_voice",
    "get_current_voice",
    "get_available_voices",
    "to_speech_phonetics",
    "number_to_words",
    "listen_from_mic",
    "is_mic_available",
    "EXHIBITION_KNOWLEDGE",
]

