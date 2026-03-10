# Meeting Refresh — What We Have Done So Far

**Purpose:** Summary for refreshing after your supervisor meeting. You had Cursor set up and an empty template; this document summarises the current state and key findings from the theory, script logic, and game logic.

---

## 1. Project Setup and Current State

### Repository structure (from README)

| Folder | Purpose |
|--------|--------|
| **thesis/** | LaTeX source: `main.tex`, `chapters/`. Build PDF from here (e.g. LaTeX Workshop in Cursor). |
| **references/** | Citavi BibTeX export → `bibliography.bib`. All citations use this file. |
| **app/** | VR/ML source: Python pose pipeline (`pose_webcam.py`), config, requirements. |
| **architect/** | Unity project: Architect game (avatar, games, UI). |
| **data/** | Pilot study data (CSV, logs). |

- **.cursorrules** — Instructions for the AI (thesis vs code tone, citations, latency focus).

### Thesis document

- **main.tex** — Uses MCI template (`template/`), includes: introduction, related work, methodology, implementation, evaluation, discussion, conclusion, appendices. Bibliography from `../references/bibliography`.
- **Chapters** — Introduction and outline are still TODO placeholders; **Related Work is fully written**; Methodology has system overview + motion capture; Implementation describes the pipeline and latency measurement; Evaluation and Discussion are present; Conclusion and appendices exist.

### What’s implemented

- **Python app:** Real-time pose from webcam (rtmlib/RTMPose or optional MMPose), UDP broadcast to Unity, latency logging, config file support.
- **Unity Architect:** PoseReceiver (UDP), PoseAvatarDriver (skeleton/limb sticks), PoseGestureDetector (gestures + balance metrics), four game modes (Pose Dodge, Single-Leg Balance, Lean Balance, Coin Mine), GameSelector, full UI. One-click **Architect → Create Complete Setup** builds the scene.
- **Thesis text:** Related Work is complete; Implementation and Methodology describe the pipeline and games; latency method is specified.

---

## 2. Key Findings from the Theory (Related Work) — Refresh

### 2.1 VR in rehabilitation

- **Scope:** VR is used for upper limb, stroke (balance/gait), and lower limb/knee rehab (e.g. TKA, ACL). Benefits: repeatable tasks, objective feedback, clinic or home use with consumer hardware.
- **Feedback modalities:** Mirror therapy is limited (asymmetric posture, fixed view). Avatar-based feedback (screen or HMD) avoids that and can be gender-neutral, third- or first-person. High-end systems (e.g. CAREN) use 3D MoCap + large screens; this thesis uses a **single RGB camera + ML pose** to drive an avatar.
- **Simulator sickness:** A major barrier. Artificial movement and **high latency** contribute. Your context (Hollaus et al.) provides tools to evaluate VR movement tolerability; controlling **latency and refresh rate** is critical for presence and reducing SS.

### 2.2 Motion tracking and latency

- **End-to-end latency** = capture + inference (and optional filtering) + render/display. **Target:** tracking loop (capture + inference) **&lt; 10 ms** so total motion-to-photon stays below comfort limits.
- **Capture:** Minimise buffered frames (e.g. buffer size 1) so the app uses the newest frame.
- **Inference:** Trade accuracy vs speed: run person detector every *N* frames (top-down), use smaller models (e.g. RTMPose-s/lightweight). Sub-10 ms tracking loop is realistic on desktop GPU (e.g. RTX 4090); on lighter hardware (e.g. Snapdragon 865) per-frame is higher (~14 ms).
- **Pose frameworks:** Top-down (person bbox → pose in crop) vs bottom-up (keypoints then group). RTMPose/MMPose are top-down; RTMPose reaches 7–10 ms on high-end GPU, 70+ FPS on mobile. MediaPipe/BlazePose also used in VR rehab; MMPose/RTMPose chosen here for reported latency and COCO performance.
- **Filtering:** Raw pose can jitter. Options: Butterworth low-pass or 1-Euro filter. For single-leg balance (slower motion), light smoothing is possible; for minimal latency, smoothing is disabled (alpha = 0).
- **Latency thresholds (literature):**
  - **~16–20 ms:** Delay noticeable in fast scenarios.
  - **63 ms:** Significant cybersickness (Stauffert et al.).
  - **75 ms:** Motor performance and simultaneity impaired.
  - **125 ms:** Body ownership and agency start to break down (Waltemate et al.).
  - **50 ms:** Often cited as ideal for immersive VR.
- **Frame rate:** 72 Hz or higher is recommended for active VR to improve tolerance.

### 2.3 Gamification and motor learning

- **Knee rehab context:** After TKA/ACL, proprioception and balance are often reduced. Rehab includes strength + balance/coordination (single-leg stance, tandem walking, etc.). **Proprioception-focused** programmes can yield better functional outcomes than strength-only (e.g. Jogi et al.).
- **External focus of attention (EFA):** Internal focus (on body) can increase conscious control and interfere with automatic control; **external focus** (on effect in the environment) promotes more stable, automatic performance. Single-leg balance with EFA is associated with lower cognitive effort in EEG (Sherman et al.). The **Architect** game (e.g. “keep the structure stable”) is designed to induce EFA.
- **Mirror therapy vs VR:** Mirror therapy has limitations (posture, fixed view). Kim et al. showed VR reflection therapy (virtual limb representation) improved balance and gait more than mirror therapy in chronic stroke (Berg Balance Scale, TUG).
- **Engagement:** Gamification (points, avatar, challenges, progress feedback) can improve adherence. Architect uses points, avatar feedback, and pose-based challenges; pilot evaluation will assess engagement and perceived responsiveness vs standard feedback.

### 2.4 Sensing and camera choice

- **Pose needs:** Moderate input resolution (e.g. 256×256, 384×384); **frame rate and low capture latency** matter more than very high resolution. 720p/1080p at 60 FPS over USB 3 (UVC) is typically only a few ms.
- **Action cameras:** Usually high **sensor-to-display** latency (e.g. 200 ms+ over USB/Wi-Fi), so **not suitable** for low-latency VR. Use **UVC-class** devices (e.g. standard USB webcam, 60 FPS).
- **Recommendation:** Standard RGB USB 3.0 webcam (60 FPS or higher); optional OAK-1 Lite for on-device inference within budget.

### 2.5 Research gap (thesis contribution)

- **Gap:** No reported system combines **(1)** low-latency (sub-30 ms, target sub-10 ms tracking) **markerless** skeletal tracking from a **consumer RGB camera** with **(2)** a **gamified**, goal-oriented single-leg balance task in VR for knee rehab, evaluated for **system feel (responsiveness)** and **engagement** vs standard visual feedback.
- **Thesis aims:** Build the tracking pipeline, Architect prototype, and run a pilot user evaluation to address this gap.

---

## 3. Script Logic (Python Pipeline — `pose_webcam.py`)

### 3.1 High-level flow

1. **Camera** — OpenCV `VideoCapture`; buffer size set to 1 to minimise capture latency; optional resolution (e.g. 640×480) for speed.
2. **Inference** — Each frame (or in a worker thread) is passed to the pose backend.
3. **Backends:**
   - **rtmlib (default):** `PoseTracker(Body, mode=…, det_frequency=N, backend="onnxruntime", device=…)`. Top-down: person detector every `det_frequency` frames, pose on crop. Modes: `lightweight` (lowest latency), `balanced`, `performance`.
   - **MMPose (optional):** `MMPoseInferencer(pose2d="human", device=…)`; full PyTorch stack.
4. **Output:** COCO-17 keypoints; coordinates normalised to [0,1] by image width/height; optional one-tap EMA smoothing (`--smooth-pose`; 0 = off for lowest latency).
5. **UDP:** If `--udp-port` is set, each pose is sent as JSON to `udp_host:port` (e.g. 127.0.0.1:5555 for Unity). Message: `{ "keypoints": [{x,y,s}, ...], "width", "height" }`.
6. **Latency logging:** With `--log-latency`, the script records (timestamp after `cap.read()` → timestamp after inference). At exit it prints mean, median, p95 of capture-to-pose time; optional `--latency-csv` writes per-frame (loop_ms, infer_ms).

### 3.2 Low-latency levers

- **Device:** `--device cuda` (needs CUDA 12 + cuDNN 9 on Windows).
- **Mode:** `--mode lightweight` (smaller models).
- **Detector:** `--det-frequency 10` (or higher) so detector runs less often.
- **Resolution:** `--width 640 --height 480` (or 0 for camera default).
- **Threaded:** `--threaded` — capture + inference in background thread, main thread only displays (reduces blocking on `imshow`).
- **No viz:** `--no-viz` — no skeleton overlay; use when only keypoints are needed (e.g. Unity).
- **Smoothing:** `--smooth-pose 0` for minimal latency; 0.5–0.7 for light smoothing.

### 3.3 Config

- Optional `pose_webcam.json` in app dir or cwd (or `--config path`). Keys: camera, backend, device, mode, det_frequency, width, height, threaded, no_viz, udp_port, udp_host, smooth_pose, etc. CLI overrides config.

---

## 4. Game Logic (Unity Architect)

### 4.1 Data flow

- **PoseReceiver:** Listens on UDP (e.g. port 5555), parses JSON into `PoseMessage` (keypoints array, width, height). Exposes `latestPose` and `TryGetKeypoint(index, out normalized, out score)`. Only accepts messages with ≥17 keypoints.
- **PoseAvatarDriver:** Reads `poseReceiver.latestPose` each frame. Maps COCO-17 keypoints to 3D: normalised (x,y) → local positions (with aspect and optional mirror flip X). Shoulder width used for scale. Optional EMA smoothing (0 = off for lowest latency). Creates debug skeleton (spheres at joints) and/or limb sticks (capsules between joints via `CocoKeypointIndex.LimbEdges`).
- **PoseData / CocoKeypointIndex:** `PoseKeypoint` (x, y, s); `PoseMessage` (keypoints, width, height). COCO-17 indices (nose, eyes, ears, shoulders, elbows, wrists, hips, knees, ankles) and limb edges for drawing sticks.

### 4.2 Gesture and balance (PoseGestureDetector)

- **Input:** Same `PoseReceiver`; uses keypoints only (no labels from Python).
- **Discrete gestures (for Pose Dodge):** ArmsUp (wrists above shoulders), Crouch (knees well below hips), LeanLeft/LeanRight (shoulder centre vs frame centre 0.5), T-pose (wrists at shoulder height, spread). Debounce: gesture must be held for `gestureHoldFrames` to register.
- **Single-leg:** Compare ankle Y (raised foot has smaller Y); threshold `singleLegAnkleDiff`. Output: `StandingLeg.Left`, `Right`, or `None`.
- **Sway (stability):** Hip centre (average of L/R hip) over a rolling window; variance → `SwayMagnitude`. `IsStable` = sway below `unstableSwayThreshold`.
- **Torso lean (for Lean Balance / Coin Mine):** Shoulder centre X minus hip centre X, smoothed. `TorsoLeanX` (optionally inverted); `CurrentTorsoLeanState`: Neutral | Left | Right using a neutral zone.

### 4.3 Game modes

- **Pose Dodge:** Obstacles move toward hit-line; each has a required gesture (Duck, Jump, Stand, Lean Left/Right). Player must match gesture when obstacle passes; wrong = lose life. Uses `PoseGestureDetector.CurrentGesture` and `DodgeObstacle.GestureMatches(...)`. Score = correct passes; game over when lives = 0.
- **Single-Leg Balance:** Get on one leg and hold with low wobble. After `singleLegRequiredAfterSeconds` of single-leg, timer and scoring start. Score from stability × time; putting foot down or too much instability (for `instabilityGraceTime`) ends the round. Stability bar reflects current stability. Aligns with thesis proprioception/balance and EFA (focus on “keeping bar full”).
- **Lean Balance:** Uses only `TorsoLeanX`. Bar/cursor shows lean; goal = keep in green (neutral) zone. Score = time in zone; optional target time to win or “out of zone” duration to fail.
- **Coin Mine:** Three lanes; lean L/C/R to move into lane. Coins spawn in a lane and move toward player; lean into the coin’s lane to collect. Uses same torso lean; UI shows “You: LEFT/CENTER/RIGHT” and hint for next coin.

### 4.4 Scene and UI

- **Architect → Create Complete Setup:** Creates PoseBridge (PoseReceiver + PoseAvatarDriver), PoseGestureDetector, all game managers (Dodge, SingleLegBalance, LeanBalance, Coin Mine), GameSelector, and full GameCanvas with panels and wiring. TMP Essentials required for UI.
- **Run:** Start Python with `python pose_webcam.py --udp-port 5555` (optionally `--no-viz`); Unity Play; choose game and Start. Avatar mirrors pose from webcam.

---

## 5. Next Steps (from thesis and docs)

- **Thesis:** Fill Introduction (context, problem, research questions, outline); expand Methodology (gamification design, evaluation design); add Evaluation results when pilot is run; align Implementation/Evaluation with actual latency and setup.
- **Pilot:** Run latency measurements (`--log-latency`, optional CSV); optionally measure end-to-end motion-to-photon with Unity; compare system feel and engagement vs standard feedback.
- **Optional extensions:** Calibration (camera ↔ avatar); more games (e.g. Weight-Shift Reach, Pose Simon Says); VR headset when moving from screen-based prototype.

---

*Summary generated from current thesis chapters, `app/`, and `architect/` as of the last edit. Use this to refresh before your next supervisor meeting.*
