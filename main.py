from __future__ import annotations

import tkinter as tk
from pathlib import Path

from growpot.app import GrowPlotApp
from growpot.assets_gen import generate_assets


def main() -> None:
    assets_dir = Path("assets")
    generate_assets(assets_dir)

    root = tk.Tk()
    root.title("GrowPlot")

    # Start app
    GrowPlotApp(root, assets_dir=assets_dir)
    root.mainloop()


if __name__ == "__main__":
    main()
