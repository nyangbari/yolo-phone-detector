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
- `opencv-python` on desktop environments
- `numpy`

### Jetson Notes

For Jetson CSI cameras such as IMX219, use the JetPack OpenCV package instead of the `pip`
wheel so `cv2` keeps GStreamer support for `nvarguscamerasrc`.

```bash
sudo apt update
sudo apt install -y python3-opencv v4l-utils gstreamer1.0-tools

python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

On `aarch64` systems, `requirements.txt` skips `opencv-python` and expects the system
`python3-opencv` package instead.

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

Use a Jetson CSI camera such as IMX219:

```bash
python3 app.py --camera-mode csi --camera-sensor-id 0
```

If you are using an Orin Nano developer kit and CAM0 does not work, try:

```bash
python3 app.py --camera-mode csi --camera-sensor-id 1
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
- `--camera-mode`: `usb` for UVC webcams, `csi` for Jetson CSI cameras
- `--camera-index`: webcam index to open
- `--camera-sensor-id`: Jetson CSI sensor-id for `nvarguscamerasrc`
- `--camera-width`: requested camera width
- `--camera-height`: requested camera height
- `--camera-fps`: requested camera FPS
- `--camera-flip-method`: Jetson CSI flip/rotation control
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
- For Jetson CSI cameras, use `--camera-mode csi`
- If IMX219 on an Orin Nano shows a green screen or fails on CAM0, try `--camera-sensor-id 1`
- On Jetson, confirm OpenCV has GStreamer enabled:

```bash
python3 - <<'PY'
import cv2
for line in cv2.getBuildInformation().splitlines():
    if "GStreamer" in line:
        print(line)
PY
```

- If GStreamer says `NO`, recreate the virtual environment with `--system-site-packages`
- Test the CSI camera directly through Argus:

```bash
gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! \
  'video/x-raw(memory:NVMM), width=1280, height=720, format=(string)NV12, framerate=(fraction)30/1' ! \
  nvvidconv ! xvimagesink -e
```

If the model file is not found:

- Check that `models/yolo26s.pt` exists
- Or pass the full path explicitly with `--model`

If package imports fail:

- Make sure your virtual environment is activated
- Reinstall dependencies:

```bash
pip install -r requirements.txt
```
