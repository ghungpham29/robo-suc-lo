# Hướng Dẫn Task 3: Điều Khiển Yanshee Bằng Giọng Nói (Speech Recognition)

Chào mừng bạn đến với Task 3! Trong nhiệm vụ này, chúng ta sẽ lập trình thu âm thanh từ microphone máy tính và sử dụng mô hình nhận diện giọng nói của Google để chuyển thành văn bản, sau đó trích xuất câu lệnh điều khiển robot.

> [!NOTE]
> **Tách riêng file logic học tập**:
> Toàn bộ các hàm em cần hoàn thiện đã được tách riêng ra file [voice_todo.py](file:///c:/Users/Admin/Desktop/CODE/dự%20án%20lab/voice_cam_control_yanshee/yanshee_workshop/task3_voice/voice_todo.py) để em dễ tìm và không bị rối bởi các đoạn code xử lý đa luồng phức tạp khác. File [voice_controller.py](file:///c:/Users/Admin/Desktop/CODE/dự%20án%20lab/voice_cam_control_yanshee/yanshee_workshop/task3_voice/voice_controller.py) sẽ tự động import và gọi lại các hàm em viết trong file đó.

---

## 1. Kiến Thức Lý Thuyết

### 1.1. Số hóa giọng nói từ Microphone và Khử nhiễu nền
*   **Microphone** thu nhận dao động sóng âm thanh vật lý và chuyển thành tín hiệu điện số.
*   Để lọc tiếng ồn từ môi trường (quạt máy, tiếng nói chuyện nhỏ ở xa), hệ thống thật sử dụng phương thức **`adjust_for_ambient_noise(source, duration=1.5)`** để đo năng lượng nhiễu trong 1.5 giây đầu tiên.
*   **`energy_threshold`** (ngưỡng năng lượng) quyết định độ lớn âm thanh tối thiểu để kích hoạt nhận diện. Khi bật **`dynamic_energy_threshold = True`**, hệ thống sẽ tự động điều chỉnh độ nhạy micro để thích ứng khi phòng trở nên ồn ào hơn.

### 1.2. Nhận diện giọng nói bằng Google Speech API
*   Chúng ta sử dụng dịch vụ **Google Web Speech API** thông qua thư viện `SpeechRecognition` của Python.
*   Hàm **`recognize_google(audio, language="vi-VN")`** gửi dữ liệu âm thanh số lên máy chủ Google để xử lý qua mô hình Deep Learning tiếng Việt và trả về chuỗi văn bản tương ứng.

---

## 2. Hướng Dẫn Lập Trình

Hãy mở file [voice_todo.py](file:///c:/Users/Admin/Desktop/CODE/dự%20án%20lab/voice_cam_control_yanshee/yanshee_workshop/task3_voice/voice_todo.py) và hoàn thành các hàm sau:

### 2.1. Khởi tạo đối tượng nhận dạng
*   **Hàm**: `init_recognizer()`
*   **Yêu cầu**: Khởi tạo và trả về đối tượng `sr.Recognizer()`.

### 2.2. Khởi tạo nguồn Microphone
*   **Hàm**: `get_microphone()`
*   **Yêu cầu**: Khởi tạo và trả về đối tượng `sr.Microphone()`.

### 2.3. Lắng nghe ghi âm giọng nói
*   **Hàm**: `record_audio(recognizer, source)`
*   **Yêu cầu**: Gọi hàm lắng nghe của đối tượng `recognizer` trên microphone `source` với cấu hình lắng nghe:
    ```python
    return recognizer.listen(source, timeout=5, phrase_time_limit=5)
    ```

### 2.4. Chuyển giọng nói thành văn bản tiếng Việt
*   **Hàm**: `recognize_speech_vietnamese(recognizer, audio)`
*   **Yêu cầu**: Sử dụng API Google Speech để giải mã `audio` sang tiếng Việt:
    ```python
    return recognizer.recognize_google(audio, language="vi-VN")
    ```

### 2.5. Khớp từ khóa động tác
*   **Hàm**: `get_action(text)`
*   **Yêu cầu**: Duyệt qua các cặp trong `MOTION_MAP` và kiểm tra xem cụm từ khóa kích hoạt có nằm trong câu thoại của người dùng viết thường không (`phrase in text_lower`).

---

## 3. Cách Chạy Kiểm Tra

### 3.1. Chạy độc lập:
Mở Terminal và chạy lệnh:
```bash
python voice_controller.py
```

### 3.2. Kiểm tra với Yanshee thật:
- Mở file [voice_controller.py](file:///c:/Users/Admin/Desktop/CODE/dự%20án%20lab/voice_cam_control_yanshee/yanshee_workshop/task3_voice/voice_controller.py).
- Tìm dòng:
  ```python
  robot = YanAPI(ip_address="127.0.0.1")
  ```
- Thay `"127.0.0.1"` thành IP thật của robot Yanshee. Khi bạn nói lệnh giọng nói thành công, hệ thống sẽ gửi lệnh thực thi động tác tới robot Yanshee thật ngay lập tức!
- **Lưu ý**: Nếu chưa có robot thật kết nối hoặc thiếu SDK, hệ thống sẽ in cảnh báo ra console nhưng vòng lặp thu âm và nhận dạng giọng nói của Google vẫn hoạt động bình thường, giúp em kiểm nghiệm kết quả dịch ngôn ngữ! Nhấn **Ctrl+C** để dừng chương trình.
