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
    """Tự động tìm kiếm cổng COM của bo mạch Matrix Mini R4 / Arduino Uno R4."""
    try:
        ports = list(serial.tools.list_ports.comports())
    except Exception:
        return "COM13"

    # Ưu tiên 1: VID chuẩn Arduino / Matrix Mini R4 (2341)
    for p in ports:
        if getattr(p, "vid", None) == 0x2341 or (p.hwid and "VID:PID=2341" in p.hwid):
            return p.device

    # Ưu tiên 2: Cổng USB Serial
    for p in ports:
        desc = (p.description or "").lower()
        if "bluetooth" not in desc and ("usb" in desc or "ch340" in desc or "cp210" in desc or "serial" in desc):
            return p.device

    return "COM13"


def open_serial_connection(port, timeout=0.5, verbose=True):
    """Mở cổng Serial và khởi tạo an toàn."""
    try:
        ser = serial.Serial(port, BAUDRATE, timeout=timeout)
        ser.dtr = True
        ser.rts = True
        time.sleep(1.2)  # Chờ bo mạch ổn định sau khi mở cổng
        ser.reset_input_buffer()
        return ser
    except serial.SerialException as e:
        err_msg = str(e)
        if verbose:
            if "PermissionError" in err_msg or "Access is denied" in err_msg:
                print(f"\n[!] CẢNH BÁO: Cổng {port} đang bị ứng dụng khác chiếm giữ (Ví dụ: Arduino IDE đang mở Serial Monitor).")
                print(f"👉 HÃY ĐÓNG TAB 'SERIAL MONITOR' TRONG ARDUINO IDE (hoặc tắt Arduino IDE) rồi thử lại.\n")
            else:
                print(f"\n[Lỗi kết nối cổng {port}]: {e}\n")
        return None
    except Exception as e:
        if verbose:
            print(f"\n[Lỗi mở {port}]: {e}\n")
        return None


def read_arduino_lines(ser):
    """Đọc dữ liệu từ Arduino một cách an toàn."""
    if ser is None:
        return None
    try:
        if ser.is_open and ser.in_waiting:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            return line if line else None
    except Exception:
        pass
    return None


def safe_send_command(ser, port, cmd):
    """
    Gửi lệnh Serial an toàn, tự động thử kết nối lại nếu kết nối USB bị ngắt hoặc chưa kết nối.
    """
    if ser is None or not ser.is_open:
        print(f"[*] Đang thử kết nối tới {port}...")
        ser = open_serial_connection(port, verbose=True)
        if not ser:
            print(f"[!] Không thể gửi lệnh '{cmd}'. Hãy đóng Serial Monitor trong Arduino IDE và thử lại.")
            return ser, False

    try:
        payload = f"{cmd.strip()}\n".encode("utf-8")
        ser.write(payload)
        ser.flush()
        print(f"[PC -> Arduino] Đã gửi lệnh '{cmd.strip()}' thành công.")
        return ser, True
    except (serial.SerialException, PermissionError, OSError) as e:
        print(f"\n[!] Kết nối Serial bị gián đoạn ({e}). Đang kết nối lại...")
        try:
            ser.close()
        except Exception:
            pass
        time.sleep(1.0)
        ser = open_serial_connection(port, verbose=True)
        if ser:
            try:
                payload = f"{cmd.strip()}\n".encode("utf-8")
                ser.write(payload)
                ser.flush()
                print(f"[PC -> Arduino] Đã gửi lại lệnh '{cmd.strip()}' thành công.")
                return ser, True
            except Exception as e2:
                print(f"[!] Gửi lại thất bại: {e2}")
        return ser, False


def main():
    print("=" * 68)
    print("       🤖 CÔNG CỤ TEST PHẦN CỨNG ROBOT MATRIX MINI R4 🤖")
    print("=" * 68)

    port = find_arduino_port()
    print(f"[*] Cổng COM phát hiện: {port} | Baudrate: {BAUDRATE} bps")
    print("[*] Đang kết nối Serial...")

    ser = open_serial_connection(port, verbose=True)
    if ser:
        print(f"[OK] Đã kết nối thành công tới {port}!")
    else:
        print(f"[LƯU Ý] Chưa kết nối được {port}. Bạn vẫn có thể nhập phím lệnh để thử lại bất cứ lúc nào.")

    while True:
        status_str = f"ĐÃ KẾT NỐI ({port})" if (ser and ser.is_open) else f"CHƯA KẾT NỐI ({port} bị khóa)"
        
        print("\n" + "-" * 60)
        print(f"TRẠNG THÁI: [{status_str}]")
        print("DANH SÁCH LỆNH KIỂM TRA:")
        print("  [1] Lệnh 'T' - Tự động quét Servo (Test Sweep)")
        print("  [2] Lệnh 'P' - Giơ tay thuyết trình (Present - RC2: 0°, RC1: 40°)")
        print("  [3] Lệnh 'W' - Vẫy 2 tay chào tạm biệt (Wave - 0° <-> 90°)")
        print("  [4] Lệnh 'D' - Hạ 2 tay về tư thế nghỉ (Down - RC1: 40°, RC2: 57°)")
        print("  [5] Lệnh 'F' - Tiến lên 1.5 giây (Forward)")
        print("  [6] Lệnh 'B' - Lùi lại 1.5 giây (Backward)")
        print("  [7] Chế độ giám sát Cảm biến PIR & Laser (Đón khách WAKE_UP)")
        print("  [R] Thử kết nối lại cổng COM")
        print("  [0] Thoát chương trình")
        print("-" * 60)

        # In thông điệp phản hồi từ Arduino nếu có
        line = read_arduino_lines(ser)
        while line:
            print(f"  [Arduino -> PC]: {line}")
            line = read_arduino_lines(ser)

        try:
            choice = input("👉 Nhập lựa chọn của bạn (0-7 hoặc R): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[*] Đang đóng kết nối và thoát...")
            break

        if not choice:
            continue

        if choice == "1":
            ser, _ = safe_send_command(ser, port, "T")
        elif choice == "2":
            ser, _ = safe_send_command(ser, port, "P")
        elif choice == "3":
            ser, _ = safe_send_command(ser, port, "W")
        elif choice == "4":
            ser, _ = safe_send_command(ser, port, "D")
        elif choice == "5":
            ser, _ = safe_send_command(ser, port, "F")
        elif choice == "6":
            ser, _ = safe_send_command(ser, port, "B")
        elif choice.upper() == "R":
            print(f"\n[*] Đang quét lại cổng COM và kết nối lại...")
            if ser:
                try:
                    ser.close()
                except Exception:
                    pass
            port = find_arduino_port()
            ser = open_serial_connection(port, verbose=True)
            if ser:
                print(f"[OK] Kết nối lại thành công tới {port}!")
            else:
                print(f"[!] Vẫn chưa mở được {port}. Hãy chắc chắn đã đóng Serial Monitor trong Arduino IDE.")
        elif choice == "7":
            print("\n[*] ĐANG GIÁM SÁT CẢM BIẾN PIR & LASER (Đưa tay trước cảm biến <= 80cm)...")
            print("[*] Nhấn Ctrl+C để quay lại menu.\n")
            try:
                while True:
                    if ser is None or not ser.is_open:
                        ser = open_serial_connection(port, verbose=False)
                        time.sleep(1.0)
                        continue

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
                ser, _ = safe_send_command(ser, port, cmd)
            else:
                print("[!] Lựa chọn không hợp lệ (Vui lòng chỉ nhập số từ 0 đến 7 hoặc R).")

        time.sleep(0.4)
        line = read_arduino_lines(ser)
        while line:
            print(f"  [Arduino Phản Hồi]: {line}")
            line = read_arduino_lines(ser)

    if ser:
        try:
            ser.close()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Đã dừng chương trình.")
