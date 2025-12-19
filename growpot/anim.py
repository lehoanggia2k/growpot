from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageTk


@dataclass
class FrameSet:
    frames: list[Image.Image]  # PIL images for compositing
    width: int
    height: int

    def get_tk_frame(self, index: int) -> ImageTk.PhotoImage:
        return ImageTk.PhotoImage(self.frames[index])

    def composite_with(self, other: FrameSet, index: int, max_w: int, max_h: int) -> ImageTk.PhotoImage:
        """Composite this frameset with another at given index."""
        base_frame = self.frames[index]
        overlay_frame = other.frames[index % len(other.frames)] if other.frames else None

        # Create new image with max size
        combined = Image.new("RGBA", (max_w, max_h), (0, 0, 0, 0))

        # Place pot at bottom center
        pot_x = (max_w - self.width) // 2
        pot_y = max_h - self.height
        combined.paste(base_frame, (pot_x, pot_y), base_frame)

        # Place plant at bottom center (if exists)
        if overlay_frame:
            plant_x = (max_w - other.width) // 2
            plant_y = max_h - other.height
            combined.paste(overlay_frame, (plant_x, plant_y), overlay_frame)

        return ImageTk.PhotoImage(combined)


def load_frames(folder: Path) -> FrameSet:
    files = sorted(folder.glob("frame_*.png"))
    if not files:
        raise FileNotFoundError(f"No frames found in {folder} (expected frame_*.png)")

    pil_frames: list[Image.Image] = [Image.open(p).convert("RGBA") for p in files]

    w = pil_frames[0].width
    h = pil_frames[0].height

    # Ensure consistent size (common mistake with frame sequences)
    for p in pil_frames:
        if p.size != (w, h):
            raise ValueError(f"Frame sizes differ in {folder}. Keep all frames same size.")

    return FrameSet(frames=pil_frames, width=w, height=h)
