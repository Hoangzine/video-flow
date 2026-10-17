# OpenShorts, thay ElevenLabs và làm video tiếng Anh với chi phí thấp

Ngày nghiên cứu: 17/10/2026. Nguồn chính là README và mã nguồn dự án được tải thực tế; không có bằng chứng đã xem được hai video tham chiếu của bạn.

## Đã xác định được gì

Có nhiều repository mang tên OpenShorts. Dự án gốc được dùng tạm cho công việc này là **mutonby/openshorts**: https://github.com/mutonby/openshorts . Đây cũng là nguồn mà một số bản fork dẫn lại. Chưa thể khẳng định video TikTok giới thiệu chính xác repository này nếu chưa đọc được tên tác giả/link trong video.

Bản đã kiểm tra: commit `e2e9e3e0a109fa36eaf63ed38f28ce71de5515a4` tại `/workspace/openshorts`.

- [README tại bản đã kiểm tra](https://github.com/mutonby/openshorts/blob/e2e9e3e0a109fa36eaf63ed38f28ce71de5515a4/README.md)
- [Pipeline tạo AI Shorts](https://github.com/mutonby/openshorts/blob/e2e9e3e0a109fa36eaf63ed38f28ce71de5515a4/saasshorts.py)
- [Backend chọn LLM](https://github.com/mutonby/openshorts/blob/e2e9e3e0a109fa36eaf63ed38f28ce71de5515a4/llm_backend.py)
- [Giấy phép mã nguồn MIT](https://github.com/mutonby/openshorts/blob/e2e9e3e0a109fa36eaf63ed38f28ce71de5515a4/LICENSE)

Hai đường dẫn bạn gửi đều bị proxy trả 403:

- YouTube: https://www.youtube.com/watch?v=hpJuB3llhbk
- TikTok: https://vt.tiktok.com/ZSg2g6ebv/

Vì vậy chưa xác nhận được bố cục, tác giả, câu chữ, công cụ và phong cách trong video hướng dẫn. Không dùng video mẫu để khẳng định đã tái tạo đúng video đó.

## OpenShorts thực sự làm gì

| Thành phần | Khả năng | Phụ thuộc/chi phí cần hiểu |
|---|---|---|
| Clip Generator | Video dài → chép lời → chọn đoạn → crop 9:16 → phụ đề | Whisper chạy máy; Gemini hoặc LLM local chọn đoạn; tải YouTube có thể bị chặn |
| AI Shorts / UGC | Viết quảng cáo, tạo nhân vật, giọng, chuyển động/lip-sync | Mã nguồn gọi Gemini, ElevenLabs và fal.ai; không phải quy trình hoàn toàn miễn phí |
| YouTube Studio | Gợi ý tiêu đề, mô tả, ảnh bìa | Nhiều tính năng gọi Gemini; không phải trình dựng giọng miễn phí độc lập |
| Xuất bản tự động | Gửi nội dung qua Upload-Post | Dịch vụ ngoài và tài khoản liên kết; quota/giá có thể thay đổi |
| Lưu trữ cloud | Backup/gallery S3 | Tùy chọn; không cần cho video chạy local |

Trong `saasshorts.py`, `generate_voiceover()` gửi HTTPS tới ElevenLabs; pipeline `generate_full_video()` yêu cầu `elevenlabs_key` và `fal_key`. Thay riêng giọng đọc chưa loại bỏ được chi phí tạo nhân vật, video chuyển động hoặc lip-sync.

`llm_backend.py` hỗ trợ Ollama/LM Studio/vLLM theo API tương thích OpenAI cho phần chọn đoạn dựa trên transcript. Đây không phải công tắc biến toàn bộ tính năng Gemini thành offline: nhận diện bố cục và một số đường xử lý video không lời vẫn có giới hạn. Chưa cài LLM local hay kiểm thử tự chọn đoạn trong lần này.

README hiện mô tả self-host miễn phí, dịch vụ hosted có gói trả phí từ $12/tháng. Đây là mô tả của tác giả ở bản đã đọc, không phải báo giá được xác minh trực tiếp hay cam kết giữ nguyên. Không dùng con số free-tier hoặc chi phí mỗi video trong README làm cam kết sản xuất.

## Phương án đã triển khai

**Kịch bản tiếng Anh do người dùng biên tập → Kokoro local → hình minh họa gốc/ảnh được tải lên → FFmpeg → MP4 dọc + SRT + ảnh bìa + văn bản đăng.**

Giao diện tiếng Việt nằm trong `/workspace/shorts-studio`, độc lập với giao diện OpenShorts. Khi chạy trong cloud, renderer dùng helper âm thanh của `video-flow` và cấu hình encoder của OpenShorts. Gói độc lập có adapter Kokoro và cấu hình FFmpeg riêng để chạy khi không có hai repository đó. Không sửa mã nguồn được Git theo dõi của repository nào.

| Công đoạn | Phương án dùng hiện tại | Phí dịch vụ theo lượt |
|---|---|---|
| Kịch bản | Viết/chỉnh trong giao diện; có thể chuẩn bị bằng cuộc trò chuyện hiện có | Không gọi API tự động |
| Giọng tiếng Anh | Kokoro ONNX 82M, CPU | Không |
| Hình | Minh họa tự dựng hoặc ảnh có quyền sử dụng do bạn tải lên | Không |
| Dựng/zoom/phụ đề | FFmpeg, Pillow | Không |
| Xuất video | H.264/AAC, 1080×1920, 30 fps | Không |
| Đăng video | Đăng thủ công bằng ứng dụng chính thức | Không cần Upload-Post |

Chi phí máy, điện, ổ đĩa, Internet hoặc phí nền tảng cloud vẫn tồn tại. Không hứa mô hình mở chạy nhanh/bằng chất lượng hệ thống trả phí trên mọi thiết bị.

### Vì sao chọn Kokoro

- Đã chạy được thực tế trên CPU của môi trường, không cần GPU hoặc API key.
- Giọng tiếng Anh phù hợp hướng làm nội dung quốc tế; có giọng nam/nữ và Anh/Mỹ.
- Mã runtime MIT: https://github.com/thewh1teagle/kokoro-onnx . Bản phát hành mô hình sử dụng: https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.1 .
- Nguồn mô hình Kokoro có giấy phép Apache-2.0: https://github.com/hexgrad/kokoro . Bản sao giấy phép được đặt trong `licenses/` để tham khảo cùng nguồn.
- Không có chức năng clone giọng hay diễn xuất cảm xúc tương đương mọi tính năng ElevenLabs. Cần tự nghe và sửa phát âm tên riêng.

Đã giữ xác minh HTTPS và thêm SHA-256 cho hai file mô hình tải từ bản phát hành. Mã băm được ghi nhận từ tải HTTPS chính thức lần này rồi dùng để kiểm tra tái lập, không được mô tả là chữ ký độc lập của nhà phát hành. Giấy phép phần mềm/mô hình không tự cấp quyền dùng ảnh, nhạc hoặc giọng của người khác.

### Phần chưa có

- Chưa tạo nhân vật nói/lip-sync miễn phí bằng GPU local.
- Chưa cài mô hình sinh ảnh/video local; máy hiện dùng CPU. FLUX/Wan/Hunyuan và các mô hình khác cần kiểm tra riêng tài nguyên và giấy phép của đúng phiên bản trước khi chọn.
- Chưa có LLM local viết kịch bản tự động; không giả vờ dùng một API miễn phí vô hạn.
- Chưa tự tìm stock footage, chưa tự đăng mạng xã hội, chưa kết nối tài khoản hoặc đủ điều kiện kiếm tiền.
- Phụ đề theo câu, chưa phải canh từng từ. Hình hiện có chuyển động zoom nhẹ, không phải hoạt hình nhân vật.
- Chưa thực nghiệm retention/CTR trên người xem; chưa có cơ sở nói đây là phong cách tối ưu kiếm tiền.

## Bằng chứng chạy thật

- OpenShorts: cài đủ `requirements.txt` với Torch CPU; import Torch/MediaPipe/OpenCV thành công.
- `npm ci` và `npm run build` thành công với lockfile gốc. Giao diện hiện được kiểm tra bằng Chromium, không có lỗi JavaScript khi mở; API qua Vite proxy phản hồi.
- Backend `/health` và `/health/ready` HTTP 200.
- Bộ tests upstream: **1306 passed, 11 failed, 4 skipped**, tổng 1321 ca, khoảng 76 giây. Các lỗi liên quan đường URL YouTube gặp DNS không phân giải; có test dùng downloader giả nhưng vẫn chạm bước DNS thật trước đó. Không đổi test/assertion, không sửa DNS để làm xanh giả, không gọi cả bộ tests đạt.
- Studio: kiểm tra trình duyệt tải 11 cảnh, gửi lệnh dựng thật, mở/lưu dự án JSON, tải ảnh, đặt lại minh họa, tải MP4 với HTTP 206 và tải ZIP.
- API từ chối đầu vào rỗng, giọng sai, tốc độ sai và đường ảnh ngoài thư mục cho phép.
- Video mẫu: 62,533 giây theo ffprobe; H.264 1080×1920 30 fps, AAC mono 48 kHz, khoảng 8,38 MB. Đã decode video và kiểm tra khung hình có phụ đề. Âm thanh được đo khoảng -16,31 LUFS, true peak -1,89 dBTP; chưa đánh giá thính giác như người xem thật.
- Chế độ độc lập đã xuất thêm video 3,33 giây bằng adapter riêng và FFmpeg đóng gói, không dùng FFmpeg trong PATH. Đồng bộ biên cảnh theo 30 fps được kiểm tra ở chế độ này.
- Windows/macOS chưa được chạy trên hệ điều hành thật. Có launcher Windows nhưng không gọi đó là bản đã kiểm thử Windows.

Log chi tiết cloud: `/workspace/.onboarding/openshorts/`. Không có nội dung nào đã được đăng ra nền tảng xã hội.

## Hướng làm kênh để có cơ hội kiếm tiền

Khán giả nước ngoài không tự động đồng nghĩa tài khoản được tham gia chương trình kiếm tiền nước ngoài. Điều kiện còn phụ thuộc nơi cư trú, quốc gia hỗ trợ, tài khoản, tuổi, số liệu kênh và quy định hiện hành.

Các trang chính thức dưới đây cũng bị mạng chặn trong lần nghiên cứu này, vì vậy không nêu ngưỡng follower/view, RPM hoặc danh sách quốc gia như số liệu vừa xác minh:

- YouTube channel monetization policies: https://support.google.com/youtube/answer/1311392
- YouTube Partner Program: https://support.google.com/youtube/answer/72851
- TikTok Creator Rewards: https://support.tiktok.com/en/business-and-creator/creator-rewards-program/creator-rewards-program
- Facebook Content Monetization Policies: https://www.facebook.com/business/help/1348682518563619

Trước khi đầu tư nhiều công, kiểm tra trực tiếp mục Earn/Monetization/Professional dashboard trên tài khoản của bạn. Video AI hoặc giọng AI không bảo đảm được kiếm tiền; nội dung tái sử dụng, lặp lại hàng loạt, thiếu giá trị bổ sung có thể gặp giới hạn. Chỉ thay giọng/crop/phụ đề cho video của người khác không tự tạo ra quyền khai thác thương mại hay bảo đảm được chấp thuận.

### Khởi đầu đề xuất

1. Chọn một ngách bạn có thể kiểm chứng thông tin, chẳng hạn giải thích khoa học đời thường, mẹo công cụ, hoặc lịch sử công nghệ. Video mẫu dùng khoa học giọng nói để thử kỹ thuật, không áp đặt đây là chủ đề kênh cuối cùng.
2. Tạo một loạt nhỏ khoảng 5–10 video gốc để thử. Một câu hỏi cụ thể/video; hook vào vấn đề ngay 1–3 giây đầu, giải thích 2–3 ý và kết thúc có ích.
3. Ưu tiên câu tiếng Anh tự nhiên, lời dẫn có luận điểm và minh họa liên quan. Thay ảnh stock chung chung bằng ví dụ/thao tác/đồ họa giải thích của riêng bạn khi có thể.
4. Giữ bản MP4 sạch và đăng riêng từng nền tảng. Đọc lại nguồn, nghe giọng, kiểm tra crop/phụ đề trước mỗi lần đăng.
5. Theo dõi tỷ lệ xem tiếp/bỏ qua, thời gian xem, đoạn rớt người xem, lượt lưu/chia sẻ và phản hồi. So sánh các video trên cùng nền tảng; không suy ra nhu cầu chỉ từ một video có nhiều view.
6. Chỉnh một yếu tố mỗi đợt: hook, chủ đề, nhịp hình hoặc thời lượng. Chỉ tăng tần suất sau khi biết loại nội dung nào giữ được người xem và phù hợp điều kiện kiếm tiền.

Không có cam kết về lượt xem, doanh thu, thời điểm bật kiếm tiền hoặc việc video mẫu hiện có sẽ được đề xuất.
