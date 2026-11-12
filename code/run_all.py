"""Draw Figures 3–12.

Requires NumPy, pandas and Matplotlib. PDFs and 600 dpi PNGs are generated
beside the plotting scripts. Keep the repository's data/ and code/ folders together.
"""
from pathlib import Path
import subprocess
import sys

def main():
    code_dir = Path(__file__).resolve().parent
    for n in range(3, 13):
        print(f"Drawing Figure {n:02d}...", flush=True)
        subprocess.run(
            [sys.executable, str(code_dir / f"plot_figure_{n:02d}.py")],
            check=True,
        )

if __name__ == "__main__":
    main()
