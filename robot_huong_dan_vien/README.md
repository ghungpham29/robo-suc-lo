# DỰ ÁN: ROBOT HƯỚNG DẪN VIÊN TRIỂN LÃM VĂN HÓA (PHIÊN BẢN v5.0 PRO)
### HỒ SƠ THUYẾT MINH DỰ THI KHOA HỌC KỸ THUẬT & TIN HỌC TRẺ

---

## 1. GIỚI THIỆU TỔNG QUAN

**Robot Hướng Dẫn Viên Triển Lãm Văn Hóa (Phiên bản v5.0 Pro)** là hệ thống Trí tuệ Nhân tạo đa phương thức (Multimodal AI) toàn diện, ứng dụng mô hình đàm thoại siêu tốc **Gemini 3.1 Flash-Lite** kết hợp công nghệ tổng hợp giọng nói thần kinh tiếng Việt **Kokoro-Vietnamese AI** theo kiến trúc **Streaming Double-Buffering Queue**.

---

## 2. BẢNG 3 GIỌNG ĐỌC AI TINH TUYỂN (KOKORO-TTS)

| STT | Mã Giọng | Giới tính | Âm sắc & Ứng dụng |
| :-: | :--- | :---: | :--- |
| 1 | `diem_trinh` | **Nữ** | Truyền cảm, ấm áp, trang trọng *(Tiêu chuẩn Hướng dẫn viên)* |
| 2 | `mai_linh` | **Nữ** | Trẻ trung, trong trẻo, tự nhiên *(Mặc định)* |
| 3 | `thanh_dat` | **Nam** | Phóng khoáng, tự tin, rõ ràng *(Giọng Nam tiêu chuẩn)* |

---

## 3. CÁC NÂNG CẤP VƯỢT TRỘI

1. **Xóa bỏ hoàn toàn hiện tượng khựng ở dấu `.` và `!`**:
   - Sử dụng cơ chế **Streaming Double-Buffering Audio Queue**: Câu 1 vừa tổng hợp xong là phát ngay ra loa, trong khi câu 1 đang phát thì câu 2 được tổng hợp ngầm. Khi câu 1 dứt lời, câu 2 nối tiếp ngay tức thì mà không có bất kỳ khoảng lặng chết nào.
2. **Bộ phiên âm ngầm bí mật (`core/phonetics.py`)**:
   - Tự động phiên âm chuẩn xác 100% các địa danh (Khmer -> Khơ me, Angkor -> Ăng co), số La Mã (thế kỷ XII -> thế kỷ mười hai), số đo (20m -> hai mươi mét, 18 mét -> mười tám mét).
   - **Tuyệt đối không hiển thị phiên âm lên màn hình**, giữ nguyên văn bản gốc đẹp mắt cho người dùng.
3. **Tốc độ đọc tối ưu (`VOICE_SPEED = 0.88`)**:
   - Nhịp điệu chậm rãi, ấm áp, đúng phong thái thuyết minh viên.

---

## 4. HƯỚNG DẪN KHỞI CHẠY

```powershell
cd "C:\Users\ADMIN\Desktop\robot_huong_dan_vien"
python main.py
```

- Để đổi nhanh giữa 3 giọng đọc trong khi chạy: gõ **/voice**.
- Để thử giọng độc lập: chạy `python demo_voices.py`.
