"""
End-to-end pipeline test.

Usage:
    python scripts/test_pipeline.py --image /path/to/car.jpg
    python scripts/test_pipeline.py --image /path/to/car.jpg --url http://localhost:8080
    python scripts/test_pipeline.py --image /path/to/car.jpg --background showroom-dark

Tests:
    1. GET /health
    2. GET /backgrounds (lists all)
    3. POST /process — sends image, saves result as test_result.png
"""

import argparse
import sys
import time
from pathlib import Path

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Car Photo API pipeline test")
    parser.add_argument("--url", default="http://localhost:8080", help="API base URL")
    parser.add_argument("--image", required=True, help="Path to a car photo (JPEG/PNG)")
    parser.add_argument(
        "--background", default="showroom-light", help="Background ID to use"
    )
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    image_path = Path(args.image)

    if not image_path.exists():
        print(f"ERROR: image not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    client = httpx.Client(timeout=60.0)

    # 1. Health
    print("1. Health check...")
    r = client.get(f"{base_url}/health")
    r.raise_for_status()
    print(f"   ✅ {r.json()}")

    # 2. Backgrounds
    print("2. Backgrounds...")
    r = client.get(f"{base_url}/backgrounds")
    r.raise_for_status()
    bgs = r.json()["backgrounds"]
    ids = [b["id"] for b in bgs]
    print(f"   ✅ {len(bgs)} backgrounds: {ids}")

    if args.background not in ids:
        print(f"   ⚠️  Warning: '{args.background}' not in list. Using first available.")
        args.background = ids[0]

    # 3. Process
    img_bytes = image_path.read_bytes()
    print(
        f"3. Processing {image_path.name} ({len(img_bytes):,} bytes)"
        f" → background={args.background}"
    )

    t0 = time.perf_counter()
    with open(image_path, "rb") as f:
        r = client.post(
            f"{base_url}/process",
            files={"image": (image_path.name, f, "image/jpeg")},
            data={"background_id": args.background},
        )
    elapsed = time.perf_counter() - t0

    if r.status_code != 200:
        print(f"   ❌ Error {r.status_code}: {r.text[:400]}", file=sys.stderr)
        sys.exit(1)

    out = Path("test_result.png")
    out.write_bytes(r.content)
    print(
        f"   ✅ Done in {elapsed:.2f}s"
        f" → {out.absolute()} ({len(r.content):,} bytes PNG)"
    )
    print("\nOpen test_result.png to verify quality.")


if __name__ == "__main__":
    main()
