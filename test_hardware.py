"""
=============================================================================
DỰ ÁN: ROBOT HƯỚNG DẪN VIÊN TRIỂN LÃM VĂN HÓA (KALEPIC)
File: test_hardware.py (CÔNG CỤ TEST TOÀN DIỆN PHẦN CỨNG & 11 LỘ TRÌNH DI CHUYỂN)
Tương thích Firmware: pipisikidi.ino / arduino_matrix_mini_r4.ino (Baudrate: 115200 bps)
=============================================================================
"""

import sys
import time
import serial
import serial.tools.list_ports

BAUDRATE = 115200

# Bảng mô tả 11 lộ trình di chuyển tượng (khớp với firmware pipisikidi.ino)
ROUTES_INFO = {
    "1": ("TƯỢNG 1", "Đi thẳng 5.0s"),
    "2": ("TƯỢNG 2", "Thẳng 5.4s -> Trái 0.98s -> Thẳng 1.9s"),
    "3": ("TƯỢNG 3", "Thẳng 5.4s -> Trái -> Thẳng 2.3s -> Lùi -> Trái -> Thẳng -> Phải"),
    "4": ("TƯỢNG 4", "Thẳng 2.0s -> Trái 0.96s -> Thẳng 1.5s"),
    "5": ("TƯỢNG 5", "Trái 0.98s -> Thẳng 2.0s"),
    "6": ("TƯỢNG 6", "Phải 0.98s -> Thẳng 1.9s"),
    "7": ("TƯỢNG 7", "Phải 1.0s -> Thẳng 1.9s -> Trái 0.98s -> Thẳng 1.0s -> Phải 1.0s"),
    "8": ("TƯỢNG 8", "Phải 0.98s -> Thẳng 3.0s -> Trái 0.98s -> Thẳng 2.8s -> Phải 0.98s"),
    "9": ("TƯỢNG 9", "Thẳng 5.5s -> Phải 0.96s -> Thẳng 1.6s"),
    "10": ("TƯỢNG 10", "Phải 0.98s -> Thẳng 3.0s -> Trái 0.96s -> Thẳng 4.1s"),
    "11": ("TƯỢNG 11", "Thẳng 5.4s -> Trái 0.98s -> Thẳng 1.9s -> Phải 0.98s"),
}


def get_all_com_ports():
    """Lấy toàn bộ danh sách cổng COM đang kết nối trên máy tính."""
    try:
        return list(serial.tools.list_ports.comports())
    except Exception:
        return []


def is_arduino_or_matrix(port_info):
    """Kiểm tra xem cổng COM có phải là Arduino hoặc Matrix Mini R4 hay không."""
    if getattr(port_info, "vid", None) == 0x2341:
        return True
    hwid = (port_info.hwid or "").upper()
    if "VID:PID=2341" in hwid or "2341:1002" in hwid:
        return True
    desc = (port_info.description or "").lower()
    if "arduino" in desc or "matrix" in desc:
        return True
    return False


def find_arduino_port():
    """Tự động dò tìm cổng COM của bo mạch Matrix Mini R4 / Arduino."""
    ports = get_all_com_ports()
    if not ports:
        return None

    # Ưu tiên 1: Bo mạch có VID Arduino (2341) hoặc Matrix Mini R4
    for p in ports:
        if is_arduino_or_matrix(p):
            return p.device

    # Ưu tiên 2: Cổng USB Serial (loại bỏ cổng Bluetooth ảo)
    for p in ports:
        desc = (p.description or "").lower()
        if "bluetooth" not in desc and ("usb" in desc or "ch340" in desc or "cp210" in desc or "ftdi" in desc or "serial" in desc):
            return p.device

    # Ưu tiên 3: Bất kỳ cổng COM nào không phải Bluetooth
    for p in ports:
        desc = (p.description or "").lower()
        if "bluetooth" not in desc:
            return p.device

    return ports[0].device if ports else None


def select_port_interactive():
    """Hiển thị danh sách tất cả các cổng COM và cho phép người dùng chọn linh hoạt."""
    ports = get_all_com_ports()
    print("\n" + "=" * 70)
    print("         🔍 DANH SÁCH CÁC CỔNG COM PHÁT HIỆN TRÊN MÁY TÍNH 🔍")
    print("=" * 70)

    if not ports:
        print("[!] Không phát hiện cổng COM nào đang cắm trên máy tính.")
        custom_port = input("👉 Nhập tên cổng COM bạn muốn thử (ví dụ COM3, COM13): ").strip().upper()
        return custom_port if custom_port else None

    print(f"Tìm thấy {len(ports)} cổng COM:\n")
    recommended_idx = None
    for i, p in enumerate(ports, start=1):
        tag = ""
        if is_arduino_or_matrix(p):
            tag = "  <-- [⭐ KHUYÊN DÙNG: Arduino / Matrix Mini R4]"
            if recommended_idx is None:
                recommended_idx = i
        elif "usb" in (p.description or "").lower():
            tag = "  <-- [USB Serial Device]"
        print(f"  [{i}] {p.device} : {p.description}{tag}")
        print(f"      Chi tiết: HWID={p.hwid}")

    print("  [0] Tự nhập cổng COM khác bằng tay")
    print("-" * 70)

    default_choice = str(recommended_idx) if recommended_idx else "1"
    prompt_str = f"👉 Chọn số cổng COM (1-{len(ports)}) hoặc [Enter] để chọn [{default_choice}]: "
    try:
        user_choice = input(prompt_str).strip()
    except (KeyboardInterrupt, EOFError):
        return None

    if not user_choice:
        user_choice = default_choice

    if user_choice == "0":
        custom_port = input("👉 Nhập cổng COM (ví dụ COM3, COM4, COM13...): ").strip().upper()
        return custom_port if custom_port else None

    if user_choice.isdigit():
        idx = int(user_choice) - 1
        if 0 <= idx < len(ports):
            return ports[idx].device

    if user_choice.upper().startswith("COM"):
        return user_choice.upper()

    return ports[0].device


def open_serial_connection(port, timeout=0.5, verbose=True):
    """Mở cổng Serial và khởi tạo an toàn."""
    if not port:
        return None
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
            print(f"\n[Lỗi kết nối]: {e}\n")
        return None


def read_arduino_lines(ser):
    """Đọc phản hồi từ Arduino nếu có."""
    if not ser or not ser.is_open:
        return None
    try:
        if ser.in_waiting > 0:
            raw_line = ser.readline()
            return raw_line.decode("utf-8", errors="ignore").strip()
    except Exception:
        pass
    return None


def safe_send_command(ser, port, cmd):
    """Gửi lệnh an toàn (ký tự hoặc số lộ trình) xuống bo mạch R4 kèm ký tự xuống dòng '\\n'."""
    if not ser or not ser.is_open:
        print(f"\n[*] Đang mở lại kết nối tới cổng {port}...")
        ser = open_serial_connection(port, verbose=True)

    if not ser or not ser.is_open:
        print(f"[!] Không thể gửi lệnh '{cmd}' vì cổng {port} chưa được kết nối.")
        return ser, False

    try:
        payload = f"{cmd.strip()}\n".encode("utf-8")
        ser.write(payload)
        ser.flush()
        print(f"[PC -> Arduino] >>> ĐÃ GỬI LỆNH: '{cmd.strip()}' <<<")
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
                print(f"[PC -> Arduino] >>> ĐÃ GỬI LẠI LỆNH '{cmd.strip()}' THÀNH CÔNG <<<")
                return ser, True
            except Exception as e2:
                print(f"[!] Gửi lại thất bại: {e2}")
        return ser, False


def main():
    print("=" * 76)
    print("   🤖 CÔNG CỤ TEST TOÀN DIỆN PHẦN CỨNG & DI CHUYỂN ROBOT KALEPIC 🤖")
    print("   Firmware: pipisikidi.ino | Bo mạch: MATRIX Mini R4 | Baudrate: 115200 bps")
    print("=" * 76)

    # 1. Tự động dò tìm cổng COM
    port = find_arduino_port()
    if port:
        print(f"[*] Cổng COM phát hiện: {port} | Baudrate: {BAUDRATE} bps")
    else:
        print("[!] Không tự động tìm thấy cổng Arduino/Matrix. Hãy chọn cổng thủ công.")
        port = select_port_interactive()

    print(f"[*] Đang kết nối Serial tới {port}...")
    ser = open_serial_connection(port, verbose=True)
    if ser:
        print(f"[OK] Đã kết nối thành công tới {port}!")
    else:
        print(f"[LƯU Ý] Chưa mở được {port}. Bạn có thể bấm [C] để chọn cổng khác hoặc [R] để thử lại.")

    while True:
        status_str = f"ĐÃ KẾT NỐI ({port})" if (ser and ser.is_open) else f"CHƯA KẾT NỐI ({port})"
        
        print("\n" + "=" * 76)
        print(f"TRẠNG THÁI: [{status_str}]")
        print("DANH SÁCH LỆNH KIỂM TRA PHẦN CỨNG & DI CHUYỂN:")
        print("=" * 76)
        print("  --- [A] KIỂM TRA CỬ CHỈ CƠ TAY SERVO ---")
        print("  [P] Lệnh 'P' - Giơ tay thuyết trình (Present - RC2: 0°, RC1: 40°)")
        print("  [W] Lệnh 'W' - Vẫy 2 tay chào tạm biệt (Wave - 0° <-> 90°)")
        print("  [D] Lệnh 'D' - Hạ 2 tay về tư thế nghỉ (Down - RC1: 40°, RC2: 57°)")
        print("  [T] Lệnh 'T' - Tự động quét toàn diện Servo (Sweep Test)")
        print()
        print("  --- [B] KIỂM TRA 11 LỘ TRÌNH DI CHUYỂN TƯỢNG (pipisikidi.ino) ---")
        for num in range(1, 12):
            key = str(num)
            name, desc = ROUTES_INFO[key]
            print(f"  [{num:2d}] Lệnh '{num:2d}' - Lộ trình {name:<10} ({desc})")
        print("  [0] Lệnh '0'  - Dừng khẩn cấp động cơ (Stop Motors)")
        print()
        print("  --- [C] CẢM BIẾN & CÔNG CỤ CỔNG KẾT NỐI ---")
        print("  [M] Chế độ giám sát Cảm biến PIR & Laser (Đón khách WAKE_UP)")
        print("  [C] DÒ & ĐỔI CỔNG COM KHÁC (Scan / Switch Port)")
        print("  [R] Thử kết nối lại cổng hiện tại")
        print("  [Q] Thoát chương trình")
        print("=" * 76)

        # In thông điệp phản hồi từ Arduino nếu có
        line = read_arduino_lines(ser)
        while line:
            print(f"  [Arduino -> PC]: {line}")
            line = read_arduino_lines(ser)

        try:
            choice = input("👉 Nhập lựa chọn của bạn (P, W, D, T, 1-11, 0, M, C, R, Q): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[*] Đang đóng kết nối và thoát...")
            break

        if not choice:
            continue

        c_upper = choice.upper()

        if c_upper == "Q":
            print("\n[*] Đang dừng robot và thoát chương trình...")
            if ser and ser.is_open:
                safe_send_command(ser, port, "0")
            break

        # 1. Các lệnh cử chỉ Servo
        elif c_upper in ["P", "W", "D", "T"]:
            print(f"\n[+] Kích hoạt Cử chỉ Servo: Lệnh '{c_upper}'...")
            ser, _ = safe_send_command(ser, port, c_upper)

        # 2. Lệnh dừng khẩn cấp
        elif choice == "0" or c_upper == "S":
            print("\n🛑 PHÁT LỆNH DỪNG KHẨN CẤP ĐỘNG CƠ (STOP MOTORS)...")
            ser, _ = safe_send_command(ser, port, "0")

        # 3. Lệnh lộ trình di chuyển 1 - 11
        elif choice in ROUTES_INFO:
            name, desc = ROUTES_INFO[choice]
            print(f"\n🚀 ĐANG CHẠY LỘ TRÌNH: {name} ({desc})...")
            ser, sent = safe_send_command(ser, port, choice)
            if sent:
                print("⏳ Robot đang chạy lộ trình... Đang lắng nghe phản hồi từ R4 (Bấm Ctrl+C để dừng khẩn cấp):")
                start_wait = time.time()
                try:
                    while time.time() - start_wait < 35.0:
                        ack_line = read_arduino_lines(ser)
                        if ack_line:
                            print(f"   [Arduino]: {ack_line}")
                            if "DONE" in ack_line or "ACK" in ack_line:
                                print(f"✅ Hoàn tất lộ trình {name}!\n")
                                break
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    print("\n🛑 Đã ngắt bởi người dùng -> Gửi lệnh dừng khẩn cấp.")
                    safe_send_command(ser, port, "0")

        # 4. Chế độ giám sát Cảm biến PIR & Laser
        elif c_upper in ["M", "7"]:
            print("\n[*] ĐANG GIÁM SÁT CẢM BIẾN PIR & LASER (Đưa tay trước cảm biến <= 80cm)...")
            print("[*] Nhấn Ctrl+C để quay lại menu chính.\n")
            try:
                while True:
                    if not ser or not ser.is_open:
                        ser = open_serial_connection(port, verbose=False)
                        if not ser:
                            time.sleep(1.0)
                            continue
                    if ser.in_waiting > 0:
                        raw = ser.readline().decode("utf-8", errors="ignore").strip()
                        if raw:
                            if "WAKE_UP" in raw:
                                print(f"  🔥 [PHÁT HIỆN DU KHÁCH]: {raw}")
                            else:
                                print(f"  [Cảm biến / Log]: {raw}")
                    time.sleep(0.05)
            except KeyboardInterrupt:
                print("\n[*] Đã dừng chế độ giám sát cảm biến.")

        # 5. Dò và đổi cổng COM khác
        elif c_upper == "C":
            new_port = select_port_interactive()
            if new_port:
                if ser:
                    try:
                        ser.close()
                    except Exception:
                        pass
                port = new_port
                print(f"\n[*] Đang kết nối tới cổng mới: {port}...")
                ser = open_serial_connection(port, verbose=True)
                if ser:
                    print(f"[OK] Đã kết nối thành công tới {port}!")
                else:
                    print(f"[!] Kết nối tới {port} thất bại.")

        # 6. Thử kết nối lại
        elif c_upper == "R":
            print(f"\n[*] Đang kết nối lại cổng {port}...")
            if ser:
                try:
                    ser.close()
                except Exception:
                    pass
            ser = open_serial_connection(port, verbose=True)
            if ser:
                print(f"[OK] Đã kết nối thành công tới {port}!")
            else:
                print(f"[!] Vẫn chưa mở được {port}. Hãy chắc chắn đã đóng Serial Monitor trong Arduino IDE.")

        else:
            print(f"[!] Lựa chọn '{choice}' không hợp lệ. Vui lòng xem danh sách menu phía trên.")

    if ser and ser.is_open:
        try:
            ser.close()
        except Exception:
            pass
    print("[*] Chương trình kết thúc an toàn. Tạm biệt!")


if __name__ == "__main__":
    main()
