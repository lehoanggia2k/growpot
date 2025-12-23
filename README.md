# GrowPlot - Trò Chơi Trồng Cây Desktop

Một trò chơi trồng cây mini chạy trên desktop Windows với các tính năng phong phú bao gồm vật nuôi, cửa hàng, và hệ thống kinh tế.

## ✨ Tính Năng Chính

### 🌱 Hệ Thống Trồng Cây
- **Trồng cây**: Chọn từ nhiều loại hạt giống khác nhau (Basic, Rose, Daisy)
- **Tưới nước**: Click để tưới nước, tăng tốc độ phát triển
- **Thu hoạch**: Thu hoạch khi cây trưởng thành
- **Phát triển theo thời gian**: Cây tự động phát triển ngay cả khi đóng game (offline progress)

### 🪴 Hệ Thống Chậu
- **Default Pot**: Chậu cơ bản, miễn phí
- **Wood Pot**: Chậu gỗ cao cấp (giảm 10% thời gian phát triển, giữ nước tốt hơn 30%, giá 💰200)

### 🐱 Hệ Thống Vật Nuôi
- **Mèo (Cat)**: Tự động tưới nước khi mức nước thấp (giá mở khóa 💰200)
- **Cho ăn**: Cho vật nuôi ăn để duy trì hoạt động (thời gian làm việc: 2 giờ)
- **Kích hoạt/Tắt**: Có thể bật/tắt vật nuôi bất kỳ lúc nào

### 💰 Hệ Thống Kinh Tế
- **Kiếm tiền**: Bán sản phẩm thu hoạch được và bắt côn trùng
- **Cửa hàng**: Mua hạt giống, chậu, vật nuôi, thức ăn và lưới bắt côn trùng
- **Kho**: Lưu trữ sản phẩm thu hoạch, bán hàng loạt
- **Hiển thị tiền**: Xem số dư hiện tại trên giao diện

### 🐛 Hệ Thống Côn Trùng
- **Xuất hiện ngẫu nhiên**: Côn trùng xuất hiện trên cây khi đang phát triển (60-80% tiến trình)
- **Bắt côn trùng**: Sử dụng lưới để bắt côn trùng (mua tại cửa hàng, giá 💰20/lưới)
- **Phạt nếu bỏ sót**: Côn trùng không bắt sẽ làm giảm chất lượng thu hoạch
- **Bán côn trùng**: Bán côn trùng đã bắt được (💰10/con)
- **Thời gian bắt**: Phải bắt trong thời gian ngắn sau khi xuất hiện

### 🎮 Giao Diện & UX
- **Luôn ở trên cùng**: Cửa sổ luôn hiển thị trên desktop
- **Kéo thả**: Có thể di chuyển bằng cách kéo
- **Menu cài đặt**: Truy cập tất cả tính năng qua nút ⚙
- **Âm thanh**: Hiệu ứng âm thanh khi tưới nước (tùy chọn)

## 📋 Yêu Cầu Hệ Thống

- **Hệ điều hành**: Windows 10/11
- **Python**: 3.10+ (bạn đang dùng 3.13)
- **Thư viện**: Pillow (PIL) cho xử lý hình ảnh
- **Không cần GPU**: Chạy mượt trên hầu hết máy tính

## 🚀 Cài Đặt & Chạy

### Cài Đặt
```powershell
# Cài đặt thư viện cần thiết
python -m pip install pillow
```

### Chạy Từ Source Code
```powershell
python main.py
```

### Chạy File Executable
File exe đã được build sẵn trong thư mục `build/main/`:
```powershell
build\main\main.exe
```

## 📁 Cấu Trúc Assets

### 🌱 Cây (Plants)
Mỗi loại cây có 3 giai đoạn:
```
assets/plants/[tên_cây]/
├── seed/           # Hạt giống (4-12 frames)
├── sprout/         # Mầm non (4-12 frames)
└── plant/          # Cây trưởng thành (12 frames)
```

**Các loại cây có sẵn:**
- **basic**: Cây cơ bản (10s phát triển, 1 sản phẩm, miễn phí)
- **rose**: Hoa hồng (15s, 1 sản phẩm, 💰20/hạt)
- **daisy**: Hoa cúc (20s, 2 sản phẩm, 💰30/hạt)

### 🪴 Chậu (Pots)
```
assets/pots/[tên_chậu]/
└── frame_001.png to frame_012.png  # 12 frames animation
```

**Các loại chậu:**
- **default**: Chậu cơ bản (miễn phí)
- **wood**: Chậu gỗ (💰200, 10% nhanh hơn, giữ nước tốt hơn)

### 🐱 Vật Nuôi (Pets)
```
assets/pets/[tên_vật_nuôi]/
└── frame_001.png to frame_012.png  # Animation vật nuôi
```

**Vật nuôi có sẵn:**
- **cat**: Mèo (💰200, tự động tưới nước)

### 🔊 Âm Thanh (Sounds)
```
assets/sounds/
└── water.wav  # Âm thanh tưới nước
```

## 🎯 Cách Chơi

1. **Khởi động game**: Chạy `python main.py`
2. **Trồng cây**: Click menu hạt giống để chọn loại cây
3. **Tưới nước**: Click vào chậu để tưới nước
4. **Bắt côn trùng**: Click vào côn trùng khi xuất hiện trên cây (cần mua lưới trước)
5. **Thu hoạch**: Click thu hoạch khi cây trưởng thành
6. **Làm nhiệm vụ**: Click menu "Nhiệm vụ" để xem và hoàn thành nhiệm vụ hàng ngày
7. **Mở rộng**: Mua chậu mới, vật nuôi, lưới bắt côn trùng từ cửa hàng
8. **Kiếm tiền**: Bán sản phẩm thu hoạch và côn trùng tại kho

### Mẹo Chơi
- Vật nuôi giúp tự động tưới nước khi bạn bận rộn
- Chậu gỗ giúp tiết kiệm thời gian và nước
- Bắt côn trùng kịp thời để tránh giảm chất lượng thu hoạch
- Bán côn trùng để kiếm thêm tiền phụ
- Chuẩn bị lưới trước khi trồng cây để có thể bắt côn trùng
- Game lưu tiến trình tự động vào `state.json`

## 🔧 Phát Triển & Build

### Build File Executable
```powershell
# Sử dụng file spec có sẵn
pyinstaller -y main.spec

# Hoặc build từ đầu
pyinstaller --onefile --add-data "assets;assets" main.py
```

### Thêm Tính Năng Mới
Xem chi tiết trong `UPDATE_GUIDE.md`

## 📝 Ghi Chú Kỹ Thuật

- **Lưu trạng thái**: Tự động lưu vào `state.json` mỗi 1.5 giây
- **Xử lý offline**: Tiếp tục phát triển cây khi đóng game
- **Animation**: 10 FPS, hỗ trợ transparency PNG
- **UI**: Tkinter với theme Windows native
- **Kích thước**: Tự động điều chỉnh theo assets (khuyến nghị 96x96px)

## 🐛 Xử Lý Sự Cố

### Game không khởi động
- Kiểm tra Python và Pillow đã cài đặt
- Đảm bảo thư mục `assets/` tồn tại và có đủ files

### Assets không hiển thị
- Kiểm tra kích thước PNG (96x96px khuyến nghị)
- Đảm bảo background transparent
- Tên file: `frame_001.png`, `frame_002.png`,...

### Performance chậm
- Giảm số lượng frames animation
- Kiểm tra RAM và CPU usage

## 📄 Giấy Phép

Dự án mã nguồn mở. Tự do sử dụng và chỉnh sửa.

## 🤝 Đóng Góp

Muốn thêm tính năng mới hoặc assets? Xem `UPDATE_GUIDE.md` để biết cách đóng góp!

## 📈 Nhật Ký Cập Nhật

### Phiên bản 1.1 (22/12/2025)
- ✅ **Thêm hệ thống nhiệm vụ hàng ngày**
  - Nhiệm vụ thu hoạch cây theo loại cụ thể
  - 2-3 nhiệm vụ mỗi ngày, reset tự động
  - Phần thưởng tiền khi hoàn thành
  - Cửa sổ nhiệm vụ có thể điều chỉnh kích thước
- ✅ **Cải thiện UX**
  - Cửa sổ nhiệm vụ resizable như shop
  - Giao diện nhất quán giữa các cửa sổ

### Phiên bản 1.0 (Ban đầu)
- Hệ thống trồng cây cơ bản
- Hệ thống vật nuôi và cửa hàng
- Hệ thống côn trùng và kinh tế
- UI/UX hoàn chỉnh

---

**Phiên bản hiện tại**: 1.1
**Ngôn ngữ**: Python 3.10+
**Framework**: Tkinter + Pillow
**Tác giả**: Le Hoang Gia
