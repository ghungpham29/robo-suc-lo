"""
DỰ ÁN: ROBOT HƯỚNG DẪN VIÊN TRIỂN LÃM VĂN HÓA
File: serial_controller.py (Cầu nối Giao tiếp Serial - Máy tính <-> Bo mạch Matrix Mini R4)

Nhiệm vụ của module này:
- Mở và duy trì kết nối Serial (USB) tới bo mạch điều khiển động cơ Matrix Mini R4.
- Lắng nghe liên tục tín hiệu "WAKE_UP" gửi lên từ R4 khi cảm biến phát hiện có khách.
- Cung cấp API điều khiển cử chỉ động cơ đồng bộ cho main.py (hoặc chạy độc lập):
  * perform_speech_gesture_start(): Robot đưa tay lên tư thế thuyết trình ('P').
  * perform_speech_gesture_end(): Phân tích câu trả lời để vẫy tay ('W') + lùi ('B'), tiến lên ('F') + hạ tay ('D'), hoặc hạ tay ('D').
- Hỗ trợ chạy ngầm song song (Background Daemon Thread) không làm gián đoạn luồng chính.
- Tự phục hồi (auto-reconnect) khi cáp USB bị rút hoặc mất kết nối đột ngột.
"""

import os
import sys
import time
import threading
from typing import Callable, Optional

import serial  # pyserial
import serial.tools.list_ports
from dotenv import load_dotenv

# Hỗ trợ chạy độc lập: đảm bảo có thể import package "core" (ai_brain.py, voice.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

load_dotenv()

# Import các hàm AI & Âm thanh CÓ SẴN của dự án
from core.ai_brain import ask_gemini
from core.voice import speak

# =============================================================================
# CẤU HÌNH KẾT NỐI SERIAL
# =============================================================================
SERIAL_PORT = os.getenv("MATRIX_R4_PORT", "auto")
BAUDRATE = 115200
SERIAL_TIMEOUT = 0.1
RECONNECT_DELAY_SECONDS = 3
WAKE_UP_SIGNAL = "WAKE_UP"

# Các mã lệnh động cơ gửi xuống R4 (1 ký tự theo giao thức)
CMD_PRESENT = "P"   # Đưa 1 tay lên tư thế chuẩn bị thuyết trình / chỉ trỏ
CMD_WAVE = "W"       # Vẫy 2 tay liên tục để chào tạm biệt
CMD_BACKWARD = "B"   # Lùi lại một chút
CMD_FORWARD = "F"    # Tiến lên một chút (mời khách tham quan tiếp)
CMD_DOWN = "D"        # Hạ tay xuống, trở về tư thế nghỉ

# Từ khóa nhận diện NGỮ CẢNH KHÁCH RỜI ĐI trong câu trả lời của AI
FAREWELL_KEYWORDS = ["tạm biệt", "hẹn", "rời đi", "cảm ơn", "chào tạm biệt", "hẹn gặp lại"]

# Từ khóa nhận diện NGỮ CẢNH MỜI KHÁCH THAM QUAN TIẾP
CONTINUE_KEYWORDS = ["mời", "tiếp tục", "tham quan", "khám phá", "chiêm ngưỡng", "phía trước"]

# Đối tượng kết nối Serial & Luồng toàn cục
ser: Optional[serial.Serial] = None
_serial_lock = threading.Lock()
_listener_thread: Optional[threading.Thread] = None
_stop_listener_event = threading.Event()
_on_wake_up_callback: Optional[Callable[[], None]] = None
_last_wake_up_time: float = 0.0


def auto_detect_serial_port() -> Optional[str]:
    """
    Tự động quét các cổng COM đang cắm trên máy để tìm bo mạch Matrix Mini R4 / Arduino / USB Serial.
    """
    try:
        ports = list(serial.tools.list_ports.comports())
    except Exception:
        return None

    if not ports:
        return None

    # Ưu tiên 1: Thiết bị có VID Arduino (2341) hoặc Matrix Mini R4
    for p in ports:
        if getattr(p, "vid", None) == 0x2341 or (p.hwid and "VID:PID=2341" in p.hwid):
            print(f"[Serial] Đã tự động phát hiện bo mạch Arduino/Matrix Mini R4 tại cổng: {p.device}")
            return p.device

    # Ưu tiên 2: Cổng USB Serial thông thường (trừ cổng Bluetooth COM ảo)
    for p in ports:
        desc = (p.description or "").lower()
        if "bluetooth" not in desc and ("usb" in desc or "ch340" in desc or "cp210" in desc or "ftdi" in desc or "serial" in desc):
            print(f"[Serial] Đã tự động phát hiện thiết bị USB Serial tại cổng: {p.device} ({p.description})")
            return p.device

    # Ưu tiên 3: Chọn cổng bất kỳ không phải Bluetooth
    for p in ports:
        desc = (p.description or "").lower()
        if "bluetooth" not in desc:
            return p.device

    return ports[0].device if ports else None


def is_serial_connected() -> bool:
    """Kiểm tra xem kết nối Serial tới R4 có đang mở hay không."""
    global ser
    with _serial_lock:
        return ser is not None and ser.is_open


def get_serial_status() -> str:
    """Trả về chuỗi thông tin trạng thái cổng Serial để hiển thị giao diện."""
    global ser
    with _serial_lock:
        if ser is not None and ser.is_open:
            return f"Đã kết nối [{ser.port} - {BAUDRATE}bps]"
        return "Chưa kết nối (Tự động dò tìm nền...)"


def connect_serial_once(silent: bool = False) -> bool:
    """
    Thực hiện thử kết nối 1 lần tới bo mạch Matrix Mini R4.
    Trả về True nếu kết nối thành công, False nếu thất bại.
    """
    global ser
    with _serial_lock:
        if ser is not None and ser.is_open:
            return True

    target_port = SERIAL_PORT
    if target_port == "auto" or not target_port:
        target_port = auto_detect_serial_port()

    if not target_port:
        if not silent:
            print(f"[Serial] Không tìm thấy cổng COM nào khả dụng cho Matrix Mini R4.")
        return False

    try:
        new_ser = serial.Serial(target_port, BAUDRATE, timeout=SERIAL_TIMEOUT)
        time.sleep(2)  # Chờ bo mạch khởi động lại sau khi mở kết nối DTR
        try:
            new_ser.reset_input_buffer()
        except Exception:
            pass
        with _serial_lock:
            ser = new_ser
        print(f"[Serial] Đã kết nối thành công tới Matrix Mini R4 tại cổng {target_port} (Baudrate: {BAUDRATE}).")
        return True
    except serial.SerialException as e:
        if not silent:
            print(f"[Serial] Không thể mở cổng '{target_port}': {e}")
        with _serial_lock:
            ser = None
        return False


def init_serial() -> Optional[serial.Serial]:
    """
    Mở kết nối Serial tới Matrix Mini R4 (dùng cho chế độ chạy độc lập).
    Sẽ liên tục thử lại mỗi 3 giây cho đến khi kết nối thành công.
    """
    while True:
        if connect_serial_once(silent=False):
            return ser
        print(f"[Serial] Vui lòng cắm cáp USB bo Matrix Mini R4. Đang thử lại sau {RECONNECT_DELAY_SECONDS}s...")
        time.sleep(RECONNECT_DELAY_SECONDS)


def send_command(cmd: str) -> bool:
    """
    Gửi một mã lệnh điều khiển động cơ (1 ký tự) xuống bo mạch Matrix Mini R4.
    Trả về True nếu gửi thành công, False nếu chưa kết nối hoặc có lỗi.
    """
    global ser
    with _serial_lock:
        if ser is None or not ser.is_open:
            print(f"[Serial][CẢNH BÁO] Chưa có kết nối tới Matrix Mini R4 -> Không thể gửi lệnh '{cmd}'.")
            return False
        try:
            # Gửi mã lệnh kèm ký tự xuống dòng và ép đẩy dữ liệu qua cổng USB ngay lập tức (flush)
            payload = f"{cmd.strip()}\n".encode("utf-8")
            ser.write(payload)
            ser.flush()
            print(f"[Serial][GỬI LỆNH R4] -> '{cmd.strip()}'")
            return True
        except serial.SerialException as e:
            print(f"[Serial][LỖI GỬI LỆNH] Có thể cáp USB đã bị rút: {e}")
            try:
                ser.close()
            except Exception:
                pass
            ser = None
            return False


# =============================================================================
# ĐỒNG BỘ CỬ CHỈ ĐỘNG CƠ CHO TOÀN DỰ ÁN
# =============================================================================
def perform_speech_gesture_start() -> None:
    """
    Robot giơ 1 tay lên ('P') tư thế chuẩn bị thuyết trình ngay khi bắt đầu tiếp nhận câu hỏi.
    """
    send_command(CMD_PRESENT)


def perform_speech_gesture_end(response_text: str) -> None:
    """
    Phân tích nội dung câu trả lời để điều khiển động cơ thực hiện cử chỉ kết thúc phù hợp.
    """
    if not response_text:
        send_command(CMD_DOWN)
        return

    noi_dung = response_text.lower()
    is_farewell = any(keyword in noi_dung for keyword in FAREWELL_KEYWORDS)
    is_continue = any(keyword in noi_dung for keyword in CONTINUE_KEYWORDS)

    if is_farewell:
        # Ngữ cảnh khách chuẩn bị rời đi -> Vẫy 2 tay chào tạm biệt ('W'), sau đó lùi lại ('B') rồi hạ tay ('D')
        print("[Phân tích Cử chỉ] Phát hiện từ khóa TẠM BIỆT -> Vẫy tay ('W') rồi Lùi lại ('B').")
        send_command(CMD_WAVE)
        time.sleep(1.5)
        send_command(CMD_BACKWARD)
        time.sleep(1.0)
        send_command(CMD_DOWN)
    elif is_continue:
        # Ngữ cảnh mời khách tiếp tục tham quan -> Tiến lên ('F') rồi hạ tay ('D')
        print("[Phân tích Cử chỉ] Phát hiện từ khóa MỜI THAM QUAN -> Tiến lên ('F') rồi Hạ tay ('D').")
        send_command(CMD_FORWARD)
        time.sleep(1.0)
        send_command(CMD_DOWN)
    else:
        # Trường hợp thông thường -> Hạ tay về tư thế nghỉ ('D')
        send_command(CMD_DOWN)


# =============================================================================
# XỬ LÝ SỰ KIỆN "WAKE_UP" - CÓ KHÁCH THAM QUAN MỚI
# =============================================================================
def handle_wake_up(query: Optional[str] = None) -> None:
    """
    Kịch bản xử lý độc lập khi R4 báo hiệu có khách đến gần (WAKE_UP).
    """
    print("\n[Sự kiện] Nhận tín hiệu WAKE_UP -> Phát hiện khách tham quan mới.")
    perform_speech_gesture_start()

    cau_hoi = query or "Hãy chào đón và giới thiệu tổng quan về triển lãm cho khách tham quan mới đến."
    try:
        ket_qua = ask_gemini(cau_hoi)
    except Exception as e:
        print(f"[AI Brain][LỖI MẠNG/API]: Không lấy được câu trả lời từ Gemini - {e}")
        send_command(CMD_DOWN)
        return

    if not ket_qua or not ket_qua.strip():
        send_command(CMD_DOWN)
        return

    speak(ket_qua)
    perform_speech_gesture_end(ket_qua)


# =============================================================================
# LUỒNG LẮNG NGHE SERIAL NỀN (BACKGROUND DAEMON THREAD)
# =============================================================================
def _background_serial_worker(on_wake_up_callback: Optional[Callable[[], None]] = None) -> None:
    """Hàm chạy ngầm trong background thread để liên tục giữ kết nối và đọc cổng Serial."""
    global ser
    while not _stop_listener_event.is_set():
        try:
            if not is_serial_connected():
                connect_serial_once(silent=True)
                if not is_serial_connected():
                    time.sleep(RECONNECT_DELAY_SECONDS)
                    continue

            with _serial_lock:
                if ser is None or not ser.is_open:
                    continue
                raw_line = ser.readline()

            if not raw_line:
                continue

            signal = raw_line.decode("utf-8", errors="ignore").strip()
            if not signal:
                continue

            if signal == WAKE_UP_SIGNAL:
                global _last_wake_up_time
                now = time.time()
                # Chống nhận dồn dập tín hiệu từ cảm biến phần cứng (Debounce tối thiểu 15s)
                if now - _last_wake_up_time >= 15.0:
                    _last_wake_up_time = now
                    print(f"\n[Matrix Mini R4] Nhận tín hiệu cảm biến: {WAKE_UP_SIGNAL}")
                    if on_wake_up_callback:
                        on_wake_up_callback()
                    else:
                        handle_wake_up()
            else:
                print(f"[Serial][NHẬN]: {signal}")

        except serial.SerialException:
            with _serial_lock:
                try:
                    if ser is not None:
                        ser.close()
                except Exception:
                    pass
                ser = None
            time.sleep(RECONNECT_DELAY_SECONDS)
        except Exception:
            time.sleep(0.5)


def start_serial_listener_thread(on_wake_up_callback: Optional[Callable[[], None]] = None) -> threading.Thread:
    """
    Khởi động luồng nền để duy trì kết nối Serial và lắng nghe tín hiệu WAKE_UP từ R4.
    Đảm bảo main.py chạy song song mượt mà, không bị block.
    """
    global _listener_thread, _stop_listener_event, _on_wake_up_callback
    _on_wake_up_callback = on_wake_up_callback
    _stop_listener_event.clear()

    if _listener_thread is None or not _listener_thread.is_alive():
        _listener_thread = threading.Thread(
            target=_background_serial_worker,
            args=(on_wake_up_callback,),
            name="SerialListenerThread",
            daemon=True,
        )
        _listener_thread.start()
        print("[Serial] Đã kích hoạt luồng kết nối phần cứng Matrix Mini R4 chạy song song.")

    return _listener_thread


def stop_serial_listener() -> None:
    """Dừng luồng Serial và giải phóng cổng COM an toàn."""
    global ser
    _stop_listener_event.set()
    with _serial_lock:
        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass
            ser = None


def main_loop():
    """Vòng lặp chính khi chạy độc lập file serial_controller.py."""
    init_serial()
    print("[Robot] Sẵn sàng lắng nghe tín hiệu từ Matrix Mini R4 (chờ 'WAKE_UP')...\n")
    try:
        _background_serial_worker()
    except KeyboardInterrupt:
        print("\n[Hệ thống] Đã dừng chương trình Serial Controller (Ctrl+C).")
    finally:
        stop_serial_listener()


if __name__ == "__main__":
    main_loop()
