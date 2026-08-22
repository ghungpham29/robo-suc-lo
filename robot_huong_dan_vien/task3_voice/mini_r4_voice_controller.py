# coding: utf-8
"""
=== MINI R4 VOICE & AI CONTROLLER ===
Điều khiển Robot Mini R4 bằng Giọng nói Tiếng Việt qua cổng Serial/Bluetooth.
Tích hợp AI Brain (Gemini Flash & Knowledge Base) để trả lời tri thức khi không phải khẩu lệnh vận động.
Cấu hình 4 Động cơ:
  - M1: Chiều thuận (+speed)
  - M2: Đảo chiều (-speed)
  - M3: Đảo chiều (-speed)
  - M4: Đảo chiều (-speed)
"""

import os
import sys
import time
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
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

# Import các hàm nhận dạng từ voice_todo
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from voice_todo import (
    MOTION_MAP,
    init_recognizer,
    get_microphone,
    record_audio,
    recognize_speech_vietnamese,
    get_action
)

# Tích hợp AI Brain (Gemini Flash)
try:
    from core.ai_brain import ask_gemini
    _AI_BRAIN_AVAILABLE = True
except Exception:
    _AI_BRAIN_AVAILABLE = False

# ==========================================
# CẤU HÌNH ĐỘNG CƠ MINI R4
# ==========================================
# Hệ số chiều quay của từng Motor:
# 1 = quay thuận, -1 = đảo ngược chiều quay
MOTOR_POLARITY = {
    "M1": 1,   # M1 bình thường
    "M2": -1,  # M2 bị ngược
    "M3": -1,  # M3 bị ngược
    "M4": -1   # M4 bị ngược
}

DEFAULT_SPEED = 70  # Công suất phần trăm (0 - 100)


class MiniR4SerialBridge:
    """Quản lý kết nối Serial với bo mạch Mini R4"""
    def __init__(self, port=None, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_connected = False
        self.lock = threading.Lock()

    def connect(self, port=None):
        if port:
            self.port = port
        if not self.port:
            return False, "Chưa chọn cổng COM"

        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            self.is_connected = True
            time.sleep(1.5)  # Chờ Arduino/Mini R4 khởi động lại sau khi mở kết nối DTR
            return True, f"Đã kết nối thành công tới {self.port}"
        except Exception as e:
            self.is_connected = False
            self.serial_conn = None
            return False, f"Lỗi mở cổng {self.port}: {e}"

    def disconnect(self):
        with self.lock:
            if self.serial_conn and self.serial_conn.is_open:
                try:
                    self.send_raw("STOP")
                    self.serial_conn.close()
                except Exception:
                    pass
            self.serial_conn = None
            self.is_connected = False

    def send_raw(self, cmd_str):
        """Gửi chuỗi lệnh thô xuống Arduino/Mini R4 qua Serial"""
        if not self.is_connected or not self.serial_conn:
            return False
        with self.lock:
            try:
                payload = (cmd_str.strip() + "\n").encode("utf-8")
                self.serial_conn.write(payload)
                self.serial_conn.flush()
                return True
            except Exception as e:
                print(f"[Serial Bridge Error] {e}")
                self.is_connected = False
                return False

    def execute_motion(self, action_name, speed=DEFAULT_SPEED):
        """
        Chuyển đổi tên action thành công suất 4 Motor có bù dấu chiều quay
        và gửi lệnh Serial xuống Mini R4.
        """
        # 1. Xác định công suất danh định (Trước khi nhân hệ số chiều quay)
        # (m1_raw, m2_raw, m3_raw, m4_raw)
        raw_powers = {
            "Forward": (speed, speed, speed, speed),
            "Move_fast": (100, 100, 100, 100),
            "Backward": (-speed, -speed, -speed, -speed),
            "TurnLeft": (-speed, speed, -speed, speed),
            "TurnRight": (speed, -speed, speed, -speed),
            "OneStepMoveLeft": (-speed, speed, speed, -speed),
            "OneStepMoveRight": (speed, -speed, -speed, speed),
            "Stop": (0, 0, 0, 0),
            "Reset": (0, 0, 0, 0),
            "EnterEnergySavingSquat": (0, 0, 0, 0),
            "ExitEnergySavingReset": (0, 0, 0, 0),
        }

        # Nếu không có trong từ điển vận động cơ bản -> dừng motor
        m1_raw, m2_raw, m3_raw, m4_raw = raw_powers.get(action_name, (0, 0, 0, 0))

        # 2. Áp dụng hệ số đảo chiều phần cứng MOTOR_POLARITY
        m1_actual = m1_raw * MOTOR_POLARITY["M1"]
        m2_actual = m2_raw * MOTOR_POLARITY["M2"]
        m3_actual = m3_raw * MOTOR_POLARITY["M3"]
        m4_actual = m4_raw * MOTOR_POLARITY["M4"]

        # 3. Đóng gói lệnh gửi xuống Mini R4 theo giao thức: SET:M1:M2:M3:M4
        # Ví dụ: SET:70:-70:-70:-70
        cmd_str = f"SET:{m1_actual}:{m2_actual}:{m3_actual}:{m4_actual}"
        self.send_raw(cmd_str)

        return m1_actual, m2_actual, m3_actual, m4_actual


class MiniR4VoiceApp:
    """Giao diện điều khiển Voice Controller kết hợp AI Brain cho Mini R4"""
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Mini R4 Voice & AI Controller (Task 3 Pro)")
        self.root.geometry("820x650")
        self.root.configure(bg="#0f172a")

        self.bridge = MiniR4SerialBridge()
        self.status_queue = queue.Queue()
        self.stop_event = threading.Event()

        self._build_ui()
        self._process_queue()
        self.start_voice_thread()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        # 1. Top Bar: Connection Controls
        top_frame = tk.Frame(self.root, bg="#1e293b", padx=15, pady=12)
        top_frame.pack(fill=tk.X)

        lbl_title = tk.Label(
            top_frame,
            text="MINI R4 VOICE & AI CONTROLLER",
            font=("Segoe UI", 13, "bold"),
            fg="#38bdf8",
            bg="#1e293b"
        )
        lbl_title.pack(side=tk.LEFT)

        self.btn_refresh = tk.Button(
            top_frame,
            text="🔄 Quét COM",
            command=self.refresh_ports,
            bg="#334155",
            fg="white",
            relief="flat",
            padx=10
        )
        self.btn_refresh.pack(side=tk.RIGHT, padx=5)

        self.btn_connect = tk.Button(
            top_frame,
            text="Kết nối COM",
            command=self.toggle_connect,
            bg="#22c55e",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=12
        )
        self.btn_connect.pack(side=tk.RIGHT, padx=5)

        self.cb_ports = ttk.Combobox(top_frame, width=15, state="readonly")
        self.cb_ports.pack(side=tk.RIGHT, padx=5)
        self.refresh_ports()

        # 2. Main Display Area
        main_area = tk.Frame(self.root, bg="#0f172a", padx=20, pady=12)
        main_area.pack(fill=tk.BOTH, expand=True)

        # Speech Card
        speech_card = tk.Frame(main_area, bg="#020617", bd=1, relief="solid", padx=20, pady=16)
        speech_card.pack(fill=tk.X, pady=(0, 10))

        self.lbl_speech_title = tk.Label(
            speech_card,
            text="🎙️ GIỌNG NÓI NHẬN DẠNG ĐƯỢC",
            font=("Segoe UI", 11, "bold"),
            fg="#94a3b8",
            bg="#020617"
        )
        self.lbl_speech_title.pack()

        self.lbl_speech = tk.Label(
            speech_card,
            text="Đang lắng nghe...",
            font=("Segoe UI", 20, "bold"),
            fg="#f8fafc",
            bg="#020617",
            wraplength=750,
            justify="center"
        )
        self.lbl_speech.pack(pady=8)

        self.lbl_action = tk.Label(
            speech_card,
            text="Trạng thái: Sẵn sàng nhận lệnh ('đi thẳng', 'lùi', 'rẽ trái', 'dừng') hoặc câu hỏi tri thức...",
            font=("Segoe UI", 11),
            fg="#38bdf8",
            bg="#020617",
            wraplength=750,
            justify="center"
        )
        self.lbl_action.pack()

        # AI Answer Card
        ai_card = tk.LabelFrame(
            main_area,
            text=" 🤖 Phản hồi Tri thức AI Brain (Gemini Flash) ",
            font=("Segoe UI", 10, "bold"),
            fg="#a855f7",
            bg="#1e293b",
            padx=12,
            pady=8
        )
        ai_card.pack(fill=tk.X, pady=(0, 10))

        self.txt_ai_answer = tk.Label(
            ai_card,
            text="Hỏi bất kỳ câu hỏi nào về văn hóa, lịch sử hoặc câu lệnh điều khiển robot...",
            font=("Segoe UI", 10),
            fg="#e2e8f0",
            bg="#1e293b",
            wraplength=740,
            justify="left"
        )
        self.txt_ai_answer.pack(fill=tk.X, pady=4)

        # 3. Motor Dashboard
        motor_frame = tk.LabelFrame(
            main_area,
            text=" Trạng thái 4 Motor (M1 Thuận | M2, M3, M4 Đảo chiều) ",
            font=("Segoe UI", 10, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
            padx=12,
            pady=10
        )
        motor_frame.pack(fill=tk.BOTH, expand=True)

        self.motor_labels = {}
        for idx, m in enumerate(["M1", "M2", "M3", "M4"]):
            card = tk.Frame(motor_frame, bg="#0f172a", bd=1, relief="ridge", padx=10, pady=8)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

            tag = " [Thuận]" if m == "M1" else " [Đảo]"
            lbl_name = tk.Label(card, text=f"{m}{tag}", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#0f172a")
            lbl_name.pack()

            lbl_val = tk.Label(card, text="0 %", font=("Segoe UI", 18, "bold"), fg="#22c55e", bg="#0f172a")
            lbl_val.pack(pady=4)
            self.motor_labels[m] = lbl_val

        # Quick Test Buttons
        test_frame = tk.Frame(self.root, bg="#1e293b", padx=15, pady=8)
        test_frame.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Label(test_frame, text="Nút Test nhanh:", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#1e293b").pack(side=tk.LEFT, padx=5)

        for act_name, label_text in [("Forward", "⬆️ Đi Thẳng"), ("Backward", "⬇️ Lùi"), ("TurnLeft", "⬅️ Rẽ Trái"), ("TurnRight", "➡️ Rẽ Phải"), ("Stop", "⏹️ Dừng")]:
            btn = tk.Button(
                test_frame,
                text=label_text,
                command=lambda a=act_name: self.on_manual_trigger(a),
                bg="#334155",
                fg="white",
                relief="flat",
                padx=8,
                pady=2
            )
            btn.pack(side=tk.LEFT, padx=3)

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.cb_ports['values'] = ports
        if ports:
            self.cb_ports.current(0)
        else:
            self.cb_ports.set("Không có COM")

    def toggle_connect(self):
        if not self.bridge.is_connected:
            port = self.cb_ports.get()
            if not port or port.startswith("Không"):
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn cổng COM của Mini R4 (USB hoặc Bluetooth)!")
                return
            success, msg = self.bridge.connect(port)
            if success:
                self.btn_connect.config(text="Ngắt kết nối", bg="#ef4444")
                self.status_queue.put(("status", (f"🟢 {msg}", "#22c55e")))
            else:
                messagebox.showerror("Lỗi kết nối", msg)
        else:
            self.bridge.disconnect()
            self.btn_connect.config(text="Kết nối COM", bg="#22c55e")
            self.update_motor_ui(0, 0, 0, 0)
            self.status_queue.put(("status", ("🟡 Đã ngắt kết nối Serial", "#eab308")))

    def on_manual_trigger(self, action):
        m1, m2, m3, m4 = self.bridge.execute_motion(action)
        self.update_motor_ui(m1, m2, m3, m4)
        self.lbl_action.config(text=f"⚙️ Lệnh thực thi: {action} (M1:{m1}, M2:{m2}, M3:{m3}, M4:{m4})", fg="#38bdf8")

    def update_motor_ui(self, m1, m2, m3, m4):
        vals = {"M1": m1, "M2": m2, "M3": m3, "M4": m4}
        for m, v in vals.items():
            color = "#22c55e" if v > 0 else ("#ef4444" if v < 0 else "#94a3b8")
            self.motor_labels[m].config(text=f"{v} %", fg=color)

    def _process_queue(self):
        while not self.status_queue.empty():
            try:
                msg_type, payload = self.status_queue.get_nowait()
                if msg_type == "status":
                    text, color = payload
                    self.lbl_action.config(text=text, fg=color)
                elif msg_type == "speech":
                    text, action = payload
                    self.lbl_speech.config(text=f'"{text}"', fg="#ffffff")
                    if action:
                        m1, m2, m3, m4 = self.bridge.execute_motion(action)
                        self.update_motor_ui(m1, m2, m3, m4)
                        self.lbl_action.config(
                            text=f"🎯 Lệnh vận động: {action} -> (M1:{m1}%, M2:{m2}%, M3:{m3}%, M4:{m4}%)",
                            fg="#4ade80"
                        )
                    else:
                        self.lbl_action.config(text="🤖 Đang hỏi AI Brain...", fg="#c084fc")
                        # Gửi câu hỏi sang luồng xử lý AI Brain
                        self._ask_ai_async(text)
                elif msg_type == "ai_answer":
                    answer = payload
                    self.txt_ai_answer.config(text=answer, fg="#f1f5f9")
                    self.lbl_action.config(text="✅ AI Brain đã phản hồi thành công.", fg="#38bdf8")
            except Exception:
                break

        if not self.stop_event.is_set():
            self.root.after(100, self._process_queue)

    def _ask_ai_async(self, question):
        """Hỏi AI Brain ngầm trong thread để không block giao diện GUI"""
        def worker():
            if _AI_BRAIN_AVAILABLE:
                try:
                    ans = ask_gemini(question)
                    self.status_queue.put(("ai_answer", ans))
                except Exception as e:
                    self.status_queue.put(("ai_answer", f"Lỗi AI: {e}"))
            else:
                self.status_queue.put(("ai_answer", "Không tìm thấy module core.ai_brain."))
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def start_voice_thread(self):
        def voice_loop():
            recognizer = init_recognizer()
            recognizer.energy_threshold = 400
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 1.2

            try:
                with get_microphone() as source:
                    self.status_queue.put(("status", ("🟡 Đang cân bằng âm thanh môi trường...", "#facc15")))
                    recognizer.adjust_for_ambient_noise(source, duration=1.2)
                    self.status_queue.put(("status", ("🟢 Đang lắng nghe giọng nói... Hãy ra lệnh hoặc đặt câu hỏi!", "#4ade80")))

                    while not self.stop_event.is_set():
                        try:
                            audio = record_audio(recognizer, source)
                            self.status_queue.put(("status", ("🔵 Đang nhận dạng giọng nói tiếng Việt...", "#38bdf8")))
                            text = recognize_speech_vietnamese(recognizer, audio)
                            if text and len(text.strip()) > 1:
                                action = get_action(text)
                                self.status_queue.put(("speech", (text, action)))
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError as e:
                            self.status_queue.put(("status", (f"⚠️ Lỗi Google Speech API: {e}", "#f87171")))
                            time.sleep(1)
                        except sr.WaitTimeoutError:
                            pass
            except Exception as e:
                self.status_queue.put(("status", (f"❌ Lỗi Microphone: {e}", "#f87171")))

        t = threading.Thread(target=voice_loop, daemon=True)
        t.start()

    def on_close(self):
        self.stop_event.set()
        self.bridge.disconnect()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MiniR4VoiceApp(root)
    root.mainloop()
