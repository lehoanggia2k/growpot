from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


def _draw_pot(pot_type: str, frame_index: int, size: int = 96) -> Image.Image:
    """Generate a pot frame based on type."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if pot_type == "earth":
        pot_color = (130 + (frame_index % 3) * 5, 80, 50, 255)
        d.rectangle([size * 0.25, size * 0.60, size * 0.75, size * 0.92], fill=pot_color)
        d.rectangle([size * 0.20, size * 0.55, size * 0.80, size * 0.60], fill=(150, 95, 60, 255))
    elif pot_type == "flame":
        # Wooden pot: darker, more brown
        wood_color = (80 + (frame_index % 3) * 3, 50, 30, 255)
        d.rectangle([size * 0.25, size * 0.60, size * 0.75, size * 0.92], fill=wood_color)
        d.rectangle([size * 0.20, size * 0.55, size * 0.80, size * 0.60], fill=(100, 70, 40, 255))
        # Add wood grain lines
        for i in range(3):
            y = size * (0.65 + i * 0.08)
            d.line([size * 0.28, y, size * 0.72, y], fill=(60, 40, 20, 255), width=1)

    return img


def _draw_plant(plant_type: str, stage: str, frame_index: int, size: int = 96) -> Image.Image:
    """Generate a plant frame based on type."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if plant_type == "leaf":
        if stage != "seed":
            green = (30, 160, 60, 255)
            sway = (frame_index % 5) - 2
            cx = size * 0.5 + sway
            d.line([cx, size * 0.55, cx, size * 0.32], fill=green, width=4)
            # leaves
            d.ellipse([cx - 18, size * 0.38, cx - 2, size * 0.48], fill=green)
            d.ellipse([cx + 2, size * 0.38, cx + 18, size * 0.48], fill=green)

        if stage == "plant":
            # add a little flower
            pink = (240, 120, 200, 255)
            d.ellipse([size * 0.46, size * 0.22, size * 0.54, size * 0.30], fill=pink)
    elif plant_type == "water":
        if stage != "seed":
            green = (40, 180, 40, 255)
            sway = (frame_index % 4) - 1.5
            cx = size * 0.5 + sway
            d.line([cx, size * 0.55, cx, size * 0.35], fill=green, width=3)
            # thorns
            d.rectangle([cx - 1, size * 0.45, cx + 1, size * 0.47], fill=(100, 60, 20, 255))

        if stage == "plant":
            # rose flower
            red = (220, 20, 60, 255)
            d.ellipse([size * 0.44, size * 0.25, size * 0.56, size * 0.35], fill=red)

    return img


def generate_assets(assets_dir: Path, size: int = 96, frames_per_stage: int = 12) -> None:
    stages = ["seed", "sprout", "plant"]

    # Generate pot assets
    pot_types = ["earth", "flame"]
    for pot_type in pot_types:
        pot_dir = assets_dir / "pots" / pot_type
        pot_dir.mkdir(parents=True, exist_ok=True)
        existing_pot = list(pot_dir.glob("frame_*.png"))
        if not existing_pot:
            for i in range(1, frames_per_stage + 1):
                img = _draw_pot(pot_type, i, size=size)
                img.save(pot_dir / f"frame_{i:03d}.png")

    # Generate plant assets for each type and stage
    plant_types = ["leaf", "water"]
    for plant_type in plant_types:
        for stage in stages:
            plant_stage_dir = assets_dir / "plants" / plant_type / stage
            plant_stage_dir.mkdir(parents=True, exist_ok=True)

            existing = list(plant_stage_dir.glob("frame_*.png"))
            if existing:
                # Don't overwrite user assets.
                continue

            for i in range(1, frames_per_stage + 1):
                img = _draw_plant(plant_type, stage, i, size=size)
                img.save(plant_stage_dir / f"frame_{i:03d}.png")

    (assets_dir / "sounds").mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    generate_assets(Path("assets"))
    print("Generated placeholder assets in ./assets (won't overwrite existing frames)")
