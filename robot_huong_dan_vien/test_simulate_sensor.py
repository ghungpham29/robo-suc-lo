"""
DỰ ÁN: ROBOT HƯỚNG DẪN VIÊN TRIỂN LÃM VĂN HÓA
File: test_simulate_sensor.py (Giả lập tín hiệu cảm biến WAKE_UP để kiểm tra toàn bộ luồng)
"""

import os
import sys

# Thiết lập đường dẫn
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from serial_controller import handle_wake_up

def main():
    print("=" * 70)
    print(" GIẢ LẬP TÍN HIỆU CẢM BIẾN TỪ MATRIX MINI R4 (TEST MODE)")
    print("=" * 70)
    print("Nhấn [ENTER] để giả lập có khách tham quan tới gần (WAKE_UP)...")
    print("Gõ 'exit' hoặc bấm Ctrl+C để thoát.\n")

    while True:
        try:
            cmd = input("Bấm [ENTER] để kích hoạt WAKE_UP > ")
            if cmd.strip().lower() == "exit":
                break
            
            print("\n>>> ĐANG KÍCH HOẠT QUY TRÌNH TIẾP ĐÓN KHÁCH...")
            handle_wake_up()
            print("\n>>> HOÀN TẤT MỘT LƯỢT TƯƠNG TÁC!\n" + "-" * 70)
        except KeyboardInterrupt:
            print("\nĐã dừng chương trình test.")
            break
        except Exception as e:
            print(f"[Lỗi test]: {e}")

if __name__ == "__main__":
    main()
