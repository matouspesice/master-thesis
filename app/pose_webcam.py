#!/usr/bin/env python3
"""
Real-time pose estimation from webcam — RTMPose (rtmlib) or MMPose.
Shows the camera stream with skeleton overlay. Tuned for low latency (Unity / high-FPS camera later).

Low-latency tips: --mode lightweight --det-frequency 10 --width 640 --height 480 --device cuda --threaded
(lightweight = smaller models; det-frequency = run detector less often; resolution = less data; threaded = display doesn't block inference)

Usage:
  python pose_webcam.py
  python pose_webcam.py --device cuda --threaded --width 640 --height 480
  python pose_webcam.py --no-viz   # keypoints only (e.g. for piping to Unity)

Press Q in the window to quit.
"""

import argparse
import json
import os
import socket
import sys
import threading
import time

# Set CUDA path before any lib loads onnxruntime (must run when --device cuda is used)
def _ensure_cuda_in_path():
    if sys.platform != "win32":
        return
    candidates = []
    # CUDA_PATH is often set by the CUDA installer
    cuda_path = os.environ.get("CUDA_PATH")
    if cuda_path and os.path.isdir(cuda_path):
        candidates.append(os.path.join(cuda_path, "bin"))
    # Default install location (prefer v12: onnxruntime-gpu needs cublasLt64_12.dll, not _13)
    for prog in (os.environ.get("ProgramFiles", "C:\\Program Files"), "C:\\Program Files (x86)"):
        cuda_base = os.path.join(prog, "NVIDIA GPU Computing Toolkit", "CUDA")
        if os.path.isdir(cuda_base):
            for name in sorted(os.listdir(cuda_base), reverse=True):
                if name.startswith("v12"):
                    candidates.append(os.path.join(cuda_base, name, "bin"))
            break
    for bin_dir in candidates:
        dll12 = os.path.join(bin_dir, "cublasLt64_12.dll")
        if not os.path.isdir(bin_dir) or not os.path.isfile(dll12):
            continue
        path = os.environ.get("PATH", "")
        if bin_dir not in path:
            os.environ["PATH"] = bin_dir + os.pathsep + path
        # Python 3.8+ on Windows: add to DLL search path so loaded extensions find dependencies
        if hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(bin_dir)
            except OSError:
                pass
        print("Using CUDA from:", bin_dir)
        # Also add cuDNN 9 so cudnn64_9.dll is found (onnxruntime-gpu needs it)
        cudnn_candidates = []
        cudnn_path = os.environ.get("CUDNN_PATH")
        if cudnn_path and os.path.isdir(cudnn_path):
            cudnn_candidates.append(os.path.join(cudnn_path, "bin"))
            cudnn_candidates.append(cudnn_path)
        for prog in (os.environ.get("ProgramFiles", "C:\\Program Files"),):
            cudnn_base = os.path.join(prog, "NVIDIA", "CUDNN")
            if os.path.isdir(cudnn_base):
                for name in sorted(os.listdir(cudnn_base), reverse=True):
                    if name.startswith("v9"):
                        v9_dir = os.path.join(cudnn_base, name)
                        cudnn_candidates.append(os.path.join(v9_dir, "bin"))
                        # NVIDIA installer puts DLLs in bin\12.x\x64 for CUDA 12
                        bin_dir_cuda = os.path.join(v9_dir, "bin")
                        if os.path.isdir(bin_dir_cuda):
                            for sub in os.listdir(bin_dir_cuda):
                                x64 = os.path.join(bin_dir_cuda, sub, "x64")
                                if sub.startswith("12") and os.path.isdir(x64):
                                    cudnn_candidates.append(x64)
                        break
                break
        cudnn_found = False
        for cudnn_bin in cudnn_candidates:
            if not os.path.isdir(cudnn_bin) or not os.path.isfile(os.path.join(cudnn_bin, "cudnn64_9.dll")):
                continue
            path = os.environ.get("PATH", "")
            if cudnn_bin not in path:
                os.environ["PATH"] = cudnn_bin + os.pathsep + path
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(cudnn_bin)
                except OSError:
                    pass
            print("Using cuDNN 9 from:", cudnn_bin)
            cudnn_found = True
            break
        if not cudnn_found:
            print("Note: cudnn64_9.dll not found. Install cuDNN 9 for CUDA 12 from https://developer.nvidia.com/cudnn and copy bin/*.dll into", bin_dir, "or add cuDNN bin to PATH.")
        return
    # Helpful message if they have CUDA 13 only
    for prog in (os.environ.get("ProgramFiles", "C:\\Program Files"),):
        cuda_base = os.path.join(prog, "NVIDIA GPU Computing Toolkit", "CUDA")
        if os.path.isdir(cuda_base):
            for name in os.listdir(cuda_base):
                if name.startswith("v13"):
                    bin_dir = os.path.join(cuda_base, name, "bin")
                    if os.path.isfile(os.path.join(bin_dir, "cublasLt64_13.dll")):
                        print("Note: You have CUDA 13 (cublasLt64_13.dll). onnxruntime-gpu needs CUDA 12 (cublasLt64_12.dll). Install CUDA Toolkit 12.x from https://developer.nvidia.com/cuda-12-0-0-download-archive to use GPU.")
                    break
            break

import cv2

# Reduce OpenCV console noise (e.g. MSMF camera warnings on Windows)
try:
    cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
except Exception:
    pass


def _default_config_path():
    """Resolve default config path: script dir or cwd, file pose_webcam.json."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for base in (script_dir, os.getcwd()):
        path = os.path.join(base, "pose_webcam.json")
        if os.path.isfile(path):
            return path
    return None


def _load_config(path):
    """Load options from a JSON config file. Unknown keys are ignored."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # Map to argparse-style names; only include known keys with valid types
    out = {}
    int_keys = ("camera", "det_frequency", "width", "height", "udp_port")
    str_keys = ("backend", "device", "mode", "udp_host")
    bool_keys = ("threaded", "no_viz", "show_fps")
    float_keys = ("smooth_pose",)
    for k in int_keys:
        if k in raw and isinstance(raw[k], (int, float)):
            out[k] = int(raw[k])
    for k in str_keys:
        if k in raw and isinstance(raw[k], str):
            out[k] = raw[k]
    for k in bool_keys:
        if k in raw and isinstance(raw[k], bool):
            out[k] = raw[k]
    for k in float_keys:
        if k in raw and isinstance(raw[k], (int, float)):
            out[k] = float(raw[k])
    return out


def parse_args():
    # First pass: get --config so we can load defaults (no -h so full parser shows full help)
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--config", type=str, default=None, help="Path to JSON config file (default: pose_webcam.json in app dir or cwd)")
    pre_args, remaining = pre.parse_known_args()
    config_path = pre_args.config or _default_config_path()
    config = {}
    if config_path:
        try:
            config = _load_config(config_path)
        except (OSError, json.JSONDecodeError) as e:
            if pre_args.config:
                print(f"Warning: could not load config from {config_path}: {e}", file=sys.stderr)

    # Defaults: config overrides built-in, then CLI overrides config
    defaults = {
        "camera": 0,
        "backend": "rtmlib",
        "device": "cpu",
        "mode": "balanced",
        "det_frequency": 5,
        "width": 0,
        "height": 0,
        "threaded": False,
        "no_viz": False,
        "show_fps": False,
        "udp_port": 0,
        "udp_host": "127.0.0.1",
        "smooth_pose": 0,
    }
    for k, v in config.items():
        if k in defaults:
            defaults[k] = v

    p = argparse.ArgumentParser(
        description="Webcam pose estimation (rtmlib or MMPose); compare with --backend"
    )
    p.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to JSON config file (default: pose_webcam.json in app dir or cwd)",
    )
    p.add_argument(
        "--camera",
        type=int,
        default=defaults["camera"],
        help="Camera device index (0 = default, 1 = first USB, etc.)",
    )
    p.add_argument(
        "--backend",
        type=str,
        default=defaults["backend"],
        choices=("rtmlib", "mmpose"),
        help="Pose backend: rtmlib (ONNX, default) or mmpose (PyTorch). Use both to find fastest.",
    )
    p.add_argument(
        "--device",
        type=str,
        default=defaults["device"],
        choices=("cpu", "cuda"),
        help="Device for inference (default: cpu; use --device cuda only if CUDA 12 + cuDNN 9 are installed)",
    )
    p.add_argument(
        "--mode",
        type=str,
        default=defaults["mode"],
        choices=("performance", "lightweight", "balanced"),
        help="rtmlib only: mode (lightweight=lowest latency, performance=most accurate)",
    )
    p.add_argument(
        "--det-frequency",
        type=int,
        default=defaults["det_frequency"],
        help="rtmlib only: run person detector every N frames (higher = lower latency, e.g. 10)",
    )
    p.add_argument(
        "--width",
        type=int,
        default=defaults["width"],
        help="Capture width (0 = camera default). Lower = less data, e.g. 640 for latency.",
    )
    p.add_argument(
        "--height",
        type=int,
        default=defaults["height"],
        help="Capture height (0 = camera default). e.g. 480 for latency.",
    )
    p.add_argument(
        "--threaded",
        action="store_true",
        default=defaults["threaded"],
        help="Run capture+inference in a background thread; main thread only displays. Reduces latency by not blocking on imshow.",
    )
    p.add_argument(
        "--no-viz",
        action="store_true",
        default=defaults["no_viz"],
        help="Skip skeleton overlay (raw frame + stats only). Slightly faster; use for keypoints-only (e.g. Unity).",
    )
    p.add_argument(
        "--show-fps",
        action="store_true",
        default=defaults["show_fps"],
        help="(Deprecated: stats are always shown.) Show FPS and inference time on the window",
    )
    p.add_argument(
        "--udp-port",
        type=int,
        default=defaults["udp_port"],
        help="If set, broadcast pose JSON to this port (e.g. for Unity Architect game). 0 = disabled.",
    )
    p.add_argument(
        "--udp-host",
        type=str,
        default=defaults["udp_host"],
        help="Target host for pose UDP (default: 127.0.0.1 for local Unity).",
    )
    p.add_argument(
        "--smooth-pose",
        type=float,
        default=defaults.get("smooth_pose", 0),
        metavar="ALPHA",
        help="Optional one-tap pose smoothing 0=off (lowest latency), 0.5-0.7=light. Weight of new sample.",
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
        tracking=False,
    )


def run_rtmlib_frame(pose_tracker, frame, show_fps: bool, no_viz: bool = False):
    t0 = time.perf_counter()
    keypoints, scores = pose_tracker(frame)
    t_infer = (time.perf_counter() - t0) * 1000
    vis = frame.copy()
    if not no_viz:
        from rtmlib import draw_skeleton
        vis = draw_skeleton(
            vis,
            keypoints,
            scores,
            openpose_skeleton=False,
            kpt_thr=0.4,
        )
    n_persons = 1 if keypoints.ndim == 2 else keypoints.shape[0]
    h, w = frame.shape[:2]
    pose_data = None
    if n_persons > 0 and w > 0 and h > 0:
        # First person: keypoints (17, 3) or (N, 17, 3) — x, y, score
        kpt = keypoints[0] if keypoints.ndim == 3 else keypoints
        if kpt.size >= 17 * 2:
            keypoints_list = []
            for i in range(min(17, len(kpt))):
                x = float(kpt[i, 0]) / w
                y = float(kpt[i, 1]) / h
                sc_flat = scores.reshape(-1) if scores is not None and hasattr(scores, "reshape") else []
                s = float(kpt[i, 2]) if kpt.shape[-1] >= 3 else (float(sc_flat[i]) if i < len(sc_flat) else 0.0)
                keypoints_list.append({"x": x, "y": y, "s": s})
            if len(keypoints_list) >= 17:
                pose_data = {"keypoints": keypoints_list, "width": w, "height": h}
    return vis, t_infer, n_persons, pose_data


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


def run_mmpose_frame(inferencer, frame, show_fps: bool, no_viz: bool = False):
    t0 = time.perf_counter()
    gen = inferencer(frame, return_vis=not no_viz)
    result = next(gen)
    t_infer = (time.perf_counter() - t0) * 1000
    if no_viz:
        vis = frame.copy()
    else:
        vis_list = result.get("visualization", [])
        if vis_list:
            vis = vis_list[0]
            if vis.ndim == 3 and vis.shape[2] == 3:
                vis = cv2.cvtColor(vis, cv2.COLOR_RGB2BGR)
        else:
            vis = frame.copy()
    h, w = frame.shape[:2]
    pose_data = None
    try:
        preds = result.get("predictions", [])
        if preds and len(preds) > 0:
            first = preds[0]
            # MMPose: keypoints shape (17, 3) or (N, 17, 3); x, y, score
            kpts = first.get("keypoints", first) if isinstance(first, dict) else first
            if hasattr(kpts, "__len__") and len(kpts) >= 17 and w > 0 and h > 0:
                keypoints_list = []
                for i in range(17):
                    pt = kpts[i]
                    x = float(pt[0]) / w
                    y = float(pt[1]) / h
                    s = float(pt[2]) if len(pt) > 2 else 1.0
                    keypoints_list.append({"x": x, "y": y, "s": s})
                pose_data = {"keypoints": keypoints_list, "width": w, "height": h}
        n_persons = len(preds[0]) if preds and hasattr(preds[0], "__len__") else (1 if preds else 0)
    except Exception:
        n_persons = 0
    return vis, t_infer, n_persons, pose_data


# -----------------------------------------------------------------------------
# UDP pose broadcast (for Unity Architect game)
# -----------------------------------------------------------------------------
def _blend_pose(pose_data: dict, prev: dict | None, alpha: float) -> dict:
    """Blend current pose with previous (one-tap EMA). alpha = weight of new; keep latency minimal."""
    if prev is None or alpha >= 1:
        return pose_data
    out = {"keypoints": [], "width": pose_data["width"], "height": pose_data["height"]}
    prev_kpts = prev.get("keypoints", [])
    for i, k in enumerate(pose_data["keypoints"]):
        if i < len(prev_kpts):
            pk = prev_kpts[i]
            out["keypoints"].append({
                "x": alpha * k["x"] + (1 - alpha) * pk["x"],
                "y": alpha * k["y"] + (1 - alpha) * pk["y"],
                "s": k["s"] if k.get("s") is not None else pk.get("s", 0),
            })
        else:
            out["keypoints"].append(dict(k))
    return out


def send_pose_udp(sock: socket.socket, host: str, port: int, pose_data: dict | None, smooth_alpha: float = 0, prev_pose: list | None = None) -> None:
    if sock is None or pose_data is None or port <= 0:
        return
    if smooth_alpha > 0 and prev_pose is not None and len(prev_pose) > 0:
        pose_data = _blend_pose(pose_data, prev_pose[0], smooth_alpha)
        prev_pose[0] = pose_data
    try:
        msg = json.dumps(pose_data).encode("utf-8")
        sock.sendto(msg, (host, port))
    except (OSError, TypeError):
        pass  # avoid spamming console on disconnect


# -----------------------------------------------------------------------------
# Stats overlay (FPS, latency, resolution, backend, device, persons)
# -----------------------------------------------------------------------------
def draw_stats(vis, fps: float, infer_ms: float, width: int, height: int, backend: str, device: str, n_persons: int | None):
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.6
    thick = 2
    color = (0, 255, 0)
    y, dy = 24, 22
    lines = [
        f"FPS: {fps:.1f}  |  Pose: {infer_ms:.1f} ms",
        f"{width}x{height}  |  {backend}  {device}",
    ]
    if n_persons is not None:
        lines.append(f"Persons: {n_persons}")
    (tw, th), _ = cv2.getTextSize(lines[0], font, scale, thick)
    cv2.rectangle(vis, (0, 0), (max(tw + 14, 280), len(lines) * dy + 12), (0, 0, 0), -1)
    for i, line in enumerate(lines):
        cv2.putText(vis, line, (10, y + i * dy), font, scale, color, thick)


def main():
    args = parse_args()

    if args.device == "cuda":
        _ensure_cuda_in_path()

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
        run_frame = lambda f: run_rtmlib_frame(pose_tracker, f, args.show_fps, args.no_viz)
    else:
        try:
            inferencer = create_mmpose_inferencer(args.device)
        except RuntimeError as e:
            print(e)
            sys.exit(1)
        run_frame = lambda f: run_mmpose_frame(inferencer, f, args.show_fps, args.no_viz)

    # Minimize capture buffer so we get the newest frame (reduces latency)
    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass
    if args.width > 0 or args.height > 0:
        if args.width > 0:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
        if args.height > 0:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
        # Read one frame so resolution takes effect
        _ = cap.read()

    # Warmup: run a few inferences so first real frame isn't cold (GPU/ONNX)
    warmup_frames = 5
    for _ in range(warmup_frames):
        ok, warm = cap.read()
        if not ok:
            break
        run_frame(warm)
    print(f"Warmup: {warmup_frames} frames.")

    udp_sock = None
    udp_prev_pose = [None]
    if args.udp_port > 0:
        try:
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Pose UDP: broadcasting to {args.udp_host}:{args.udp_port} (Unity Architect).")
        except OSError as e:
            print(f"Warning: could not create UDP socket: {e}")
    if getattr(args, "smooth_pose", 0) > 0:
        print(f"Pose smoothing: alpha={args.smooth_pose} (0=off for lowest latency).")

    print(f"Backend: {backend}  Camera: {args.camera}  Device: {device}")
    if args.threaded:
        print("Threaded mode: capture+inference in background, display on main thread.")
    print("Press Q to quit.")
    print("(Console: 'load ... onnx' and 'Tracking is on' from rtmlib are normal. Camera warnings are usually harmless.)")

    window_name = f"Pose ({backend}) — Q to quit"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    fps_alpha = 0.2
    fps_smooth = 30.0
    infer_smooth_ms = 10.0

    if args.threaded:
        # Single-slot "latest" result; worker overwrites, main thread displays (decouples imshow from inference)
        latest_lock = threading.Lock()
        latest_result = None
        stop_worker = threading.Event()

        def worker():
            while not stop_worker.is_set():
                ok, frame = cap.read()
                if not ok:
                    break
                vis, infer_ms, n_persons, pose_data = run_frame(frame)
                send_pose_udp(udp_sock, args.udp_host, args.udp_port, pose_data, getattr(args, "smooth_pose", 0), udp_prev_pose)
                with latest_lock:
                    nonlocal latest_result
                    latest_result = {
                        "vis": vis,
                        "infer_ms": infer_ms,
                        "n_persons": n_persons,
                        "w": vis.shape[1],
                        "h": vis.shape[0],
                        "t": time.perf_counter(),
                    }

        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()

        prev_t = None
        while True:
            with latest_lock:
                if latest_result is not None:
                    data = {
                        "vis": latest_result["vis"].copy(),
                        "infer_ms": latest_result["infer_ms"],
                        "n_persons": latest_result["n_persons"],
                        "w": latest_result["w"],
                        "h": latest_result["h"],
                        "t": latest_result["t"],
                    }
                else:
                    data = None
            if data is not None:
                if prev_t is not None:
                    elapsed = data["t"] - prev_t
                    fps_smooth = fps_alpha * (1.0 / max(elapsed, 1e-6)) + (1 - fps_alpha) * fps_smooth
                prev_t = data["t"]
                infer_smooth_ms = fps_alpha * data["infer_ms"] + (1 - fps_alpha) * infer_smooth_ms
                draw_stats(data["vis"], fps_smooth, infer_smooth_ms, data["w"], data["h"], backend, device, data["n_persons"])
                cv2.imshow(window_name, data["vis"])
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        stop_worker.set()
    else:
        while True:
            t0 = time.perf_counter()
            ok, frame = cap.read()
            if not ok:
                break

            vis, infer_ms, n_persons, pose_data = run_frame(frame)
            send_pose_udp(udp_sock, args.udp_host, args.udp_port, pose_data, getattr(args, "smooth_pose", 0), udp_prev_pose)
            elapsed = time.perf_counter() - t0
            h, w = vis.shape[:2]

            fps_smooth = fps_alpha * (1.0 / max(elapsed, 1e-6)) + (1 - fps_alpha) * fps_smooth
            infer_smooth_ms = fps_alpha * infer_ms + (1 - fps_alpha) * infer_smooth_ms
            draw_stats(vis, fps_smooth, infer_smooth_ms, w, h, backend, device, n_persons)

            cv2.imshow(window_name, vis)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    if udp_sock:
        try:
            udp_sock.close()
        except Exception:
            pass
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
