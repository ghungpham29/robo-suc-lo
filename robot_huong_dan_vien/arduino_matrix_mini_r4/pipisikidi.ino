/*
 * =========================================================================================
 * DỰ ÁN: ROBOT HƯỚNG DẪN VIÊN TRIỂN LÃM VĂN HÓA
 * PHẦN CỨNG: Bo mạch MATRIX Mini R4 (Bộ Matrix Future Innovators)
 * FILE: pipisikidi.ino (Firmware Điều khiển Cảm biến & Cơ cấu Chấp hành)
 * TỐC ĐỘ SERIAL: 115200 bps
 * =========================================================================================
 * MÔ TẢ HỆ THỐNG:
 * - Bo mạch đóng vai trò làm "Giác quan & Tay chân", truyền nhận dữ liệu với PC qua Serial.
 * - Đầu vào: 1 x PIR Sensor (Cổng D1), 1 x Laser Sensor MXLaserV2 (Cổng I2C1).
 * - Đầu ra: 2 x Động cơ DC di chuyển (M1, M2), 2 x Micro Servo (RC1, RC2).
 * - DI CHUYỂN: Robot di chuyển theo các lộ trình "tượng" định sẵn (Tượng 1 - Tượng 11).
 *   Gửi số thứ tự tượng (1 - 11) qua Serial để chạy lộ trình tương ứng.
 * - CỬ CHỈ: Các lệnh ký tự (P, W, D, T) điều khiển 2 cánh tay Servo như cũ.
 * =========================================================================================
 */

#include <MatrixMiniR4.h>

// =============================================================================
// 1. CẤU HÌNH THÔNG SỐ HỆ THỐNG
// =============================================================================
const unsigned long SERIAL_BAUDRATE   = 115200; // Tốc độ giao tiếp Serial với Máy tính AI
const unsigned long COOLDOWN_MS       = 5000;   // Chống dội kích hoạt (Debounce Cooldown 5 giây)
const uint16_t LASER_DETECT_MAX_MM    = 800;    // Khoảng cách Laser phát hiện khách (<= 800mm / 80cm)
const uint16_t LASER_DETECT_MIN_MM    = 40;     // Khoảng cách tối thiểu loại trừ nhiễu bề mặt

// Cấu hình góc quay Servo (Micro Servo SG90 / MG90S)
const int SERVO1_REST_ANGLE    = 40;    // Góc nghỉ mặc định tay trái (RC1)
const int SERVO2_REST_ANGLE    = 57;    // Góc nghỉ mặc định tay phải (RC2)
const int SERVO2_PRESENT_ANGLE = 0;     // Góc tay phải (RC2) khi giơ tay thuyết trình

// Bổ sung: Cấu hình góc quay cho chế độ vẫy tay (Lệnh W)
const int SERVO_WAVE_HIGH_ANGLE = 0;    // Góc đưa tay lên cao khi vẫy
const int SERVO_WAVE_LOW_ANGLE  = 90;   // Góc hạ tay xuống thấp khi vẫy

// Cấu hình công suất động cơ DC di chuyển (dùng chung cho các lộ trình tượng)
const int MOVE_SPEED = 40;    // Công suất di chuyển mặc định (0 - 100%)

// Biến quản lý thời gian
unsigned long lastWakeUpTime = 0;

// =============================================================================
// 2. CÁC HÀM ĐIỀU KHIỂN CƠ CẤU CHẤP HÀNH (ACTUATORS)
// =============================================================================

/**
 * @brief Dừng cả 2 động cơ di chuyển (M1, M2).
 */
void stopMotors() {
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

/**
 * @brief Đưa cả 2 cánh tay về tư thế nghỉ mặc định.
 */
void gestureDown() {
  Serial.println("[STATUS]: Arms to Rest Position (D)");
  MiniR4.RC1.setAngle(SERVO1_REST_ANGLE); // Tay trái
  MiniR4.RC2.setAngle(SERVO2_REST_ANGLE); // Tay phải
  Serial.println("ACK:ARMS_DOWN");
}

/**
 * @brief Cử chỉ thuyết trình ('P'): Giơ MỘT cánh tay (Tay phải - RC2) lên cao.
 */
void gesturePresent() {
  Serial.println("[STATUS]: Presenting Gesture (P - Right Arm Up)");
  MiniR4.RC1.setAngle(SERVO1_REST_ANGLE);    // Tay trái giữ nguyên vị trí nghỉ
  MiniR4.RC2.setAngle(SERVO2_PRESENT_ANGLE); // Tay phải giơ lên làm cử chỉ chỉ trỏ thuyết minh
  Serial.println("ACK:PRESENT");
}

/**
 * @brief Cử chỉ vẫy tay chào tạm biệt ('W'): Vẫy liên tục cả 2 tay 4 nhịp (lên/xuống), sau đó về vị trí nghỉ.
 */
void gestureWave() {
  Serial.println("[STATUS]: Waving Goodbye (W - 4 cycles)");
  for (int i = 0; i < 4; i++) {
    // Đưa cả 2 tay lên cao
    MiniR4.RC1.setAngle(SERVO_WAVE_HIGH_ANGLE);
    MiniR4.RC2.setAngle(SERVO_WAVE_HIGH_ANGLE);
    delay(300);

    // Hạ cả 2 tay xuống thấp
    MiniR4.RC1.setAngle(SERVO_WAVE_LOW_ANGLE);
    MiniR4.RC2.setAngle(SERVO_WAVE_LOW_ANGLE);
    delay(300);
  }

  // Trở về tư thế nghỉ mặc định
  gestureDown();
  Serial.println("ACK:WAVE_DONE");
}

/**
 * @brief Kiểm tra quét hoạt động Servo ('T'): Thử nghiệm các góc giơ tay & vẫy tay rồi về vị trí nghỉ.
 */
void testSweep() {
  Serial.println("[STATUS]: Testing Servo Sweep (T)");
  // Giơ tay thuyết trình 1s
  MiniR4.RC1.setAngle(SERVO1_REST_ANGLE);
  MiniR4.RC2.setAngle(SERVO2_PRESENT_ANGLE);
  delay(1000);

  // Vẫy tay 2 nhịp
  for (int i = 0; i < 2; i++) {
    MiniR4.RC1.setAngle(SERVO_WAVE_HIGH_ANGLE);
    MiniR4.RC2.setAngle(SERVO_WAVE_HIGH_ANGLE);
    delay(300);
    MiniR4.RC1.setAngle(SERVO_WAVE_LOW_ANGLE);
    MiniR4.RC2.setAngle(SERVO_WAVE_LOW_ANGLE);
    delay(300);
  }

  // Trở về tư thế nghỉ
  gestureDown();
  Serial.println("ACK:SWEEP_DONE");
}

// =============================================================================
// 3. CÁC HÀM LỘ TRÌNH DI CHUYỂN THEO TỪNG "TƯỢNG" (Lệnh số 1 - 11)
// =============================================================================

/**
 * @brief Lộ trình Tượng 1: Đi thẳng.
 */
void tuong1() {
  Serial.println("[STATUS]: Moving Route - TUONG 1");
  thang(MOVE_SPEED);
  delay(5000);

  stopMotors();
  Serial.println("ACK:TUONG_1_DONE");
}

/**
 * @brief Lộ trình Tượng 2.
 */
void tuong2() {
  Serial.println("[STATUS]: Moving Route - TUONG 2");
  thang(MOVE_SPEED);
  delay(5400);
  delay(500);
  trai(MOVE_SPEED);
  delay(980);
  thang(MOVE_SPEED);
  delay(1900);

  stopMotors();
  Serial.println("ACK:TUONG_2_DONE");
}

/**
 * @brief Lộ trình Tượng 3.
 */
void tuong3() {
  Serial.println("[STATUS]: Moving Route - TUONG 3");
  thang(MOVE_SPEED);
  delay(5400);
  delay(500);
  trai(MOVE_SPEED);
  delay(980);
  thang(MOVE_SPEED);
  delay(2300);
  lui(MOVE_SPEED);
  delay(400);
  trai(MOVE_SPEED);
  delay(980);
  thang(MOVE_SPEED);
  delay(1000);
  phai(MOVE_SPEED);
  delay(960);

  stopMotors();
  Serial.println("ACK:TUONG_3_DONE");
}

/**
 * @brief Lộ trình Tượng 4.
 */
void tuong4() {
  Serial.println("[STATUS]: Moving Route - TUONG 4");
  thang(MOVE_SPEED);
  delay(2000);
  trai(MOVE_SPEED);
  delay(960);
  thang(MOVE_SPEED);
  delay(1500);

  stopMotors();
  Serial.println("ACK:TUONG_4_DONE");
}

/**
 * @brief Lộ trình Tượng 5.
 */
void tuong5() {
  Serial.println("[STATUS]: Moving Route - TUONG 5");
  trai(MOVE_SPEED);
  delay(980);
  thang(MOVE_SPEED);
  delay(2000);

  stopMotors();
  Serial.println("ACK:TUONG_5_DONE");
}

/**
 * @brief Lộ trình Tượng 6.
 */
void tuong6() {
  Serial.println("[STATUS]: Moving Route - TUONG 6");
  phai(MOVE_SPEED);
  delay(980);
  thang(MOVE_SPEED);
  delay(1900);

  stopMotors();
  Serial.println("ACK:TUONG_6_DONE");
}

/**
 * @brief Lộ trình Tượng 7.
 */
void tuong7() {
  Serial.println("[STATUS]: Moving Route - TUONG 7");
  phai(MOVE_SPEED);
  delay(1000);
  thang(MOVE_SPEED);
  delay(1900);
  delay(500);
  trai(MOVE_SPEED);
  delay(980);
  thang(MOVE_SPEED);
  delay(1000);
  delay(500);
  phai(MOVE_SPEED);
  delay(1000);

  stopMotors();
  Serial.println("ACK:TUONG_7_DONE");
}

/**
 * @brief Lộ trình Tượng 8.
 */
void tuong8() {
  Serial.println("[STATUS]: Moving Route - TUONG 8");
  phai(MOVE_SPEED);
  delay(980);
  thang(MOVE_SPEED);
  delay(3000);
  delay(500);
  trai(MOVE_SPEED);
  delay(980);
  thang(MOVE_SPEED);
  delay(2800);
  delay(500);
  phai(MOVE_SPEED);
  delay(980);

  stopMotors();
  Serial.println("ACK:TUONG_8_DONE");
}

/**
 * @brief Lộ trình Tượng 9.
 */
void tuong9() {
  Serial.println("[STATUS]: Moving Route - TUONG 9");
  thang(MOVE_SPEED);
  delay(5500);
  delay(500);
  phai(MOVE_SPEED);
  delay(960);
  thang(MOVE_SPEED);
  delay(1600);

  stopMotors();
  Serial.println("ACK:TUONG_9_DONE");
}

/**
 * @brief Lộ trình Tượng 10.
 */
void tuong10() {
  Serial.println("[STATUS]: Moving Route - TUONG 10");
  phai(MOVE_SPEED);
  delay(980);
  thang(MOVE_SPEED);
  delay(3000);
  delay(500);
  trai(MOVE_SPEED);
  delay(960);
  thang(MOVE_SPEED);
  delay(4100);

  stopMotors();
  Serial.println("ACK:TUONG_10_DONE");
}

/**
 * @brief Lộ trình Tượng 11.
 */
void tuong11() {
  Serial.println("[STATUS]: Moving Route - TUONG 11");
  thang(MOVE_SPEED);
  delay(5400);
  delay(500);
  trai(MOVE_SPEED);
  delay(980);
  thang(MOVE_SPEED);
  delay(1900);
  delay(500);
  phai(MOVE_SPEED);
  delay(980);

  stopMotors();
  Serial.println("ACK:TUONG_11_DONE");
}

/**
 * @brief Điều phối: gọi đúng hàm lộ trình theo số thứ tự tượng (1 - 11).
 */
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
  // 1. Khởi tạo toàn bộ hệ thống phần cứng bo mạch Matrix Mini R4
  MiniR4.begin();

  // 2. Cấu hình nguồn pin 2 Cell 18650
  MiniR4.PWR.setBattCell(2);

  // 3. Khởi tạo giao tiếp Serial với máy tính
  Serial.begin(SERIAL_BAUDRATE);
  while (!Serial && millis() < 2000) {
    ; // Chờ kết nối Serial trong tối đa 2s
  }

  // 4. Khởi tạo Cảm biến Laser V2 tại cổng I2C1
  MiniR4.I2C1.MXLaserV2.begin();

  // 5. Reset bộ đếm xung Encoder động cơ M1 & M2
  MiniR4.M1.resetCounter();
  MiniR4.M2.resetCounter();

  // 6. Đảm bảo toàn bộ động cơ đang dừng
  stopMotors();

  // 7. Đưa 2 Servo về tư thế nghỉ mặc định
  gestureDown();

  Serial.println("[SYSTEM_READY]: Matrix Mini R4 Robot Controller Initialized.");
  Serial.println("[HELP]: Gui so 1-11 de chay lo trinh tuong. Lenh: P, W, D, T.");
}

// =============================================================================
// 5. VÒNG LẶP CHÍNH (LOOP)
// =============================================================================
void loop() {
  unsigned long currentMillis = millis();

  // ---------------------------------------------------------------------------
  // [A] ĐỌC CẢM BIẾN & GỬI TÍN HIỆU WAKE_UP (KÈM CHỐNG DỘI DEBOUNCE 5S)
  // ---------------------------------------------------------------------------
  if (currentMillis - lastWakeUpTime >= COOLDOWN_MS) {
    // 1. Đọc cảm biến chuyển động PIR tại cổng D1
    bool pirDetected = MiniR4.D1.getL();

    // 2. Đọc cảm biến khoảng cách Laser tại cổng I2C1 (đơn vị: mm)
    uint16_t laserDistanceMM = MiniR4.I2C1.MXLaserV2.getDistance();
    bool laserDetected = (laserDistanceMM >= LASER_DETECT_MIN_MM && laserDistanceMM <= LASER_DETECT_MAX_MM);

    // Nếu PIR phát hiện chuyển động HOẶC Laser phát hiện người trong cự ly <= 800mm
    if (pirDetected || laserDetected) {
      Serial.println("WAKE_UP");
      lastWakeUpTime = currentMillis; // Cập nhật thời điểm kích hoạt gần nhất
    }
  }

  // ---------------------------------------------------------------------------
  // [B] NHẬN VÀ THỰC THI LỆNH ĐIỀU KHIỂN SERIAL TỪ MÁY TÍNH
  // ---------------------------------------------------------------------------
  if (Serial.available() > 0) {
    // Đọc trọn 1 dòng lệnh để hỗ trợ số thứ tự tượng 2 chữ số (VD: 10, 11)
    String lenh = Serial.readStringUntil('\n');
    lenh.trim(); // Loại bỏ khoảng trắng, ký tự '\r' thừa

    if (lenh.length() == 0) {
      return;
    }

    Serial.print("[COMMAND_RECEIVED]: ");
    Serial.println(lenh);

    // Kiểm tra xem lệnh có phải là số (lệnh di chuyển theo tượng 1-11) hay không
    bool laSo = true;
    for (unsigned int i = 0; i < lenh.length(); i++) {
      if (!isDigit(lenh.charAt(i))) {
        laSo = false;
        break;
      }
    }

    if (laSo) {
      // ----- LỆNH DI CHUYỂN: SỐ TƯỢNG (1 - 11) -----
      int soTuong = lenh.toInt();
      runTuong(soTuong);
    } else {
      // ----- LỆNH CỬ CHỈ / TIỆN ÍCH: KÝ TỰ ĐƠN -----
      char cmd = lenh.charAt(0);

      switch (cmd) {
        case 'P': // Cử chỉ thuyết trình (Chỉ tay phải lên)
        case 'p':
          gesturePresent();
          break;

        case 'W': // Cử chỉ vẫy tay chào tạm biệt
        case 'w':
          gestureWave();
          break;

        case 'D': // Hạ 2 tay về tư thế nghỉ
        case 'd':
          gestureDown();
          break;

        case 'T': // Kiểm tra quét toàn diện Servo
        case 't':
          testSweep();
          break;

        default:
          Serial.print("[WARNING]: Unknown command -> ");
          Serial.println(lenh);
          break;
      }
    }
  }
}
