"""
Module Quản lý Bộ nhớ đệm Thông minh (Smart Fuzzy & Dynamic LRU Cache 2.0)
Tối ưu hóa thời gian phản hồi (0ms Latency) với khả năng nhận diện sai chính tả (Fuzzy Matching)
và tự động ghi nhớ các câu hỏi/đáp mới vào bộ nhớ đệm động (Dynamic Cache).
"""

import re
import unicodedata
from typing import Optional
from collections import OrderedDict

# Kiểm tra thư viện rapidfuzz để so khớp mờ siêu tốc
try:
    from rapidfuzz import fuzz
    _RAPIDFUZZ_AVAILABLE = True
except ImportError:
    _RAPIDFUZZ_AVAILABLE = False
    import difflib

# Bảng băm các câu hỏi cơ bản và câu trả lời chuẩn mực
STATIC_CACHE: dict[str, str] = {
    # Nhóm câu hỏi Chào hỏi
    "xin chao": "Xin chào quý khách! Tôi là Kalepic, robot hướng dẫn viên triển lãm văn hóa. Rất hân hạnh được đồng hành cùng bạn hôm nay.",
    "xin chào": "Xin chào quý khách! Tôi là Kalepic, robot hướng dẫn viên triển lãm văn hóa. Rất hân hạnh được đồng hành cùng bạn hôm nay.",
    "chao ban": "Chào bạn! Tôi là Kalepic, chúc bạn có một chuyến tham quan triển lãm thật thú vị và bổ ích.",
    "chào bạn": "Chào bạn! Tôi là Kalepic, chúc bạn có một chuyến tham quan triển lãm thật thú vị và bổ ích.",
    "hello": "Xin chào! Tôi là Kalepic, tôi có thể giúp gì cho bạn trong chuyến tham quan văn hóa hôm nay?",
    "hi robot": "Xin chào! Tôi là Kalepic, rất vui được đón tiếp quý khách đến với không gian triển lãm.",

    # Nhóm câu hỏi Danh tính / Giới thiệu
    "ban ten gi": "Tôi là Kalepic - Robot Hướng Dẫn Viên Triển Lãm Văn Hóa, được phát triển bởi các bạn học sinh trường Quốc Học Quy Nhơn để giới thiệu nét đẹp di sản.",
    "bạn tên gì": "Tôi là Kalepic - Robot Hướng Dẫn Viên Triển Lãm Văn Hóa, được phát triển bởi các bạn học sinh trường Quốc Học Quy Nhơn để giới thiệu nét đẹp di sản.",
    "ban la ai": "Tôi là Kalepic - Robot Hướng Dẫn Viên Triển Lãm Văn Hóa, người bạn đồng hành thuyết minh các hiện vật lịch sử và văn hóa.",
    "bạn là ai": "Tôi là Kalepic - Robot Hướng Dẫn Viên Triển Lãm Văn Hóa, người bạn đồng hành thuyết minh các hiện vật lịch sử và văn hóa.",
    "gioi thieu ban than": "Tôi là Kalepic, robot hướng dẫn viên trí tuệ nhân tạo, có nhiệm vụ thuyết minh về các di tích và hiện vật văn hóa tiêu biểu.",
    "giới thiệu bản thân": "Tôi là Kalepic, robot hướng dẫn viên trí tuệ nhân tạo, có nhiệm vụ thuyết minh về các di tích và hiện vật văn hóa tiêu biểu.",

    # Nhóm câu hỏi Tiện ích triển lãm & Bảo tàng
    "gio mo cua": "Triển lãm mở cửa đón du khách tham quan từ 7 giờ 30 sáng đến 17 giờ chiều tất cả các ngày trong tuần.",
    "giờ mở cửa": "Triển lãm mở cửa đón du khách tham quan từ 7 giờ 30 sáng đến 17 giờ chiều tất cả các ngày trong tuần.",
    "gia ve": "Triển lãm văn hóa hiện đang mở cửa phục vụ miễn phí cho tất cả du khách và học sinh, sinh viên tham quan học tập.",
    "giá vé": "Triển lãm văn hóa hiện đang mở cửa phục vụ miễn phí cho tất cả du khách và học sinh, sinh viên tham quan học tập.",
    "ve tham quan": "Triển lãm mở cửa tự do phục vụ cộng đồng. Quý khách vui lòng giữ gìn vệ sinh và trật tự chung trong không gian trưng bày.",
    "vé tham quan": "Triển lãm mở cửa tự do phục vụ cộng đồng. Quý khách vui lòng giữ gìn vệ sinh và trật tự chung trong không gian trưng bày.",
    "quy dinh": "Khi tham quan, quý khách vui lòng không chạm tay trực tiếp vào hiện vật trưng bày, không xả rác và giữ âm lượng vừa phải.",
    "quy định": "Khi tham quan, quý khách vui lòng không chạm tay trực tiếp vào hiện vật trưng bày, không xả rác và giữ âm lượng vừa phải.",
    "chup anh": "Quý khách được phép chụp ảnh lưu niệm tại khu vực triển lãm, nhưng vui lòng không sử dụng đèn flash chiếu thẳng vào cổ vật.",
    "chụp ảnh": "Quý khách được phép chụp ảnh lưu niệm tại khu vực triển lãm, nhưng vui lòng không sử dụng đèn flash chiếu thẳng vào cổ vật.",

    # Nhóm Cảm ơn
    "cam on": "Không có gì ạ! Rất vui được hỗ trợ quý khách. Nếu cần thêm thông tin gì, bạn cứ hỏi tôi nhé.",
    "cảm ơn": "Không có gì ạ! Rất vui được hỗ trợ quý khách. Nếu cần thêm thông tin gì, bạn cứ hỏi tôi nhé.",
    "cam on ban": "Rất hân hạnh được phục vụ bạn! Chúc bạn tiếp tục có những trải nghiệm tuyệt vời tại triển lãm.",
    "cảm ơn bạn": "Rất hân hạnh được phục vụ bạn! Chúc bạn tiếp tục có những trải nghiệm tuyệt vời tại triển lãm.",

    # Nhóm câu hỏi Chào hỏi & Giới thiệu kết hợp
    "xin chao ban la ai": "Xin chào quý khách! Tôi là Kalepic - Robot Hướng Dẫn Viên Triển Lãm Văn Hóa, người bạn đồng hành thuyết minh các di tích và hiện vật lịch sử.",
    "xin chào bạn là ai": "Xin chào quý khách! Tôi là Kalepic - Robot Hướng Dẫn Viên Triển Lãm Văn Hóa, người bạn đồng hành thuyết minh các di tích và hiện vật lịch sử.",
    "ban co the lam gi": "Tôi là Kalepic, tôi có thể thuyết minh chi tiết về các di tích tháp Chăm Pa, thần thoại Ấn Độ giáo, không gian cồng chiêng Tây Nguyên, trống đồng Đông Sơn và giải đáp các thắc mắc của quý khách.",
    "bạn có thể làm gì": "Tôi là Kalepic, tôi có thể thuyết minh chi tiết về các di tích tháp Chăm Pa, thần thoại Ấn Độ giáo, không gian cồng chiêng Tây Nguyên, trống đồng Đông Sơn và giải đáp các thắc mắc của quý khách.",
    "giup gi duoc cho toi": "Tôi là Kalepic, tôi có thể hỗ trợ thuyết minh thông tin lịch sử các hiện vật triển lãm và hướng dẫn tham quan cho quý khách.",
    "giúp gì được cho tôi": "Tôi là Kalepic, tôi có thể hỗ trợ thuyết minh thông tin lịch sử các hiện vật triển lãm và hướng dẫn tham quan cho quý khách.",
}

# Bộ nhớ đệm động LRU lưu trữ các câu trả lời gần đây (Tối đa 150 câu)
_DYNAMIC_LRU_CACHE: OrderedDict[str, str] = OrderedDict()
MAX_DYNAMIC_CACHE_SIZE = 150


def _strip_accents(text: str) -> str:
    """Loại bỏ dấu tiếng Việt để đối chiếu linh hoạt."""
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)
    text = text.replace("đ", "d").replace("Đ", "D")
    return text


def _clean_text(text: str) -> str:
    """Xóa ký tự đặc biệt, dấu câu và chuẩn hóa khoảng trắng."""
    text = re.sub(r"[?!.,\-:;\"'~@#$%^&*()]", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def add_to_dynamic_cache(question: str, answer: str) -> None:
    """Lưu câu hỏi và câu trả lời mới vào bộ nhớ đệm động LRU."""
    if not question or not answer:
        return
    key = _clean_text(question)
    if key in _DYNAMIC_LRU_CACHE:
        _DYNAMIC_LRU_CACHE.move_to_end(key)
    _DYNAMIC_LRU_CACHE[key] = answer
    if len(_DYNAMIC_LRU_CACHE) > MAX_DYNAMIC_CACHE_SIZE:
        _DYNAMIC_LRU_CACHE.popitem(last=False)


# Danh sách các từ khóa đánh dấu câu hỏi cần tư duy sâu, so sánh, phân tích (Bắt buộc chuyển đến Gemini AI Brain)
ANALYTICAL_INDICATORS = [
    "so sánh", "so sanh", "khác nhau", "khac nhau", "giống nhau", "giong nhau",
    "tại sao", "tai sao", "vì sao", "vi sao", "nguyên nhân", "nguyen nhan",
    "ý nghĩa", "y nghia", "phân tích", "phan tich", "đánh giá", "danh gia",
    "như thế nào", "nhu the nao", "thế nào", "the nao", "mối quan hệ", "moi quan he",
    "ảnh hưởng", "anh huong", "giao thoa", "giao thoa", "liên hệ", "lien he",
    "quan điểm", "quan diem", "lý do", "ly do", "chi tiết", "chi tiet",
    "kể thêm", "ke them", "sâu hơn", "sau hon", "bình luận", "binh luan"
]


def _is_complex_query(text: str) -> bool:
    """Kiểm tra xem câu hỏi có mang tính so sánh, phân tích hoặc hỏi sâu cần AI tư duy hay không."""
    if not text:
        return False
    q_clean = _clean_text(text)
    q_norm = _strip_accents(q_clean)
    
    # Nếu chứa từ khóa so sánh/phân tích
    for indicator in ANALYTICAL_INDICATORS:
        if indicator in q_clean or indicator in q_norm:
            return True
            
    # Nếu câu hỏi dài và phức tạp (chứa liên từ nối 'và', 'hay', 'với', 'giữa')
    words = q_clean.split()
    if len(words) >= 6 and any(w in words for w in ["va", "giua", "voi", "hay", "sao"]):
        return True

    return False


def check_cache(question: str, fuzzy_threshold: float = 85.0) -> Optional[str]:
    """
    Kiểm tra câu hỏi trong Bộ nhớ đệm Tĩnh và Động.
    CÁC CÂU HỎI SO SÁNH, PHÂN TÍCH HOẶC TƯ DUY PHỨC TẠP SẼ LUÔN ĐƯỢC CHUYỂN ĐẾN GEMINI AI BRAIN.
    
    Args:
        question (str): Câu hỏi của du khách.
        fuzzy_threshold (float): Ngưỡng tương đồng (0-100) để chấp nhận khớp mờ.
        
    Returns:
        Optional[str]: Câu trả lời tương ứng hoặc None nếu cần chuyển đến Gemini AI Brain.
    """
    if not question:
        return None

    # Nếu là câu hỏi so sánh, phân tích hoặc tư duy -> Chuyển ngay cho Gemini AI Brain xử lý
    if _is_complex_query(question):
        return None

    cleaned_q = _clean_text(question)
    unaccented_q = _strip_accents(cleaned_q)

    # 1. Tra cứu trực tiếp O(1) trong Static Cache (Chào hỏi, Danh tính, Giờ mở cửa, Giá vé, Nội quy)
    if cleaned_q in STATIC_CACHE:
        return STATIC_CACHE[cleaned_q]
    if unaccented_q in STATIC_CACHE:
        return STATIC_CACHE[unaccented_q]

    # 2. Tra cứu trong Dynamic LRU Cache
    if cleaned_q in _DYNAMIC_LRU_CACHE:
        _DYNAMIC_LRU_CACHE.move_to_end(cleaned_q)
        return _DYNAMIC_LRU_CACHE[cleaned_q]

    # 3. So khớp từ khóa chính xác theo Word Boundary cho Static Cache
    for key, answer in STATIC_CACHE.items():
        pattern = r"\b" + re.escape(key) + r"\b"
        if re.search(pattern, cleaned_q) or re.search(pattern, unaccented_q):
            if len(cleaned_q.split()) <= 7:
                return answer

    # 4. So khớp mờ (Fuzzy Matching) cho các câu chào hỏi/danh tính khi gõ sai chính tả
    if len(cleaned_q.split()) <= 5:
        if _RAPIDFUZZ_AVAILABLE:
            for key, answer in STATIC_CACHE.items():
                ratio = fuzz.ratio(cleaned_q, key)
                if ratio >= fuzzy_threshold:
                    return answer
        else:
            matches = difflib.get_close_matches(cleaned_q, STATIC_CACHE.keys(), n=1, cutoff=fuzzy_threshold/100.0)
            if matches:
                return STATIC_CACHE[matches[0]]

    # Không tự động gán câu hỏi mở vào tri thức tĩnh để đảm bảo Gemini AI có không gian tư duy
    return None
