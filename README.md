# Car Photo API

FastAPI backend for AI-powered car photo background replacement via Photoroom Plus.

## Architecture

```
Flutter app → POST /process (image + background_id) → Photoroom /v2/edit → PNG
Flutter app → GET /backgrounds → list of available backgrounds
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Liveness check |
| GET | /backgrounds | List available backgrounds |
| POST | /process | Process a car photo (returns PNG) |

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
cp .env.example .env
# Edit .env and set PHOTOROOM_API_KEY

# Run
uvicorn app.main:app --reload --port 8080
```

API docs available at http://localhost:8080/docs

## Test the Pipeline

```bash
python scripts/test_pipeline.py --image /path/to/car.jpg
```

## Deploy to Fly.io

```bash
# Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
flyctl auth login

# Create app (first time only — edit fly.toml app name if 'car-photo-api' is taken)
flyctl launch --no-deploy

# Set the API key secret (never in code or repo)
flyctl secrets set PHOTOROOM_API_KEY=your_key_here

# Deploy
flyctl deploy
```

## Background Library

Backgrounds are defined in `app/services/backgrounds.py`.

**Colour-based** (current): `color` field → Photoroom `background.color`  
**Image-based** (future): `image_path` field → Photoroom `background.imageFile`

To add a custom background PNG, drop it in `backgrounds/` and add an entry with `"image_path": "filename.png"`.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PHOTOROOM_API_KEY` | Yes | Photoroom API key (sandbox or live) |
| `MAX_LONG_EDGE_PX` | No | Max image resize (default 3000) |

## Phase Roadmap

- **Phase 2 Step 1** ✅ — Backend skeleton + Photoroom integration
- **Phase 2 Step 2** — Flutter app integration (replace ML Kit flow)
- **Phase 2 Step 3** — Background picker fetching from backend
- **Phase 2 Step 4** — Parallel processing + error handling
- **Phase 3** — Design pass, branding, dealer onboarding
