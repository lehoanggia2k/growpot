# GrowPlot (mini desktop pot widget)

A tiny always-on-top desktop “plant pot” you can **drag anywhere** and **water**.
The plant **grows over time** and watering speeds it up.

## Requirements
- Windows
- Python 3.10+ (you have 3.13)
- `Pillow` (for PNG frame animations)

## Install
```powershell
python -m pip install pillow
```

## Run
```powershell
python main.py
```

## Assets
Place your animation frames here:

```
assets/
  pots/
    <pot_type>/
      frame_001.png
      ...
  plants/
    <plant_type>/
      seed/
        frame_001.png
        ...
      sprout/
        frame_001.png
        ...
      plant/
        frame_001.png
        ...
  sounds/
    water.wav
```

- Frames should be **PNG with transparency**.
- Keep all frames same size (recommended 96x96 or 128x128).
- Pot frames are composited with plant frames at runtime.

## Features

### Basic Gameplay
- **Water** your plant to speed up growth
- **Harvest** when the plant is fully grown (pot becomes empty after harvest)
- **Plant Seeds**: Choose from available seed types with different costs
- **Seed Costs**: Basic seeds (free) or Rose seeds (💰20)
- **Change Pots**: Default (free, unlocked) or Wood (10% faster growth, unlock for 💰200)

### Economy & Warehouse System
- **Money System**: Earn money by selling harvested crops
- **Store Harvested Items**: Harvested crops are automatically stored in your warehouse
- **View Inventory**: Access the Warehouse from the settings menu (⚙)
- **Sell Crops**: Sell stored items for money using the Warehouse interface
- **Money Display**: Current balance shown on the main interface

## Notes
- State is persisted to `state.json` (growth, last update time, window position, inventory, money).
- Drag the pot by **holding left-click on the pot image area**.
- If you want sound, put a WAV file at `assets/sounds/water.wav`.

## Swapping in your own animation frames
1) For each stage folder (`assets/seed`, `assets/sprout`, `assets/plant`), replace the files with your own:
   - `frame_001.png`, `frame_002.png`, ...
2) Keep all frames the **same size**.
3) Restart the app.
