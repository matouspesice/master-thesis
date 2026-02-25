# App — ML + Display Source Code

Real-time pose from webcam (RTMPose) and, later, the “Architect” game and avatar/visual feedback.

## Quick start — pose webcam

1. **Install**
   ```bash
   cd app
   pip install -r requirements.txt
   ```
   Default is CPU (no CUDA setup needed). For GPU use `pip install onnxruntime-gpu`, install [CUDA 12 and cuDNN 9](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html#requirements) and add them to PATH, then run with `--device cuda`.
2. **Run**
   ```bash
   python pose_webcam.py
   ```
   Uses default camera (index 0). Press **Q** to quit.
3. **Switch camera** (e.g. lab USB)
   ```bash
   python pose_webcam.py --camera 1
   ```
4. **Compare backends and measure latency (test both)**
   - **rtmlib (default):** works after `pip install -r requirements.txt` (any supported Python).
   - **MMPose (optional):** needs **Python 3.10 or 3.11** (MMPose/mmcv do not support Python 3.12+ yet). On Python 3.14, use a separate env:
     ```bash
     conda create -n pose python=3.11 -y
     conda activate pose
     cd path\to\Master Thesis\app
     pip install -r requirements.txt -r requirements-mmpose.txt
     ```
   - **Test both backends:**
     ```bash
     # Test 1: rtmlib (ONNX)
     python pose_webcam.py --backend rtmlib --show-fps

     # Test 2: MMPose (PyTorch) — only if mmpose installed
     python pose_webcam.py --backend mmpose --show-fps
     ```
   - Compare the FPS and “Pose: X ms” shown on the window to see which is faster on your machine.

See **`PLAN.md`** for the full plan (phases, camera switching, no Unity for now).

## Contents

- **`pose_webcam.py`** — Webcam → pose (rtmlib or MMPose) → skeleton overlay. Use `--backend rtmlib|mmpose` and `--show-fps` to compare latency.
- **`requirements.txt`** — opencv-python, rtmlib, onnxruntime (optional: onnxruntime-gpu).
- **`requirements-mmpose.txt`** — Optional MMPose stack for `--backend mmpose`.
- **`PLAN.md`** — Phases, camera/config, and what comes next.

Pose stack uses **rtmlib** (RTMPose models); you do **not** need to download the full MMPose repo. Models are downloaded automatically on first run.

**Console messages:** You may see rtmlib lines like “load … onnx” and “Tracking is on” (normal), and sometimes OpenCV/videoio warnings (e.g. MSMF on Windows). These are usually harmless; the app reduces OpenCV log level to limit noise.

Build outputs and large binaries stay out of version control (see root `.gitignore`).
