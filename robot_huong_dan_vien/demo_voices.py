"""
Chương trình Thử nghiệm & Chuyển đổi 3 Giọng đọc AI Tiếng Việt Tinh tuyển (Kokoro-TTS)
  1. diem_trinh : Nữ - Truyền cảm, ấm áp, trang trọng (Tiêu chuẩn Hướng dẫn viên)
  2. mai_linh   : Nữ - Trẻ trung, trong trẻo, tự nhiên (Mặc định)
  3. thanh_dat  : Nam - Phóng khoáng, tự tin, rõ ràng (Giọng Nam tiêu chuẩn)
"""

import sys
import time
import os
from dotenv import load_dotenv, set_key

# Thiết lập UTF-8 cho Windows Terminal
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            getattr(sys.stdout, "reconfigure")(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

from core.voice import speak, set_voice, get_available_voices, get_current_voice

SAMPLE_CULTURAL = "Tháp Đôi gồm hai tháp: tháp lớn cao 20m và tháp nhỏ cao 18m, được xây dựng từ thế kỷ XII mang phong cách văn hóa Khmer thời kỳ Angkor và đạo Hindu thờ thần Shiva."


def main():
    while True:
        voices = get_available_voices()
        curr = get_current_voice()

        print("\n" + "=" * 76)
        print("       🎙️  STUDIO THỬ NGHIỆM 3 GIỌNG ĐỌC AI TINH TUYỂN (KOKORO-TTS)  🎙️")
        print("=" * 76)
        print(f"  Giọng hiện tại đang dùng: [{curr}]\n")
        print("  Danh sách 3 Giọng đọc:")
        
        voice_list = list(voices.items())
        for idx, (v_name, v_desc) in enumerate(voice_list, 1):
            tag = "⭐ (ĐANG CHỌN)" if v_name == curr else ""
            print(f"   {idx}. {v_name:12s} : {v_desc} {tag}")

        print("=" * 76)
        print("  LỰA CHỌN:")
        print("   • Nhập số (1-3)  : Nghe thử câu chào bằng giọng đó")
        print("   • Nhập 'all'     : Nghe lần lượt cả 3 giọng (Showcase)")
        print("   • Nhập 'doc'     : Nghe thử đoạn thuyết minh văn hóa có số đo và địa danh")
        print("   • Nhập 'save'    : Lưu giọng đang chọn làm mặc định vào file .env")
        print("   • Nhập 'exit'    : Thoát")
        print("=" * 76)

        choice = input("\nXin mời nhập lựa chọn: ").strip().lower()

        if choice in ["exit", "quit", "thoat", "0"]:
            print("\nĐã đóng Studio Thử giọng.\n")
            break
        elif choice == "all":
            for idx, (v_name, v_desc) in enumerate(voices.items(), 1):
                print(f"\n[{idx}/3] Đang phát thử giọng '{v_name}'...")
                set_voice(v_name)
                speak(f"Xin chào! Tôi là giọng đọc {v_name}. {v_desc}.", voice=v_name)
                time.sleep(0.3)
        elif choice == "doc":
            print(f"\n[THUYẾT MINH VĂN HÓA] Đang đọc bằng giọng: [{curr}]...")
            speak(SAMPLE_CULTURAL, voice=curr)
        elif choice == "save":
            set_key(".env", "KOKORO_VOICE", curr)
            print(f"\n✅ Đã lưu thành công giọng '[{curr}]' làm mặc định vào .env!")
        elif choice.isdigit() and 1 <= int(choice) <= len(voice_list):
            selected = voice_list[int(choice) - 1][0]
            set_voice(selected)
            print(f"\n[THỬ GIỌNG]: Đang phát giọng '{selected}'...")
            speak(f"Xin chào quý khách! Tôi là giọng đọc {selected}. Rất vui được đồng hành cùng bạn.", voice=selected)
        else:
            print("[Lỗi] Lựa chọn không hợp lệ.")


if __name__ == "__main__":
    main()
