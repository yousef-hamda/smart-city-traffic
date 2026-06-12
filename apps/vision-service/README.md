# Vision Service

Consumes camera frames from Kafka (`vision.frames`), detects vehicles, tracks
them across frames, flags incidents, and publishes enriched `vision.events`.
Exposes the latest annotated frame per segment over REST.

## Pipeline

```
vision.frames ─► decode JPEG ─► detect ─► ByteTrack ─► incidents ─► aggregate
                                                                       │
                          /snapshot/{segment} ◄── annotate         vision.events
```

Per camera, a dedicated `CameraPipeline` (and its tracker) persists so vehicle
identities survive across frames.

## Detection — an honest split

Two detectors implement one `Detector` protocol:

| Detector              | Use                         | Notes                                                        |
| --------------------- | --------------------------- | ------------------------------------------------------------ |
| `synthetic` (default) | the camera simulator's feed | classical OpenCV color/contour on the rendered sprites       |
| `yolo`                | real photographic footage   | Ultralytics YOLOv8, lazy-loaded (`pip install -e ".[yolo]"`) |

COCO-trained YOLOv8 does **not** reliably fire on the simulator's flat-colored
cartoon sprites, so the synthetic feed uses a classical detector to produce
meaningful tracks. Everything downstream — tracking, incident detection,
aggregation, the event schema — is identical regardless of detector, so the
pipeline is a faithful stand-in for a real YOLO deployment. Point `DETECTOR=yolo`
at an RTSP/video source of real traffic for the production path.

## Tracking (ByteTrack-style)

`tracking.py` keeps low-confidence detections and runs a second association
stage against them, recovering objects whose score dips under occlusion — the
core ByteTrack idea that cuts ID switches. Constant-velocity motion model,
greedy IoU association (Hungarian is the drop-in upgrade), and a
tentative→confirmed→lost state machine with a lost-track buffer so brief
occlusions don't mint new IDs.

## Incidents

Computed from confirmed tracks: **stopped vehicle** (negligible travel over
the last 30 s), **wrong-way** (velocity opposes the median flow), **sudden
lane change** (large vertical displacement vs vehicle height).

## Interfaces

| Kind      | Endpoint                     | Notes                                          |
| --------- | ---------------------------- | ---------------------------------------------- |
| REST      | `GET /health`                | liveness                                       |
| REST      | `GET /snapshot/{segment_id}` | latest annotated frame (PNG) or 404            |
| REST      | `GET /segments`              | segments with a snapshot available             |
| Kafka in  | `vision.frames`              | base64-JPEG envelope from the camera simulator |
| Kafka out | `vision.events`              | per-frame counts, dwell, incidents, tracks     |

## Environment

| Variable                      | Default                    | Purpose                              |
| ----------------------------- | -------------------------- | ------------------------------------ |
| `KAFKA_BOOTSTRAP_SERVERS`     | `localhost:29092`          | frames in / events out               |
| `REDIS_URL`                   | `redis://localhost:6379/0` | reserved for shared snapshot store   |
| `DETECTOR`                    | `synthetic`                | `synthetic` or `yolo`                |
| `YOLO_WEIGHTS`                | `yolov8n.pt`               | YOLOv8 weights (yolo mode)           |
| `STOPPED_SECONDS`             | `30`                       | stopped-vehicle threshold            |
| `ASSUMED_FPS`                 | `15`                       | frame rate for dwell/incident timing |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _unset_                    | tracing when set                     |

## Local development

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"        # add ",yolo" for real YOLOv8
pytest -q && ruff check src tests && mypy src
```

## Performance vs accuracy

The `synthetic` detector is sub-millisecond per 720p frame. For real footage,
`yolov8n` (nano) is the latency-optimized weight — target < 100 ms/frame on
CPU — at the cost of accuracy versus `yolov8s/m`. Swap weights via
`YOLO_WEIGHTS` to trade latency for precision.
