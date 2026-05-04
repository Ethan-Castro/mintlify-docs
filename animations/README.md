# Animations

Source files for the concept-explainer animations embedded in the CSI HPCC docs site.

## Layout

```
animations/
  manim/           Manim Community Edition scenes (Python) → MP4
  matplotlib/      Matplotlib FuncAnimation scripts (Python) → MP4
  threejs/         Three.js single-file HTML interactives
  d3/              D3.js single-file HTML interactives
```

Outputs are written into the repo's static asset folders so Mintlify serves them directly:

- MP4s land in `../images/videos/`
- Interactive HTML lands in `../images/interactives/`

## Prerequisites

- Python 3.11+
- ffmpeg (`brew install ffmpeg` on macOS, `apt install ffmpeg` on Debian/Ubuntu)
- LaTeX (Manim uses it for typeset text — TeX Live or MacTeX)

## Setup (uv, recommended)

```bash
cd animations
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Or with stock pip:

```bash
cd animations
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Render everything

```bash
make all
```

Individual targets:

- `make manim` — render every Manim scene at `-qm` (720p30) into `images/videos/`
- `make matplotlib` — run Matplotlib scripts that save MP4 via ffmpeg
- `make interactives` — copy `threejs/*.html` and `d3/*.html` into `images/interactives/`

Set `Q=h` to render Manim at 1080p60:

```bash
make manim Q=h
```

## Adding a new animation

1. Drop the source file in the matching subdirectory.
2. Add a render rule to the `Makefile` (mirror an existing entry).
3. Author a corresponding `visualizations/<slug>.mdx` page that embeds the output.
4. Register the page in `docs.json` under a `Visualizations` group.
5. Optionally add an inline embed on the natural topic page.

## Notes

- Manim writes intermediate files into `media/` inside this directory; those are gitignored.
- Output MP4s are committed to the repo so the docs site doesn't depend on a render pipeline at deploy time.
- Mintlify only deploys MDX from the repo root and registered subdirectories. The whole `animations/` directory is excluded via `.mintignore`.
