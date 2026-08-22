/*
 * =========================================================================================
 * DỰ ÁN: ROBOT DI CHUYỂN THEO LỘ TRÌNH TƯỢNG (MATRIX MINI R4)
 * FILE: di_chuyen.ino (Firmware Điều khiển Di chuyển - Test Lộ Trình Từng Tượng)
 * TỐC ĐỘ SERIAL: 115200 bps
 * =========================================================================================
 * MÔ TẢ HỆ THỐNG:
 * - Mỗi "tượng" là một lộ trình di chuyển riêng (chuỗi lệnh thang/trai/phai/lui + delay).
 * - Gửi số thứ tự tượng (1 - 11) qua Serial Monitor rồi Enter để chạy lộ trình tương ứng.
 * - Sau khi chạy xong lộ trình, robot tự động dừng lại (stopRobot).
 * =========================================================================================
 */

#include <MatrixMiniR4.h>

// =============================================================================
// 1. CÁC HÀM ĐIỀU KHIỂN ĐỘNG CƠ CƠ BẢN
// =============================================================================

/**
 * @brief Dừng cả 2 động cơ di chuyển (M1, M2).
 */
void stopRobot() {
  MiniR4.M1.setPower(0);
  MiniR4.M2.setPower(0);
}

/**
 * @brief Đi thẳng về phía trước.
 */
void thang(int speed) {
  MiniR4.M1.setPower(speed);
  MiniR4.M2.setPower(-speed - 5);
}

/**
 * @brief Quay/rẽ trái.
 */
void trai(int speed) {
  MiniR4.M1.setPower(speed);
  MiniR4.M2.setPower(speed + 5);
}

/**
 * @brief Quay/rẽ phải.
 */
void phai(int speed) {
  MiniR4.M1.setPower(-speed);
  MiniR4.M2.setPower(-speed - 5);
}

/**
 * @brief Đi lùi về phía sau.
 */
void lui(int speed) {
  MiniR4.M1.setPower(-speed);
  MiniR4.M2.setPower(speed + 5);
}

// =============================================================================
// 2. CÁC HÀM LỘ TRÌNH DI CHUYỂN THEO TỪNG "TƯỢNG"
// =============================================================================

/**
 * @brief Lộ trình Tượng 1: Đi thẳng.
 */
void tuong1() {
  Serial.println("[STATUS]: Chay lo trinh TUONG 1");
  thang(40);
  delay(5000);

  stopRobot();
  Serial.println("ACK:TUONG_1_DONE");
}

/**
 * @brief Lộ trình Tượng 2.
 */
void tuong2() {
  Serial.println("[STATUS]: Chay lo trinh TUONG 2");
  thang(40);
  delay(5400);
  delay(500);
  trai(40);
  delay(980);
  thang(40);
  delay(1900);

  stopRobot();
  Serial.println("ACK:TUONG_2_DONE");
}

/**
 * @brief Lộ trình Tượng 3.
 */
void tuong3() {
  Serial.println("[STATUS]: Chay lo trinh TUONG 3");
  thang(40);
  delay(5400);
  delay(500);
  trai(40);
  delay(980);
  thang(40);
  delay(2300);
  lui(40);
  delay(400);
  trai(40);
  delay(980);
  thang(40);
  delay(1000);
  phai(40);
  delay(960);

  stopRobot();
  Serial.println("ACK:TUONG_3_DONE");
}

/**
 * @brief Lộ trình Tượng 4.
 */
void tuong4() {
  Serial.println("[STATUS]: Chay lo trinh TUONG 4");
  thang(40);
  delay(2000);
  trai(40);
  delay(960);
  thang(40);
  delay(1500);

  stopRobot();
  Serial.println("ACK:TUONG_4_DONE");
}

/**
 * @brief Lộ trình Tượng 5.
 */
void tuong5() {
  Serial.println("[STATUS]: Chay lo trinh TUONG 5");
  trai(40);
  delay(980);
  thang(40);
  delay(2000);

  stopRobot();
  Serial.println("ACK:TUONG_5_DONE");
}

/**
 * @brief Lộ trình Tượng 6.
 */
void tuong6() {
  Serial.println("[STATUS]: Chay lo trinh TUONG 6");
  phai(40);
  delay(980);
  thang(40);
  delay(1900);

  stopRobot();
  Serial.println("ACK:TUONG_6_DONE");
}

/**
 * @brief Lộ trình Tượng 7.
 */
void tuong7() {
  Serial.println("[STATUS]: Chay lo trinh TUONG 7");
  phai(40);
  delay(1000);
  thang(40);
  delay(1900);
  delay(500);
  trai(40);
  delay(980);
  thang(40);
  delay(1000);
  delay(500);
  phai(40);
  delay(1000);

  stopRobot();
  Serial.println("ACK:TUONG_7_DONE");
}

/**
 * @brief Lộ trình Tượng 8.
 */
void tuong8() {
  Serial.println("[STATUS]: Chay lo trinh TUONG 8");
  phai(40);
  delay(980);
  thang(40);
  delay(3000);
  delay(500);
  trai(40);
  delay(980);
  thang(40);
  delay(2800);
  delay(500);
  phai(40);
  delay(980);

  stopRobot();
  Serial.println("ACK:TUONG_8_DONE");
}

/**
 * @brief Lộ trình Tượng 9.
 */
void tuong9() {
  Serial.println("[STATUS]: Chay lo trinh TUONG 9");
  thang(40);
  delay(5500);
  delay(500);
  phai(40);
  delay(960);
  thang(40);
  delay(1600);

  stopRobot();
  Serial.println("ACK:TUONG_9_DONE");
}

/**
 * @brief Lộ trình Tượng 10.
 */
void tuong10() {
  Serial.println("[STATUS]: Chay lo trinh TUONG 10");
  phai(40);
  delay(980);
  thang(40);
  delay(3000);
  delay(500);
  trai(40);
  delay(960);
  thang(40);
  delay(4100);

  stopRobot();
  Serial.println("ACK:TUONG_10_DONE");
}

/**
 * @brief Lộ trình Tượng 11.
 */
void tuong11() {
  Serial.println("[STATUS]: Chay lo trinh TUONG 11");
  thang(40);
  delay(5400);
  delay(500);
  trai(40);
  delay(980);
  thang(40);
  delay(1900);
  delay(500);
  phai(40);
  delay(980);

  stopRobot();
  Serial.println("ACK:TUONG_11_DONE");
}

// =============================================================================
// 3. HÀM XỬ LÝ LỆNH: NHẬN SỐ TƯỢNG (1 - 11) VÀ GỌI HÀM TƯƠNG ỨNG
// =============================================================================
void runTuong(int soTuong) {
  switch (soTuong) {
    case 1:  tuong1();  break;
    case 2:  tuong2();  break;
    case 3:  tuong3();  break;
    case 4:  tuong4();  break;
    case 5:  tuong5();  break;
    case 6:  tuong6();  break;
    case 7:  tuong7();  break;
    case 8:  tuong8();  break;
    case 9:  tuong9();  break;
    case 10: tuong10(); break;
    case 11: tuong11(); break;
    default:
      Serial.print("[WARNING]: So tuong khong hop le -> ");
      Serial.println(soTuong);
      break;
  }
}

// =============================================================================
// 4. HÀM KHỞI TẠO HỆ THỐNG (SETUP)
// =============================================================================
void setup() {
  Serial.begin(115200);

  MiniR4.begin();

  delay(1000);

  stopRobot();

  Serial.println("[SYSTEM_READY]: Nhap so tuong (1 - 11) roi Enter de chay lo trinh.");
}

// =============================================================================
// 5. VÒNG LẶP CHÍNH (LOOP): NHẬN LỆNH SỐ QUA SERIAL
// =============================================================================
void loop() {
  // Đọc trọn 1 dòng lệnh (kết thúc bằng '\n') để hỗ trợ số 2 chữ số (VD: 10, 11)
  if (Serial.available() > 0) {
    String lenh = Serial.readStringUntil('\n');
    lenh.trim(); // Loại bỏ khoảng trắng, ký tự '\r' thừa

    if (lenh.length() == 0) {
      return;
    }

    Serial.print("[COMMAND_RECEIVED]: ");
    Serial.println(lenh);

    int soTuong = lenh.toInt();

    if (soTuong == 0 && lenh != "0") {
      Serial.print("[WARNING]: Lenh khong hop le -> ");
      Serial.println(lenh);
      return;
    }

    runTuong(soTuong);
  }
}
