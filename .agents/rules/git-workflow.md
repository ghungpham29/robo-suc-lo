# Git Workflow Rules

Khi bắt đầu một phiên làm việc/cuộc trò chuyện hoặc nhận yêu cầu mới:
1. **Kiểm tra trạng thái & Đồng bộ trước khi làm việc:**
   - Luôn chạy `git status` để kiểm tra thay đổi hiện tại.
   - Chạy `git pull` để cập nhật code mới nhất từ remote (`origin/main`).
2. **Thực hiện yêu cầu:**
   - Tiến hành giải quyết yêu cầu của người dùng.
3. **Đồng bộ sau khi hoàn thành công việc:**
   - Sau khi hoàn thành các chỉnh sửa/tính năng, kiểm tra `git status` và commit các thay đổi hợp lý.
   - Luôn luôn `git push` các thay đổi lên GitHub repository (`origin/main`).
