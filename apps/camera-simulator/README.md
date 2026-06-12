# Camera Simulator

Renders synthetic 720p traffic-camera frames with OpenCV and publishes them to
Kafka (`vision.frames`), local files, or an RTSP endpoint. The vision service
consumes the Kafka feed and runs YOLOv8 — the synthetic vehicles use the same
class labels (`car`/`bus`/`truck`/`motorcycle`) the detector expects, so the
whole CV path is exercised end to end without real footage.

## What it models

- **Scene** (`scene.py`) — vehicles spawn per lane to hold a configurable
  density, move along the road, and recycle at the edges. Pure simulation,
  deterministic under a seed.
- **Incidents** — `stopped_vehicle` (holds position, boxed red) and
  `wrong_way` (travels against traffic). Injected on demand; the frame
  envelope carries ground-truth `incident_hints` for evaluation (the vision
  service must still detect them independently).
- **Renderer** (`renderer.py`) — draws asphalt, lane markings, vehicle
  sprites, and a HUD (camera id, timestamp, count, a "SIMULATED FEED" badge),
  then JPEG-encodes.
- **Cameras** (`cameras.py`) — camera→segment ids are derived with the same
  rule the DB seed uses, so published `camera_id`s already exist in Postgres.

## Output modes

| `--output` | Sink                  | Notes                                           |
| ---------- | --------------------- | ----------------------------------------------- |
| `file`     | JPEG sequence on disk | default; used by tests, screenshots             |
| `kafka`    | `vision.frames` topic | JSON envelope, base64 JPEG, gzip                |
| `rtsp`     | RTSP push via ffmpeg  | needs `ffmpeg` + a media server (e.g. mediamtx) |
| `all`      | all of the above      |                                                 |

## Usage

```bash
# Write a few frames to disk to eyeball the render
python -m camera_simulator run --output file --out-dir ./frames --cameras 4 --max-frames 20

# Publish into the local stack
python -m camera_simulator run --output kafka --kafka localhost:29092 --fps 15

# Inject a wrong-way incident on the first camera
python -m camera_simulator run --output file --out-dir ./frames --incident wrong_way --max-frames 30
```

`vision.frames` envelope:

```json
{
  "camera_id": "C-jaffa-road-02",
  "segment_id": "jaffa-road-02",
  "seq": 41,
  "ts": "2026-06-08T08:00:00+03:00",
  "width": 1280,
  "height": 720,
  "format": "jpeg",
  "image_b64": "...",
  "incident_hints": []
}
```

## Environment

| Variable                  | Purpose               |
| ------------------------- | --------------------- |
| `KAFKA_BOOTSTRAP_SERVERS` | default for `--kafka` |

## Local development

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q && ruff check src tests && mypy src
```

## Performance

At 1280×720 the renderer produces and JPEG-encodes a frame in a few
milliseconds on CPU, comfortably ahead of the 15 fps target per camera. JPEG
quality is tunable (`--jpeg-quality`) to trade bandwidth against fidelity.
