# Shorts Studio — bắt đầu ở đây

Đã có một quy trình chạy thật để tạo video tiếng Anh bằng Kokoro, không gọi ElevenLabs, fal.ai hoặc dịch vụ dựng video trả phí. Đây là Studio phụ trợ riêng; không phải bản OpenShorts gốc đã được thay toàn bộ dịch vụ AI.

## Xem kết quả trước

- `exports/d6005408c716/video.mp4`: video mẫu 62,53 giây, 1080×1920, 30 fps, 11 cảnh.
- `exports/d6005408c716/publish-pack.zip`: MP4, giọng WAV, phụ đề SRT, ảnh bìa, mô tả, dự án và timeline.
- `projects/voice-science.json`: dự án mẫu có thể sửa lại.
- `NGHIEN_CUU.md`: kết quả nghiên cứu, chi phí, giới hạn và hướng kiếm tiền.

Video mẫu dùng hình minh họa tự dựng và giọng tổng hợp. Đây là mẫu kỹ thuật để bạn đánh giá phong cách và giọng trước khi sản xuất nội dung cho kênh. Thông tin tham khảo trong dự án cần được mở và kiểm chứng trước khi đăng; mạng của môi trường đã chặn các trang này. File không chứa nhạc nền hoặc footage của người khác.

## Dùng trong môi trường cloud hiện tại

Chạy lệnh sau trong terminal:

```bash
bash /workspace/shorts-studio/start.sh
```

Studio dùng cổng **8787**, OpenShorts gốc dùng frontend **5175** và backend **8000**. Các dịch vụ hiện chỉ lắng nghe trên loopback. Giao diện onboarding không cung cấp web preview; không có URL công khai để mở Studio trên điện thoại. Bạn có thể tải video, gói dự án và gói phần mềm trực tiếp từ các file được đính kèm trong chat.

Nếu cần xuất video bằng lệnh trong cloud:

```bash
cd /workspace/shorts-studio
OMP_NUM_THREADS=2 /workspace/.onboarding/video-flow/venv/bin/python render.py projects/voice-science.json --out /workspace/shorts-studio/exports/my-video-001
```

Đặt một thư mục đầu ra mới cho mỗi video. Lệnh CLI ghi đè file trong thư mục đầu ra được chọn. Giao diện tự tạo mã thư mục riêng nên không ghi đè video trước.

## Dùng trên Windows của bạn

1. Tải `shorts-studio-offline-models.zip`, giải nén ra một thư mục riêng, giữ nguyên cấu trúc.
2. Cài **Python 3.12 bản 64-bit** từ python.org, có Python Launcher (`py`). Cần Internet để cài thư viện lần đầu. Máy Windows này chưa được kiểm thử trực tiếp; phần độc lập và FFmpeg đi kèm đã được kiểm thử trên Linux.
3. Nhấp đúp `CHAY_STUDIO_WINDOWS.bat`. Lần đầu sẽ cài thư viện và kiểm tra mô hình; cần khoảng 1–2 GB ổ trống, RAM nên từ 4 GB. Không cần GPU.
4. Khi cửa sổ báo Uvicorn đang chạy, mở trình duyệt **trên cùng máy**, nhập địa chỉ loopback **127.0.0.1**, cổng **8787**. Giữ cửa sổ lệnh mở. Nhấn Ctrl+C để dừng.

Gói tải về đã chứa hai file mô hình. `setup.py` kiểm tra SHA-256 trước khi dùng; nếu thiếu/hỏng sẽ tải lại từ bản phát hành chính thức. FFmpeg hệ thống được ưu tiên; nếu không có, chương trình dùng FFmpeg đi kèm gói `imageio-ffmpeg`.

## Dùng trên Linux/macOS cá nhân

Trong thư mục giải nén, dùng Python 3.12 và chạy:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python setup.py
OMP_NUM_THREADS=2 .venv/bin/python -m uvicorn server:app --host 127.0.0.1 --port 8787
```

Sau đó mở trình duyệt trên cùng máy theo địa chỉ/cổng ở trên. macOS chưa được kiểm thử trực tiếp. Chỉ dùng bản local, không tự mở cổng này ra Internet: Studio không có cơ chế đăng nhập đa người dùng.

## Tạo video đầu tiên

1. Bấm **Nạp video mẫu** để hiểu cấu trúc, hoặc **Mở dự án JSON** để mở dự án đã lưu.
2. Sửa tiêu đề, mô tả và nguồn kiểm chứng. Dùng một ý chính cho mỗi video.
3. Mỗi cảnh nhập tiêu đề ngắn và 1–2 câu tiếng Anh. Khoảng 140–170 từ thường cho video gần một phút; thời lượng thực tế phụ thuộc giọng và tốc độ.
4. Chọn giọng: `af_heart` mặc định nữ Mỹ; `am_michael`/`am_fenrir` nam Mỹ; `bf_emma` nữ Anh; `bm_george` nam Anh. Nghe thử video để chọn giọng hợp chủ đề. Kokoro không phải công cụ clone giọng ElevenLabs.
5. Chọn minh họa hoặc tải ảnh riêng. Ảnh được crop theo khung dọc; kiểm tra khuôn mặt/chữ sau khi xuất. Chỉ dùng ảnh có quyền khai thác phù hợp.
6. Bấm **Lưu dự án JSON** để tránh mất chỉnh sửa khi tải lại trang. Dự án JSON không kèm file ảnh; giữ thư mục `uploads` nếu chuyển dự án sang máy khác.
7. Bấm **Tạo video**, đợi tiến trình kết thúc; một video CPU có thể mất vài phút. Mỗi lần dựng chỉ nhận một video.
8. Nghe từ đầu đến cuối, kiểm tra phát âm tên riêng, phụ đề, nguồn tin và bố cục. Tải **MP4** hoặc **Gói đăng video ZIP**.

Phụ đề được đồng bộ theo **câu được tổng hợp**, không phải nhận dạng hoặc highlight từng từ. Chương trình không tự tìm footage trên Internet, không tự sinh kịch bản AI, không có nhân vật lip-sync và không tự đăng tài khoản.

## Đăng lên YouTube, TikTok và Facebook

- Dùng MP4 dọc sạch làm bản gốc; đăng riêng trên từng nền tảng. Không tải video đã có watermark của một nền tảng để đăng lại.
- Lấy tiêu đề/mô tả từ `publish.txt`, sửa cho đúng nội dung và cách diễn đạt của từng kênh. Ảnh bìa là `cover.jpg`; khả năng chọn ảnh bìa Shorts tùy giao diện thiết bị/nền tảng.
- Khai báo nội dung tổng hợp/chỉnh sửa theo câu hỏi thực tế của nền tảng khi đăng. Tag metadata trong video không thay được nút khai báo của nền tảng.
- Tải lên chưa đồng nghĩa có quyền kiếm tiền. Kiểm tra mục kiếm tiền trong tài khoản thật và điều kiện khu vực cư trú.
- Chưa kết nối hay đăng bất cứ nội dung nào lên tài khoản của bạn.

## Khi có lỗi

- `py` không tìm thấy: kiểm tra Python 3.12 và Python Launcher trên Windows.
- Cài thư viện lỗi: giữ nguyên thông báo, kiểm tra Internet và đúng phiên bản Python; không tắt TLS/checksum.
- Mô hình lỗi: chạy `setup.py` để kiểm tra/tải lại, không sửa mã băm.
- Port 8787 đã dùng: đóng phiên Studio cũ hoặc đổi `--port` khi khởi động thủ công.
- Tên riêng đọc sai: sửa cách viết phát âm trong lời đọc; giữ cách viết chuẩn trong tiêu đề.
- Dựng lỗi: xem `exports/<mã-video>/render.log` và trạng thái lỗi trên giao diện. Dừng máy giữa quá trình dựng sẽ làm gián đoạn video; tạo lại sau khi khởi động.

Không cần nhập khóa API hay giá trị bí mật để chạy quy trình này.
