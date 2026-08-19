"""
Module Thị giác Máy tính & Nhận diện Hiện vật (Gemini Multimodal Vision)
Cho phép Robot quan sát hiện vật qua Webcam hoặc phân tích ảnh tư liệu triển lãm,
tự động nhận diện và thuyết minh lịch sử - văn hóa của hiện vật trước mắt.
"""

import os
import re
from dotenv import load_dotenv
from google.genai import Client, types

load_dotenv()

FALLBACK_VISION_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

# Quản lý OpenCV (Lazy Loading để tăng tốc độ khởi động)
_cv2_module = None


def _get_cv2():
    """Tải thư viện cv2 khi cần sử dụng (Lazy Import)."""
    global _cv2_module
    if _cv2_module is None:
        try:
            import cv2
            _cv2_module = cv2
        except ImportError:
            _cv2_module = False
    return _cv2_module


def capture_image_from_camera(output_path: str = "assets/images/snapshot.jpg") -> bool:
    """
    Chụp một khung hình từ Webcam và lưu vào thư mục assets/images/.
    
    Returns:
        bool: True nếu chụp và lưu ảnh thành công.
    """
    cv2 = _get_cv2()
    if not cv2:
        print("[Camera] Thư viện opencv-python chưa được cài đặt.")
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[Camera] Không thể kết nối với Webcam của thiết bị.")
        return False

    # Đọc thử vài frame đầu để camera tự cân bằng sáng
    for _ in range(5):
        cap.read()

    ret, frame = cap.read()
    cap.release()

    if ret:
        cv2.imwrite(output_path, frame)
        print(f"[Camera] Đã chụp và lưu ảnh hiện vật tại: {output_path}")
        return True
    else:
        print("[Camera] Không chụp được ảnh từ camera.")
        return False


def analyze_artifact_image(image_path: str = "assets/images/snapshot.jpg") -> str:
    """
    Gửi ảnh hiện vật tới Gemini Multimodal để phân tích và thuyết minh.
    
    Args:
        image_path (str): Đường dẫn đến file ảnh hiện vật.
        
    Returns:
        str: Lời thuyết minh ngắn gọn, súc tích về hiện vật.
    """
    if not os.path.exists(image_path):
        return "Không tìm thấy file ảnh hiện vật để phân tích."

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key.startswith("your_api_key") or len(api_key) < 15:
        return "Chưa cấu hình Google Gemini API Key hợp lệ trong file .env để sử dụng tính năng nhận diện hiện vật bằng thị giác."

    try:
        client = Client(api_key=api_key)
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        prompt = (
            "Bạn là robot hướng dẫn viên triển lãm văn hóa. Hãy quan sát hình ảnh này, "
            "nhận diện hiện vật văn hóa/lịch sử và thuyết minh chính xác, ngắn gọn tối đa 2 đến 3 câu bằng tiếng Việt thuần túy. "
            "Tuyệt đối không dùng ký tự đặc biệt như *, # hay gạch đầu dòng."
        )

        for model_name in FALLBACK_VISION_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                        prompt,
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=300,
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                    ),
                )

                if response and response.text:
                    cleaned = re.sub(r"[\*#_~`>]", "", response.text)
                    return re.sub(r"\s+", " ", cleaned).strip()
            except Exception:
                continue

        return "Tôi chưa nhận diện rõ hiện vật này trong khung hình."
    except Exception as e:
        return f"Không thể phân tích ảnh hiện vật lúc này."
