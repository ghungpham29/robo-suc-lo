/*
 * =========================================================================================
 * DỰ ÁN: ROBOT HƯỚNG DẪN VIÊN TRIỂN LÃM VĂN HÓA
 * PHẦN CỨNG: Bo mạch MATRIX Mini R4 (Bộ Matrix Future Innovators)
 * FILE: arduino_matrix_mini_r4.ino (Firmware Điều khiển Cảm biến & Cơ cấu Chấp hành)
 * TỐC ĐỘ SERIAL: 115200 bps
 * =========================================================================================
 * MÔ TẢ HỆ THỐNG:
 * - Bo mạch đóng vai trò làm "Giác quan & Tay chân", truyền nhận dữ liệu với PC qua Serial.
 * - Đầu vào: 1 x PIR Sensor (Cổng D1), 1 x Laser Sensor MXLaserV2 (Cổng I2C1).
 * - Đầu ra: 4 x Động cơ DC di chuyển (M1, M2 bánh sau; M3, M4 bánh trước), 2 x Micro Servo (RC1, RC2).
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
const int SERVO_WAVE_LOW_ANGLE  = 80;   // Góc hạ tay xuống thấp khi vẫy

// Cấu hình công suất động cơ DC
const int MOTOR_FORWARD_POWER         = 55;     // Công suất tiến (0 - 100%)
const int MOTOR_BACKWARD_POWER        = -55;    // Công suất lùi (-100 - 0%)
const unsigned long MOTOR_RUN_TIME_MS = 1500;   // Thời gian chạy tiến/lùi (1.5 giây)

// Biến quản lý thời gian
unsigned long lastWakeUpTime = 0;

// =============================================================================
// 2. CÁC HÀM ĐIỀU KHIỂN CƠ CẤU CHẤP HÀNH (ACTUATORS)
// =============================================================================

/**
 * @brief Dừng toàn bộ 4 động cơ DC.
 */
void stopMotors() {
  MiniR4.M1.setPower(0);
  MiniR4.M2.setPower(0);
  MiniR4.M3.setPower(0);
  MiniR4.M4.setPower(0);
}

/**
 * @brief Điều khiển 4 động cơ tiến tới trong 1.5 giây rồi dừng.
 */
void moveForward() {
  Serial.println("[STATUS]: Moving Forward (F)");
  MiniR4.M1.setPower(MOTOR_FORWARD_POWER);
  MiniR4.M2.setPower(MOTOR_FORWARD_POWER);
  MiniR4.M3.setPower(MOTOR_FORWARD_POWER);
  MiniR4.M4.setPower(MOTOR_FORWARD_POWER);
  
  delay(MOTOR_RUN_TIME_MS);
  stopMotors();
  Serial.println("ACK:MOVING_FORWARD");
}

/**
 * @brief Điều khiển 4 động cơ lùi lại trong 1.5 giây rồi dừng.
 */
void moveBackward() {
  Serial.println("[STATUS]: Moving Backward (B)");
  MiniR4.M1.setPower(MOTOR_BACKWARD_POWER);
  MiniR4.M2.setPower(MOTOR_BACKWARD_POWER);
  MiniR4.M3.setPower(MOTOR_BACKWARD_POWER);
  MiniR4.M4.setPower(MOTOR_BACKWARD_POWER);
  
  delay(MOTOR_RUN_TIME_MS);
  stopMotors();
  Serial.println("ACK:MOVING_BACKWARD");
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
// 3. HÀM KHỞI TẠO HỆ THỐNG (SETUP)
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
}

// =============================================================================
// 4. VÒNG LẶP CHÍNH (LOOP)
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
    char cmd = Serial.read();

    // Bỏ qua các ký tự khoảng trắng hoặc xuống dòng dư thừa
    if (cmd == '\r' || cmd == '\n' || cmd == ' ') {
      return;
    }

    Serial.print("[COMMAND_RECEIVED]: ");
    Serial.println(cmd);

    switch (cmd) {
      case 'F': // Tiến tới 1.5s
      case 'f':
        moveForward();
        break;

      case 'B': // Lùi lại 1.5s
      case 'b':
        moveBackward();
        break;

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
        Serial.println(cmd);
        break;
    }
  }

  // Trì hoãn nhẹ 10ms để giảm tải CPU cho vi điều khiển
  delay(10);
}