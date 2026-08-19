"""
DỰ ÁN: ROBOT HƯỚNG DẪN VIÊN TRIỂN LÃM VĂN HÓA (PHIÊN BẢN v6.0 PRO - VOICE-TO-VOICE CHUYÊN DỤNG)
Đơn vị phát triển: Đội thi Tin học trẻ & KHKT - Trường THPT Quốc Học Quy Nhơn
File: main.py (Entry Point - Trung tâm Điều phối Đàm thoại Giọng nói & Phần cứng Động cơ Matrix Mini R4)
"""

import os
import sys
import time
import threading
from dotenv import load_dotenv

# Thiết lập mã hóa UTF-8 cho Windows Terminal
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            getattr(sys.stdout, "reconfigure")(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            getattr(sys.stderr, "reconfigure")(encoding="utf-8")
    except Exception:
        pass

# Tải cấu hình biến môi trường
load_dotenv()

# Import các thành phần từ core
from core.ai_brain import ask_gemini, reset_conversation
from core.cache import check_cache, add_to_dynamic_cache
from core.voice import (
    speak,
    set_voice,
    get_current_voice,
    get_available_voices,
    is_speaking,
    wait_until_speaking_done,
    create_speech_pipeline,
)
from core.listener import listen_from_mic, is_mic_available

# Import module điều khiển phần cứng Serial (Matrix Mini R4)
from serial_controller import (
    start_serial_listener_thread,
    stop_serial_listener,
    perform_speech_gesture_start,
    perform_speech_gesture_end,
    send_command,
    get_serial_status,
    is_serial_connected,
    CMD_PRESENT,
    CMD_DOWN,
    CMD_WAVE,
    CMD_BACKWARD,
)

# Quản lý trạng thái & Chống lặp chào dồn dập
_query_lock = threading.Lock()
_last_interaction_time = time.time()
WAKE_UP_COOLDOWN = 35.0  # Tối thiểu 35 giây sau khi tương tác mới cho phép cảm biến chào khách mới


def print_banner():
    """Hiển thị giao diện khởi động chuyên nghiệp."""
    curr_voice = get_current_voice()
    serial_info = get_serial_status()
    mic_info = "Khả dụng" if is_mic_available() else "Không tìm thấy Micro"

    banner = f"""
================================================================================
     ROBOT HƯỚNG DẪN VIÊN TRIỂN LÃM VĂN HÓA (AI CULTURAL GUIDE v6.0 PRO)
              Trường THPT Quốc Học Quy Nhơn - Tỉnh Bình Định
================================================================================
  * Chế độ hoạt động: 🎙️ Voice-to-Voice (Đàm thoại Giọng nói qua Micro) [{mic_info}]
  * AI Core: Google Gemini Flash (Phản hồi tức thì < 200ms)
  * Voice Engine: Động cơ phát giọng nói thời gian thực (Zero Latency)
  * Giọng đọc mặc định: [{curr_voice}]
  * Smart Cache: Tra cứu tri thức đa tầng (0ms Latency)
  * Matrix Mini R4: Kết nối phần cứng động cơ [{serial_info}]
================================================================================
  [Quy trình tương tác]
    1. Khi phát hiện khách mới: Robot chào đón 1 lần duy nhất.
    2. Chờ khách hỏi trong 15 giây qua Micro.
    3. Trả lời tức thì & cử động tay theo nội dung thuyết minh.
    4. Nói "tạm biệt" hoặc nhấn Ctrl+C để kết thúc.
================================================================================
"""
    print(banner)


def process_user_query(user_input: str) -> None:
    """
    Xử lý luồng dữ liệu câu hỏi với cơ chế:
      1. Kích hoạt động cơ Matrix Mini R4: Giơ tay thuyết trình ('P') ngay lập tức.
      2. Tra cứu Smart Cache hoặc gọi Gemini Flash Streaming.
      3. Phát âm thanh thời gian thực qua Loa.
      4. Phân tích nội dung để cử động kết thúc (vẫy tay tạm biệt/tiến lên/hạ tay).
      * Có cơ chế khóa độc quyền (Query Lock) để KHÔNG BAO GIỜ bị nói chồng chéo.
    """
    global _last_interaction_time
    if not user_input or not user_input.strip():
        return

    # Khóa độc quyền: tránh trường hợp cảm biến và Micro cùng kích hoạt một lúc
    if not _query_lock.acquire(blocking=False):
        return

    try:
        _last_interaction_time = time.time()
        print(f"\n[DU KHÁCH]: {user_input}")
        start_time = time.time()

        # BƯỚC 1: KÍCH HOẠT CỬ CHỈ ĐỘNG CƠ - Giơ tay thuyết trình ('P') ngay lập tức
        perform_speech_gesture_start()

        answer = ""
        # BƯỚC 2: Tra cứu Smart Cache (0ms)
        cached_answer = check_cache(user_input)

        if cached_answer:
            answer = cached_answer
            elapsed = (time.time() - start_time) * 1000
            print(f"[CACHE HIT] Phản hồi tức thì từ Cache ({elapsed:.1f}ms):")
            print(f"\n[ROBOT]: {answer}\n")
            speak(answer, play_alert=False)
        else:
            # BƯỚC 3: Khởi tạo Token-to-Speech Realtime Pipeline
            print(f"[AI STREAMING] Đang phản hồi trực tiếp...")
            print(f"\n[ROBOT]: ", end="", flush=True)

            pipeline = create_speech_pipeline()

            def print_and_stream_token(token: str):
                sys.stdout.write(token)
                sys.stdout.flush()
                pipeline.feed_token(token)

            api_start = time.time()
            answer = ask_gemini(user_input, stream_callback=print_and_stream_token)
            api_elapsed = (time.time() - api_start) * 1000
            print(f"\n\n[TỐC ĐỘ PHẢN HỒI]: Hoàn tất trong {api_elapsed:.0f}ms.")
            
            # Báo hiệu dòng token từ Gemini đã kết thúc
            pipeline.finish()
            
            # Tự động lưu vào Dynamic LRU Cache
            if answer and answer.strip():
                add_to_dynamic_cache(user_input, answer)

            # Chờ phát âm thanh hoàn tất trước khi đón lượt tiếp theo
            pipeline.wait_until_done()

        # BƯỚC 4: ĐỒNG BỘ CỬ CHỈ KẾT THÚC CHO ĐỘNG CƠ R4
        perform_speech_gesture_end(answer)
        _last_interaction_time = time.time()
        print(f"[HOÀN TẤT] Đang lắng nghe câu hỏi tiếp theo từ khách hàng (chờ 15s)...")

    finally:
        _query_lock.release()


def on_hardware_wake_up():
    """
    Hàm xử lý tự động khi cảm biến R4 phát hiện có khách (WAKE_UP).
    Có cơ chế Cooldown thông minh để KHÔNG lặp lại câu chào liên tục khi khách đang đứng trước mặt.
    """
    global _last_interaction_time
    now = time.time()

    # 1. Nếu Robot đang nói hoặc đang xử lý -> Bỏ qua
    if is_speaking() or _query_lock.locked():
        return

    # 2. Nếu vừa mới tương tác/chào khách trong khoảng thời gian Cooldown -> Bỏ qua, tránh lặp lại
    if now - _last_interaction_time < WAKE_UP_COOLDOWN:
        return

    _last_interaction_time = now
    print("\n🔔 [PHẦN CỨNG] Cảm biến Matrix Mini R4 phát hiện du khách mới đến gần!")
    greeting_query = "Hãy chào đón và giới thiệu ngắn gọn trong 1 câu thân thiện về triển lãm cho khách tham quan mới đến."
    process_user_query(greeting_query)


def main():
    """Hàm điều khiển chính của Robot (Chuyên dụng Voice-to-Voice)."""
    global _last_interaction_time

    # 1. Khởi động luồng nền giao tiếp phần cứng Serial (Matrix Mini R4)
    start_serial_listener_thread(on_wake_up_callback=on_hardware_wake_up)

    print_banner()

    initial_greeting = "Xin chào quý khách! Tôi là robot hướng dẫn viên triển lãm văn hóa. Rất hân hạnh được phục vụ bạn."
    print(f"[ROBOT]: {initial_greeting}\n")
    try:
        perform_speech_gesture_start()
        # Phát lời chào mở đầu tuần tự và đợi phát xong để không bị chồng chéo
        speak(initial_greeting, play_alert=False)
        perform_speech_gesture_end(initial_greeting)
    except Exception as e:
        print(f"[Cảnh báo Loa]: {e}")

    _last_interaction_time = time.time()
    print("\n>>> ĐÃ SẴN SÀNG CHẾ ĐỘ ĐÀM THOẠI GIỌNG NÓI (VOICE-TO-VOICE) <<<\n")

    idle_count = 0  # Đếm số chu kỳ 15s không có ai nói

    while True:
        try:
            print("\n" + "-" * 60)
            # Đảm bảo Robot phát xong lời chào/thuyết minh trước khi kích hoạt Micro
            wait_until_speaking_done()

            # Chờ khách nói trong 15 giây
            user_input = listen_from_mic(timeout=15, phrase_time_limit=30)

            if not user_input:
                # Khách chưa nói gì trong 15 giây
                idle_count += 1
                if idle_count == 1:
                    # Sau 15 giây đầu tiên im lặng, Robot hỏi gợi ý nhẹ 1 lần
                    prompt_text = "Quý khách có cần tôi hỗ trợ tìm hiểu thêm về hiện vật nào không ạ? Hãy nói vào Microphone nhé."
                    print(f"\n[ROBOT (Gợi ý)]: {prompt_text}\n")
                    perform_speech_gesture_start()
                    speak(prompt_text, play_alert=False)
                    perform_speech_gesture_end(prompt_text)
                    _last_interaction_time = time.time()
                elif idle_count >= 3:
                    # Sau nhiều chu kỳ (hơn 45s) không có tiếng nói -> Khách có thể đã rời đi, hạ tay nghỉ
                    send_command(CMD_DOWN)
                    idle_count = 0
                continue

            # Khi khách có nói -> reset chu kỳ im lặng
            idle_count = 0
            _last_interaction_time = time.time()

            cmd = user_input.lower().strip()
            if any(kw in cmd for kw in ["tạm biệt", "bye", "dừng lại", "kết thúc", "thoát"]):
                farewell = "Cảm ơn quý khách đã tham quan triển lãm. Kính chúc quý khách thật nhiều sức khỏe và niềm vui!"
                print(f"\n[ROBOT]: {farewell}")
                perform_speech_gesture_start()
                speak(farewell)
                perform_speech_gesture_end(farewell)
                print("\n[HỆ THỐNG]: Đã kết thúc phiên làm việc. Tạm biệt!\n")
                stop_serial_listener()
                break

            process_user_query(user_input)

        except KeyboardInterrupt:
            print("\n\n[HỆ THỐNG]: Đã ngắt bởi người dùng (Ctrl+C). Tạm biệt!")
            stop_serial_listener()
            sys.exit(0)
        except Exception as ex:
            print(f"\n[LỖI HỆ THỐNG]: Đã xảy ra lỗi: {ex}")


if __name__ == "__main__":
    main()
