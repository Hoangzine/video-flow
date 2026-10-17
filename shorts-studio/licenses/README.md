# Nguồn mô hình và thư viện

- Kokoro ONNX runtime: https://github.com/thewh1teagle/kokoro-onnx — MIT. Bản sao giấy phép: `kokoro-onnx-MIT.txt`.
- Nguồn Kokoro: https://github.com/hexgrad/kokoro — Apache-2.0. Bản sao giấy phép: `kokoro-Apache-2.0.txt`.
- Hai file mô hình được lấy qua HTTPS từ https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.1 . Mã SHA-256 nằm trong `setup.py`. Đây là bản đóng gói ONNX của cộng đồng; cần giữ nguồn gốc khi phân phối lại.
- Các thư viện Python khác và bản FFmpeg đóng gói có giấy phép riêng, đi cùng bản phân phối được pip cài. Xem metadata/license của đúng phiên bản trước khi phân phối thành sản phẩm khác.
- Khi có checkout cloud, Studio gọi helper của Hoangzine/video-flow và mutonby/openshorts. Gói portable không kèm mã nguồn hai repository đó; adapter độc lập được dùng khi không có chúng.

Minh họa mặc định trong video mẫu được dựng bằng các hình hình học và chữ. Chưa bao gồm ảnh stock/nhạc/giọng của cá nhân khác. Ảnh bạn bổ sung cần có quyền sử dụng riêng.
