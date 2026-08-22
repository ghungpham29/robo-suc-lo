"""
Module Cơ sở Tri thức Triển lãm Cục bộ (Exhibition Knowledge Base)
Cung cấp dữ liệu số hóa chính xác 100% về các hiện vật, di tích lịch sử và văn hóa
nhằm bổ trợ ngữ cảnh chuyên sâu cho mô hình Gemini Flash.
"""

import re
import unicodedata

EXHIBITION_KNOWLEDGE: dict[str, dict] = {
    # --- PHẦN 1: NIÊN BIỂU & TỔNG QUAN VĂN MINH CHĂM PA ---
    "tong_quan_champa": {
        "title": "Nền Văn minh Chăm Pa & Khung lịch sử Tổng quát",
        "period": "Năm 192 đến 1832 (Hơn 16 thế kỷ lịch sử)",
        "location": "Dọc duyên hải miền Trung và Tây Nguyên (4 địa khu: Amaravati, Vijaya, Kauthara, Panduranga)",
        "keywords": [
            "nền văn hóa chăm pa", "nen van hoa cham pa", "nền văn hóa champa", "nen van hoa champa",
            "văn hóa chăm pa", "van hoa cham pa", "văn hóa champa", "van hoa champa",
            "nền văn minh chăm pa", "nen van minh cham pa", "nền văn minh champa", "nen van minh champa",
            "văn minh chăm pa", "van minh cham pa", "văn minh champa", "van minh champa",
            "vương quốc chăm pa", "vuong quoc cham pa", "vương quốc champa", "vuong quoc champa",
            "chăm pa cổ", "champa cổ", "người chăm pa", "nguoi cham pa", "4 địa khu", "amaravati", "kauthara", "panduranga"
        ],
        "description": "Nền văn minh Chăm Pa trải dài hơn 16 thế kỷ (từ năm 192 đến 1832) với khoảng 10 triều đại và gần 100 vị vua. Vương quốc gồm bốn địa khu chính từ Bắc vào Nam là Amaravati, Vijaya, Kauthara và Panduranga, nổi tiếng với nghệ thuật xây tháp gạch bí ẩn, điêu khắc đá tinh xảo và chế độ mẫu hệ độc đáo.",
    },
    "nien_bieu_vuong_trieu": {
        "title": "Niên biểu 5 Thời kỳ Vương triều Chăm Pa",
        "period": "Năm 192 - 1832",
        "location": "Miền Trung Việt Nam",
        "keywords": ["niên biểu", "nien bieu", "các triều đại", "cac trieu dai", "vương triều", "vuong trieu", "lịch sử chăm pa", "lich su cham pa", "5 thời kỳ", "các giai đoạn"],
        "description": "Lịch sử Chăm Pa trải qua năm giai đoạn lớn: Giai đoạn Lâm Ấp từ năm 192, Giai đoạn Hoàn Vương từ 757 đến 854 với kinh đô Virapura, Vương triều Indrapura từ 875 đến 982 rực rỡ Phật giáo, Vương triều Vijaya Đồ Bàn từ 982 đến 1471 tại Bình Định, và Giai đoạn Panduranga thu hẹp tại Nam Trung Bộ trước khi sáp nhập hoàn toàn vào năm 1832 dưới triều vua Minh Mạng.",
    },

    # --- PHẦN 2: CÁC DI TÍCH & THÁP CHĂM TIÊU BIỂU TẠI BÌNH ĐỊNH & MIỀN TRUNG ---
    "thap_doi_quy_nhon": {
        "title": "Tháp Đôi (Tháp Hưng Thạnh)",
        "period": "Cuối thế kỷ XII - Đầu thế kỷ XIII (Thời kỳ Vijaya)",
        "location": "Phường Đống Đa, thành phố Quy Nhơn, tỉnh Bình Định",
        "keywords": [
            "tháp đôi", "thap doi", "tháp đôi quy nhơn", "thap doi quy nhon", "quy nhơn", "quy nhon", "hưng thạnh", "hung thanh",
            "shiva", "linga", "apsara", "garuda", "nandin", "khỉ hanuman", "khi hanuman", "thần điểu", "vũ nữ", "hai ngọn tháp", "hai thap", "trần hưng đạo"
        ],
        "description": "Tháp Đôi là cụm di tích gồm hai ngọn tháp mang đậm phong cách kiến trúc Chăm Pa kết hợp nghệ thuật Khmer. Tháp thờ thần Shiva với biểu tượng Linga bên trong. Vòm cửa và thân tháp được trang trí bằng hệ thống phù điêu tinh xảo tạc hình chim thần Garuda, vũ nữ Apsara, đầu bò thần Nandin và khỉ Hanuman.",
    },
    "thap_duong_long": {
        "title": "Tháp Dương Long (Tháp Ngà)",
        "period": "Thế kỷ XII - XIII (Thời kỳ Vijaya)",
        "location": "Xã Bình Hòa và Tây Bình, huyện Tây Sơn, tỉnh Bình Định",
        "keywords": [
            "tháp dương long", "thap duong long", "tây sơn", "tay son", "tháp ngà", "thap nga", "dương long", "duong long",
            "rắn naga", "ran naga", "mặt kala", "mat kala", "gajasimha", "phù điêu đá", "phu dieu da",
            "nghệ thuật angkor", "tháp gạch cao nhất", "cao nhất đông nam á", "39 mét", "39m", "ba ngọn tháp"
        ],
        "description": "Tháp Dương Long là quần thể gồm 3 tháp thẳng hàng, cao nhất trong các tháp Chăm hiện còn tại Việt Nam (tháp giữa cao 39 mét). Điểm đặc biệt của di tích này là nghệ thuật điêu khắc đá đồ sộ trên các diềm mái, cửa giả. Nổi bật nhất là bộ sưu tập phù điêu rắn Naga, mặt thần thời gian Kala và thủy quái Gajasimha mang ảnh hưởng rõ nét của nghệ thuật Angkor.",
    },
    "thap_banh_it": {
        "title": "Tháp Bánh Ít (Tháp Bạc)",
        "period": "Cuối thế kỷ XI - Đầu thế kỷ XII (Thời kỳ Vijaya)",
        "location": "Xã Phước Hiệp, huyện Tuy Phước, tỉnh Bình Định",
        "keywords": [
            "tháp bánh ít", "thap banh it", "tháp bạc", "thap bac", "bánh ít", "banh it", "tuy phước", "tuy phuoc", "phước hiệp",
            "shiva", "kiến trúc quần thể", "phong cách bình định", "bốn ngọn tháp", "bốn tháp", "1001 công trình", "mỹ sơn a1"
        ],
        "description": "Quần thể Tháp Bánh Ít gồm 4 ngọn tháp nằm trên một ngọn đồi cao, từng được đưa vào cuốn sách 1.001 công trình kiến trúc phải đến trong đời. Đây là di tích có giá trị nghệ thuật cao, đánh dấu sự chuyển tiếp từ phong cách Mỹ Sơn A1 sang phong cách Bình Định. Tháp chính thờ thần Shiva, có vòm mái hình vút nhọn đặc trưng và các chi tiết trang trí mặt thần Kala uy dũng.",
    },
    "thap_canh_tien": {
        "title": "Tháp Cánh Tiên",
        "period": "Thế kỷ XII (Thời kỳ Vijaya)",
        "location": "Xã Nhơn Hậu, thị xã An Nhơn, tỉnh Bình Định (Trung tâm Thành Hoàng Đế)",
        "keywords": ["tháp cánh tiên", "thap canh tien", "cánh tiên", "canh tien", "thành hoàng đế", "thanh hoang de", "đá hoa cương trắng", "nhơn hậu", "an nhơn", "đồ bàn"],
        "description": "Tháp Cánh Tiên tọa lạc ngay trung tâm cố đô Đồ Bàn xưa, nổi bật với các tầng mái thon vút như đôi cánh tiên thanh thoát. Các góc tháp được ốp đá hoa cương trắng chạm trổ tinh xảo, tạo nên vẻ uy nghiêm giữa lòng thành cổ.",
    },
    "thap_thu_thien": {
        "title": "Tháp Thủ Thiện",
        "period": "Thế kỷ XI (Thời kỳ Vijaya)",
        "location": "Xã Bình Nghi, huyện Tây Sơn, tỉnh Bình Định",
        "keywords": ["tháp thủ thiện", "thap thu thien", "thủ thiện", "thu thien", "tây sơn", "tay son", "tháp champa", "phong cách bình định", "sông kôn", "song kon", "bình nghi"],
        "description": "Tháp Thủ Thiện là một ngôi tháp nhỏ bé nhưng giữ nguyên được vóc dáng đặc trưng của phong cách Bình Định: khối hình vuông vức, các trụ ốp tường phẳng, không có hoa văn trang trí rườm rà. Ngôi tháp mang vẻ đẹp mộc mạc, trầm mặc soi bóng bên dòng sông Kôn.",
    },
    "thap_binh_lam": {
        "title": "Tháp Bình Lâm",
        "period": "Cuối thế kỷ X - Đầu thế kỷ XI",
        "location": "Xã Phước Hòa, huyện Tuy Phước, tỉnh Bình Định",
        "keywords": [
            "tháp bình lâm", "thap binh lam", "bình lâm", "binh lam", "tuy phước", "tuy phuoc", "phước hòa",
            "kiến trúc gạch", "phong cách chuyển tiếp", "mỹ sơn a1"
        ],
        "description": "Khác với hầu hết các tháp Chăm thường nằm trên đồi, Tháp Bình Lâm được xây dựng ngay trên vùng đồng bằng. Kiến trúc tháp là sự chuyển tiếp tinh tế giữa phong cách Mỹ Sơn A1 trang nhã và phong cách Bình Định đồ sộ, nổi bật với các môtíp hoa văn hoa lá vươn lên mạnh mẽ.",
    },
    "thap_phu_loc": {
        "title": "Tháp Phú Lốc (Tháp Vàng)",
        "period": "Thế kỷ XII",
        "location": "Xã Nhơn Thành, thị xã An Nhơn, tỉnh Bình Định",
        "keywords": [
            "tháp phú lốc", "thap phu loc", "tháp vàng", "thap vang", "phú lốc", "phu loc", "an nhơn", "nhơn thành",
            "kiến trúc champa", "hải đăng đồ bàn"
        ],
        "description": "Nằm trên đỉnh đồi cao hơn 76m, Tháp Phú Lốc (còn gọi là Tháp Vàng) như một ngọn hải đăng của vương quốc Đồ Bàn xưa. Ngôi tháp phô diễn sự hùng vĩ với cửa chính nhô ra phía trước như một sảnh điện và những góc tháp ốp đá uy nghi.",
    },
    "thanh_do_ban": {
        "title": "Thành cổ Đồ Bàn (Thành Hoàng Đế)",
        "period": "Thế kỷ X - XV (Kinh đô của vương quốc Vijaya)",
        "location": "Xã Nhơn Hậu, thị xã An Nhơn, tỉnh Bình Định",
        "keywords": [
            "thành đồ bàn", "thanh do ban", "cố đô đồ bàn", "co do do ban", "thành hoàng đế", "thanh hoang de", "vijaya",
            "an nhơn", "kinh đô", "chế bồng nga", "che bong nga", "tường đá ong", "voi đá", "sư tử đá"
        ],
        "description": "Đồ Bàn từng là kinh đô tráng lệ của vương triều Chăm Pa (Vijaya) suốt 5 thế kỷ. Nơi đây gắn liền với nhiều biến cố lịch sử và các triều đại vua Chăm như Chế Bồng Nga. Hiện nay, di tích còn lưu giữ nhiều bức tường thành cổ bằng đá ong, tượng voi đá, sư tử đá và các bệ thờ Hindu giáo cổ xưa.",
    },
    "thanh_dia_my_son": {
        "title": "Thánh địa Mỹ Sơn (Di sản Thế giới UNESCO)",
        "period": "Thế kỷ IV - XIII",
        "location": "Huyện Duy Xuyên, tỉnh Quảng Nam",
        "keywords": ["mỹ sơn", "my son", "thánh địa mỹ sơn", "thanh dia my son", "duy xuyên", "di sản thế giới", "thung lũng mỹ sơn", "70 công trình"],
        "description": "Thánh địa Mỹ Sơn là quần thể hơn 70 công trình đền tháp xây dựng liên tục qua 9 thế kỷ trong thung lũng thiêng. Được UNESCO công nhận năm 1999, nơi đây được ví như Angkor thu nhỏ, là trung tâm tế lễ thần linh và an táng các vị vua Chăm Pa cổ đại.",
    },
    "thap_po_klong_garai": {
        "title": "Tháp Po Klong Garai & Hệ thống Thủy lợi Đập Nha Trinh",
        "period": "Cuối thế kỷ XIII - đầu thế kỷ XIV",
        "location": "Đồi Trầu, TP. Phan Rang - Tháp Chàm, tỉnh Ninh Thuận",
        "keywords": ["po klong garai", "pô klông ga rai", "tháp po klong garai", "ninh thuận", "đồi trầu", "phan rang", "dẫn thủy nhập điền", "đập nha trinh", "chaklin"],
        "description": "Tháp Po Klong Garai là cụm tháp Chăm hùng vĩ và nguyên vẹn nhất Việt Nam gồm tháp Kalan, tháp cổng Gopura và tháp lửa Kosagrha. Tháp thờ vị vua hiền Po Klong Garai gắn liền với đập Nha Trinh dài 385m tưới mát cho hơn 12.000 héc-ta ruộng đồng.",
    },
    "thap_po_nagar": {
        "title": "Tháp Bà Po Nagar (Nữ thần Mẹ Xứ Sở)",
        "period": "Thế kỷ VIII - XIII",
        "location": "Đồi Cù Lao, TP. Nha Trang, tỉnh Khánh Hòa",
        "keywords": ["po nagar", "pô na ga", "tháp bà", "thap ba", "nha trang", "thiên y a na", "thien y a na", "mẹ xứ sở", "đồi cù lao", "sông cái", "yang pu nagara"],
        "description": "Tháp Bà Po Nagar là trung tâm tín ngưỡng phụng thờ Nữ thần Mẹ Xứ Sở Yang Pu Nagara của người Chăm và Thiên Y A Na của người Việt. Nữ thần sinh ra từ bọt biển và mây trời núi Đại An, dạy dân trồng lúa, dệt vải và ban phước lành no ấm.",
    },

    # --- PHẦN 3: BẢO VẬT QUỐC GIA & ĐIÊU KHẮC ĐÁ NGHỆ THUẬT TẠI BÌNH ĐỊNH ---
    "phu_dieu_mahishasura_mardini": {
        "title": "Phù điêu Nữ thần diệt quỷ Mahishasura Mardini",
        "period": "Cuối thế kỷ XII - Đầu thế kỷ XIII (Phong cách tháp Mẫm)",
        "location": "Bảo tàng Bình Định (Phát hiện tại phế tích tháp Rừng Cấm, Tây Sơn)",
        "keywords": [
            "mahishasura mardini", "nữ thần diệt quỷ", "nu than diet quy", "tháp rừng cấm", "thap rung cam",
            "bảo vật quốc gia", "bao vat quoc gia", "bảo tàng bình định", "bao tang binh dinh", "phong cách tháp mẫm", "parvati"
        ],
        "description": "Bức phù điêu bằng đá nguyên khối này là Bảo vật Quốc gia vô giá của nghệ thuật điêu khắc Chăm Pa. Tác phẩm khắc họa hình ảnh Nữ thần Mahishasura Mardini (một hiện thân quyền năng của nữ thần Parvati) đang tiêu diệt ác quỷ trâu Mahisha, bệ thờ bên dưới chạm trổ hoa văn hình cánh sen đặc trưng của phong cách tháp Mẫm.",
    },
    "tuong_su_tu_do_ban": {
        "title": "Tượng Sư tử đá Đồ Bàn",
        "period": "Thế kỷ XI - XV (Kinh đô Đồ Bàn - Thời kỳ Vijaya)",
        "location": "Trưng bày tại Bảo tàng Bình Định",
        "keywords": [
            "sư tử đá", "su tu da", "sư tử đồ bàn", "su tu do ban", "đồ bàn", "do ban", "vijaya", "bảo tàng bình định",
            "thần vishnu", "bảo vật quốc gia", "điêu khắc champa", "điêu khắc chăm pa"
        ],
        "description": "Cặp tượng sư tử đá Đồ Bàn là Bảo vật Quốc gia mang hình tượng sư tử nửa nằm nửa đứng độc nhất vô nhị trong lịch sử điêu khắc Chăm Pa. Trong Hindu giáo, sư tử là một kiếp hóa thân của thần Vishnu. Các họa tiết tinh xảo trên cổ linh vật minh chứng cho trí óc sáng tạo và bàn tay tài hoa của nghệ nhân Chăm xưa.",
    },
    "tuong_avalokitesvara_hoai_nhon": {
        "title": "Tượng Bồ Tát Avalokitesvara Hoài Nhơn",
        "period": "Thế kỷ VIII - IX",
        "location": "Phát hiện tại Hoài Nhơn, Bình Định (Lưu giữ tại Bảo tàng Lịch sử TP.HCM / Bảo tàng Bình Định)",
        "keywords": [
            "avalokitesvara", "hoài nhơn", "hoai nhon", "tượng đồng", "tuong dong", "bảo vật quốc gia",
            "phật giáo chăm pa", "phat giao cham pa", "quan âm", "quan am", "4 tay"
        ],
        "description": "Được phát hiện tại Bình Định, đây là một trong những tác phẩm điêu khắc Phật giáo bằng đồng xuất sắc nhất của văn hóa Chăm Pa. Tượng Bồ Tát Avalokitesvara mang thân hình uyển chuyển với 4 tay cầm tràng hạt, quyển sách, nụ sen và bình nước cam lồ, phản ánh sự hưng thịnh của Phật giáo trong giai đoạn này.",
    },
    "phu_dieu_shiva_nataraja": {
        "title": "Phù điêu thần Shiva múa (Shiva Nataraja)",
        "period": "Thế kỷ XII - XIII (Phong cách Tháp Mẫm)",
        "location": "Bảo tàng Bình Định (Phát hiện tại tháp Mẫm, An Nhơn)",
        "keywords": [
            "shiva múa", "shiva mua", "shiva nataraja", "vũ điệu vũ trụ", "vu dieu vu tru", "tháp mẫm", "thap mam",
            "bảo tàng bình định", "thần hủy diệt", "nataraja"
        ],
        "description": "Bức phù điêu chạm khắc hình tượng thần Shiva trong vũ điệu vũ trụ (Nataraja) uyển chuyển và mạnh mẽ. Vũ điệu này tượng trưng cho chu kỳ sáng tạo, bảo tồn và hủy diệt của vũ trụ. Tác phẩm mang những đặc trưng nghệ thuật đỉnh cao của phong cách Tháp Mẫm với hoa văn trang trí dày đặc, chi tiết.",
    },
    "tuong_than_brahma_do_ban": {
        "title": "Tượng thần Brahma 4 mặt",
        "period": "Thế kỷ XII (Phong cách Tháp Mẫm)",
        "location": "Bảo tàng Bình Định (Kinh đô Đồ Bàn)",
        "keywords": [
            "thần brahma", "than brahma", "brahma 4 mặt", "brahma 4 mat", "thần sáng tạo", "than sang tao",
            "bảo tàng bình định", "điêu khắc champa", "trimurti"
        ],
        "description": "Tượng thần Brahma (Thần Sáng tạo) hiếm hoi được tìm thấy tại vùng Đồ Bàn. Tượng được khắc họa với 4 mặt nhìn ra 4 hướng tượng trưng cho sự toàn tri. Dù Phật giáo và tín ngưỡng thờ Shiva lấn át, bức tượng này chứng minh sự hiện diện mạnh mẽ của tư tưởng Trimurti (Tam vị nhất thể) tại kinh đô Vijaya.",
    },
    "phu_dieu_gajasimha": {
        "title": "Phù điêu Voi - Sư tử (Gajasimha)",
        "period": "Thế kỷ XII - XIV",
        "location": "Bảo tàng Bình Định (Phát hiện tại Tháp Mẫm)",
        "keywords": [
            "gajasimha", "voi sư tử", "voi su tu", "thủy quái", "thuy quai", "makara",
            "bảo tàng bình định", "linh vật champa", "linh vật chăm pa"
        ],
        "description": "Gajasimha là một linh vật tưởng tượng kết hợp giữa đầu voi (Gaja) và thân sư tử (Simha). Trong nghệ thuật Chăm Pa thời Vijaya, Gajasimha thường được đặt làm người bảo vệ ở các cửa tháp. Đầu voi tượng trưng cho sức mạnh thiêng liêng, trong khi sư tử là biểu tượng của uy quyền hoàng gia.",
    },
    "tuong_than_ganesha": {
        "title": "Tượng thần Ganesha (Thần Voi)",
        "period": "Thế kỷ XI - XII",
        "location": "Bảo tàng Bình Định",
        "keywords": [
            "ganesha", "thần voi", "than voi", "con của shiva", "thần trí tuệ", "than tri tue",
            "bảo tàng bình định", "thần ganesha"
        ],
        "description": "Thần Ganesha, vị thần mình người đầu voi, là con trai của thần Shiva và Parvati. Ngài được người Chăm thờ phụng như vị thần của trí tuệ, hạnh phúc và người dẹp bỏ mọi trở ngại. Bức tượng Ganesha tại Bình Định mang vẻ đẹp mập mạp, hiền hòa, với các đồ trang sức được chạm trổ công phu.",
    },
    "be_tho_yoni_linga_thap_mam": {
        "title": "Bệ thờ Yoni và Linga tháp Mẫm",
        "period": "Thế kỷ XII - XIII (Phong cách Tháp Mẫm)",
        "location": "Bảo tàng Bình Định",
        "keywords": [
            "yoni", "linga", "yoni linga", "phồn thực", "phon thuc", "sáng tạo vũ trụ",
            "tháp mẫm", "thap mam", "thần shiva", "uroja", "vú phụ nữ"
        ],
        "description": "Bệ thờ kết hợp Yoni (biểu tượng nữ tính) và Linga (biểu tượng nam tính) là tâm điểm trong tín ngưỡng phồn thực thờ thần Shiva. Điểm nhấn của bệ thờ thời kỳ Vijaya là các bệ Yoni được chạm khắc hình ảnh vú phụ nữ xếp thành vòng tròn (Uroja) bao quanh, thể hiện sự cầu mong sinh sôi nảy nở của người Chăm.",
    },
    "phong_cach_dieu_khac": {
        "title": "Hệ thống 8 Phong cách Điêu khắc Chăm Pa",
        "period": "Từ thế kỷ VII đến thế kỷ XVII",
        "location": "Bảo tàng Điêu khắc Chăm Đà Nẵng và các di tích miền Trung",
        "keywords": ["phong cách điêu khắc", "phong cach dieu khac", "8 phong cách", "mỹ sơn e1", "hòa lai", "đồng dương", "mỹ sơn a1", "trà kiệu", "chánh lộ", "tháp mẫm", "yang mun"],
        "description": "Nghệ thuật điêu khắc Chăm Pa trải qua 8 phong cách đỉnh cao: Mỹ Sơn E1 cổ kính, Hòa Lai hoa văn cuộn xoắn, Đồng Dương biểu cảm ấn tượng, Mỹ Sơn A1 chuẩn mực cổ điển, Trà Kiệu vũ nữ uyển chuyển, Chánh Lộ chuyển tiếp, Tháp Mẫm Bình Định cường tráng đồ sộ và Yang Mun dân gian hóa.",
    },
    "bi_an_xay_gach": {
        "title": "Bí ẩn Kỹ thuật Xây gạch Không Mạch Vữa Chăm Pa",
        "period": "Thế kỷ IV - XVII",
        "location": "Tại tất cả các đền tháp Chăm Pa",
        "keywords": ["bí ẩn xây gạch", "bi an xay gach", "không mạch vữa", "khong mach vua", "kỹ thuật xây tháp", "gạch nung", "dầu rái", "núi meru", "trục vũ trụ", "kalan"],
        "description": "Bí ẩn lớn nhất của tháp Chăm là các viên gạch nung đỏ cam được xếp khít không thấy mạch vữa. Các nhà khoa học đưa ra giả thuyết người Chăm đã mài phẳng từng viên gạch và dùng keo thực vật từ dầu rái liên kết, tạo nên những tòa tháp mô phỏng ngọn núi Meru trục vũ trụ vững bền qua ngàn năm.",
    },
    "bieu_tuong_linga_yoni": {
        "title": "Biểu tượng Linh thiêng Linga - Yoni, Mukhalinga & Kosa",
        "period": "Tín ngưỡng Ấn Độ giáo & Chăm Pa",
        "location": "Đặt tại trung tâm lòng tháp Kalan",
        "keywords": ["linga yoni", "linga", "yoni", "mukhalinga", "kosa", "phồn thực", "nguyên lý sáng tạo", "thần shiva", "hủy diệt và tái sinh"],
        "description": "Linga hình trụ tượng trưng cho nam thần Shiva kết hợp bệ Yoni tượng trưng cho nữ thần, biểu trưng cho nguyên lý sáng tạo và phồn thực của vũ trụ. Mukhalinga là loại linga đặc biệt có tạc khuôn mặt vua thần hóa, còn Kosa là bao chụp kim loại quý bằng vàng hay bạc trùm lên linga trong các dịp đại lễ.",
    },
    # --- PHẦN 3.1: DANH MỤC 11 TƯỢNG VĂN HÓA ĐIÊU KHẮC CHĂM PA ---
    "tuong_2_than_shiva": {
        "title": "Tượng số 2: Thần Shiva",
        "period": "Thời kỳ Tháp Mẫm đến giai đoạn muộn",
        "location": "Trán cửa tháp Chăm Pa",
        "keywords": ["tượng số 2", "tượng 2", "thần shiva", "shiva lá đề", "shiva thiền định", "tháp mẫm"],
        "description": "Đại thần Shiva được tôn là vị thần bảo hộ tối cao. Phù điêu thần ngồi thiền định tạc nổi trên khối đá hình lá đề tại trán cửa tháp nhằm trấn giữ, xua đuổi tà ma và khẳng định uy quyền vương triều. Hình tượng tiến hóa từ vẻ đẹp mảnh mai thời sơ kỳ sang nét uy nghiêm, dồn khối vững chắc với râu rậm, mắt lồi ở thời Tháp Mẫm, trước khi phẳng hóa ở giai đoạn muộn."
    },
    "tuong_3_tuong_su_tu": {
        "title": "Tượng số 3: Tượng Sư tử",
        "period": "Từ sơ kỳ đến đỉnh cao thời Tháp Mẫm",
        "location": "Cửa ra vào hoặc góc đền tháp Chăm Pa",
        "keywords": ["tượng số 3", "tượng 3", "tượng sư tử", "sư tử sa thạch", "sư tử góc tháp"],
        "description": "Bắt nguồn từ Ấn Độ, tượng sư tử biểu trưng cho vương quyền, sức mạnh chiến thắng cái ác và sự bảo vệ. Được đục đẽo công phu từ khối sa thạch đặt tại cửa ra vào hoặc góc tháp, sư tử đóng vai trò xua đuổi tà ma khỏi không gian linh thiêng. Tạo hình tiến hóa từ dáng vẻ tự nhiên thời sơ kỳ vươn tới đỉnh cao lực lưỡng, hoành tráng với mắt lồi, nanh nhọn thời Tháp Mẫm."
    },
    "tuong_4_garuda_diet_ran": {
        "title": "Tượng số 4: Garuda diệt rắn",
        "period": "Thế kỷ XII - XIII (Đỉnh cao thời Tháp Mẫm)",
        "location": "Góc hoặc cửa đền tháp Chăm Pa",
        "keywords": ["tượng số 4", "tượng 4", "garuda diệt rắn", "garuda naga", "garuda cắn xé naga"],
        "description": "Bắt nguồn từ thần thoại về mối thù truyền kiếp với loài rắn Naga, phù điêu Garuda diệt rắn đặt tại góc hoặc cửa tháp biểu trưng cho sự cân bằng vũ trụ giữa ánh sáng và bóng tối. Tác phẩm thể hiện kỹ thuật đục đẽo sa thạch nguyên khối đỉnh cao thời Tháp Mẫm với tư thế võ sĩ ghì siết, cắn xé Naga bạo liệt trước khi chuyển thành phù điêu phẳng mang tính nghi lễ ở giai đoạn muộn."
    },
    "tuong_5_dau_chim_than_garuda": {
        "title": "Tượng số 5: Đầu chim thần Garuda",
        "period": "Thế kỷ XII - XIII (Thời kỳ Tháp Mẫm)",
        "location": "Góc mái hoặc vòm cửa đền tháp",
        "keywords": ["tượng số 5", "tượng 5", "đầu chim thần garuda", "đầu garuda", "garuda makara"],
        "description": "Chế tác vào thế kỷ 12-13, đầu Garuda là cấu kiện trang trí góc mái hoặc vòm cửa đền tháp. Sự kết hợp độc đáo giữa nét dữ tợn của chim thần và tai, bờm thủy quái Makara mang ý nghĩa xua đuổi tà ma và biểu thị sự cân bằng vũ trụ. Tác phẩm thể hiện đỉnh cao cơ bắp hoành tráng với mỏ quặp, mắt lồi ở thời Tháp Mẫm trước khi suy tàn từ thế kỷ 14."
    },
    "tuong_6_su_tu_nang_do_be": {
        "title": "Tượng số 6: Sư tử nâng đỡ bệ",
        "period": "Thời kỳ Tháp Mẫm",
        "location": "Chân tháp và bệ thờ Chăm Pa",
        "keywords": ["tượng số 6", "tượng 6", "sư tử nâng đỡ bệ", "sư tử gánh bệ", "atlas phương đông"],
        "description": "Đóng vai trò như Atlas phương Đông, sư tử gánh vác bệ thờ và đền tháp nhằm phong ấn tà khí dưới lòng đất. Nghệ nhân tạc tượng tròn 3D ở chân tháp với thế hai chân khuỳnh, hai tay giơ cao dồn lực nâng đỡ, lồng ngực phồng to căng tràn sức mạnh. Từ hình khối nhỏ thời sơ kỳ, linh vật tiến hóa thành hình mẫu lực lưỡng, cường điệu hóa cơ bắp ở thời Tháp Mẫm."
    },
    "tuong_7_ho_phap_dvarapala": {
        "title": "Tượng số 7: Thần Hộ pháp Mã Chúa (Dvarapala)",
        "period": "Thời kỳ Tháp Mẫm",
        "location": "Trụ đá vuông lối vào đền tháp",
        "keywords": ["tượng số 7", "tượng 7", "thần hộ pháp mã chúa", "dvarapala", "thần hộ pháp", "chiến binh gác cửa"],
        "description": "Là chiến binh gác cửa uy nghiêm trên trụ đá vuông lối vào tháp, Thần Hộ pháp trấn giữ không gian linh thiêng và xua đuổi tà ma. Thần hiện lên ở tư thế quỳ chiến đấu, tay ghì chặt đao chùy cùng khuôn mặt dạ xoa dữ tợn với mắt lồi, nanh nhọn. Tác phẩm đạt đỉnh cao cơ bắp hung tợn, dứt khoát ở thời Tháp Mẫm trước khi bị giản lược thành các nét rạch phẳng ở giai đoạn muộn."
    },
    "tuong_8_phu_dieu_garuda": {
        "title": "Tượng số 8: Phù điêu Garuda",
        "period": "Thời kỳ Tháp Mẫm và tháp Dương Long (Thế kỷ XII - XIII)",
        "location": "Lá đề trán cửa tháp Dương Long, Bình Định",
        "keywords": ["tượng số 8", "tượng 8", "phù điêu garuda", "garuda dương long", "garuda tháp mẫm"],
        "description": "Là vua loài chim và biểu tượng của ánh sáng, Garuda mang sứ mệnh tiêu diệt loài rắn Naga. Phù điêu lá đề trán cửa tháp Dương Long mang dấu ấn giao thoa Champa - Khmer với tạo hình Garuda đầu to, má phính đang giang tay, dùng mỏ kẹp chặt khống chế hai con rắn Naga đối xứng. Nghệ thuật tạc Garuda đạt đỉnh cao sức mạnh bạo liệt, cơ bắp cuồn cuộn ở thời Tháp Mẫm và Dương Long."
    },
    "tuong_9_nu_than_sarasvati": {
        "title": "Tượng số 9: Nữ thần Sarasvati",
        "period": "Thời kỳ Tháp Mẫm - Châu Thành",
        "location": "Phù điêu lá đề vòm cửa tháp",
        "keywords": ["tượng số 9", "tượng 9", "nữ thần sarasvati", "sarasvati", "nữ thần tri thức"],
        "description": "Nữ thần Sarasvati đại diện cho tri thức, nghệ thuật và sự thanh khiết. Phù điêu lá đề vòm cửa tháp chạm khắc nữ thần vô cùng uyển chuyển với 3 đầu, 4 cánh tay cầm búp sen, tràng hạt ngự trên bệ hoa sen để ban phước lành. Tác phẩm tôn vinh trọn vẹn đường cong nữ tính, đạt đỉnh cao quyền năng và đa diện ở thời Tháp Mẫm - Châu Thành."
    },
    "tuong_10_nu_than_mahisasuramardini": {
        "title": "Tượng số 10: Nữ thần Mahisasuramardini",
        "period": "Thời kỳ Tháp Mẫm",
        "location": "Vòm cửa đền tháp Chăm Pa",
        "keywords": ["tượng số 10", "tượng 10", "nữ thần mahisasuramardini", "mahisasuramardini", "nữ thần durga diệt quỷ"],
        "description": "Đại diện cho năng lượng nữ tính tối thượng Shakti, Nữ thần Durga mang sức mạnh chư thần để tiêu diệt quỷ trâu. Tác phẩm chạm nổi cao tại vòm cửa tháp thể hiện nữ thần trong tư thế múa chiến đấu Tandava sống động với 10 cánh tay giương cao binh khí. Hình tượng đạt đỉnh cao bạo liệt, căng tràn sức lực ở thời Tháp Mẫm trước khi dần phẳng hóa ở thời kỳ muộn."
    },
    "tuong_11_than_brahma": {
        "title": "Tượng số 11: Thần Brahma",
        "period": "Thời kỳ Dương Long đến giai đoạn muộn",
        "location": "Phù điêu trán cửa tháp Chăm Pa",
        "keywords": ["tượng số 11", "tượng 11", "thần brahma", "brahma 3 mặt 8 tay", "thần sáng tạo brahma"],
        "description": "Brahma là vị thần Sáng tạo đại diện cho tri thức và sự khởi đầu. Bức phù điêu nổi cao 3D với 3 mặt, 8 cánh tay ngự trên trán cửa tháp mang ý nghĩa thanh lọc u tối, thể hiện nụ cười mỉm thanh thản mang đậm dấu ấn nghệ thuật Angkor. Từ vị thế phụ trợ thời sơ kỳ, Brahma vươn lên thành nhân vật trung tâm uy quyền thời Dương Long trước khi bị khắc phẳng ở giai đoạn muộn."
    },

    # --- PHẦN 4: TÔN GIÁO, CHỨC SẮC & CỘNG ĐỒNG ---
    "ton_giao_chuc_sac": {
        "title": "Tôn giáo Chăm Pa (Bà La Môn Ahiêr, Hồi giáo Bani & Islam)",
        "period": "Từ cổ đại đến nay",
        "location": "Ninh Thuận, Bình Thuận, An Giang và TP.HCM",
        "keywords": ["tôn giáo chăm", "ton giao cham", "bà la môn", "chăm ahiêr", "chăm bani", "chăm awal", "chăm islam", "pô adhia", "sang magik", "thầy char", "trimurti"],
        "description": "Người Chăm hiện nay gồm các cộng đồng chính: Chăm Ahiêr giữ đạo Bà La Môn thờ thần Shiva với chức sắc cao nhất là Pô Adhia; Chăm Bani (Awal) theo Hồi giáo bản địa hóa sinh hoạt tại thánh đường Sang Magik do thầy Char chủ trì; và Chăm Islam theo Hồi giáo Sunni chính thống tại Nam Bộ.",
    },
    "phat_vien_dong_duong": {
        "title": "Phật viện Đồng Dương & Tượng Bồ Tát Laksmindra-Lokesvara",
        "period": "Năm 875 (Thế kỷ IX, Vương triều Indrapura)",
        "location": "Xã Bình Định Bắc, huyện Thăng Bình, tỉnh Quảng Nam",
        "keywords": ["phật viện đồng dương", "phat vien dong duong", "đồng dương", "dong duong", "indrapura", "indravarman ii", "laksmindra lokesvara", "bồ tát đồng dương", "bảo vật quốc gia"],
        "description": "Phật viện Đồng Dương xây dựng năm 875 dưới thời vua Indravarman II là trung tâm Phật giáo Đại thừa lớn bậc nhất Đông Nam Á. Tượng đồng Bồ Tát Laksmindra-Lokesvara khai quật tại đây là Bảo vật quốc gia vô giá với phong cách biểu cảm chân thực và uy quyền.",
    },

    # --- PHẦN 5: XÃ HỘI MẪU HỆ, NGHỀ THỦ CÔNG & CHỮ VIẾT ---
    "che_do_mau_he": {
        "title": "Chế độ Mẫu hệ & Tập quán Gia đình Chăm Pa",
        "period": "Truyền thống ngàn đời",
        "location": "Cộng đồng người Chăm Ninh Thuận và Bình Thuận",
        "keywords": ["chế độ mẫu hệ", "che do mau he", "mẫu hệ", "mau he", "họ mẹ", "ở rể", "con gái út", "ngăn hnam", "atau", "nghĩa trang kut", "ghur"],
        "description": "Xã hội Chăm vận hành theo chế độ mẫu hệ: con cái theo họ mẹ, con gái út thừa kế gia sản và đảm nhiệm thờ cúng tổ tiên gọi là ngăn hnam. Khi kết hôn nhà gái chủ động cưới hỏi và chú rể về ở rể. Dòng họ mẫu hệ Atau có nghĩa trang chung là Kut cho người Ahiêr và Ghur cho người Bani.",
    },
    "gom_bau_truc_my_nghiep": {
        "title": "Gốm Bàu Trúc (UNESCO) & Dệt Thổ cẩm Mỹ Nghiệp",
        "period": "Di sản Văn hóa Phi vật thể UNESCO 2022",
        "location": "Huyện Ninh Phước, tỉnh Ninh Thuận",
        "keywords": ["gốm bàu trúc", "gom bau truc", "bàu trúc", "bau truc", "dệt mỹ nghiệp", "thổ cẩm mỹ nghiệp", "thủ công", "nung lộ thiên", "không dùng bàn xoay", "unesco 2022"],
        "description": "Gốm Bàu Trúc được UNESCO ghi danh năm 2022, là một trong những làng gốm cổ nhất Đông Nam Á làm hoàn toàn thủ công: người thợ đi giật lùi quanh khối đất nặn tay và nung lộ thiên. Làng dệt Mỹ Nghiệp kế bên nổi danh với thổ cẩm hoa văn hình học linga-yoni dệt trên khung cửi gỗ truyền thống.",
    },
    "chu_cham_akhar_thrah": {
        "title": "Chữ Chăm Cổ Akhar Thrah & Bia Đông Yên Châu",
        "period": "Từ thế kỷ IV đến nay (Ngữ hệ Nam Đảo)",
        "location": "Bia Đông Yên Châu tại Trà Kiệu, Quảng Nam",
        "keywords": ["chữ chăm cổ", "chu cham co", "akhar thrah", "bia đông yên châu", "ngữ hệ nam đảo", "austronesian", "chữ brahmi", "văn tự cổ"],
        "description": "Tiếng Chăm thuộc ngữ hệ Nam Đảo, dùng văn tự Akhar Thrah bắt nguồn từ chữ Brahmi Ấn Độ. Bia Đông Yên Châu niên đại thế kỷ IV tại Quảng Nam là văn bản tiếng Chăm cổ nhất và là một trong những chứng tích chữ viết bản địa sớm nhất Đông Nam Á.",
    },

    # --- PHẦN 6: LỄ HỘI & NGHỆ THUẬT BIỂU DIỄN ---
    "le_hoi_kate": {
        "title": "Lễ hội Katê & 4 Bước Nghi lễ Truyền thống",
        "period": "Đầu tháng 7 Chăm lịch (khoảng tháng 9 - 10 Dương lịch)",
        "location": "Tại tháp Po Klong Garai, Po Rome và tháp Bà Po Nagar",
        "keywords": ["lễ hội katê", "le hoi kate", "lễ hội kate", "katê", "kate", "rước y phục", "mnei yang", "muk rija", "raglai", "tháng 7 chăm lịch"],
        "description": "Lễ hội Katê là Di sản văn hóa phi vật thể quốc gia gồm 4 bước thiêng liêng: lễ rước y phục thần linh do đồng bào Raglai mang tới, lễ tắm tượng Mnei Yang, đại lễ dâng cúng múa Muk Rija tại tháp chính, và phần hội sum họp gia đình cúng gia tiên ấm cúng.",
    },
    "le_hoi_ramuwan": {
        "title": "Lễ hội Ramưwan của Đồng bào Chăm Bani",
        "period": "Tháng Ramadan Hồi lịch",
        "location": "Nghĩa trang Ghur và Thánh đường Sang Magik tại Ninh Thuận, Bình Thuận",
        "keywords": ["lễ hội ramưwan", "ramưwan", "ramuwan", "chăm bani", "tảo mộ ghur", "sang magik", "chay tịnh", "tháng chay"],
        "description": "Lễ hội Ramưwan là dịp lễ trang trọng nhất của người Chăm Bani. Mở đầu là nghi thức tảo mộ và cúng gia tiên tại nghĩa trang Ghur, sau đó các vị chức sắc Char vào thánh đường Sang Magik tịnh tâm chay tịnh cầu nguyện quốc thái dân an.",
    },
    "nhac_cu_va_mua_cham": {
        "title": "Nhạc cụ & Vũ điệu Truyền thống (Trống Ginăng, Kèn Saranai, Múa Biyên)",
        "period": "Nghệ thuật dân gian Chăm Pa",
        "location": "Biểu diễn trong các lễ hội Katê, Ramưwan",
        "keywords": ["nhạc cụ chăm", "nhac cu cham", "trống ginăng", "trống baranưng", "kèn saranai", "đàn kanhi", "múa biyên", "múa apsara", "múa quạt", "đội nước"],
        "description": "Âm vang lễ hội Chăm rộn rã với bộ ba nhạc cụ thiêng: trống đôi Ginăng, trống vỗ Baranưng và kèn bầu Saranai kết hợp đàn Kanhi hai dây. Các thiếu nữ Chăm uyển chuyển trong điệu múa quạt, múa Apsara và điệu múa đội nước Biyên giữ bình thăng bằng tuyệt kỹ.",
    },

    # --- PHẦN 7: CÁC VỊ VUA & DANH NHÂN LỊCH SỬ CHĂM PA ---
    "vua_khu_lien": {
        "title": "Vua Khu Liên (Sri Mara) - Người Sáng lập Lâm Ấp",
        "period": "Năm 192",
        "location": "Khu vực miền Trung Việt Nam",
        "keywords": ["khu liên", "khu lien", "sri mara", "lập nước lâm ấp", "năm 192", "khởi nghĩa", "nhà hán", "vua đầu tiên"],
        "description": "Năm 192, thủ lĩnh Khu Liên (Sri Mara) lãnh đạo nhân dân nổi dậy lật đổ ách thống trị của nhà Hán, lập nên nhà nước Lâm Ấp độc lập, đặt nền móng đầu tiên cho lịch sử vương quốc Chăm Pa rực rỡ.",
    },
    "vua_bhadravarman": {
        "title": "Vua Bhadravarman I & Khởi nguồn Thánh địa Mỹ Sơn",
        "period": "Thế kỷ IV",
        "location": "Thánh địa Mỹ Sơn, Quảng Nam",
        "keywords": ["bhadravarman", "bhadresvara", "vua bhadravarman", "dựng mỹ sơn", "thánh địa mỹ sơn đầu tiên", "thế kỷ 4", "thế kỷ iv"],
        "description": "Thế kỷ IV, vua Bhadravarman I cho dựng ngôi đền gỗ đầu tiên tại Mỹ Sơn thờ thần Shiva ghép với tên mình là Bhadresvara, mở ra truyền thống thờ tự vua thần linh thiêng kéo dài hơn 900 năm tại thánh địa.",
    },
    "vua_che_man": {
        "title": "Vua Chế Mân (Jaya Simhavarman III) & Công chúa Huyền Trân",
        "period": "Cuối thế kỷ XIII - đầu thế kỷ XIV (Năm 1306)",
        "location": "Kinh đô Vijaya Đồ Bàn và vùng đất Châu Ô, Châu Lý",
        "keywords": ["chế mân", "che man", "vua chế mân", "jaya simhavarman", "huyền trân", "công chúa huyền trân", "châu ô", "châu lý", "châu rí", "sính lễ", "hòa hiếu"],
        "description": "Vua Chế Mân (Jaya Simhavarman III) là vị vua anh minh đã liên minh cùng Đại Việt đánh tan quân Nguyên Mông. Năm 1306, ông kết duyên cùng Công chúa Huyền Trân nhà Trần và dâng hai châu Ô, Lý làm sính lễ hòa hiếu giữa hai quốc gia.",
    },
    "vua_che_bong_nga": {
        "title": "Vua Chế Bồng Nga (Po Binasuor) - Vua Chiến Binh Lỗi Lạc",
        "period": "Trị vì từ năm 1360 đến 1390",
        "location": "Kinh thành Thăng Long và Sông Hải Triều",
        "keywords": ["chế bồng nga", "che bong nga", "po binasuor", "che bunga", "vua chiến binh", "tiến vào thăng long", "sông hải triều", "1390", "trần khát chân"],
        "description": "Vua Chế Bồng Nga (Po Binasuor) là vị vua - chiến binh kiệt xuất nhất lịch sử Chăm Pa, từng 4 lần dẫn quân tiến vào kinh thành Thăng Long. Ông tử trận năm 1390 trong trận thủy chiến trên sông Hải Triều trước tướng Trần Khát Chân.",
    },
    "vua_po_rome": {
        "title": "Vua Po Rome & Tháp Po Rome Ninh Thuận",
        "period": "Đầu thế kỷ XVII (1627 - 1651)",
        "location": "Làng Hậu Sanh, xã Phước Hữu, huyện Ninh Phước, tỉnh Ninh Thuận",
        "keywords": ["po rome", "pô rô mê", "vua po rome", "tháp po rome", "tháp po rômê", "thế kỷ 17", "vua thần cuối cùng"],
        "description": "Vua Po Rome là vị vua thần hóa cuối cùng được cộng đồng người Chăm thờ phụng tôn kính, nổi tiếng với công lao trị thủy và phát triển nông nghiệp. Ngôi tháp Po Rome bằng gạch nung tại Ninh Thuận hiện vẫn là nơi sinh hoạt tâm linh trang trọng của đồng bào.",
    },
    "vua_tra_toan": {
        "title": "Vua Trà Toàn & Biến cố Thành Đồ Bàn Năm 1471",
        "period": "Năm 1471",
        "location": "Thành Đồ Bàn (Vijaya), Bình Định",
        "keywords": ["trà toàn", "tra toan", "vua trà toàn", "năm 1471", "thất thủ đồ bàn", "lê thánh tông", "thừa tuyên quảng nam"],
        "description": "Năm 1471, vua Lê Thánh Tông đem đại quân đánh chiếm thành Đồ Bàn và bắt vua Trà Toàn. Biến cố lịch sử này đánh dấu việc Chăm Pa mất quyền kiểm soát vùng phía Bắc (Amaravati và Vijaya), trung tâm chuyển dần về Panduranga phương Nam.",
    },
    "bao_vat_quoc_gia_cham": {
        "title": "Các Bảo vật Quốc gia Điêu khắc Chăm Pa",
        "period": "Từ thế kỷ VII đến thế kỷ XIII",
        "location": "Bảo tàng Điêu khắc Chăm Đà Nẵng, Bảo tàng Lịch sử TP.HCM, Bảo tàng Bình Định",
        "keywords": ["bảo vật quốc gia", "bao vat quoc gia", "đài thờ mỹ sơn e1", "đài thờ trà kiệu", "tượng đồng bồ tát đồng dương", "voi đá tháp mẫm", "bảo tàng chăm đà nẵng"],
        "description": "Việt Nam hiện lưu giữ nhiều Bảo vật quốc gia Chăm Pa vô giá như: Đài thờ Mỹ Sơn E1, Đài thờ Trà Kiệu với hàng vũ nữ Apsara tuyệt mỹ, Tượng đồng Bồ Tát Laksmindra-Lokesvara Đồng Dương, và bộ tượng rồng voi đá Tháp Mẫm tại Bình Định.",
    },

    # --- PHẦN 8: CÁC DI SẢN VĂN HÓA BỔ TRỢ KHÁC ---
    "co_do_do_ban": {
        "title": "Cố đô Đồ Bàn (Kinh đô Vijaya Hào hùng)",
        "period": "Thế kỷ XI - XV (Năm 982 - 1471)",
        "location": "Xã Nhơn Hậu, thị xã An Nhơn, tỉnh Bình Định",
        "keywords": ["cố đô đồ bàn", "co do do ban", "kinh đô đồ bàn", "kinh do do ban", "đồ bàn", "do ban", "vijaya", "vi gia ya", "14 tháp chăm", "bình định"],
        "description": "Đồ Bàn (Vijaya) là kinh đô rực rỡ suốt gần 500 năm của Chăm Pa tại Bình Định. Vùng đất võ này hiện còn lưu giữ 14 ngọn tháp Chăm cổ kính độc nhất vô nhị trải khắp các ngọn đồi hùng vĩ.",
    },
    "cong_chieng_tay_nguyen": {
        "title": "Không gian văn hóa Cồng chiêng Tây Nguyên",
        "period": "Di sản văn hóa phi vật thể đại diện của nhân loại (UNESCO 2005)",
        "location": "5 tỉnh Tây Nguyên: Kon Tum, Gia Lai, Đắk Lắk, Đắk Nông, Lâm Đồng",
        "keywords": ["cồng chiêng tây nguyên", "cồng chiêng", "cong chieng", "tây nguyên", "tay nguyen", "buôn làng", "buon lang", "đại ngàn", "nhạc khí", "unesco 2005"],
        "description": "Cồng chiêng Tây Nguyên là nhạc khí thiêng liêng gắn liền với vòng đời con người và các nghi lễ thần linh. Mỗi thanh âm cồng chiêng là sợi dây kết nối giữa cộng đồng buôn làng với thế giới tâm linh của đại ngàn hùng vĩ.",
    },
    "trong_dong_dong_son": {
        "title": "Trống đồng Đông Sơn",
        "period": "Khoảng thế kỷ VII TCN đến thế kỷ I SCN (Thời kỳ Văn Lang - Âu Lạc)",
        "location": "Văn hóa Đông Sơn, lưu vực sông Hồng, sông Mã, sông Cả",
        "keywords": ["trống đồng đông sơn", "trống đồng", "trong dong", "đông sơn", "dong son", "văn lang", "âu lạc", "chim lạc", "hùng vương", "văn minh lúa nước"],
        "description": "Trống đồng Đông Sơn là biểu tượng đỉnh cao của kỹ thuật đúc đồng và văn minh lúa nước của người Việt cổ. Hoa văn ngôi sao nhiều cánh, chim Lạc và cảnh sinh hoạt giã gạo trên mặt trống phản ánh đời sống tinh thần phong phú thời Hùng Vương.",
    },
    "quoc_hoc_quy_nhon": {
        "title": "Trường THPT Quốc Học Quy Nhơn",
        "period": "Thành lập năm 1921",
        "location": "Số 09 đường Trần Phú, TP. Quy Nhơn, tỉnh Bình Định",
        "keywords": ["quốc học quy nhơn", "quoc hoc quy nhon", "trường quốc học", "truong quoc hoc", "quốc học", "quoc hoc", "trăm năm tuổi", "100 năm tuổi", "1921", "trần phú"],
        "description": "Trường THPT Quốc Học Quy Nhơn là ngôi trường trăm năm tuổi giàu truyền thống hiếu học và cách mạng, là cái nôi đào tạo nhiều nhân tài, trí thức ưu tú cho quê hương Bình Định và đất nước Việt Nam.",
    },
    "bao_tang_quang_trung": {
        "title": "Bảo tàng Quang Trung & Trống trận Tây Sơn",
        "period": "Thế kỷ XVIII (Thời kỳ phong trào nông dân Tây Sơn)",
        "location": "Thị trấn Phú Phong, huyện Tây Sơn, tỉnh Bình Định",
        "keywords": ["bảo tàng quang trung", "bao tang quang trung", "quang trung", "nguyễn huệ", "nguyen hue", "trống trận tây sơn", "trống trận", "trong tran", "cây me", "giếng nước", "phú phong"],
        "description": "Bảo tàng Quang Trung là nơi lưu giữ những hiện vật lịch sử hào hùng về Hoàng đế Quang Trung Nguyễn Huệ và phong trào Tây Sơn. Nơi đây nổi tiếng với cây me cổ thụ, giếng nước xưa và nghệ thuật biểu diễn nhạc võ, trống trận Tây Sơn giục giã lòng người.",
    },
}


def _normalize(text: str) -> str:
    """Chuẩn hóa chuỗi tiếng Việt để so khớp chính xác."""
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)
    text = text.replace("đ", "d").replace("Đ", "D")
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def get_exhibition_context_prompt() -> str:
    """
    Tạo văn bản tóm tắt tri thức triển lãm để nhúng trực tiếp vào system instruction của AI.
    """
    lines = ["Dưới đây là tri thức chuẩn xác về các hiện vật/di tích trong triển lãm:"]
    for item in EXHIBITION_KNOWLEDGE.values():
        lines.append(
            f"- {item['title']} ({item.get('period', '')}): {item['description']}"
        )
    return "\n".join(lines)


try:
    from rapidfuzz import fuzz
    _RAPIDFUZZ_AVAILABLE = True
except ImportError:
    _RAPIDFUZZ_AVAILABLE = False


# Danh sách các cụm từ đệm phổ biến trong giao tiếp để lọc lấy từ khóa cốt lõi
FILLER_PATTERNS = [
    r"\b(tôi muốn tìm hiểu về|tôi muốn biết về|muốn tìm hiểu về|muốn biết về|tôi muốn hỏi về|hãy giới thiệu cho tôi về|giới thiệu cho tôi về|cho tôi hỏi về|cho em hỏi về|xin hỏi về|cho mình hỏi về)\b",
    r"\b(cho tôi hỏi|cho em hỏi|xin hỏi|hãy cho tôi biết|hãy kể cho tôi nghe|kể về|nói về|bạn có biết|bạn có hiểu|thuyết minh về|giới thiệu về|tìm hiểu về|thông tin về)\b",
    r"\b(là gì|ở đâu|ở chỗ nào|như thế nào|thế nào|có gì đặc biệt|có ý nghĩa gì|được xây dựng khi nào|được xây khi nào|bao nhiêu tuổi|bao nhiêu mét|cao bao nhiêu|được tạo ra khi nào|xuất xứ từ đâu|có nguồn gốc từ đâu)\b",
    r"\b(ạ|nhé|nhỉ|với|giúp tôi|cho tôi|với ạ|nha)\b",
]

# Danh sách từ dừng (Stopwords) để tránh dương tính giả khi so khớp nội dung chi tiết
_GENERIC_STOPWORDS = {
    "van", "hoa", "nen", "lich", "su", "tim", "hieu", "biet", "nghe", "thuat",
    "viet", "nam", "tinh", "huyen", "thanh", "pho", "quan", "nguoi", "trong",
    "ngoai", "duoc", "nhung", "cac", "mot", "hai", "nay", "kia", "tai", "cho",
    "cua", "cac", "nhung", "cung", "nhu", "voi"
}


def _extract_core_query(text: str) -> str:
    """Lọc bỏ các từ đệm hội thoại để trích xuất trọng tâm câu hỏi của du khách."""
    if not text:
        return ""
    cleaned = text.lower()
    for pat in FILLER_PATTERNS:
        cleaned = re.sub(pat, " ", cleaned, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip()


def _find_multiple_matches(query: str) -> list[dict]:
    """Tìm tất cả các hiện vật/di tích được nhắc đến trong câu hỏi để phục vụ so sánh, tổng hợp."""
    matched = []
    query_raw = query.lower().strip()
    query_norm = _normalize(query)

    for item_id, data in EXHIBITION_KNOWLEDGE.items():
        if item_id == "tong_quan_champa":
            continue
        title_norm = _normalize(data.get("title", ""))
        # Kiểm tra tiêu đề hoặc từ khóa
        is_hit = False
        if title_norm in query_norm:
            is_hit = True
        else:
            for kw in data.get("keywords", []):
                kw_norm = _normalize(kw)
                if len(kw_norm) >= 4 and (kw in query_raw or kw_norm in query_norm):
                    is_hit = True
                    break
        if is_hit:
            matched.append(data)

    return matched


def search_knowledge_base(query: str, min_confidence: float = 75.0) -> str | None:
    """
    Đối chiếu câu nói của du khách với Cơ sở Tri thức Triển lãm (Chính xác 100%, không nhận vơ chủ đề ngoài):
    1. Tự động nhận diện câu hỏi so sánh/tổng hợp đa đối tượng Chăm Pa.
    2. Tầng 1: So khớp cụm từ khóa đặc trưng (Distinctive Entity Keyword Matching).
    3. Tầng 2: So khớp Tiêu đề di tích/hiện vật.
    4. Tầng 3: So khớp mờ có kiểm soát độ dài từ khóa (Fuzzy Match với ngưỡng cao).
    """
    if not query or not query.strip():
        return None

    query_raw = query.lower().strip()
    query_norm = _normalize(query)
    core_q = _extract_core_query(query)
    core_norm = _normalize(core_q) if core_q else query_norm

    # --- KIỂM TRA SO SÁNH / TỔNG HỢP ĐA ĐỐI TƯỢNG TRIỂN LÃM ---
    is_comparative = any(k in query_raw or k in query_norm for k in ["so sanh", "khac nhau", "giong nhau", "va", "giua", "voi"])
    if is_comparative:
        multi_matches = _find_multiple_matches(query)
        if len(multi_matches) >= 2:
            item1, item2 = multi_matches[0], multi_matches[1]
            return (
                f"Về sự đối chiếu: {item1['title']} ({item1.get('period', '')}) mang nét đặc trưng: {item1['description']} "
                f"Trong khi đó, {item2['title']} ({item2.get('period', '')}) lại nổi bật với: {item2['description']} "
                f"Cả hai công trình/hiện vật này đều phản ánh sự đa dạng và đỉnh cao nghệ thuật của nền văn hóa Chăm Pa cổ."
            )

    best_match = None
    highest_score = 0.0

    for item_id, data in EXHIBITION_KNOWLEDGE.items():
        title = data.get("title", "")
        title_norm = _normalize(title)
        description = data.get("description", "")
        keywords = data.get("keywords", [])

        score = 0.0

        # --- TẦNG 1: So khớp từ khóa đặc trưng theo ranh giới từ (Word Boundary) ---
        for kw in keywords:
            kw_raw = kw.lower().strip()
            kw_norm = _normalize(kw)
            # Yêu cầu từ khóa có độ dài tối thiểu 4 ký tự và không phải từ ngữ chung chung
            if len(kw_norm) >= 4 and kw_norm not in ["van hoa", "lich su", "viet nam", "binh dinh"]:
                pattern = r"\b" + re.escape(kw_norm) + r"\b"
                if re.search(pattern, query_norm) or re.search(pattern, core_norm):
                    match_score = 90.0 + len(kw_norm)
                    if match_score > score:
                        score = match_score

        # --- TẦNG 2: So khớp Tiêu đề di tích/hiện vật ---
        # Kiểm tra tiêu đề chính (loại bỏ phần chú thích trong ngoặc đơn)
        clean_title = re.sub(r"\(.*?\)", "", title).strip()
        clean_title_norm = _normalize(clean_title)
        if len(clean_title_norm) >= 5:
            pattern = r"\b" + re.escape(clean_title_norm) + r"\b"
            if re.search(pattern, query_norm) or re.search(pattern, core_norm):
                score = max(score, 100.0)

        # --- TẦNG 3: So khớp mờ (Fuzzy Matching) qua RapidFuzz có kiểm soát ---
        if _RAPIDFUZZ_AVAILABLE and score < 75.0:
            for kw in keywords:
                kw_norm = _normalize(kw)
                if len(kw_norm) >= 5 and kw_norm not in ["van hoa", "lich su", "viet nam"]:
                    ratio = fuzz.token_sort_ratio(core_norm, kw_norm)
                    if ratio >= 85:
                        score = max(score, ratio * 0.95)

        # Ghi nhận kết quả có điểm khớp cao nhất
        if score > highest_score:
            highest_score = score
            best_match = description

    # Chỉ chấp nhận khi độ tin cậy vượt ngưỡng nghiêm ngặt (75.0)
    if highest_score >= min_confidence:
        return best_match

    return None
