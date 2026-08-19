"""
Script chạy thử nghiệm nhanh Module AI Brain (Gemini Flash)
Dùng để kiểm tra kết nối API Key và phản hồi của mô hình mà không cần kích hoạt loa/voice.
"""

import sys
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            getattr(sys.stdout, "reconfigure")(encoding="utf-8")
    except Exception:
        pass

from core.ai_brain import ask_gemini

if __name__ == "__main__":
    cau_hoi = "Ý nghĩa của cồng chiêng Tây Nguyên là gì?"
    print("=" * 60)
    print("  KIỂM THỬ ĐỘC LẬP MODULE AI BRAIN (GEMINI FLASH)")
    print("=" * 60)
    print(f"Hỏi: {cau_hoi}")
    print("-" * 60)
    
    ket_qua = ask_gemini(cau_hoi)
    print(f"🤖 Mô hình trả lời:\n{ket_qua}")
    print("=" * 60)
