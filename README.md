# YOLO Phone Detector

A simple YOLO-based webcam app that detects cell phones in real time, draws detections on screen, and logs alert messages in the terminal through a custom Focus Guard dashboard.

## Features

- Real-time phone detection from a webcam
- Bounding box visualization on the camera feed
- Focus Guard side panel with live status and alert timeline
- Terminal alert logs with icons
- Press `q` to quit

## Requirements

- Python 3.8+
- A working webcam
- A YOLO model file

Default model location:

```text
models/yolo26s.pt
```

## Installation

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

This installs:

- `ultralytics`
- `opencv-python`
- `numpy`

## Model File

The app uses `models/yolo26s.pt` by default.

If you already placed `yolo26s.pt` inside the `models/` folder, the app will use that local file.

If the file is not present locally, Ultralytics can download `yolo26s.pt` automatically on first use and save it under `models/`.

If you want to use a different model, pass it with `--model`:

```bash
python3 app.py --model models/my-model.pt
```

Default detection target:

```text
cell phone
```

Default tuning:

- Confidence threshold: `0.45`
- Minimum box area ratio: `0.012`
- Cooldown: `4.0s`
- Streak required: `8` frames

## Run

Start the detector:

```bash
python3 app.py
```

Use a different camera:

```bash
python3 app.py --camera-index 1
```

Adjust detection sensitivity:

```bash
python3 app.py --confidence 0.5 --streak 10
```

To exit, focus the detector window and press `q`.

## Command-Line Options

Show all options:

```bash
python3 app.py --help
```

Common options:

- `--model`: path to the YOLO model file
- `--camera-index`: webcam index to open
- `--confidence`: minimum confidence threshold
- `--min-area-ratio`: minimum detection box area relative to the frame
- `--cooldown`: cooldown in seconds between alerts
- `--streak`: number of consecutive frames required before alerting
- `--camera-retries`: number of times to retry opening the camera

## Example Logs

Alert messages are printed in this format:

```text
ℹ️ Focus Guard is live. Press 'q' in the detector window to quit.
⚠️ Camera open failed (1/5), retrying...
🚨📱 2026-03-26 14:32:10 | Phone detected
```

## Project Structure

```text
yolo-phone-detector/
├── app.py
├── config.py
├── detector.py
├── events.py
├── ui.py
├── requirements.txt
└── models/
    └── yolo26s.pt
```

## Troubleshooting

If the camera does not open:

- Try `--camera-index 1` or `--camera-index 2`
- Make sure another app is not already using the webcam

If the model file is not found:

- Check that `models/yolo26s.pt` exists
- Or pass the full path explicitly with `--model`

If package imports fail:

- Make sure your virtual environment is activated
- Reinstall dependencies:

```bash
pip install -r requirements.txt
```
