"""Download ONE georeferenced Sentinel-2 true-color GeoTIFF around Seattle.

Reads a geographic window from a public Cloud Optimized GeoTIFF using HTTP range
requests. Retains native 10 m pixels, the CRS, and the affine transform. No API key.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import rasterio
from rasterio.warp import transform_bounds
from rasterio.windows import Window, from_bounds

ITEM = "S2B_10TET_20240829_0_L2A"
SOURCE = "https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items/" + ITEM
URL = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/10/T/ET/2024/8/" + ITEM + "/TCI.tif"
BBOX = (-122.48, 47.48, -122.06, 47.75)  # west, south, east, north (WGS84)


def download_image(root: Path) -> Path:
    folder = Path(root) / "data" / "satellite"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "seattle_sentinel2.tif"
    if target.exists():
        with rasterio.open(target) as image:
            if image.crs is None or image.count != 3:
                raise ValueError(f"Invalid existing RGB GeoTIFF: {target}")
        return target
    print("Downloading one Sentinel-2 GeoTIFF window (native 10 m RGB)...", flush=True)
    temporary = target.with_suffix(".tif.part")
    # The S3 asset is a COG, so only blocks intersecting this window are fetched.
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                      CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif", GDAL_HTTP_TIMEOUT=120):
        with rasterio.open(URL) as source:
            bounds = transform_bounds("EPSG:4326", source.crs, *BBOX, densify_pts=21)
            window = from_bounds(*bounds, source.transform).round_offsets().round_lengths()
            window = window.intersection(Window(0, 0, source.width, source.height))
            pixels = source.read([1, 2, 3], window=window)
            profile = source.profile.copy()
            profile.update(driver="GTiff", width=int(window.width), height=int(window.height),
                           count=3, transform=source.window_transform(window), compress="deflate",
                           tiled=True, blockxsize=256, blockysize=256)
            with rasterio.open(temporary, "w", **profile) as output:
                output.write(pixels)
                output.update_tags(source=SOURCE, acquisition_date="2024-08-29",
                                   description="Copernicus Sentinel-2 L2A rendered true color, native 10 m subset")
    temporary.replace(target)
    (folder / "source.json").write_text(json.dumps({
        "item": ITEM, "source": SOURCE, "asset": URL,
        "acquired": "2024-08-29", "bbox_wgs84": BBOX,
        "credit": "Contains modified Copernicus Sentinel data (2024); distributed via Earth Search / AWS Open Data",
        "notes": "One georeferenced RGB subset at native 10 m; display-scaled TCI, not raw spectral reflectance.",
    }, indent=2) + "\n")
    print(target, flush=True)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(download_image(args.root))
