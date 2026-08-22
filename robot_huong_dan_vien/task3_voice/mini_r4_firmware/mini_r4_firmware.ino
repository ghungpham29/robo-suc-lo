#include <MatrixMiniR4.h>

/**
 * === MATRIX MINI R4 FIRMWARE ===
 * Nhận lệnh từ Serial (qua USB hoặc Bluetooth) định dạng:
 * M:m1,m2,m3,m4\n
 * Ví dụ: "M:70,-70,-70,-70\n" để đi thẳng khi M1 thuận, M2/M3/M4 đảo chiều.
 */

void setup() {
  MiniR4.begin();
  Serial.begin(115200);
  
  // Dừng an toàn khi khởi động
  stopAllMotors();
}

void stopAllMotors() {
  MiniR4.M1.setPower(0);
  MiniR4.M2.setPower(0);
  MiniR4.M3.setPower(0);
  MiniR4.M4.setPower(0);
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    // Kiểm tra định dạng lệnh "M:m1,m2,m3,m4"
    if (input.startsWith("M:")) {
      String data = input.substring(2);
      
      int comma1 = data.indexOf(',');
      int comma2 = data.indexOf(',', comma1 + 1);
      int comma3 = data.indexOf(',', comma2 + 1);

      if (comma1 > 0 && comma2 > 0 && comma3 > 0) {
        int m1 = data.substring(0, comma1).toInt();
        int m2 = data.substring(comma1 + 1, comma2).toInt();
        int m3 = data.substring(comma2 + 1, comma3).toInt();
        int m4 = data.substring(comma3 + 1).toInt();

        // Cập nhật công suất cho 4 động cơ Mini R4
        MiniR4.M1.setPower(m1);
        MiniR4.M2.setPower(m2);
        MiniR4.M3.setPower(m3);
        MiniR4.M4.setPower(m4);
      }
    }
  }
}
