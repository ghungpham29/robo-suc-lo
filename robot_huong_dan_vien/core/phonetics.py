"""
Module Phiên âm Âm vị học & Chuẩn hóa Ngữ âm Bí mật (Hidden Phonetic Engine)
Chuyên trách chuyển đổi âm thầm các địa danh, tên riêng, thuật ngữ lịch sử, số La Mã
và số đo sang ngôn ngữ mà mô hình Kokoro-TTS / vig2p có thể phát âm chuẩn xác 100%.

LƯU Ý: Module này chạy ngầm trong tầng Voice, TUYỆT ĐỐI KHÔNG hiển thị kết quả phiên âm
lên giao diện màn hình của người dùng.
"""

import re
from typing import Dict

# Bảng tra cứu số La Mã lịch sử
ROMAN_NUMERALS: Dict[str, str] = {
    "XXI": "hai mươi mốt", "XX": "hai mươi", "XIX": "mười chín", "XVIII": "mười tám", "XVII": "mười bảy",
    "XVI": "mười sáu", "XV": "mười lăm", "XIV": "mười bốn", "XIII": "mười ba", "XII": "mười hai",
    "XI": "mười một", "X": "mười", "IX": "chín", "VIII": "tám", "VII": "bảy", "VI": "sáu",
    "V": "năm", "IV": "bốn", "III": "ba", "II": "hai", "I": "một",
}

# Từ điển ánh xạ phiên âm chuẩn cho từ mượn, tên di tích, thần thoại và tổ chức
PHONETIC_DICTIONARY = [
    # Tên Robot & Dự án
    (r"\bKalepic\b", "Ca lê bit"),
    (r"\bkalepic\b", "ca lê bit"),

    # Địa danh & Nền văn minh Chăm Pa
    (r"\bKhmer\b", "Khơ me"),
    (r"\bkhmer\b", "khơ me"),
    (r"\bAngkor Wat\b", "Ăng co Vát"),
    (r"\bAngkor Thom\b", "Ăng co Thom"),
    (r"\bAngkor\b", "Ăng co"),
    (r"\bangkor\b", "ăng co"),
    (r"\bChampa\b", "Chăm Pa"),
    (r"\bChăm-pa\b", "Chăm Pa"),
    (r"\bVijaya\b", "Vi-gia-ya"),
    (r"\bSimhapura\b", "Sim-ha-pu-ra"),
    (r"\bIndrapura\b", "In-đra-pu-ra"),
    (r"\bVirapura\b", "Vi-ra-pu-ra"),
    (r"\bAmaravati\b", "A-ma-ra-va-ti"),
    (r"\bKauthara\b", "Kao-tha-ra"),
    (r"\bPanduranga\b", "Pan-đu-ran-ga"),
    (r"\bPo Klong Garai\b", "Pô Klông Ga rai"),
    (r"\bPo Klaung Garai\b", "Pô Klông Ga rai"),
    (r"\bPo Nagar\b", "Pô Na ga"),
    (r"\bPo Rome\b", "Pô Rô-mê"),
    (r"\bMy Son\b", "Mỹ Sơn"),
    (r"\bPhù Nam\b", "Phù Nam"),
    (r"\bÓc Eo\b", "Óc Eo"),
    (r"\bSa Huỳnh\b", "Sa Huỳnh"),
    (r"\bĐông Sơn\b", "Đông Sơn"),
    (r"\bTây Sơn\b", "Tây Sơn"),
    (r"\bBàu Trúc\b", "Bàu Trúc"),
    (r"\bMỹ Nghiệp\b", "Mỹ Nghiệp"),
    (r"\bNha Trinh\b", "Nha Trinh"),
    (r"\bChaklin\b", "Chắc lin"),
    (r"\bĐông Yên Châu\b", "Đông Yên Châu"),
    
    # Nhân vật Lịch sử & Vương triều Chăm Pa
    (r"\bKhu Liên\b", "Khu Liên"),
    (r"\bBhadravarman\b", "Bát-đra-vác-man"),
    (r"\bIndravarman\b", "In-đra-vác-man"),
    (r"\bHarivarman\b", "Ha-ri-vác-man"),
    (r"\bSuryavarman\b", "Su-ri-a-vác-man"),
    (r"\bJaya Simhavarman\b", "Gia-ya Sim-ha-vác-man"),
    (r"\bJaya Indravarman\b", "Gia-ya In-đra-vác-man"),
    (r"\bChế Bồng Nga\b", "Chế Bồng Nga"),
    (r"\bChe Bunga\b", "Chế Bồng Nga"),
    (r"\bPo Binasuor\b", "Pô Bi-na-su-o"),
    (r"\bTrà Toàn\b", "Trà Toàn"),
    (r"\bChế Mân\b", "Chế Mân"),
    (r"\bHuyền Trân\b", "Huyền Trân"),

    # Tôn giáo, Thần linh & Linh vật
    (r"\bHindu giáo\b", "Hin đu giáo"),
    (r"\bHindu\b", "Hin đu"),
    (r"\bhindu\b", "hin đu"),
    (r"\bTrimurti\b", "Tri-mu-ti"),
    (r"\bBrahma\b", "Bờ ram ma"),
    (r"\bShiva\b", "Si va"),
    (r"\bshiva\b", "si va"),
    (r"\bVishnu\b", "Vít nu"),
    (r"\bParvati\b", "Pác-va-ti"),
    (r"\bMahishasura Mardini\b", "Ma-hi-sa-su-ra Mác-đi-ni"),
    (r"\bMahishasura\b", "Ma-hi-sa-su-ra"),
    (r"\bNataraja\b", "Na-ta-ra-gia"),
    (r"\bBhadresvara\b", "Bát-đrê-sva-ra"),
    (r"\bLaksmindra-Lokesvara\b", "Lắc-smin-đra Lô-kê-sva-ra"),
    (r"\bAvalokitesvara\b", "A-va-lô-ki-tê-sva-ra"),
    (r"\bLokesvara\b", "Lô-kê-sva-ra"),
    (r"\bLinga\b", "Lin ga"),
    (r"\bYoni\b", "Y ô ni"),
    (r"\bMukhalinga\b", "Múc-kha-lin-ga"),
    (r"\bKosa\b", "Cô-sa"),
    (r"\bGaruda\b", "Ga ru đa"),
    (r"\bGanesha\b", "Ga nê sa"),
    (r"\bNandin\b", "Nan đin"),
    (r"\bApsara\b", "Áp sa ra"),
    (r"\bKala\b", "Ka la"),
    (r"\bMakara\b", "Ma-ka-ra"),
    (r"\bNaga\b", "Na-ga"),
    (r"\bGajasimha\b", "Ga-gia-sim-ha"),
    (r"\bHanuman\b", "Ha-nu-man"),
    (r"\bUroja\b", "U-rô-gia"),
    (r"\bHamsa\b", "Ham sa"),
    (r"\bDevaraja\b", "Đê-va-ra-gia"),
    (r"\bTribhanga\b", "Tri-băng-ga"),
    (r"\bKalan\b", "Ka-lan"),
    (r"\bGopura\b", "Gô-pu-ra"),
    (r"\bKosagrha\b", "Cô-sa-gơ-ra-ha"),

    # Tín ngưỡng, Lễ hội & Nhạc cụ
    (r"\bChăm Ahiêr\b", "Chăm A-hi-e"),
    (r"\bChăm Awal\b", "Chăm A-oan"),
    (r"\bChăm Bani\b", "Chăm Ba-ni"),
    (r"\bChăm Islam\b", "Chăm Ít-xlam"),
    (r"\bAhiêr\b", "A-hi-e"),
    (r"\bBani\b", "Ba-ni"),
    (r"\bSang Magik\b", "Sang Ma-gích"),
    (r"\bKatê\b", "Ka tê"),
    (r"\bkate\b", "ka tê"),
    (r"\bRamưwan\b", "Ra-mư-oan"),
    (r"\bMnei Yang\b", "Mờ-nây Dang"),
    (r"\bMuk Rija\b", "Múc Ri-gia"),
    (r"\bPô Adhia\b", "Pô Át-đi-a"),
    (r"\bPô Bác\b", "Pô Bác"),
    (r"\bPô Kadhar\b", "Pô Ka-đa"),
    (r"\bGinăng\b", "Ghi-năng"),
    (r"\bBaranưng\b", "Ba-ra-nưng"),
    (r"\bParanưng\b", "Pa-ra-nưng"),
    (r"\bSaranai\b", "Sa-ra-nai"),
    (r"\bKanhi\b", "Kan-nhi"),
    (r"\bBiyên\b", "Bi-yên"),
    (r"\bAw kamei\b", "Ao ka-mây"),
    (r"\bKhan matum\b", "Khăn ma-tum"),
    (r"\bAtau\b", "A-tau"),
    (r"\bKut\b", "Cút"),
    (r"\bGhur\b", "Gu"),
    (r"\bAkhar Thrah\b", "A-kha Thơ-ra"),
    (r"\bBrahmi\b", "Bờ-ram-mi"),
    (r"\bSanskrit\b", "Xăng-xcơ-rít"),

    # Tổ chức & Viết tắt
    (r"\bUNESCO\b", "U nét xcô"),
    (r"\bTP\.\s*", "Thành phố "),
    (r"\bTp\.\s*", "Thành phố "),
    (r"\bTP\b", "Thành phố"),
    (r"\bTCN\b", "Trước Công Nguyên"),
    (r"\bSCN\b", "Sau Công Nguyên"),
    (r"\bTHPT\b", "Trung học phổ thông"),
    (r"\bKHKT\b", "Khoa học Kỹ thuật"),
    (r"\bWRO\b", "Đắp-liu Rờ-ô"),
]


def number_to_words(n: int) -> str:
    """Chuyển đổi mọi số nguyên từ 0 đến hàng tỷ sang chuỗi tiếng Việt chuẩn mực."""
    units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    if n == 0:
        return "không"
    if n < 10:
        return units[n]
    if n < 20:
        rem = n % 10
        if rem == 0:
            return "mười"
        elif rem == 1:
            return "mười một"
        elif rem == 5:
            return "mười lăm"
        else:
            return f"mười {units[rem]}"
    if n < 100:
        tens = n // 10
        rem = n % 10
        s = f"{units[tens]} mươi" if tens > 1 else "mười"
        if rem == 1:
            s += " mốt"
        elif rem == 4:
            s += " tư"
        elif rem == 5:
            s += " lăm"
        elif rem > 0:
            s += f" {units[rem]}"
        return s
    if n < 1000:
        h = n // 100
        rem = n % 100
        s = f"{units[h]} trăm"
        if rem == 0:
            return s
        if rem < 10:
            return f"{s} lẻ {units[rem]}"
        return f"{s} {number_to_words(rem)}"
    if n < 1000000:
        th = n // 1000
        rem = n % 1000
        s = f"{number_to_words(th)} nghìn"
        if rem == 0:
            return s
        if rem < 100:
            if rem < 10:
                return f"{s} không trăm lẻ {units[rem]}"
            return f"{s} không trăm {number_to_words(rem)}"
        return f"{s} {number_to_words(rem)}"
    if n < 1000000000:
        mil = n // 1000000
        rem = n % 1000000
        s = f"{number_to_words(mil)} triệu"
        if rem == 0:
            return s
        return f"{s} {number_to_words(rem)}"
    return str(n)


def to_speech_phonetics(text: str) -> str:
    """
    Chuyển đổi âm thầm văn bản sang dạng ngữ âm hoàn hảo cho Kokoro-TTS:
    1. Phiên âm các địa danh, từ khóa nước ngoài (Khmer, Angkor, Hindu, Shiva...).
    2. Phiên âm số La Mã (thế kỷ XII -> thế kỷ mười hai).
    3. Phiên âm số liệu và đơn vị đo (20m -> hai mươi mét, 18 mét -> mười tám mét).
    4. Phiên âm toàn bộ các con số Ả Rập (1921, 2005, 1001...).
    5. Làm sạch ký tự đặc biệt (*, #, ~).
    """
    if not text:
        return ""

    # 1. Áp dụng từ điển phiên âm địa danh và thuật ngữ
    for pattern, replacement in PHONETIC_DICTIONARY:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # 2. Xử lý số La Mã trong các cụm ngữ cảnh
    for rom, vn in ROMAN_NUMERALS.items():
        text = re.sub(r"\bthế kỷ\s+" + rom + r"\b", f"thế kỷ {vn}", text, flags=re.IGNORECASE)
        text = re.sub(r"\bthế kỉ\s+" + rom + r"\b", f"thế kỉ {vn}", text, flags=re.IGNORECASE)
        text = re.sub(r"\bthời kỳ\s+" + rom + r"\b", f"thời kỳ {vn}", text, flags=re.IGNORECASE)
        text = re.sub(r"\bthứ\s+" + rom + r"\b", f"thứ {vn}", text, flags=re.IGNORECASE)
        text = re.sub(r"\b" + rom + r"\b", vn, text)

    # 3. Xử lý số liệu có kèm đơn vị đo lường
    text = re.sub(r"(\d+)\s*(m\b|mét|met)", lambda m: f"{number_to_words(int(m.group(1)))} mét", text, flags=re.IGNORECASE)
    text = re.sub(r"(\d+)\s*(cm\b|xentimét)", lambda m: f"{number_to_words(int(m.group(1)))} xăng ti mét", text, flags=re.IGNORECASE)
    text = re.sub(r"(\d+)\s*(km\b|kilômét)", lambda m: f"{number_to_words(int(m.group(1)))} ki lô mét", text, flags=re.IGNORECASE)
    text = re.sub(r"(\d+)\s*(ha\b|hécta)", lambda m: f"{number_to_words(int(m.group(1)))} héc ta", text, flags=re.IGNORECASE)
    text = re.sub(r"(\d+)\s*%", lambda m: f"{number_to_words(int(m.group(1)))} phần trăm", text)

    # 4. Xử lý tất cả các con số nguyên còn lại
    text = re.sub(r"\b(\d+)\b", lambda m: number_to_words(int(m.group(1))), text)

    # 5. Loại bỏ ký tự thừa
    text = re.sub(r"[\*#_~`>]", "", text)
    return re.sub(r"\s+", " ", text).strip()
