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

    # --- PHẦN 2: CÁC DI TÍCH & THÁP CHĂM TIÊU BIỂU ---
    "thap_doi": {
        "title": "Tháp Đôi Quy Nhơn (Tháp Hưng Thạnh)",
        "period": "Thế kỷ XII - XIII (Thời kỳ Vijaya)",
        "location": "Đường Trần Hưng Đạo, phường Đống Đa, TP. Quy Nhơn, Bình Định",
        "keywords": ["tháp đôi", "thap doi", "hưng thạnh", "hung thanh", "hai ngọn tháp", "hai tháp", "trần hưng đạo", "đống đa quy nhơn"],
        "description": "Tháp Đôi gồm hai ngọn tháp cổ xây dựng từ thế kỷ XII, tháp lớn cao 20m và tháp nhỏ cao 18m. Kiến trúc tháp mang dấu ấn giao thoa đậm nét giữa văn hóa Chăm Pa và phong cách nghệ thuật Khmer thời kỳ Angkor, là niềm tự hào của vùng đất Quy Nhơn.",
    },
    "thap_banh_it": {
        "title": "Tháp Bánh Ít (Tháp Bạc)",
        "period": "Cuối thế kỷ XI - đầu thế kỷ XII",
        "location": "Xã Phước Hiệp, huyện Tuy Phước, tỉnh Bình Định",
        "keywords": ["tháp bánh ít", "thap banh it", "tháp bạc", "thap bac", "bánh ít", "banh it", "tuy phước", "tuy phuoc", "phước hiệp", "bốn ngọn tháp", "bốn tháp", "1001 công trình"],
        "description": "Tháp Bánh Ít là quần thể bốn ngọn tháp kỳ vĩ ngự trên đỉnh đồi cao, vinh dự được đưa vào cuốn sách 1.001 công trình kiến trúc phải đến trong đời. Đây là tuyệt tác giao thời giữa phong cách cổ điển Mỹ Sơn A1 và phong cách Bình Định đồ sộ.",
    },
    "thap_duong_long": {
        "title": "Tháp Dương Long (Tháp Ngà)",
        "period": "Cuối thế kỷ XII - đầu thế kỷ XIII",
        "location": "Xã Tây Bình, huyện Tây Sơn, tỉnh Bình Định",
        "keywords": ["tháp dương long", "thap duong long", "tháp ngà", "thap nga", "dương long", "duong long", "tháp gạch cao nhất", "cao nhất đông nam á", "39 mét", "39m", "ba ngọn tháp"],
        "description": "Tháp Dương Long là cụm tháp gạch cao nhất Đông Nam Á với tháp giữa cao tới 39 mét. Cụm ba ngọn tháp hùng vĩ này là đỉnh cao nghệ thuật xây gạch kết hợp điêu khắc đá chạm trổ hoa văn tinh xảo thời kỳ Vijaya hưng thịnh.",
    },
    "thap_canh_tien": {
        "title": "Tháp Cánh Tiên",
        "period": "Thế kỷ XII (Thời kỳ Vijaya)",
        "location": "Xã Nhơn Hậu, thị xã An Nhơn, tỉnh Bình Định (Trung tâm Thành Hoàng Đế)",
        "keywords": ["tháp cánh tiên", "thap canh tien", "cánh tiên", "canh tien", "thành hoàng đế", "thanh hoang de", "đá hoa cương trắng", "nhơn hậu", "an nhơn"],
        "description": "Tháp Cánh Tiên tọa lạc ngay trung tâm cố đô Đồ Bàn xưa, nổi bật với các tầng mái thon vút như đôi cánh tiên thanh thoát. Các góc tháp được ốp đá hoa cương trắng chạm trổ tinh xảo, tạo nên vẻ uy nghiêm giữa lòng thành cổ.",
    },
    "thap_thu_thien": {
        "title": "Tháp Thủ Thiện",
        "period": "Thế kỷ XI - XII",
        "location": "Xã Bình Nghi, huyện Tây Sơn, tỉnh Bình Định",
        "keywords": ["tháp thủ thiện", "thap thu thien", "thủ thiện", "thu thien", "sông kôn", "song kon", "bình nghi", "mũi giáo"],
        "description": "Tháp Thủ Thiện là một ngọn tháp cổ thanh nhã đứng soi bóng bên dòng sông Kôn. Tháp mang phong cách kiến trúc Bình Định với các vòm cửa nhọn hình mũi giáo vút thẳng lên trời cao và thân tháp vững chãi.",
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

    # --- PHẦN 3: ĐIÊU KHẮC, BIỂU TƯỢNG & NGHỆ THUẬT KIẾN TRÚC ---
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
    "linh_vat_dieu_khac": {
        "title": "Linh vật Thần thoại Chăm Pa (Kala, Makara, Garuda, Nandin, Apsara)",
        "period": "Thần thoại Ấn Độ giáo & Điêu khắc Chăm Pa",
        "location": "Trang trí trên vòm cửa, diềm mái và bệ thờ đền tháp",
        "keywords": ["kala", "makara", "garuda", "nandin", "apsara", "linh vật", "mặt quỷ", "thủy quái", "bò thần", "chim thần", "vũ nữ"],
        "description": "Kala là mặt quỷ hộ pháp xua đuổi tà khí ở trán cửa; Makara là thủy quái biển nhả linh vật tượng trưng cho sự trù phú của nguồn nước; chim thần Garuda dũng mãnh là vật cưỡi của thần Vishnu; bò thần Nandin biểu trưng cho công lý của thần Shiva; và nàng Apsara với điệu múa uốn cong ba đoạn thân Tribhanga tuyệt mỹ.",
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
