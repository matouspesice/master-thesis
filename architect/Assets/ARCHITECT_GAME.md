# Architect — Game Principle and Purpose

## Purpose (Master Thesis Context)

**Architect** is the target application of the real-time pose pipeline from the thesis: it demonstrates **body-driven control** of a 3D avatar using **MMPose/RTMPose** pose estimation from a webcam. The game serves as proof that the low-latency pose stack (Python app) can drive a real-time interactive experience (Unity).

- **Input:** Live webcam → pose estimation (rtmlib/MMPose) → streamed keypoints.
- **Output:** A 3D avatar in Unity that mirrors the user’s pose in real time.

The name *Architect* suggests the user “builds” or “designs” with their body—e.g. placing or manipulating objects through gesture—while the core mechanic is **you are the avatar**: your skeleton drives the character.

---

## Core Principle

1. **Single user, single avatar**  
   One person in front of the camera controls one in-game avatar. The pipeline is tuned for one tracked person (first/best detection).

2. **Pose as input, not keyboard/mouse**  
   Movement and posture come from 2D pose keypoints (e.g. COCO 17) sent over the network. No traditional controls are required for the avatar (optional fallback can be added later).

3. **Real-time mirroring**  
   The avatar should reflect the user’s pose with minimal delay. Latency is kept low via:
   - Lightweight models and optional GPU in the Python app
   - UDP broadcast of keypoints (no handshake)
   - Unity consuming the latest pose each frame

4. **Extensible for thesis experiments**  
   The same link (UDP/JSON) can be used to:
   - Compare backends (rtmlib vs MMPose) on latency and accuracy
   - Test different camera sources (e.g. lab vs home)
   - Add future gameplay (e.g. “architect” building gestures, menus, calibration)

---

## Technical Design

| Component        | Role |
|-----------------|------|
| **Python app**  | Webcam → RTMPose/MMPose → 2D keypoints → UDP broadcast (JSON). |
| **Unity**       | UDP listener → parse JSON → drive avatar (skeleton or Humanoid). |
| **Protocol**    | One JSON message per pose: `keypoints` (normalized or pixel), `width`, `height`, optional `scores`. COCO 17 keypoint order. |

---

## Keypoint Convention (COCO 17)

Index | Name  
-----|------  
0 | nose  
1 | left_eye  
2 | right_eye  
3 | left_ear  
4 | right_ear  
5 | left_shoulder  
6 | right_shoulder  
7 | left_elbow  
8 | right_elbow  
9 | left_wrist  
10 | right_wrist  
11 | left_hip  
12 | right_hip  
13 | left_knee  
14 | right_knee  
15 | left_ankle  
16 | right_ankle  

Each keypoint: `[x, y, score]`. Coordinates could be normalized [0,1] or in image pixels; `width`/`height` in the message disambiguate.

---

## Scene setup (Unity)

**Option A — Menu (if you see “Architect”)**

1. Open the Architect Unity project and your scene (e.g. **SampleScene**).
2. In the **top menu bar** (same row as *File*, *Edit*, *GameObject*, *Window*, *Help*), look for **Architect**.
3. Click **Architect → Create Pose Bridge**. This adds a **PoseBridge** GameObject with PoseReceiver and PoseAvatarDriver.
4. Save the scene (Ctrl+S).

**Option B — Manual (if “Architect” menu is missing)**

If you don’t see **Architect** in the menu bar (e.g. scripts didn’t compile or menu didn’t load), create the bridge by hand:

1. In the **Hierarchy**, right‑click → **Create Empty**. Rename it to **PoseBridge**.
2. With **PoseBridge** selected, in the **Inspector** click **Add Component**.
3. Search for **Pose Receiver** and add it. Set **Port** to `5555`.
4. Click **Add Component** again, search for **Pose Avatar Driver** and add it.
5. On **Pose Avatar Driver**, leave **Pose Receiver** empty (it will find it automatically), set **Avatar Scale** to `2`, and ensure **Create Debug Skeleton** is checked.
6. Save the scene (Ctrl+S).

**What’s on the bridge**

- **PoseReceiver** — listens on UDP port `5555` (match `--udp-port` in Python).
- **PoseAvatarDriver** — joints (spheres) + optional **limb sticks** (capsules). Options (tune for low latency):
  - **Mirror Flip X** — on by default so your right = avatar right (mirror view).
  - **Smoothing** — 0 = off (lowest latency), 0.3–0.5 = light; higher adds lag.
  - **Create Limb Sticks** — capsules between joints (arms, legs, torso).

## How to Run

1. **Start pose stream (Python)**  
   From the thesis `app` folder:
   ```bash
   cd app
   python pose_webcam.py --udp-port 5555 --no-viz
   ```
   Use `--device cuda --mode lightweight` for lower latency if GPU is available.  
   For a visible camera window, omit `--no-viz`.

2. **Start Unity**  
   Press **Play** in the Architect scene. Ensure **PoseReceiver** port is `5555` (or match `--udp-port`).

3. **Play**  
   The in-game avatar (debug skeleton or your character) should follow your body pose from the webcam.

---

## Possible Future Extensions (Thesis / Post-Thesis)

- **Calibration:** One-time or runtime mapping from camera space to avatar scale/orientation.
- **Gesture commands:** Map specific poses (e.g. arms raised, T-pose) to actions (e.g. “place block”, “undo”).
- **Architect gameplay:** Use pose to place or rotate objects in a level, or to navigate a simple world.
