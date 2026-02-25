#!/usr/bin/env python3
"""
Real-time pose estimation from webcam — RTMPose (rtmlib) or MMPose.
Shows the camera stream with skeleton overlay. Use --backend to compare latency/FPS.

Latency note: rtmlib (ONNX) often matches or beats MMPose (PyTorch) on latency;
run both with --show-fps to measure on your machine.

Usage:
  python pose_webcam.py
  python pose_webcam.py --backend mmpose   # requires mmpose + mmdet installed
  python pose_webcam.py --camera 1 --show-fps

Press Q in the window to quit.
"""

import argparse
import time
import sys

import cv2

# Reduce OpenCV console noise (e.g. MSMF camera warnings on Windows)
try:
    cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
except Exception:
    pass


def parse_args():
    p = argparse.ArgumentParser(
        description="Webcam pose estimation (rtmlib or MMPose); compare with --backend"
    )
    p.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Camera device index (0 = default, 1 = first USB, etc.)",
    )
    p.add_argument(
        "--backend",
        type=str,
        default="rtmlib",
        choices=("rtmlib", "mmpose"),
        help="Pose backend: rtmlib (ONNX, default) or mmpose (PyTorch). Use both to find fastest.",
    )
    p.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=("cpu", "cuda"),
        help="Device for inference (default: cpu; use --device cuda only if CUDA 12 + cuDNN 9 are installed)",
    )
    p.add_argument(
        "--mode",
        type=str,
        default="balanced",
        choices=("performance", "lightweight", "balanced"),
        help="rtmlib only: mode (lightweight=fast, performance=accurate)",
    )
    p.add_argument(
        "--det-frequency",
        type=int,
        default=5,
        help="rtmlib only: run person detector every N frames",
    )
    p.add_argument(
        "--show-fps",
        action="store_true",
        help="Show FPS and inference time (ms) on the window",
    )
    return p.parse_args()


# -----------------------------------------------------------------------------
# rtmlib backend
# -----------------------------------------------------------------------------
def create_rtmlib_tracker(device: str, mode: str, det_frequency: int):
    from rtmlib import Body, PoseTracker
    return PoseTracker(
        Body,
        mode=mode,
        det_frequency=det_frequency,
        backend="onnxruntime",
        device=device,
        to_openpose=False,
    )


def run_rtmlib_frame(pose_tracker, frame, show_fps: bool):
    from rtmlib import draw_skeleton
    t0 = time.perf_counter()
    keypoints, scores = pose_tracker(frame)
    t_infer = (time.perf_counter() - t0) * 1000
    vis = frame.copy()
    vis = draw_skeleton(
        vis,
        keypoints,
        scores,
        openpose_skeleton=False,
        kpt_thr=0.4,
    )
    return vis, t_infer


# -----------------------------------------------------------------------------
# MMPose backend (optional)
# -----------------------------------------------------------------------------
def create_mmpose_inferencer(device: str):
    try:
        from mmpose.apis import MMPoseInferencer  # type: ignore[reportMissingImports]
    except ImportError as e:
        raise RuntimeError(
            "MMPose not installed. Install with: pip install -r requirements-mmpose.txt"
        ) from e
    device_str = "cuda:0" if device == "cuda" else "cpu"
    return MMPoseInferencer(
        pose2d="human",
        device=device_str,
    )


def run_mmpose_frame(inferencer, frame, show_fps: bool):
    t0 = time.perf_counter()
    # Inferencer accepts image array; returns generator
    gen = inferencer(frame, return_vis=True)
    result = next(gen)
    t_infer = (time.perf_counter() - t0) * 1000
    vis_list = result.get("visualization", [])
    if vis_list:
        vis = vis_list[0]
        if vis.ndim == 3 and vis.shape[2] == 3:
            vis = cv2.cvtColor(vis, cv2.COLOR_RGB2BGR)
    else:
        vis = frame.copy()
    return vis, t_infer


# -----------------------------------------------------------------------------
# FPS / latency overlay
# -----------------------------------------------------------------------------
def draw_fps(vis, fps: float, infer_ms: float):
    cv2.putText(
        vis,
        f"FPS: {fps:.1f}  |  Pose: {infer_ms:.1f} ms",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
    )


def main():
    args = parse_args()

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Cannot open camera {args.camera}. Try --camera 0 or another index.")
        sys.exit(1)

    backend = args.backend
    device = args.device
    if backend == "rtmlib":
        try:
            pose_tracker = create_rtmlib_tracker(
                device, args.mode, args.det_frequency
            )
        except ImportError as e:
            print("rtmlib not found. Install with: pip install -r requirements.txt")
            sys.exit(1)
        except Exception as e:
            if device == "cuda":
                print("GPU failed, falling back to CPU:", e)
                device = "cpu"
                pose_tracker = create_rtmlib_tracker(
                    device, args.mode, args.det_frequency
                )
            else:
                raise
        run_frame = lambda f: run_rtmlib_frame(pose_tracker, f, args.show_fps)
    else:
        try:
            inferencer = create_mmpose_inferencer(args.device)
        except RuntimeError as e:
            print(e)
            sys.exit(1)
        run_frame = lambda f: run_mmpose_frame(inferencer, f, args.show_fps)

    print(f"Backend: {backend}  Camera: {args.camera}  Device: {device}")
    print("Press Q to quit.")
    print("(Console: 'load ... onnx' and 'Tracking is on' from rtmlib are normal. Camera warnings are usually harmless.)")
    if args.show_fps:
        print("FPS and inference time are shown on the window.")

    window_name = f"Pose ({backend}) — Q to quit"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # FPS smoothing
    fps_alpha = 0.2
    fps_smooth = 30.0
    infer_smooth_ms = 10.0

    while True:
        t0 = time.perf_counter()
        ok, frame = cap.read()
        if not ok:
            break

        vis, infer_ms = run_frame(frame)
        elapsed = time.perf_counter() - t0

        if args.show_fps:
            fps_smooth = fps_alpha * (1.0 / max(elapsed, 1e-6)) + (1 - fps_alpha) * fps_smooth
            infer_smooth_ms = fps_alpha * infer_ms + (1 - fps_alpha) * infer_smooth_ms
            draw_fps(vis, fps_smooth, infer_smooth_ms)

        # Resize image to fill window (so fullscreen actually fills the screen)
        try:
            _, _, w, h = cv2.getWindowImageRect(window_name)
            if w > 0 and h > 0:
                vis = cv2.resize(vis, (w, h), interpolation=cv2.INTER_LINEAR)
        except Exception:
            pass
        cv2.imshow(window_name, vis)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
