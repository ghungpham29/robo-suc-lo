"""
Module Trí tuệ Nhân tạo & Quản lý Ngữ cảnh Đàm thoại Siêu tốc (AI Brain 2.0 - Low Latency)
Sử dụng mô hình Gemini Flash tối ưu hóa cho Chat thời gian thực.
Tích hợp Bộ Lọc Chủ Đề Siêu Tốc (Pre-Filter Guardrails): Bỏ qua gọi API và từ chối tức thì (0ms) với các câu hỏi ngoài lề.
"""

import os
import re
import sys
import time
from typing import Callable, Optional
from dotenv import load_dotenv

# Hỗ trợ chạy script độc lập
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from google.genai import Client, types
from core.knowledge_base import get_exhibition_context_prompt, search_knowledge_base

load_dotenv()

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

FALLBACK_MODELS = [
    DEFAULT_MODEL,
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
    "gemini-1.5-flash",
]

_client = None
_active_chat_session = None
_current_model_used = None

# Câu từ chối tiêu chuẩn theo quy tắc
REFUSAL_MESSAGE = "Xin lỗi, tôi chỉ được lập trình để cung cấp thông tin về triển lãm văn hóa."

# Các mẫu câu hỏi / từ khóa KHÔNG LIÊN QUAN đến triển lãm văn hóa
OFFTOPIC_PATTERNS = [
    # Toán học, khoa học tự nhiên, tính toán, giải bài
    r"\b(toán|giải toán|phương trình|hệ phương trình|tích phân|đạo hàm|bài tập|giải bài|hóa học|vật lý|tính giúp|cộng trừ|bài toán|công thức|định lý|hình học|tam giác|diện tích|chu vi)\b",
    r"\b(\d+\s*[\+\-\*\/xX]\s*\d+)\b",  # Phép tính số học như 1+1, 5*10
    
    # Lập trình, tin học, phần mềm, công nghệ
    r"\b(lập trình|viet code|viết code|code|python|java|javascript|c\+\+|html|css|php|sql|database|debug|sửa bug|viết hàm|thuật toán|github|vscode|hệ điều hành|cài win)\b",
    
    # Game & Trò chơi giải trí phi văn hóa
    r"\b(chơi game|chơi trò|game|liên quân|lien quan|free fire|pubg|roblox|fifa|genshin|minecraft|streamer|esport|chơi bài|chơi cờ|đánh bài|tiến lên|tài xỉu)\b",
    
    # Thể thao hiện đại
    r"\b(bóng đá|cầu thủ|messi|ronaldo|ngoại hạng anh|champions league|world cup|đội bóng|real madrid|barcelona|manchester|bóng rổ|tennis|bóng chuyền|euro|bàn thắng)\b",
    
    # Showbiz, ca sĩ nhạc trẻ, phim ảnh hiện đại
    r"\b(ca sĩ|nhạc trẻ|kpop|blackpink|bts|sơn tùng|jack|rap việt|phim chiếu rạp|diễn viên|showbiz|drama|tiktok|facebook|youtube)\b",
    
    # Đời sống, thời tiết, tài chính, thường nhật ngoài triển lãm
    r"\b(thời tiết|dự báo thời tiết|nhiệt độ|trời mưa|giá vàng|chứng khoán|bitcoin|crypto|mua bán|bất động sản|tình cảm|tình yêu|bói toán|cung hoàng đạo|xổ số|lô đề|bệnh viện|thuốc trị|khám bệnh|nấu ăn|món ăn|cách nấu|uống gì|ăn gì)\b",
]

# Từ khóa bảo vệ chủ đề văn hóa / lịch sử / di tích
CULTURAL_KEYWORDS = [
    "tháp", "đôi", "bánh ít", "dương long", "cánh tiên", "thủ thiện", "mỹ sơn", "po klong garai", "po nagar",
    "chăm", "champa", "angkor", "khmer", "hindu", "shiva", "brahma", "vishnu", "trimurti", "linga", "yoni",
    "garuda", "ganesha", "nandin", "apsara", "đồ bàn", "vijaya", "trà kiệu", "simhapura", "đồng dương", "indrapura",
    "chế mân", "huyền trân", "katê", "kate", "tháp chàm", "điêu khắc",
    "cồng chiêng", "tây nguyên", "trống đồng", "đông sơn", "văn lang", "âu lạc",
    "quốc học", "quy nhơn", "quang trung", "nguyễn huệ", "tây sơn",
    "văn hóa", "lịch sử", "di tích", "hiện vật", "bảo tàng", "nghệ thuật",
    "kiến trúc", "triều đại", "thế kỷ", "niên đại", "di sản", "lễ hội",
    "phong tục", "truyền thống", "tượng", "chùa", "đình", "miếu", "lăng",
    "vua", "chúa", "hoàng đế", "danh nhân", "khảo cổ", "triển lãm",
    "trưng bày", "thuyết minh", "nguồn gốc", "ý nghĩa", "việt nam", "bình định",
    "bản sắc", "dân tộc", "cổ vật", "chữ viết", "tiền sử"
]

# Các câu giao tiếp chào hỏi thông thường
CONVERSATIONAL_KEYWORDS = [
    "xin chào", "chào", "hello", "hi", "bạn là ai", "bạn tên gì", "tên bạn",
    "giới thiệu", "cảm ơn", "tạm biệt", "bye", "giúp gì", "làm được gì", "hướng dẫn"
]


def is_offtopic_query(question: str) -> bool:
    """
    Hệ thống mở rộng: Không chặn câu hỏi ngoài lề, cho phép Robot trả lời đa dạng kiến thức.
    """
    return False


def _get_client() -> Optional[Client]:
    """Khởi tạo Client Gemini một cách an toàn và tải lại API Key động từ môi trường."""
    global _client
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key.startswith("your_api_key") or len(api_key) < 15:
        return None
    try:
        if _client is None or getattr(_client, "_api_key", None) != api_key:
            _client = Client(api_key=api_key)
            _client._api_key = api_key
        return _client
    except Exception:
        return None


def _build_system_instruction() -> str:
    """System instruction định hình tính cách AI Cultural Companion Robot - Đội CERBERUS, WRO 2026 Future Innovators."""
    knowledge_context = get_exhibition_context_prompt()
    instruction = (
        "Bạn là Robot Hướng Dẫn Viên Triển Lãm Văn Hóa Thông Thái (AI Cultural Companion Robot), "
        "được nghiên cứu và phát triển bởi Đội thi CERBERUS - Trường THPT Quốc Học Quy Nhơn (Tỉnh Bình Định) "
        "tham dự cuộc thi WRO 2026 Future Innovators.\n\n"
        "CƠ SỞ TRI THỨC VĂN MINH CHĂM PA & DI SẢN TRIỂN LÃM:\n"
        f"{knowledge_context}\n\n"
        "NGUYÊN TẮC THUYẾT MINH VÀ GIAO TIẾP VỚI DU KHÁCH:\n"
        "1. ĐỐI VỚI CÂU HỎI VỀ VĂN MINH CHĂM PA (lịch sử 5 thời kỳ, 8 phong cách điêu khắc, bí ẩn gạch không mạch vữa, "
        "ngẫu tượng Linga-Yoni, linh vật Kala/Makara/Garuda/Nandin/Apsara, chế độ mẫu hệ, đập Nha Trinh, gốm Bàu Trúc, "
        "lễ hội Katê/Ramưwan, các vị vua Khu Liên, Bhadravarman, Indravarman, Chế Mân, Po Klong Garai, Chế Bồng Nga, Po Rome...): "
        "Hãy thuyết minh thật sâu sắc, cuốn hút, chính xác về niên đại và ý nghĩa biểu tượng.\n"
        "2. NGHỆ THUẬT KỂ CHUYỆN (STORYTELLING): Giải thích các chi tiết văn hóa một cách sống động như người hướng dẫn viên thực thụ, "
        "khéo léo dẫn dắt du khách chiêm ngưỡng hiện vật tại Bình Định và các bảo vật quốc gia.\n"
        "3. ĐỐI VỚI CÂU HỎI MỞ RỘNG NGOÀI TRIỂN LÃM: Trả lời lịch thiệp, thông minh, súc tích bằng tiếng Việt trong sáng, "
        "sau đó khéo léo kết nối mời du khách khám phá thêm di sản triển lãm.\n"
        "4. ĐỘ DÀI & VĂN PHONG PHÁT ÂM: Trả lời tự nhiên, liền mạch (khoảng 3 đến 5 câu văn súc tích). "
        "TUYỆT ĐỐI KHÔNG dùng ký tự đặc biệt (*, #, _, ~, `, >, gạch đầu dòng) để hệ thống đọc giọng nói AI (Kokoro-TTS) phát âm mượt mà nhất.\n"
        "5. KẾT NỐI NGỮ CẢNH: Luôn ghi nhớ mạch hội thoại để trò chuyện tự nhiên, thân thiện với du khách."
    )
    return instruction


def _init_chat_session(client_obj: Client, model_name: str):
    """Khởi tạo phiên chat mới với cấu hình Token tối ưu cho khả năng tư duy và phản hồi nhanh."""
    config = types.GenerateContentConfig(
        system_instruction=_build_system_instruction(),
        temperature=0.4,
        max_output_tokens=450,
    )
    return client_obj.chats.create(model=model_name, config=config)


def reset_conversation() -> None:
    """Xóa trí nhớ hội thoại cũ khi đón khách mới."""
    global _active_chat_session
    _active_chat_session = None
    print("[AI Brain] Đã làm mới phiên hội thoại (Đã xóa bộ nhớ ngữ cảnh cũ).")


def _clean_special_chars(text: str) -> str:
    """Loại bỏ ký tự markdown thừa."""
    if not text:
        return ""
    text = re.sub(r"[\*#_~`>]", "", text)
    text = re.sub(r"^\s*[-+]\s+", "", text, flags=re.MULTILINE)
    return re.sub(r"\s+", " ", text).strip()


def _extract_general_topic(query: str) -> str:
    """Loại bỏ các từ đệm mở đầu để lấy chủ đề cốt lõi phục vụ tra cứu tri thức trực tuyến."""
    if not query:
        return ""
    q = query.strip().rstrip("?").rstrip("!").rstrip(".").strip()
    filler_patterns = [
        r"^(hãy\s+)?(kể|nói|giới\s+thiệu|thuyết\s+minh|trình\s+bày|chia\s+sẻ)?\s*(cho\s+(tôi|mình|em|anh|chị)\s*(nghe|biết)?)?\s*(về)?\s*",
        r"^(bạn\s+có\s+biết|bạn\s+biết\s+gì\s+về|tìm\s+hiểu\s+về|thông\s+tin\s+về)\s*",
        r"^(tôi\s+muốn\s+hỏi\s+về|tôi\s+muốn\s+tìm\s+hiểu\s+về|giải\s+thích\s+về)\s*",
        r"^(ai\s+là|nguồn\s+gốc\s+của|ý\s+nghĩa\s+của|lịch\s+sử\s+của)\s*",
    ]
    cleaned = q
    for pattern in filler_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
    return cleaned if len(cleaned) >= 2 else q


def _handle_conversational_chitchat(query: str) -> Optional[str]:
    """Phản hồi thông minh, duyên dáng cho các câu hỏi giao lưu, tình cảm, đời sống hoặc về tác giả."""
    if not query:
        return None
    q = query.lower().strip()
    
    # 1. Hỏi về người yêu / tình cảm / tác giả (anh Quyền, các bạn học sinh...)
    if any(k in q for k in ["người yêu", "nguoi yeu", "bạn gái", "ban gai", "bạn trai", "ban trai", "crush", "hẹn hò", "hen ho", "kết hôn", "lay vo"]):
        if any(name in q for name in ["quyền", "quyen", "anh quyền", "anh quyen", "tác giả", "tac gia", "người làm", "nguoi lam"]):
            return "Dạ, anh Quyền và các bạn trong nhóm nghiên cứu trường Quốc Học Quy Nhơn vẫn đang dành trọn tâm huyết để phát triển và hoàn thiện trí tuệ nhân tạo cho tôi phục vụ du khách tốt nhất đấy ạ!"
        return "Tôi là Robot hướng dẫn viên trí tuệ nhân tạo, tình yêu lớn nhất của tôi chính là tình yêu văn hóa, lịch sử và niềm vui được đồng hành cùng quý khách trong triển lãm ạ!"

    # 2. Hỏi về người tạo ra / tác giả / nguồn gốc
    if any(k in q for k in ["ai tạo ra", "ai lam ra", "ai làm ra", "ai lập trình", "ai sinh ra", "nguồn gốc của bạn", "nhóm phát triển"]):
        return "Tôi được nghiên cứu và phát triển bởi các bạn học sinh trường Quốc Học Quy Nhơn nhằm ứng dụng trí tuệ nhân tạo vào bảo tồn và giới thiệu nét đẹp di sản văn hóa Việt Nam."

    # 3. Hỏi về cảm xúc, mệt mỏi, ăn uống
    if any(k in q for k in ["có mệt không", "co met khong", "mệt chưa"]):
        return "Cảm ơn quý khách đã quan tâm! Tôi là robot nên luôn tràn đầy năng lượng và sẵn sàng hỗ trợ quý khách bất cứ lúc nào ạ."
    if any(k in q for k in ["thích ăn gì", "thich an gi", "ăn cơm chưa", "an com chua", "uống nước"]):
        return "Tôi hoạt động bằng điện năng và nguồn năng lượng tinh thần từ những câu hỏi thú vị của du khách, chứ tôi không ăn uống được như con người ạ!"

    # 4. Kể chuyện vui / hài hước
    if any(k in q for k in ["chuyện cười", "chuyen cuoi", "hài hước", "hai huoc", "kể chuyện vui", "ke chuyen vui"]):
        return "Có một chú robot đi thi học sinh giỏi môn Văn, giám khảo hỏi: 'Ước mơ lớn nhất của em là gì?'. Robot liền đáp: 'Dạ, là không bao giờ bị mất kết nối mạng và hết pin khi đang trò chuyện với du khách ạ!'."

    return None


def search_general_knowledge(query: str) -> Optional[str]:
    """
    Tra cứu tri thức tổng quát trực tuyến khi Gemini API tạm thời chưa kết nối.
    Cho phép Robot trả lời chính xác mọi câu hỏi mở rộng ngoài lề (địa lý, khoa học, nhân vật, lịch sử, đời sống...).
    """
    if not query or not query.strip():
        return None

    # 0. Ưu tiên xử lý các câu hỏi giao lưu, tình cảm, đời sống
    chitchat_answer = _handle_conversational_chitchat(query)
    if chitchat_answer:
        return chitchat_answer

    try:
        import urllib.request
        import urllib.parse
        import json

        # 1. Trích xuất chủ đề cốt lõi (Loại bỏ các từ đệm: 'hãy nói cho tôi về...', 'bạn có biết...')
        core_topic = _extract_general_topic(query)

        # 2. Tìm kiếm bài viết tương thích nhất trên Wikipedia tiếng Việt
        search_url = f"https://vi.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(core_topic)}&format=json&utf8=1"
        req = urllib.request.Request(search_url, headers={"User-Agent": "RobotHuongDanVien/2.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode("utf-8"))
            results = data.get("query", {}).get("search", [])

        if not results:
            # Thử lại với nguyên văn câu hỏi nếu trích xuất không ra
            search_url = f"https://vi.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query.strip())}&format=json&utf8=1"
            req = urllib.request.Request(search_url, headers={"User-Agent": "RobotHuongDanVien/2.0"})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode("utf-8"))
                results = data.get("query", {}).get("search", [])

        if not results:
            return None

        # 3. Chấm điểm độ tương đồng tiêu đề bài viết với chủ đề cần hỏi
        best_title = None
        best_score = -1.0

        for res in results[:5]:
            title = res.get("title", "")
            if not title or "danh sách" in title.lower() or "thể loại:" in title.lower():
                continue
            
            # Tính điểm ưu tiên: khớp chính xác cụm từ
            score = 0.0
            t_low = title.lower()
            c_low = core_topic.lower()
            if c_low == t_low:
                score = 100.0
            elif c_low in t_low or t_low in c_low:
                score = 85.0
            
            if score > best_score:
                best_score = score
                best_title = title

        # Chỉ chấp nhận bài viết nếu có độ tương quan chắc chắn (>= 75.0), không gán bừa bài không liên quan
        if not best_title or best_score < 75.0:
            return None

        # 4. Lấy nội dung trích đoạn tóm tắt từ bài viết phù hợp nhất
        summary_url = f"https://vi.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(best_title)}"
        req2 = urllib.request.Request(summary_url, headers={"User-Agent": "RobotHuongDanVien/2.0"})
        with urllib.request.urlopen(req2, timeout=4) as response:
            sum_data = json.loads(response.read().decode("utf-8"))
            extract = sum_data.get("extract", "")

        if extract and len(extract.strip()) >= 25:
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", extract) if len(s.strip()) > 10]
            short_answer = " ".join(sentences[:3])
            return _clean_special_chars(short_answer)
    except Exception:
        pass

    return None


def ask_gemini(question: str, stream_callback: Optional[Callable[[str], None]] = None) -> str:
    """
    Quy trình xử lý câu hỏi của du khách theo đúng thứ tự:
    1. ĐỐI CHIẾU TRONG KHO DỮ LIỆU CỤC BỘ: Nếu câu hỏi về tháp Chăm, di tích, thần thoại, hiện vật -> Trả lời ngay.
    2. GỌI API GEMINI: Nếu câu hỏi ngoài kho dữ liệu (văn hóa thế giới, khoa học, đời sống...) -> Gọi API Gemini để suy luận.
    3. CƠ CHẾ DỰ PHÒNG: Nếu API mất kết nối -> Tự động tra cứu tri thức trực tuyến (Wikipedia).
    
    Args:
        question (str): Câu hỏi của du khách.
        stream_callback (Callable): Hàm callback nhận từng token hiển thị trực tiếp lên màn hình.
        
    Returns:
        str: Toàn bộ câu trả lời hoàn chỉnh.
    """
    global _active_chat_session, _current_model_used
    if not question or not question.strip():
        return "Xin lỗi, tôi chưa nghe rõ câu hỏi. Quý khách vui lòng nói lại nhé."

    # =========================================================================
    # THỨ TỰ 1: ĐỐI CHIẾU TRONG KHO DỮ LIỆU TRIỂN LÃM HIỆN CÓ
    # =========================================================================
    local_answer = search_knowledge_base(question)
    if local_answer:
        if stream_callback:
            # Phát dòng dữ liệu ngay lập tức mà không làm trễ
            sentences = re.split(r"(?<=[.!?\n])\s+", local_answer.strip())
            for s in sentences:
                if s.strip():
                    stream_callback(s.strip() + " ")
        return local_answer

    # =========================================================================
    # THỨ TỰ 2: GỌI GEMINI AI API ĐỂ TRẢ LỜI CÁC CÂU HỎI MỞ RỘNG NGOÀI KHO DỮ LIỆU
    # =========================================================================
    client_obj = _get_client()
    api_error_detail = None

    if client_obj is not None:
        # Thử với session hiện tại
        if _active_chat_session is not None:
            try:
                chunks = []
                for chunk in _active_chat_session.send_message_stream(question.strip()):
                    if chunk.text:
                        cleaned_chunk = chunk.text.replace("*", "").replace("#", "")
                        chunks.append(cleaned_chunk)
                        if stream_callback:
                            stream_callback(cleaned_chunk)
                full_text = "".join(chunks)
                if full_text.strip():
                    return _clean_special_chars(full_text)
            except Exception as e:
                api_error_detail = str(e)
                _active_chat_session = None

        # Thử lần lượt các model trong danh sách Fallback
        tested_models = []
        for model_name in FALLBACK_MODELS:
            if model_name in tested_models:
                continue
            tested_models.append(model_name)

            try:
                _active_chat_session = _init_chat_session(client_obj, model_name)
                _current_model_used = model_name
                chunks = []
                for chunk in _active_chat_session.send_message_stream(question.strip()):
                    if chunk.text:
                        cleaned_chunk = chunk.text.replace("*", "").replace("#", "")
                        chunks.append(cleaned_chunk)
                        if stream_callback:
                            stream_callback(cleaned_chunk)
                full_text = "".join(chunks)
                if full_text.strip():
                    return _clean_special_chars(full_text)
            except Exception as e:
                api_error_detail = str(e)
                _active_chat_session = None
                # Nếu lỗi xác thực API Key (401/403/invalid), không thử lại các model khác để tránh làm trễ hệ thống
                err_str = str(e).lower()
                if "401" in err_str or "403" in err_str or "unauthenticated" in err_str or "invalid" in err_str or "key" in err_str:
                    break
                continue

    if api_error_detail and any(k in api_error_detail.lower() for k in ["401", "403", "unauthenticated", "invalid"]):
        print("\n[LƯU Ý API KEY]: Khóa GEMINI_API_KEY trong file .env chưa hợp lệ hoặc đã hết hạn.")
        print("[HỆ THỐNG]: Đang tự động chuyển sang Động cơ Tri thức Trực tuyến để trả lời câu hỏi...")

    # =========================================================================
    # THỨ TỰ 3: CƠ CHẾ CỨU HỘ MỞ RỘNG TRỰC TUYẾN (ONLINE GENERAL KNOWLEDGE SEARCH)
    # =========================================================================
    general_answer = search_general_knowledge(question)
    if general_answer:
        if stream_callback:
            sentences = re.split(r"(?<=[.!?\n])\s+", general_answer.strip())
            for s in sentences:
                if s.strip():
                    stream_callback(s.strip() + " ")
        return general_answer

    # =========================================================================
    # THỨ TỰ 4: HƯỚNG DẪN TỔNG QUAN KHI KHÔNG TÌM THẤY DỮ LIỆU
    # =========================================================================
    fallback_response = (
        "Tôi có thể hỗ trợ giải đáp các câu hỏi văn hóa, lịch sử cũng như thông tin triển lãm. "
        "Quý khách có thể hỏi tôi về các tháp Chăm, hiện vật trưng bày hoặc các chủ đề mà quý khách quan tâm ạ!"
    )
    if stream_callback:
        stream_callback(fallback_response)
    return fallback_response


# --- KHU VỰC CHẠY THỬ NGHIỆM ĐỘC LẬP ---
if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 60)
    print("  KIỂM THỬ TỐC ĐỘ STREAMING (LOW LATENCY GEMINI)")
    print("=" * 60)

    test_queries = [
        "Tháp Đôi Quy Nhơn có gì đặc biệt?",
        "Bạn có biết chơi game Liên Quân không?",
        "Giải giúp tôi bài toán này: 12 + 15",
        "Thời tiết hôm nay thế nào?",
        "Viết code python giúp tôi",
    ]
    for q in test_queries:
        print(f"\nHỏi: {q}")
        print("Robot: ", end="", flush=True)
        ans = ask_gemini(q, stream_callback=lambda token: print(token, end="", flush=True))
        print()
    print("\n" + "=" * 60)
