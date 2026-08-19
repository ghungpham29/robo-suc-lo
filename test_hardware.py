"""
=============================================================================
DỰ ÁN: ROBOT HƯỚNG DẪN VIÊN TRIỂN LÃM VĂN HÓA
File: test_hardware.py (Công cụ kiểm tra phần cứng tương tác)
Bo mạch: MATRIX Mini / Arduino UNO R4 (Cổng COM13)
=============================================================================
"""

import sys
import time
import serial
import serial.tools.list_ports

BAUDRATE = 115200


def find_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if getattr(p, "vid", None) == 0x2341 or (p.hwid and "VID:PID=2341" in p.hwid):
            return p.device
    for p in ports:
        desc = (p.description or "").lower()
        if "usb" in desc or "ch340" in desc or "cp210" in desc or "serial" in desc:
            return p.device
    return "COM13"


def read_arduino_lines(ser):
    """Đọc dữ liệu từ Arduino một cách an toàn, không bị crash nếu cáp bị lỏng."""
    try:
        if ser and ser.is_open and ser.in_waiting:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            return line
    except Exception:
        pass
    return None


def main():
    port = find_arduino_port()
    print("=" * 65)
    print("       🤖 CÔNG CỤ TEST PHẦN CỨNG ROBOT MATRIX MINI R4 🤖")
    print("=" * 65)
    print(f"[*] Cổng COM phát hiện: {port} | Tốc độ: {BAUDRATE} bps")
    print("[*] Đang mở kết nối Serial...")

    try:
        ser = serial.Serial(port, BAUDRATE, timeout=0.5)
        time.sleep(2)  # Đợi vi điều khiển reset sau khi mở cổng
        print(f"[OK] Đã kết nối thành công tới {port}!")
    except Exception as e:
        print(f"[LỖI] Không thể mở cổng {port}: {e}")
        print("Vui lòng kiểm tra cáp USB hoặc đóng Arduino Serial Monitor nếu đang mở.")
        return

    # Đọc thông điệp khởi động ban đầu từ Arduino
    start_time = time.time()
    while time.time() - start_time < 1.5:
        line = read_arduino_lines(ser)
        if line:
            print(f"  [Arduino -> PC]: {line}")
        time.sleep(0.05)

    menu = """
-------------------------------------------------------------
DANH SÁCH LỆNH KIỂM TRA:
  [1] Lệnh 'T' - Tự động quét Servo (Test Sweep)
  [2] Lệnh 'P' - Giơ tay thuyết trình (Present)
  [3] Lệnh 'W' - Vẫy 2 tay chào tạm biệt (Wave)
  [4] Lệnh 'D' - Hạ 2 tay về tư thế nghỉ (Down)
  [5] Lệnh 'F' - Tiến lên 0.8 giây (Forward)
  [6] Lệnh 'B' - Lùi lại 0.8 giây (Backward)
  [7] Chế độ giám sát Cảm biến Siêu âm (Đón khách WAKE_UP)
  [0] Thoát chương trình
-------------------------------------------------------------
Nhập lựa chọn của bạn (0-7): """

    while True:
        line = read_arduino_lines(ser)
        while line:
            print(f"\n  [Arduino -> PC]: {line}")
            line = read_arduino_lines(ser)

        try:
            choice = input(menu).strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[*] Đang đóng kết nối và thoát...")
            break

        if choice == "1":
            print("[PC -> Arduino] Gửi lệnh 'T' (Test Sweep)...")
            try:
                ser.write(b"T\n")
            except Exception as e:
                print(f"[Lỗi gửi lệnh]: {e}")
        elif choice == "2":
            print("[PC -> Arduino] Gửi lệnh 'P' (Present - Giơ tay)...")
            try:
                ser.write(b"P\n")
            except Exception as e:
                print(f"[Lỗi gửi lệnh]: {e}")
        elif choice == "3":
            print("[PC -> Arduino] Gửi lệnh 'W' (Wave - Vẫy tay)...")
            try:
                ser.write(b"W\n")
            except Exception as e:
                print(f"[Lỗi gửi lệnh]: {e}")
        elif choice == "4":
            print("[PC -> Arduino] Gửi lệnh 'D' (Down - Hạ tay)...")
            try:
                ser.write(b"D\n")
            except Exception as e:
                print(f"[Lỗi gửi lệnh]: {e}")
        elif choice == "5":
            print("[PC -> Arduino] Gửi lệnh 'F' (Forward - Tiến lên)...")
            try:
                ser.write(b"F\n")
            except Exception as e:
                print(f"[Lỗi gửi lệnh]: {e}")
        elif choice == "6":
            print("[PC -> Arduino] Gửi lệnh 'B' (Backward - Lùi lại)...")
            try:
                ser.write(b"B\n")
            except Exception as e:
                print(f"[Lỗi gửi lệnh]: {e}")
        elif choice == "7":
            print("\n[*] ĐANG GIÁM SÁT CẢM BIẾN SIÊU ÂM (Đưa tay trước cảm biến <= 80cm để kích hoạt)...")
            print("[*] Nhấn Ctrl+C để quay lại menu.\n")
            try:
                while True:
                    line = read_arduino_lines(ser)
                    if line:
                        if line == "WAKE_UP":
                            print("  🎉 [PHÁT HIỆN KHÁCH] -> Nhận tín hiệu: WAKE_UP từ cảm biến!")
                        else:
                            print(f"  [Arduino -> PC]: {line}")
                    time.sleep(0.05)
            except KeyboardInterrupt:
                print("\n[*] Đã thoát chế độ giám sát cảm biến.")
        elif choice == "0":
            print("[*] Đang đóng cổng COM và thoát...")
            break
        else:
            if choice.upper() in ["P", "W", "D", "F", "B", "T"]:
                cmd = choice.upper()
                print(f"[PC -> Arduino] Gửi lệnh trực tiếp '{cmd}'...")
                try:
                    ser.write(f"{cmd}\n".encode("utf-8"))
                except Exception as e:
                    print(f"[Lỗi gửi lệnh]: {e}")
            else:
                print("[!] Lựa chọn không hợp lệ (Vui lòng chỉ nhập số từ 0 đến 7).")

        time.sleep(0.5)
        line = read_arduino_lines(ser)
        while line:
            print(f"  [Arduino Phản Hồi]: {line}")
            line = read_arduino_lines(ser)

    try:
        ser.close()
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Đã dừng chương trình.")
