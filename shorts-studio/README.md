# Shorts Studio — tiếp tục dự án đã làm

Đây là mã nguồn và video mẫu được chuyển nguyên từ môi trường cloud. Không cần nhờ AI dựng lại dự án.

## Xem video ngay trên Windows

Mở `shorts-studio/sample/video.mp4` bằng Media Player hoặc VLC sau khi clone repository. Video dài khoảng 62,5 giây, 1080×1920, 30 fps, có giọng đọc và phụ đề. Video là mẫu kỹ thuật; xem `NGHIEN_CUU.md` để hiểu giới hạn.

## Chạy Studio

1. Cài Python 3.12 64-bit, có Python Launcher (`py`).
2. Trong thư mục `shorts-studio`, chạy `CHAY_STUDIO_WINDOWS.bat`.
3. Lần đầu cần Internet để cài thư viện và tải mô hình Kokoro qua HTTPS chính thức. Mô hình không đưa lên GitHub; `setup.py` kiểm tra SHA-256.
4. Giữ cửa sổ lệnh mở. Trên trình duyệt của cùng máy, mở địa chỉ loopback 127.0.0.1, cổng 8787.
5. Sửa kịch bản, chọn giọng và hình minh họa, rồi xuất video. File mới nằm trong `shorts-studio/exports/`.

Đọc `BAT_DAU.md` để xem hướng dẫn đầy đủ. Trong tài liệu lịch sử, các đường `/workspace/...` là đường cloud cũ, không phải đường Windows. Video mẫu trong nhánh Git này ở `sample/video.mp4`, không ở thư mục exports lịch sử. Gói source Git này không kèm mô hình, venv hoặc publish-pack ZIP.

## Tiếp tục bằng Codex trong VS Code

Mở **thư mục repository đã clone** bằng VS Code và gửi cho Codex:

> Đây là dự án đã có mã, không viết lại. Đọc shorts-studio/README.md và BAT_DAU.md. Trước tiên mở shorts-studio/sample/video.mp4 bằng trình phát trên máy tôi. Sau đó kiểm tra Python 3.12, thiết lập venv và các phụ thuộc cho shorts-studio trên Windows, tải mô hình bằng setup.py, chạy và kiểm tra Studio. Giữ nguyên mã trừ khi cần sửa lỗi được xác minh; chỉ sửa phần cần thiết. Không dùng API trả phí hoặc tự đăng mạng xã hội. Báo kết quả kiểm thử Windows thực tế.

Đã kiểm thử thực tế ở cloud Linux. Launcher Windows được cung cấp nhưng chưa được chạy trên Windows trong lần bàn giao này. Việc cài thư viện/chạy kiểm tra không đòi AI tạo lại mã nhưng Codex vẫn dùng token nếu bạn yêu cầu nó hỗ trợ.

`TRANSFER_MANIFEST.json` ghi SHA-256 các file gốc được chuyển để kiểm tra tính nguyên vẹn.
