# coding: utf-8
"""
=============================================================================
=== CÔNG CỤ TEST CHUYÊN BIỆT: THUYẾT MINH 11 TƯỢNG VĂN HÓA CHĂM PA ===
Chức năng:
  - Chọn nhanh số tượng (1 -> 11) để nghe Robot đọc bài thuyết trình ngay lập tức.
  - Không cần kết nối phần cứng Arduino/Robot.
  - Test tốc độ và chất lượng âm thanh phát ra loa.
=============================================================================
"""

import os
import sys
import time

# Fix UTF-8
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    if hasattr(sys.stdout, "reconfigure"):
        getattr(sys.stdout, "reconfigure")(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        getattr(sys.stderr, "reconfigure")(encoding="utf-8", errors="replace")
except Exception:
    pass

_this_dir = os.path.dirname(os.path.abspath(__file__))
_robot_dir = os.path.join(_this_dir, "robot_huong_dan_vien")
for p in [_this_dir, _robot_dir]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

from voice_controller import STATUES_PRESENTATION, speak_guaranteed, get_champa_answer


def main():
    print("\n" + "═" * 70)
    print("       🏺 CÔNG CỤ TEST THUẦN THUYẾT MINH 11 TƯỢNG CHĂM PA 🏺")
    print("═" * 70)
    print("DANH SÁCH 11 TƯỢNG CÓ SẴN:")
    for num in range(1, 12):
        title = STATUES_PRESENTATION[num]["title"]
        print(f"  [{num:2d}] {title}")

    print("\n  [ 0] Lời chào mở đầu Kalepic")
    print("  [ w] Lời chào tạm biệt (Wave)")
    print("  [ q] Thoát chương trình")
    print("═" * 70)

    while True:
        try:
            choice = input("\n👉 Nhập số tượng (1-11), '0', 'w' hoặc gõ câu hỏi: ").strip()
            if not choice:
                continue

            if choice.lower() in ["q", "quit", "exit"]:
                print("Đã thoát công cụ test.")
                break

            # Trường hợp 1: Nhập số từ 1 đến 11
            if choice.isdigit() and int(choice) in STATUES_PRESENTATION:
                statue_num = int(choice)
                statue = STATUES_PRESENTATION[statue_num]
                title = statue["title"]
                content = statue["content"]

                print("\n" + "─" * 70)
                print(f"🏺 ĐANG PHÁT THUYẾT MINH: {title}")
                print("─" * 70)
                print(f"{content}\n")
                print("🔊 Đang đọc ra loa...")
                t0 = time.time()
                speak_guaranteed(content)
                print(f"✅ Hoàn tất phát âm thanh ({time.time() - t0:.2f}s)!")

            # Trường hợp 2: Lời chào mở đầu
            elif choice == "0":
                welcome = "Xin chào quý khách! Tôi là Kalepic, robot hướng dẫn viên văn hóa Chăm Pa & Bình Định. Rất vui được đồng hành cùng quý khách!"
                print(f"\n[KALEPIC]: {welcome}")
                print("🔊 Đang đọc ra loa...")
                speak_guaranteed(welcome)

            # Trường hợp 3: Tạm biệt
            elif choice.lower() in ["w", "tam biet", "tạm biệt"]:
                goodbye = "Tạm biệt quý khách! Kalepic rất vinh dự được đồng hành cùng quý khách trong chuyến tham quan văn hóa Chăm Pa. Kính chúc quý khách thật nhiều niềm vui và sức khỏe! Hẹn gặp lại quý khách!"
                print(f"\n[KALEPIC]: {goodbye}")
                print("🔊 Đang đọc ra loa...")
                speak_guaranteed(goodbye)

            # Trường hợp 4: Gõ câu hỏi tự do
            else:
                print(f"\n🔍 Đang tra cứu câu hỏi: '{choice}'...")
                ans = get_champa_answer(choice)
                print(f"\n[TRẢ LỜI]:\n{ans}\n")
                print("🔊 Đang đọc ra loa...")
                speak_guaranteed(ans)

        except KeyboardInterrupt:
            print("\nĐã dừng.")
            break


if __name__ == "__main__":
    main()
