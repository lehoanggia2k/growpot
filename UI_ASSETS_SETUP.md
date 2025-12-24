# UI Assets Setup Guide

Hướng dẫn setup assets cho UI elements trong GrowPlot game.

## 📁 Cấu trúc thư mục Assets

```
assets/
├── ui/                          # Thư mục chứa tất cả UI assets
│   ├── buttons/                 # Assets cho các buttons
│   │   ├── settings_normal.png
│   │   ├── settings_hover.png
│   │   ├── settings_pressed.png
│   │   ├── close_normal.png
│   │   ├── close_hover.png
│   │   ├── buy_normal.png
│   │   ├── buy_hover.png
│   │   ├── sell_normal.png
│   │   └── sell_hover.png
│   ├── windows/                 # Background cho các cửa sổ popup
│   │   ├── popup_background.png
│   │   ├── menu_background.png
│   │   ├── dialog_background.png
│   │   ├── shop_background.png
│   │   ├── warehouse_background.png
│   │   ├── profile_background.png
│   │   └── quest_background.png
│   ├── icons/                   # Icons nhỏ dùng trong UI
│   │   ├── money_icon.png
│   │   ├── water_icon.png
│   │   ├── harvest_icon.png
│   │   ├── seed_icon.png
│   │   ├── pot_icon.png
│   │   ├── pet_icon.png
│   │   ├── bug_icon.png
│   │   └── exp_icon.png
│   └── backgrounds/             # Backgrounds cho main UI
│       ├── main_bg.png
│       └── controls_bg.png
├── pets/                        # Game assets hiện tại
├── plants/                      # Game assets hiện tại
├── pots/                        # Game assets hiện tại
└── sounds/                      # Sound assets
```

## 🎨 Quy tắc thiết kế Assets

### 1. **Định dạng và chất lượng**
- **Format**: PNG với transparency (RGBA)
- **Resolution**: 72-96 DPI
- **Color depth**: 32-bit (true color với alpha)
- **Compression**: Không nén hoặc nén nhẹ để giữ quality

### 2. **Kích thước chuẩn**

#### Buttons
- **Small buttons** (settings, close): 32x32px
- **Medium buttons** (buy, sell): 120x40px
- **Large buttons** (main actions): 150x50px

#### Windows/Popups
- **Small dialogs**: 400x300px
- **Medium windows**: 600x400px
- **Large windows** (shop, warehouse): 800x600px

#### Icons
- **Small icons**: 16x16px hoặc 24x24px
- **Medium icons**: 32x32px
- **Large icons**: 48x48px

#### Backgrounds
- **Main background**: Tự động scale theo canvas size
- **Window backgrounds**: 9-patch hoặc tileable patterns

### 3. **Button States**
Mỗi button cần có 3 states:
- `*_normal.png`: Trạng thái bình thường
- `*_hover.png`: Khi chuột hover
- `*_pressed.png`: Khi click

### 4. **Naming Convention**
```
{component}_{state}_{variant}.png

Ví dụ:
- settings_normal.png
- buy_hover_large.png
- close_pressed.png
- water_icon_small.png
```

## 🔧 Cách sử dụng trong Code

### 1. **Load UI Assets**
Thêm vào `growpot/assets_gen.py` hoặc tạo file mới `growpot/ui_assets.py`:

```python
from pathlib import Path
from PIL import Image, ImageTk
import tkinter as tk

class UIAssetsManager:
    def __init__(self, assets_dir: Path):
        self.assets_dir = assets_dir
        self.ui_dir = assets_dir / "ui"
        self._images = {}  # Cache cho images

    def load_button(self, name: str, state: str = "normal") -> tk.PhotoImage:
        """Load button image với state"""
        path = self.ui_dir / "buttons" / f"{name}_{state}.png"
        if path.exists():
            img = Image.open(path)
            tk_img = ImageTk.PhotoImage(img)
            self._images[f"button_{name}_{state}"] = tk_img
            return tk_img
        return None

    def load_icon(self, name: str, size: str = "medium") -> tk.PhotoImage:
        """Load icon"""
        path = self.ui_dir / "icons" / f"{name}_icon_{size}.png"
        if path.exists():
            img = Image.open(path)
            tk_img = ImageTk.PhotoImage(img)
            self._images[f"icon_{name}_{size}"] = tk_img
            return tk_img
        return None

    def load_window_bg(self, window_type: str) -> tk.PhotoImage:
        """Load window background"""
        path = self.ui_dir / "windows" / f"{window_type}_background.png"
        if path.exists():
            img = Image.open(path)
            tk_img = ImageTk.PhotoImage(img)
            self._images[f"window_{window_type}"] = tk_img
            return tk_img
        return None
```

### 2. **Sử dụng trong UIManager**
Sửa `growpot/ui_components.py`:

```python
class UIManager:
    def __init__(self, root: tk.Tk, ..., ui_assets: UIAssetsManager):
        self.ui_assets = ui_assets
        # ... existing code ...

    def setup_buttons(self):
        """Setup buttons với custom images"""
        # Settings button
        settings_img = self.ui_assets.load_button("settings", "normal")
        if settings_img:
            self.btn_settings.config(image=settings_img, text="")
        else:
            self.btn_settings.config(text="⚙")  # Fallback

        # Hover effects
        def on_enter(e):
            hover_img = self.ui_assets.load_button("settings", "hover")
            if hover_img:
                self.btn_settings.config(image=hover_img)

        def on_leave(e):
            normal_img = self.ui_assets.load_button("settings", "normal")
            if normal_img:
                self.btn_settings.config(image=normal_img)

        self.btn_settings.bind("<Enter>", on_enter)
        self.btn_settings.bind("<Leave>", on_leave)
```

## 🚀 Các bước Setup

### Bước 1: Chuẩn bị Assets
1. Thiết kế assets theo quy tắc trên
2. Export thành PNG với transparency
3. Đặt vào thư mục tương ứng trong `assets/ui/`

### Bước 2: Implement Code
1. Tạo `UIAssetsManager` class
2. Integrate vào `UIManager`
3. Test từng component

### Bước 3: Fallback System
Luôn có fallback khi assets không tồn tại:
```python
# Trong UI code
if custom_image:
    widget.config(image=custom_image, text="")
else:
    widget.config(text="Default Text")  # Fallback
```

## ⚠️ Lưu ý quan trọng

### 1. **Memory Management**
- Tkinter `PhotoImage` cần được giữ reference, không bị garbage collected
- Cache images trong dictionary để reuse

### 2. **Resize Behavior**
- Images không tự động scale khi window resize
- Cần implement scaling logic nếu muốn responsive UI
- Hoặc thiết kế UI với fixed size

### 3. **Performance**
- Load images khi cần, không load tất cả cùng lúc
- Sử dụng image caching để tránh reload

### 4. **Compatibility**
- Test trên Windows (target platform)
- Đảm bảo paths case-insensitive

## 📝 Checklist Setup

- [ ] Tạo thư mục `assets/ui/` với subfolders
- [ ] Thiết kế và export assets theo specs
- [ ] Implement `UIAssetsManager`
- [ ] Update `UIManager` để sử dụng assets
- [ ] Test button states (normal/hover/pressed)
- [ ] Test window backgrounds
- [ ] Implement fallback cho missing assets
- [ ] Test resize behavior
- [ ] Performance test với nhiều assets

## 🔄 Migration Plan

1. **Phase 1**: Settings button và basic buttons
2. **Phase 2**: Window backgrounds
3. **Phase 3**: Icons và advanced UI elements
4. **Phase 4**: Custom styling và themes

Bắt đầu với settings button để test workflow trước khi scale up!
