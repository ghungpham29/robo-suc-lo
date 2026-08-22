"""
=============================================================================
DỰ ÁN: ROBOT HƯỚNG DẪN VIÊN TRIỂN LÃM VĂN HÓA (KALEPIC)
File: test_ai.py (Kiểm thử Toàn diện Module AI Brain & Tích hợp Task 3 Voice)
=============================================================================
Tính năng:
  - Kiểm tra kết nối AI Brain (Google Gemini Flash & Knowledge Base).
  - Tích hợp trích xuất khẩu lệnh vận động từ Task 3 Voice (MOTION_MAP, get_action).
  - Chế độ tương tác hỏi đáp liên tục qua bàn phím.
"""

import os
import sys

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            getattr(sys.stdout, "reconfigure")(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Thêm đường dẫn import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
task3_dir = os.path.join(current_dir, "task3_voice")
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if task3_dir not in sys.path:
    sys.path.insert(0, task3_dir)

from core.ai_brain import ask_gemini

# Import Task 3 Voice
try:
    from voice_todo import get_action, MOTION_MAP
    _TASK3_AVAILABLE = True
except Exception:
    try:
        from task3_voice.voice_todo import get_action, MOTION_MAP
        _TASK3_AVAILABLE = True
    except Exception:
        _TASK3_AVAILABLE = False


def process_query(user_text: str):
    """Xử lý câu hỏi kết hợp nhận diện khẩu lệnh Task 3 và AI Brain."""
    print(f"\n[NGƯỜI DÙNG]: {user_text}")
    print("-" * 65)

    # 1. Kiểm tra khẩu lệnh vận động từ Task 3 Voice
    if _TASK3_AVAILABLE:
        action = get_action(user_text)
        if action:
            print(f"🎯 [TASK 3 VOICE DETECTED]: Khẩu lệnh điều khiển -> '{action}'")
        else:
            print(f"ℹ️  [TASK 3 VOICE]: Không phải khẩu lệnh vận động.")

    # 2. Truy vấn AI Brain (Gemini Flash & Tri thức)
    print("🤖 [AI BRAIN ĐANG SUY NGHĨ]...")
    try:
        response = ask_gemini(user_text)
        print(f"\n[ROBOT KALEPIC]:\n{response}\n")
    except Exception as e:
        print(f"[!] Lỗi AI Brain: {e}\n")
    print("=" * 65)


def main():
    print("=" * 65)
    print("   🤖 KIỂM THỬ MODULE AI BRAIN & TASK 3 VOICE (KALEPIC) 🤖")
    print("=" * 65)

    # 1. Test mẫu mặc định
    cau_hoi_mau = "Ý nghĩa của cồng chiêng Tây Nguyên là gì?"
    print(f"[*] CHẠY KIỂM THỬ MẪU:")
    process_query(cau_hoi_mau)

    # 2. Test mẫu khẩu lệnh Task 3
    khau_lenh_mau = "Robot hãy đi thẳng và nhanh lên nhé"
    print(f"[*] CHẠY KIỂM THỬ KHẨU LỆNH TASK 3:")
    process_query(khau_lenh_mau)

    # 3. Chế độ tương tác qua bàn phím
    print("\n👉 BẠN CÓ THỂ NHẬP BẤT KỲ CÂU HỎI HOẶC KHẨU LỆNH NÀO ĐỂ TEST:")
    print("   (Gõ 'q' hoặc 'exit' để thoát)\n")

    while True:
        try:
            user_input = input("👉 Nhập câu hỏi / khẩu lệnh: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[*] Tạm biệt!")
            break

        if not user_input:
            continue

        if user_input.lower() in ["q", "exit", "quit"]:
            print("[*] Đã thoát chương trình test AI. Tạm biệt!")
            break

        process_query(user_input)


if __name__ == "__main__":
    main()
