# coding: utf-8
"""
=============================================================================
=== ROBOT KALEPIC - ĐIỀU KHIỂN BẰNG GIỌNG NÓI & THUYẾT MINH 11 TƯỢNG ===
Tính năng nổi bật:
  1. Khẩu lệnh di chuyển 11 Tượng: "tượng số 1" -> "tượng số 11":
     -> Gửi lệnh di chuyển (1-11) qua Serial đến Matrix Mini R4.
     -> Robot di chuyển tới vị trí tượng -> Tự động gửi lệnh 'P' (Giơ tay thuyết trình).
     -> Hiển thị bài thuyết minh lên Màn hình Đen & Đọc to rõ qua loa bằng giọng đọc AI.
     -> Sau khi đọc xong bài thuyết trình -> Tự động gửi lệnh 'D' (Hạ tay về vị trí nghỉ).
  2. Khẩu lệnh "tạm biệt" / "bye":
     -> Gửi lệnh 'W' (Vẫy tay chào) qua Serial đến robot.
     -> Phát âm thanh chào tạm biệt to rõ qua loa & hiển thị lên màn hình.
  3. Màn hình Đen Fullscreen (nhấn [ESC] / [F11] để thu nhỏ / phóng to).
  4. Hỏi đáp mọi câu hỏi tri thức Chăm Pa và di sản Bình Định.
=============================================================================
"""

import os
import re
import sys
import time
import queue
import threading
import tkinter as tk
import speech_recognition as sr
import serial
import serial.tools.list_ports

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
_task3_dir = os.path.join(_robot_dir, "task3_voice")

for p in [_root_dir, _robot_dir, _task3_dir, _this_dir]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

# Import module Nhận dạng giọng nói
try:
    from robot_huong_dan_vien.task3_voice.voice_todo import (
        MOTION_MAP,
        init_recognizer,
        get_microphone,
        record_audio,
        recognize_speech_vietnamese,
        get_action
    )
except ImportError:
    try:
        from task3_voice.voice_todo import (  # type: ignore
            MOTION_MAP,
            init_recognizer,
            get_microphone,
            record_audio,
            recognize_speech_vietnamese,
            get_action
        )
    except ImportError:
        from voice_todo import (  # type: ignore
            MOTION_MAP,
            init_recognizer,
            get_microphone,
            record_audio,
            recognize_speech_vietnamese,
            get_action
        )

# Import module Tri thức Chăm Pa, AI Brain & Loa TTS
try:
    from robot_huong_dan_vien.core.knowledge_base import search_knowledge_base
    from robot_huong_dan_vien.core.ai_brain import ask_gemini
    from robot_huong_dan_vien.core.voice import speak
    _HAS_CHAMPA = True
except Exception:
    try:
        from core.knowledge_base import search_knowledge_base  # type: ignore
        from core.ai_brain import ask_gemini  # type: ignore
        from core.voice import speak  # type: ignore
        _HAS_CHAMPA = True
    except Exception:
        _HAS_CHAMPA = False


# =============================================================================
# DANH MỤC 11 BÀI THUYẾT TRÌNH TƯỢNG VĂN HÓA CHĂM PA
# =============================================================================
STATUES_PRESENTATION = {
    1: {
        "title": "TƯỢNG SỐ 1: BẢO VẬT ĐIÊU KHẮC CHĂM PA",
        "duration": 5.0,
        "content": "Kính chào quý khách đến với Triển lãm Văn hóa Chăm Pa. Đây là điểm khởi đầu của hành trình chiêm ngưỡng 11 kiệt tác điêu khắc sa thạch cổ đại, nơi hội tụ tinh hoa nghệ thuật Ấn Độ giáo và bản sắc độc đáo của vương triều Chăm Pa qua các thời kỳ lịch sử."
    },
    2: {
        "title": "TƯỢNG SỐ 2: THẦN SHIVA",
        "duration": 8.5,
        "content": "Đại thần Shiva được tôn là vị thần bảo hộ tối cao. Phù điêu thần ngồi thiền định tạc nổi trên khối đá hình lá đề tại trán cửa tháp nhằm trấn giữ, xua đuổi tà ma và khẳng định uy quyền vương triều. Hình tượng tiến hóa từ vẻ đẹp mảnh mai thời sơ kỳ sang nét uy nghiêm, dồn khối vững chắc với râu rậm, mắt lồi ở thời Tháp Mẫm, trước khi phẳng hóa ở giai đoạn muộn."
    },
    3: {
        "title": "TƯỢNG SỐ 3: TƯỢNG SƯ TỬ",
        "duration": 11.0,
        "content": "Bắt nguồn từ Ấn Độ, tượng sư tử biểu trưng cho vương quyền, sức mạnh chiến thắng cái ác và sự bảo vệ. Được đục đẽo công phu từ khối sa thạch đặt tại cửa ra vào hoặc góc tháp, sư tử đóng vai trò xua đuổi tà ma khỏi không gian linh thiêng. Tạo hình tiến hóa từ dáng vẻ tự nhiên thời sơ kỳ vươn tới đỉnh cao lực lưỡng, hoành tráng với mắt lồi, nanh nhọn thời Tháp Mẫm."
    },
    4: {
        "title": "TƯỢNG SỐ 4: GARUDA DIỆT RẮN",
        "duration": 5.5,
        "content": "Bắt nguồn từ thần thoại về mối thù truyền kiếp với loài rắn Naga, phù điêu Garuda diệt rắn đặt tại góc hoặc cửa tháp biểu trưng cho sự cân bằng vũ trụ giữa ánh sáng và bóng tối. Tác phẩm thể hiện kỹ thuật đục đẽo sa thạch nguyên khối đỉnh cao thời Tháp Mẫm với tư thế võ sĩ ghì siết, cắn xé Naga bạo liệt trước khi chuyển thành phù điêu phẳng mang tính nghi lễ ở giai đoạn muộn."
    },
    5: {
        "title": "TƯỢNG SỐ 5: ĐẦU CHIM THẦN GARUDA",
        "duration": 3.5,
        "content": "Chế tác vào thế kỷ 12-13, đầu Garuda là cấu kiện trang trí góc mái hoặc vòm cửa đền tháp. Sự kết hợp độc đáo giữa nét dữ tợn của chim thần và tai, bờm thủy quái Makara mang ý nghĩa xua đuổi tà ma và biểu thị sự cân bằng vũ trụ. Tác phẩm thể hiện đỉnh cao cơ bắp hoành tráng với mỏ quặp, mắt lồi ở thời Tháp Mẫm trước khi suy tàn từ thế kỷ 14."
    },
    6: {
        "title": "TƯỢNG SỐ 6: SƯ TỬ NÂNG ĐỠ BỆ",
        "duration": 3.5,
        "content": "Đóng vai trò như Atlas phương Đông, sư tử gánh vác bệ thờ và đền tháp nhằm phong ấn tà khí dưới lòng đất. Nghệ nhân tạc tượng tròn 3D ở chân tháp với thế hai chân khuỳnh, hai tay giơ cao dồn lực nâng đỡ, lồng ngực phồng to căng tràn sức mạnh. Từ hình khối nhỏ thời sơ kỳ, linh vật tiến hóa thành hình mẫu lực lưỡng, cường điệu hóa cơ bắp ở thời Tháp Mẫm."
    },
    7: {
        "title": "TƯỢNG SỐ 7: THẦN HỘ PHÁP MÃ CHÚA (DVARAPALA)",
        "duration": 6.0,
        "content": "Là chiến binh gác cửa uy nghiêm trên trụ đá vuông lối vào tháp, Thần Hộ pháp trấn giữ không gian linh thiêng và xua đuổi tà ma. Thần hiện lên ở tư thế quỳ chiến đấu, tay ghì chặt đao chùy cùng khuôn mặt dạ xoa dữ tợn với mắt lồi, nanh nhọn. Tác phẩm đạt đỉnh cao cơ bắp hung tợn, dứt khoát ở thời Tháp Mẫm trước khi bị giản lược thành các nét rạch phẳng ở giai đoạn muộn."
    },
    8: {
        "title": "TƯỢNG SỐ 8: PHÙ ĐIÊU GARUDA",
        "duration": 9.0,
        "content": "Là vua loài chim và biểu tượng của ánh sáng, Garuda mang sứ mệnh tiêu diệt loài rắn Naga. Phù điêu lá đề trán cửa tháp Dương Long mang dấu ấn giao thoa Champa - Khmer với tạo hình Garuda đầu to, má phính đang giang tay, dùng mỏ kẹp chặt khống chế hai con rắn Naga đối xứng. Nghệ thuật tạc Garuda đạt đỉnh cao sức mạnh bạo liệt, cơ bắp cuồn cuộn ở thời Tháp Mẫm và Dương Long."
    },
    9: {
        "title": "TƯỢNG SỐ 9: NỮ THẦN SARASVATI",
        "duration": 8.5,
        "content": "Nữ thần Sarasvati đại diện cho tri thức, nghệ thuật và sự thanh khiết. Phù điêu lá đề vòm cửa tháp chạm khắc nữ thần vô cùng uyển chuyển với 3 đầu, 4 cánh tay cầm búp sen, tràng hạt ngự trên bệ hoa sen để ban phước lành. Tác phẩm tôn vinh trọn vẹn đường cong nữ tính, đạt đỉnh cao quyền năng và đa diện ở thời Tháp Mẫm - Châu Thành."
    },
    10: {
        "title": "TƯỢNG SỐ 10: NỮ THẦN MAHISASURAMARDINI",
        "duration": 9.5,
        "content": "Đại diện cho năng lượng nữ tính tối thượng Shakti, Nữ thần Durga mang sức mạnh chư thần để tiêu diệt quỷ trâu. Tác phẩm chạm nổi cao tại vòm cửa tháp thể hiện nữ thần trong tư thế múa chiến đấu Tandava sống động với 10 cánh tay giương cao binh khí. Hình tượng đạt đỉnh cao bạo liệt, căng tràn sức lực ở thời Tháp Mẫm trước khi dần phẳng hóa ở thời kỳ muộn."
    },
    11: {
        "title": "TƯỢNG SỐ 11: THẦN BRAHMA",
        "duration": 8.5,
        "content": "Brahma là vị thần Sáng tạo đại diện cho tri thức và sự khởi đầu. Bức phù điêu nổi cao 3D với 3 mặt, 8 cánh tay ngự trên trán cửa tháp mang ý nghĩa thanh lọc u tối, thể hiện nụ cười mỉm thanh thản mang đậm dấu ấn nghệ thuật Angkor. Từ vị thế phụ trợ thời sơ kỳ, Brahma vươn lên thành nhân vật trung tâm uy quyền thời Dương Long trước khi bị khắc phẳng ở giai đoạn muộn."
    },
}


# =============================================================================
# HÀM PHÁT HIỆN KHẨU LỆNH TƯỢNG 1-11 & TẠM BIỆT
# =============================================================================
def detect_statue_command(text: str):
    """Phát hiện khẩu lệnh di chuyển đến Tượng số 1 đến Tượng số 11."""
    if not text:
        return None
    text_lower = text.lower().strip()

    word_to_num = {
        "mười một": 11, "11": 11, "mười": 10, "10": 10,
        "chín": 9, "9": 9, "tám": 8, "8": 8,
        "bảy": 7, "bẩy": 7, "7": 7, "sáu": 6, "6": 6,
        "năm": 5, "5": 5, "bốn": 4, "tư": 4, "4": 4,
        "ba": 3, "3": 3, "hai": 2, "2": 2,
        "một": 1, "mốt": 1, "1": 1
    }

    for word, num in word_to_num.items():
        patterns = [
            rf"\btượng\s*(?:số)?\s*{word}\b",
            rf"\bhướng\s*dẫn\s*tượng\s*(?:số)?\s*{word}\b",
            rf"\bđi\s*(?:đến|tới)?\s*tượng\s*(?:số)?\s*{word}\b",
            rf"\bthuyết\s*minh\s*tượng\s*(?:số)?\s*{word}\b",
            rf"\bgiới\s*thiệu\s*tượng\s*(?:số)?\s*{word}\b",
        ]
        for pat in patterns:
            if re.search(pat, text_lower):
                return num
    return None


def detect_goodbye_command(text: str) -> bool:
    """Phát hiện khẩu lệnh tạm biệt để kích hoạt lệnh 'W' (Vẫy tay chào)."""
    if not text:
        return False
    text_lower = text.lower().strip()
    goodbye_phrases = [
        "tạm biệt", "tam biet", "chào tạm biệt", "tạm biệt robot",
        "bye", "goodbye", "hẹn gặp lại", "vẫy tay", "vẫy tay chào"
    ]
    return any(p in text_lower for p in goodbye_phrases)


# =============================================================================
# KẾT NỐI SERIAL MATRIX MINI R4 / ARDUINO
# =============================================================================
_serial_conn = None


def init_serial_connection():
    """Tự động kết nối cổng COM tới Matrix Mini R4 / Arduino."""
    global _serial_conn
    try:
        ports = list(serial.tools.list_ports.comports())
        target_port = None
        for p in ports:
            hwid = (p.hwid or "").upper()
            desc = (p.description or "").lower()
            if getattr(p, "vid", None) == 0x2341 or "VID:PID=2341" in hwid or "arduino" in desc or "matrix" in desc:
                target_port = p.device
                break
            if "bluetooth" not in desc and ("usb" in desc or "ch340" in desc or "cp210" in desc or "serial" in desc):
                target_port = p.device

        if not target_port and ports:
            target_port = ports[0].device

        if target_port:
            _serial_conn = serial.Serial(target_port, 115200, timeout=1)
            print(f"[Serial] ✅ Đã kết nối thành công tới phần cứng tại cổng: {target_port}")
            time.sleep(1.5)
            return True
        else:
            print("[Serial] ℹ️ Không phát hiện cổng COM phần cứng. Chạy ở chế độ mô phỏng ảo.")
            return False
    except Exception as e:
        print(f"[Serial] ℹ️ Chạy ở chế độ mô phỏng ({e}).")
        return False


def send_serial(cmd: str):
    """Gửi lệnh ký tự qua Serial tới Arduino (ví dụ '1', 'P', 'D', 'W')."""
    global _serial_conn
    clean_cmd = cmd.strip()
    print(f"[SERIAL SEND] >>> Lệnh: '{clean_cmd}'")
    if _serial_conn and _serial_conn.is_open:
        try:
            _serial_conn.write(f"{clean_cmd}\n".encode("utf-8"))
            _serial_conn.flush()
        except Exception as e:
            print(f"[!] Lỗi gửi Serial: {e}")


# =============================================================================
# HÀM PHÁT ÂM THANH TO RÕ QUA LOA (TTS)
# =============================================================================
def speak_guaranteed(text: str):
    """Phát âm thanh đảm bảo 100% bằng Edge-TTS / Kokoro qua Pygame."""
    if not text or not text.strip():
        return

    # 1. Thử gọi hàm speak chuẩn
    try:
        if _HAS_CHAMPA:
            speak(text, play_alert=False)
            return
    except Exception as e:
        print(f"[!] Thử speak tiêu chuẩn thất bại: {e}")

    # 2. Dự phòng trực tiếp Edge-TTS qua Pygame
    try:
        import asyncio, edge_tts, io, pygame
        async def _fetch_edge():
            comm = edge_tts.Communicate(text, "vi-VN-HoaiMyNeural", rate="+6%")
            bio = io.BytesIO()
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    bio.write(chunk["data"])
            bio.seek(0)
            return bio

        loop = asyncio.new_event_loop()
        bio = loop.run_until_complete(_fetch_edge())
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(bio)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)
    except Exception as e2:
        print(f"[!] Fallback Edge-TTS thất bại: {e2}")


def get_champa_answer(query: str) -> str:
    """Tra cứu câu trả lời chuẩn xác dựa trên toàn bộ bộ dữ liệu Chăm Pa & AI Brain."""
    if not query or len(query.strip()) == 0:
        return "Xin chào! Bạn có thể đặt bất kỳ câu hỏi nào về các di tích Chăm Pa, Tháp Đôi, Tháp Bánh Ít, Bảo vật Quốc gia nhé."

    q_lower = query.lower().strip()

    # Xử lý tức thì các câu chào hỏi & giới thiệu thông dụng (0ms)
    greetings = ["xin chào", "chào bạn", "chào robot", "hello", "hi robot", "chào"]
    if any(g in q_lower for g in greetings) and len(q_lower) < 25:
        return "Xin chào quý khách! Tôi là Kalepic - robot hướng dẫn viên văn hóa Chăm Pa & Bình Định. Quý khách muốn di chuyển đến Tượng số mấy (từ 1 đến 11) hoặc tìm hiểu về cụm tháp nào ạ?"

    if any(k in q_lower for k in ["bạn là ai", "bạn tên gì", "tên của bạn", "giới thiệu bản thân"]):
        return "Tôi là Kalepic, robot hướng dẫn viên triển lãm văn hóa Chăm Pa và di sản Bình Định. Tôi có thể dẫn đường tới 11 bức tượng và thuyết minh về các bảo vật điêu khắc đá Chăm Pa cổ đại!"

    if _HAS_CHAMPA:
        # 1. Tra cứu trực tiếp từ Knowledge Base (45 mục di tích & bảo vật)
        try:
            kb_ans = search_knowledge_base(query)
            if kb_ans and isinstance(kb_ans, str) and len(kb_ans.strip()) > 10:
                return kb_ans.strip()
        except Exception as e:
            print(f"[!] Lỗi tra cứu tri thức: {e}")

        # 2. Gọi AI Brain Gemini Flash
        try:
            gemini_ans = ask_gemini(query)
            if gemini_ans and len(gemini_ans.strip()) > 5:
                return gemini_ans.strip()
        except Exception as e:
            print(f"[!] Lỗi Gemini: {e}")

    return f"Về '{query}', đây là một nét đặc sắc trong văn hóa và lịch sử. Quý khách có thể yêu cầu: 'Tượng số 1', 'Tượng số 2' hoặc hỏi về Tháp Đôi, Tháp Bánh Ít nhé."


# =============================================================================
# GIAO DIỆN MÀN HÌNH ĐEN TRÀN MÀN HÌNH (FULLSCREEN BLACK SCREEN GUI)
# =============================================================================
class FullscreenBlackScreenGUI:
    """
    Giao diện màn hình đen tràn toàn màn hình:
    - Nửa trên: Câu hỏi của du khách vừa nói (chữ to màu trắng).
    - Nửa dưới: Câu trả lời thuyết minh Chăm Pa (chữ vàng sáng, to rõ).
    - Dưới cùng: Trạng thái micro và cử chỉ robot (P/D/W).
    - Nhấn phím [ESC] hoặc [F11] để thoát/bật chế độ tràn màn hình.
    """
    def __init__(self, root, stop_event, status_queue):
        self.root = root
        self.stop_event = stop_event
        self.status_queue = status_queue
        self.is_fullscreen = True

        self.root.title("Robot Kalepic - Voice Recognition Fullscreen")
        self.root.configure(bg="#000000")

        # Bật chế độ tràn màn hình đen
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", self._toggle_fullscreen)
        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<q>", lambda e: self._on_close())

        self._build_ui()

        # Ép cửa sổ hiển thị nổi bật lên màn hình
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(1000, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Configure>", self._on_resize)
        self.root.after(50, self._process_queue)

    def _toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if not self.is_fullscreen:
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            w, h = min(1100, screen_w - 50), min(750, screen_h - 50)
            x = (screen_w - w) // 2
            y = (screen_h - h) // 2
            self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # Container chính tràn toàn bộ màn hình đen
        self.main_frame = tk.Frame(self.root, bg="#000000", padx=50, pady=25)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # [1. NỬA TRÊN]: CÂU NÓI CỦA DU KHÁCH
        self.lbl_user_tag = tk.Label(
            self.main_frame,
            text="🎙️ DU KHÁCH VỪA HỎI / RA LỆNH:",
            font=("Segoe UI", 13, "bold"),
            fg="#38bdf8",
            bg="#000000"
        )
        self.lbl_user_tag.pack(anchor="center", pady=(10, 5))

        self.lbl_user_text = tk.Label(
            self.main_frame,
            text='"Đang lắng nghe câu lệnh từ bạn..."',
            font=("Segoe UI", 26, "bold"),
            fg="#ffffff",
            bg="#000000",
            wraplength=1200,
            justify="center"
        )
        self.lbl_user_text.pack(fill=tk.X, pady=(0, 15))

        # Đường kẻ phân cách mờ nhẹ
        separator = tk.Frame(self.main_frame, bg="#1e293b", height=2)
        separator.pack(fill=tk.X, padx=50, pady=(0, 15))

        # [2. NỬA DƯỚI]: CÂU TRẢ LỜI THUYẾT MINH CHĂM PA & ĐỌC RA LOA
        self.lbl_ai_tag = tk.Label(
            self.main_frame,
            text="🏺 ROBOT KALEPIC THUYẾT MINH TRI THỨC CHĂM PA:",
            font=("Segoe UI", 13, "bold"),
            fg="#facc15",
            bg="#000000"
        )
        self.lbl_ai_tag.pack(anchor="center", pady=(0, 8))

        # Khung văn bản thuần đen tự động bẻ dòng và hiển thị toàn bộ nội dung
        self.txt_ai_text = tk.Text(
            self.main_frame,
            font=("Segoe UI", 17),
            fg="#fef08a",
            bg="#000000",
            bd=0,
            highlightthickness=0,
            wrap="word",
            padx=20,
            pady=8
        )
        default_welcome = (
            "Xin chào quý khách! Tôi là Kalepic, robot hướng dẫn viên văn hóa Chăm Pa & Bình Định.\n\n"
            "👉 Quý khách hãy ra lệnh giọng nói:\n"
            "   • 'Tượng số 1' đến 'Tượng số 11' -> Robot di chuyển, giơ tay P, thuyết trình và hạ tay D!\n"
            "   • 'Tạm biệt' -> Robot vẫy tay chào W và nói lời tạm biệt!\n"
            "   • Hoặc hỏi bất kỳ câu hỏi nào về: Tháp Đôi, Tháp Bánh Ít, Bảo vật Quốc gia..."
        )
        self.txt_ai_text.insert("1.0", default_welcome)
        self.txt_ai_text.tag_configure("center", justify="center")
        self.txt_ai_text.tag_add("center", "1.0", "end")
        self.txt_ai_text.config(state="disabled")
        self.txt_ai_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # [3. ĐÁY MÀN HÌNH]: DÒNG TRẠNG THÁI
        self.lbl_footer = tk.Label(
            self.root,
            text="🟢 Micro đang bật... (Hãy nói 'Tượng số 1' hoặc 'Tạm biệt')",
            font=("Segoe UI", 11),
            fg="#4ade80",
            bg="#000000"
        )
        self.lbl_footer.pack(side=tk.BOTTOM, pady=15)

    def _on_resize(self, event=None):
        new_width = max(500, self.root.winfo_width() - 100)
        self.lbl_user_text.config(wraplength=new_width)

    def _on_close(self):
        self.stop_event.set()
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.stop()
        except Exception:
            pass
        self.root.destroy()

    def update_user_speech(self, text: str):
        length = len(text)
        if length <= 20:
            font_size = 32
        elif length <= 45:
            font_size = 26
        elif length <= 80:
            font_size = 22
        else:
            font_size = 18

        self.lbl_user_text.config(
            text=f'"{text}"',
            font=("Segoe UI", font_size, "bold"),
            fg="#ffffff"
        )

    def update_ai_response(self, text: str):
        length = len(text)
        if length <= 120:
            font_size = 20
        elif length <= 300:
            font_size = 17
        elif length <= 600:
            font_size = 15
        else:
            font_size = 13

        self.txt_ai_text.config(state="normal", font=("Segoe UI", font_size))
        self.txt_ai_text.delete("1.0", tk.END)
        self.txt_ai_text.insert("1.0", text)
        self.txt_ai_text.tag_configure("center", justify="center")
        self.txt_ai_text.tag_add("center", "1.0", "end")
        self.txt_ai_text.config(state="disabled")

    def _process_queue(self):
        while not self.status_queue.empty():
            try:
                msg_type, payload = self.status_queue.get_nowait()
                if msg_type == "status":
                    text, color = payload
                    self.lbl_footer.config(text=text, fg=color)
                elif msg_type == "user_speech":
                    self.update_user_speech(payload)
                elif msg_type == "ai_answer":
                    self.update_ai_response(payload)
            except Exception:
                break

        if not self.stop_event.is_set():
            self.root.after(50, self._process_queue)


# =============================================================================
# LUỒNG XỬ LÝ: NHẬN DIỆN GIỌNG NÓI -> ĐIỀU KHIỂN SERIAL -> THUYẾT TRÌNH
# =============================================================================
def start_voice_control(callback=None, stop_event=None, status_queue=None):
    """Luồng nhận diện giọng nói và điều khiển robot qua Serial."""
    print("\n" + "═" * 70)
    print("  🎤 ROBOT KALEPIC - ĐIỀU KHIỂN GIỌNG NÓI & THUYẾT MINH 11 TƯỢNG")
    print("═" * 70)

    def put_status(text, color):
        if status_queue:
            status_queue.put(("status", (text, color)))

    # 1. Khởi tạo kết nối Serial phần cứng
    init_serial_connection()

    recognizer = init_recognizer()
    recognizer.energy_threshold = 200
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 1.2

    put_status("🟡 Đang đo tạp âm môi trường (1.0s)... Vui lòng giữ im lặng", "#facc15")

    try:
        with get_microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source, duration=1.0)
            except Exception:
                pass

            put_status("🟢 Sẵn sàng nhận lệnh! (Hãy nói 'Tượng số 1' hoặc 'Tạm biệt')", "#4ade80")
            print("[VoiceCtrl] ✅ Microphone đã sẵn sàng! Bắt đầu lắng nghe...\n")

            while stop_event is None or not stop_event.is_set():
                try:
                    put_status("🟢 Đang lắng nghe... (Hãy ra lệnh hoặc đặt câu hỏi)", "#4ade80")
                    audio = record_audio(recognizer, source)

                    if audio is None:
                        continue

                    put_status("🔵 Đang dịch giọng nói qua Google API...", "#38bdf8")
                    text = recognize_speech_vietnamese(recognizer, audio)

                    if not text or len(text.strip()) < 2:
                        continue

                    user_query = text.strip()
                    print(f"\n[DU KHÁCH RA LỆNH]: \"{user_query}\"")

                    # Hiển thị câu nói của du khách lên Màn hình Đen
                    if status_queue:
                        status_queue.put(("user_speech", user_query))

                    # =========================================================
                    # TRƯỜNG HỢP 1: KHẨU LỆNH TƯỢNG SỐ 1 ĐẾN 11
                    # Quy trình: Di chuyển (1-11) -> Giơ tay 'P' -> Thuyết trình -> Hạ tay 'D'
                    # =========================================================
                    statue_num = detect_statue_command(user_query)
                    if statue_num and statue_num in STATUES_PRESENTATION:
                        statue_info = STATUES_PRESENTATION[statue_num]
                        title = str(statue_info["title"])
                        speech_content = str(statue_info["content"])
                        duration = float(statue_info["duration"])

                        print(f"\n>>> [KÍCH HOẠT LỆNH]: Di chuyển đến {title}")
                        put_status(f"🤖 Đang gửi lệnh di chuyển '{statue_num}' đến phần cứng...", "#38bdf8")

                        # BƯỚC 1: Gửi lệnh di chuyển qua Serial
                        send_serial(str(statue_num))
                        if status_queue:
                            status_queue.put(("ai_answer", f"🤖 Đang di chuyển đến {title}...\n(Thời gian ước tính: {duration:.1f}s)"))

                        # Đợi robot hoàn thành lộ trình di chuyển
                        time.sleep(duration)

                        # BƯỚC 2: Tự động thực hiện cử chỉ 'P' (Giơ tay thuyết trình)
                        print(">>> [CỬ CHỈ]: Tự động gửi lệnh 'P' (Giơ tay thuyết trình)")
                        send_serial("P")
                        time.sleep(0.5)

                        # BƯỚC 3: Hiển thị bài thuyết trình lên Màn hình Đen & Đọc to rõ ra loa
                        display_text = f"【{title}】\n\n{speech_content}"
                        if status_queue:
                            status_queue.put(("ai_answer", display_text))
                        print(f"[ROBOT KALEPIC THUYẾT MINH]:\n{display_text}\n")

                        put_status(f"🔊 Đang thuyết trình {title}...", "#f59e0b")
                        speak_guaranteed(speech_content)

                        # BƯỚC 4: Sau khi đọc xong, tự động gửi lệnh 'D' (Hạ tay về vị trí nghỉ)
                        print(">>> [CỬ CHỈ]: Tự động gửi lệnh 'D' (Hạ tay về vị trí nghỉ)")
                        send_serial("D")
                        time.sleep(0.5)

                        put_status(f"🟢 Đã hoàn thành thuyết trình {title}! Sẵn sàng nhận lệnh tiếp theo...", "#4ade80")
                        continue

                    # =========================================================
                    # TRƯỜNG HỢP 2: KHẨU LỆNH "TẠM BIỆT" -> GỬI LỆNH 'W' (VẪY TAY)
                    # =========================================================
                    if detect_goodbye_command(user_query):
                        print("\n>>> [KÍCH HOẠT LỆNH]: Tạm biệt -> Gửi lệnh 'W' (Vẫy tay)")
                        put_status("🤖 Đang thực hiện cử chỉ vẫy tay chào tạm biệt (W)...", "#22c55e")
                        send_serial("W")

                        goodbye_msg = "Tạm biệt quý khách! Kalepic rất vinh dự được đồng hành cùng quý khách trong chuyến tham quan văn hóa Chăm Pa. Kính chúc quý khách thật nhiều niềm vui và sức khỏe! Hẹn gặp lại quý khách!"
                        if status_queue:
                            status_queue.put(("ai_answer", f"👋 CHÀO TẠM BIỆT QUÝ KHÁCH!\n\n{goodbye_msg}"))
                        print(f"[ROBOT KALEPIC]:\n{goodbye_msg}\n")

                        speak_guaranteed(goodbye_msg)
                        put_status("🟢 Hoàn tất! Sẵn sàng lắng nghe tiếp...", "#4ade80")
                        continue

                    # =========================================================
                    # TRƯỜNG HỢP 3: CÂU HỎI TRI THỨC CHĂM PA & HỘI THOẠI KHÁC
                    # =========================================================
                    put_status("🧠 Đang tra cứu tri thức Chăm Pa...", "#c084fc")
                    answer = get_champa_answer(user_query)

                    if status_queue:
                        status_queue.put(("ai_answer", answer))
                    print(f"[ROBOT KALEPIC]:\n{answer}\n")

                    # Giơ tay nhẹ khi trả lời câu hỏi văn hóa
                    send_serial("P")
                    put_status("🔊 Robot đang đọc câu trả lời ra loa...", "#f59e0b")
                    speak_guaranteed(answer)
                    send_serial("D")

                    put_status("🟢 Hoàn tất! Đang lắng nghe câu hỏi tiếp theo...", "#4ade80")

                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"⚠️ Lỗi Google Speech API: {e}")
                    put_status(f"⚠️ Lỗi mạng Google Speech API: {e}", "#f87171")
                    time.sleep(1)
                except sr.WaitTimeoutError:
                    pass

    except OSError as e:
        print(f"[VoiceCtrl] ❌ Lỗi Microphone: {e}")
        put_status(f"❌ Lỗi Microphone: {e}", "#f87171")
    except KeyboardInterrupt:
        print("\n[VoiceCtrl] Dừng chương trình.")


def start_voice_gui(callback=None):
    """Khởi chạy Màn hình Đen Fullscreen và luồng giọng nói."""
    root = tk.Tk()
    stop_event = threading.Event()
    status_queue = queue.Queue()

    t = threading.Thread(
        target=start_voice_control,
        args=(callback, stop_event, status_queue),
        daemon=True
    )
    t.start()

    FullscreenBlackScreenGUI(root, stop_event, status_queue)
    root.mainloop()


if __name__ == "__main__":
    def test_callback(action):
        print(f"[Callback Motion]: {action}")

    start_voice_gui(callback=test_callback)
