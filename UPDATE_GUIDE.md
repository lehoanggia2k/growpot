# Hướng Dẫn Cập Nhật GrowPlot

## Tổng Quan
Tài liệu này hướng dẫn cách cập nhật tính năng mới và thêm assets cho game GrowPlot, sau đó build lại file exe.

## Yêu Cầu
- Python 3.10+
- PyInstaller đã được cài đặt
- Pillow đã được cài đặt

## 1. Cập Nhật Tính Năng (Code Changes)

### Thêm Tính Năng Mới
1. **Chỉnh sửa code Python** trong thư mục `growplot/`:
   - `app.py`: Logic chính của ứng dụng
   - `anim.py`: Xử lý animation
   - `game_config.py`: Cấu hình game
   - `ui_config.py`: Cấu hình giao diện
   - `state.py`: Quản lý trạng thái game

2. **Thêm import mới** nếu cần thiết trong `main.py`

3. **Test code** bằng cách chạy:
   ```powershell
   python main.py
   ```

### Ví dụ: Thêm tính năng mới
```python
# Trong growplot/app.py
def new_feature(self):
    # Code tính năng mới
    pass
```

## 2. Thông Số Assets

### Yêu Cầu Chung
- **Kích thước**: 96x96 pixels (rộng × cao)
- **Format**: PNG với transparency (RGBA)
- **Đặt tên**: `frame_001.png`, `frame_002.png`, ... (3 chữ số)
- **Số frames**: Thường 12 frames cho mỗi animation
- **Background**: Phải là transparent (không có nền)

### Mô tả Assets Theo Loại

#### 🌱 Cây (Plants)
Mỗi loại cây có 3 giai đoạn phát triển:
- **seed**: Hạt giống (thường 4-12 frames)
- **sprout**: Mầm non (thường 4-12 frames)
- **plant**: Cây trưởng thành (thường 12 frames)

**Ví dụ cấu trúc**:
```
assets/plants/your_plant/
├── seed/
│   ├── frame_001.png  # Hạt giống nhỏ
│   ├── frame_002.png  # Hạt nứt ra
│   └── frame_003.png  # Mầm đầu tiên
├── sprout/
│   ├── frame_001.png  # Mầm nhỏ
│   ├── frame_002.png  # Lá đầu tiên
│   └── ...            # Tăng dần kích thước
└── plant/
    ├── frame_001.png  # Cây nhỏ với hoa/quả
    ├── frame_002.png  # Cây lớn hơn
    └── ...            # Animation sway (đung đưa)
```

#### 🪴 Chậu (Pots)
- **Mục đích**: Nền cho cây, được composite với plant frames
- **Số frames**: 12 frames cho animation subtle
- **Vị trí**: Luôn ở dưới cùng của pot area

**Ví dụ**:
```
assets/pots/your_pot/
├── frame_001.png  # Chậu rỗng
├── frame_002.png  # Chậu với đất
└── ...            # Animation nhẹ (thở, rung)
```

#### 🔊 Âm Thanh (Sounds)
- **Format**: WAV
- **Mục đích**: Hiệu ứng âm thanh khi tưới nước
- **Đặt tên**: `water.wav`

### Quy Tắc Thiết Kế Assets

#### Cho Cây (Plants)
1. **Seed stage**: Bắt đầu từ hạt nhỏ, phát triển thành mầm
2. **Sprout stage**: Tập trung vào sự phát triển của lá và thân
3. **Plant stage**: Cây trưởng thành với hoa/quả, thêm animation sway
4. **Color palette**: Xanh lá cho thân/lá, màu phù hợp cho hoa/quả
5. **Center alignment**: Cây nên được căn giữa frame

#### Cho Chậu (Pots)
1. **Consistent style**: Giữ phong cách nhất quán với game
2. **Subtle animation**: Chỉ animation nhẹ (không quá rõ)
3. **Bottom alignment**: Chậu nên chạm đáy frame
4. **Transparent areas**: Phần trên chậu phải transparent để cây hiển thị

#### Animation Tips
- **Frame count**: 12 frames = 1.2 giây animation ở 10 FPS
- **Loop smoothly**: Frame cuối nên chuyển mượt sang frame đầu
- **Subtle changes**: Không cần thay đổi lớn giữa frames
- **Consistent timing**: Tất cả frames cùng kích thước và style

## 3. Thêm Assets Mới

### Thêm Loại Cây Mới
1. **Tạo thư mục mới** trong `assets/plants/`:
   ```
   assets/plants/new_plant/
   ├── seed/
   │   ├── frame_001.png  # 96x96, RGBA, transparent bg
   │   ├── frame_002.png
   │   └── frame_012.png  # Tối đa 12 frames
   ├── sprout/
   │   ├── frame_001.png
   │   └── ...
   └── plant/
       ├── frame_001.png
       └── ...
   ```

2. **Cập nhật game_config.py** để thêm thông tin cây mới:
   ```python
   PLANT_STATS: dict[str, PlantStats] = field(default_factory=lambda: {
       "basic": PlantStats(growth_time_sec=10.0, yield_amount=1, seed_price=0, harvest_price_per_item=20),
       "new_plant": PlantStats(growth_time_sec=15.0, yield_amount=2, seed_price=25, harvest_price_per_item=35),
   })
   ```

### Thêm Chậu Mới
1. **Tạo thư mục** `assets/pots/new_pot/`
2. **Thêm frames** giống như chậu hiện tại
3. **Cập nhật cấu hình** trong code

### Thêm Âm Thanh
1. **Thêm file WAV** vào `assets/sounds/`
2. **Cập nhật code** để sử dụng âm thanh mới

## 3. Build Lại File Exe

### Sử dụng file .spec hiện tại
```powershell
pyinstaller -y main.spec
```

### Hoặc build từ đầu
```powershell
pyinstaller --onefile --add-data "assets;assets" main.py
```

**Lưu ý**: File exe mới sẽ ghi đè file cũ trong `dist/main.exe`

## 4. Test File Exe

1. **Đóng game** đang chạy (nếu có)
2. **Chạy file exe mới**: `dist\main.exe`
3. **Kiểm tra tính năng mới**
4. **Kiểm tra assets mới** có load đúng không

## 5. Troubleshooting

### Lỗi "Module not found"
- Đảm bảo tất cả import đều đúng
- Kiểm tra file `__init__.py` trong thư mục growplot

### Assets không load
- Kiểm tra đường dẫn file PNG
- Đảm bảo tên file đúng format: `frame_001.png`, `frame_002.png`,...
- Kiểm tra kích thước và format PNG

### Exe không chạy
- Kiểm tra file exe có bị virus scanner block không
- Thử chạy với quyền admin
- Kiểm tra log lỗi trong console

### Performance chậm
- Giảm số lượng frames animation
- Tối ưu kích thước hình ảnh
- Sử dụng UPX compression: thêm `--upx` khi build

## 6. Best Practices

- **Backup** file exe cũ trước khi build mới
- **Version control** code với Git
- **Test thoroughly** trên máy khác
- **Document changes** trong README.md
- **Optimize assets** trước khi thêm vào

## 7. Cấu Trúc Thư Mục Sau Khi Cập Nhật

```
growplot/
├── dist/
│   └── main.exe          # File exe mới
├── assets/               # Assets được cập nhật
├── growplot/             # Code được cập nhật
├── main.spec             # File build config
├── README.md             # Tài liệu gốc
└── UPDATE_GUIDE.md       # Tài liệu này
