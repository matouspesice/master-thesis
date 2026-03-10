# Scopus AI Report → Thesis Improvement Analysis

**Source:** *Development of a Low-Latency ML-Based Motion Tracking System for Gamified Knee Rehabilitation in VR* (Scopus AI, Mar 2026).  
**Purpose:** Map the report’s themes to your thesis (theory, methodology, app) and list what you already do vs. what could be added.

---

## 1. What You Are Already Aligned With

### 1.1 Theory / Related Work

| Scopus theme | Your current coverage |
|--------------|------------------------|
| **Low-latency ML motion tracking** | Strong: Related Work §2 (Motion Tracking and Latency), RTMPose/MMPose, target &lt;10 ms tracking loop, 63 ms cybersickness threshold, latency thresholds table. |
| **Pose estimation for rehab** | You use RTMPose/MMPose (top-down); report compares OpenPose, MediaPipe, AlphaPose, BlazePose. You cite Jiang et al. (RTMPose), Lugaresi (MediaPipe); table of RTMPose variants. |
| **Gamification for knee rehab** | Strong: §3 Gamification and Motor Learning, knee context (TKA/ACL), proprioception, external focus of attention, Architect as goal-oriented balance. |
| **VR in rehabilitation** | §1 VR scope, avatar vs mirror, simulator sickness; §4 mirror therapy limitations. |
| **Camera/sensor choice** | §5 USB webcam vs action camera, UVC 60 FPS, table of sensor options; no action camera for low latency. |
| **Latency thresholds** | Table: 16–20 ms noticeable, 63 ms cybersickness, 75 ms motor, 125 ms body ownership; target sub-10 ms tracking. |

### 1.2 Methodology

| Scopus theme | Your current coverage |
|--------------|------------------------|
| **Modular pipeline** | Camera → ML → UDP → Unity; Methodology still TODO but design is modular (app vs Architect). |
| **Single RGB camera** | Explicit choice (no multi-camera / IMU fusion yet). |
| **Gamified balance task** | Architect: Pose Dodge + Single-Leg Balance; external focus, knee ROM. |

### 1.3 App / System

| Scopus theme | Your current coverage |
|--------------|------------------------|
| **Lightweight, real-time pose** | RTMPose (rtmlib/MMPose), `--mode lightweight`, detector frequency, GPU option. |
| **Low-latency pipeline** | UDP broadcast, optional smoothing (alpha), no handshake; Unity consumes latest pose per frame. |
| **Real-time corrective feedback** | Pose Dodge: match pose to pass (duck, jump, lean); Single-Leg Balance: stability feedback. |
| **Standard protocol** | JSON over UDP, COCO 17 keypoints; documented in ARCHITECT_GAME.md. |

**Summary:** Your thesis and app already match the report’s core message: low-latency ML tracking + gamified knee rehab in VR, with a clear latency target and gamification rationale.

---

## 2. Suggested Additions (Theory / Related Work)

### 2.1 Pose model comparison table (optional, 1 paragraph + table)

The report’s table (OpenPose, MediaPipe, AlphaPose, BlazePose — accuracy, latency, platform) is a good reference. You already have an RTMPose table; you could add a **short comparative sentence** in Related Work, e.g.:

- *“MediaPipe and AlphaPose are often cited as best trade-off for real-time home VR rehab; OpenPose remains a clinical accuracy benchmark where compute allows. For this thesis, RTMPose was chosen for its reported 7–14 ms inference range and strong COCO performance (Table X).”*

Optionally add a small table: Model | Accuracy (knee) | Latency | Platform | Notes (one line each for OpenPose, MediaPipe, AlphaPose, BlazePose, RTMPose). That strengthens the “state of the art” and justifies your choice.

### 2.2 Latency reduction beyond inference

Report highlights: **predictive tracking** (Kalman, LSTM, transformers), **sensor fusion**, **edge computing**, **&lt;50 ms ideal**, 90–130 ms degrades performance. You already cite 63 ms and 125 ms. You could add:

- One sentence that **&lt;50 ms** is often cited as “ideal” for immersive VR (with a citation from the report’s refs if you add them).
- In Implementation or Discussion: “Future work could explore prediction (e.g. Kalman or LSTM) to compensate pipeline delay”; no need to implement for the thesis.

### 2.3 Gamification elements (engagement)

Report: **points, avatars, challenges, leaderboards, progress bars, social support, personalized feedback**; **personalization** is under-explored. You already have:

- Points/scores (Dodge, Balance), avatar (body-driven), challenges (obstacles, single-leg hold). You do **not** have leaderboards, social support, or adaptive difficulty.

**Suggestion:** In Related Work §3 (Engagement and compliance) or Discussion, add 1–2 sentences: *“Literature identifies points, avatars, and challenges as effective; leaderboards and personalized difficulty are promising but less often implemented [cite]. The Architect prototype focuses on points, avatar feedback, and pose-based challenges; personalization could be a future extension.”*

### 2.4 Standardization and clinical translation (gaps)

Report: lack of **standardized protocols**, **data formats**, **outcome measures**; need for **clinical validation**. You can reflect this in **Discussion** (and optionally in Related Work):

- *“Existing work notes a lack of standardized protocols and outcome measures in ML-based VR rehab [cite]. This pilot uses [your outcome measures, e.g. system feel, engagement]; future work could align with PROMs (e.g. KOOS, IKDC) and standardized rehab timelines for clinical translation.”*

This shows you are aware of the field’s gaps without overclaiming.

### 2.5 Privacy and federated learning (optional, 1 sentence)

Report: **federated learning**, **edge AI**, **privacy-preserving** personalization. For your thesis (single-user, lab/home pilot), one sentence in **Discussion / Future work** is enough:

- *“Privacy-preserving approaches such as federated learning are emerging for personalized rehab [cite]; they were out of scope for this prototype but relevant for future at-home deployment.”*

---

## 3. Suggested Additions (Methodology)

### 3.1 Camera placement and patient positioning

Report: **camera angle and patient positioning** (e.g. supine) improve accuracy; MediaPipe validated vs goniometers. You can add to **Methodology (Motion Capture Pipeline)** or **Implementation**:

- Short protocol: camera height, distance, angle (e.g. frontal/slight angle), and body in frame (full body or lower body + trunk). Refer to “camera placement” best practices from the literature.

### 3.2 Latency measurement method

You already plan a **Latency Measurement** section (implementation.tex). The report stresses **motion-to-photon** and **&lt;50 ms ideal**. Suggested content:

- **What you measure:** e.g. camera frame timestamp → pose timestamp → Unity display timestamp (or high-speed camera / known motion).
- **What you report:** mean and/or percentiles (e.g. p50, p95), and comparison to 63 ms / 125 ms thresholds.
- One sentence citing that motion-to-photon is the standard for VR latency (you can use report refs or existing ones like Stauffert).

### 3.3 Pilot outcome measures

Report: **PROMs** (e.g. IKDC, KOOS), **standardized outcomes**. If your pilot is “system feel + engagement” only:

- Keep your current design; in **Evaluation** or **Discussion** state that you did not use clinical PROMs and that future work could include them for clinical translation.

---

## 4. Suggested Additions (App / Implementation)

### 4.1 Already planned: latency measurement

- Implement timestamp-based (or external) latency measurement and document it in Implementation + report in Evaluation. This directly addresses the report’s “latency reduction” and “real-time” themes.

### 4.2 Optional: compare backends

You have `--backend rtmlib|mmpose`. You could:

- Run a **short benchmark** (e.g. 30 s same camera, same resolution): mean inference time and FPS for rtmlib vs mmpose. One table in Implementation or Evaluation. This aligns with the report’s “comparative analysis” of pose models.

### 4.3 Optional: smoothing vs latency

Report mentions **1-Euro filter**, **Butterworth** for jitter. You have `--smooth-pose` (alpha). You could:

- In Implementation: one sentence + optional one graph or table (smoothing off vs 0.3 vs 0.5: latency vs jitter or subjective stability). Keeps scope small.

### 4.4 Not recommended for current scope

- **Sensor fusion (IMU + camera):** Report recommends it for robustness; your thesis is “single RGB + ML.” Mention as future work in Discussion.
- **Federated learning / edge AI:** Mention as future work only.
- **LSTM/transformer prediction:** Mention as future work for latency compensation.
- **New games or leaderboards:** Only if you have time; otherwise “future work.”

---

## 5. References From the Report You Might Cite

If you add any of the above, consider citing (from the report’s reference list):

- **MediaPipe validation / knee:** Francia et al. (2024) – MediaPipe for VR rehab; Phang et al. (2025) – YOLOv8 vs MediaPipe for knee rehab.
- **Latency thresholds / motion-to-photon:** Kelkkanen et al. (2023) – hand-controller latency; Warburton et al. (2023) – motion-to-photon measurement.
- **Gamification:** Ren et al. (2025) – gamification in knee OA rehab; McClincy et al. (2021) – gamification for pediatric ACL rehab.
- **Standardization / gaps:** Wang et al. (2025) – AI and gamification in rehab scoping review; Plavoukou et al. (2025) – sensors and TKA rehab.
- **Federated / privacy:** Chen et al. (2025), Piechowiak et al. (2025) – for one sentence on future work.

Add only those that you actually use; keep one consistent citation style (e.g. IEEE as in your plan).

---

## 6. Summary Table: Do Now vs Later vs Skip

| Item | Where | Do now | Later / optional | Skip |
|------|--------|--------|-------------------|------|
| Pose model comparison sentence (RTMPose vs MediaPipe/OpenPose) | Related Work | ✓ | | |
| &lt;50 ms “ideal” latency sentence | Related Work or Implementation | ✓ | | |
| Gamification elements + personalization (1–2 sentences) | Related Work or Discussion | ✓ | | |
| Standardization / PROMs (1–2 sentences) | Discussion | ✓ | | |
| Federated / privacy (1 sentence) | Discussion / Future work | | ✓ | |
| Camera placement protocol | Methodology / Implementation | ✓ | | |
| Latency measurement (method + numbers) | Implementation + Evaluation | ✓ (must-have) | | |
| Backend comparison table (rtmlib vs mmpose) | Implementation / Evaluation | | ✓ | |
| Smoothing vs latency (optional graph) | Implementation | | ✓ | |
| Sensor fusion / IMU | Discussion / Future work | | ✓ | |
| LSTM/transformer prediction | Discussion / Future work | | ✓ | |
| New games / leaderboards | — | | | ✓ (unless you have time) |

---

## 7. Bottom Line

- **You are already well aligned** with the Scopus report: low-latency ML tracking, gamified knee rehab, single RGB camera, UDP pipeline, latency thresholds, and gamification theory.
- **High-impact, low-effort additions:** (1) Latency measurement (implement + document); (2) short theory/discussion sentences (pose comparison, &lt;50 ms, gamification elements, standardization, optional privacy); (3) camera placement in methodology/implementation.
- **Optional:** Backend comparison table, smoothing vs latency, and “future work” on sensor fusion, prediction, and federated learning.

Using this map, you can tighten the theory, methodology, and app description without overreaching for the May 31 deadline.
