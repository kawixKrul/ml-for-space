# Machine learning for space

## Environment

Run from the repository root:

```sh
uv sync
uv run jupyter server
```

The Python environment and its configuration stay here: `.venv/`, `pyproject.toml`, `uv.lock`, and `.python-version`. Open `lab1/algebra.ipynb` in Jupyter and run all cells.

## Labs

- [Lab 1: SVD image reconstruction](lab1/README.md) — [executed notebook](lab1/algebra.ipynb), [observations and plots](lab1/results/observations.md).

Lab 1 contains its notebook, supplied image, one satellite GeoTIFF, downloader, and saved results. To download its GeoTIFF if missing:

```sh
uv run python lab1/download_satellite.py
```
