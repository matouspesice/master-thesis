# Experiment Design: Measuring End-to-End Delay (Motion-to-Photon)

**Goal:** Measure the overall delay from the person's movement to the avatar's movement in the game — i.e. **motion-to-photon** (or motion-to-display) latency.

---

## 1. Your Initial Idea: Phone Slow-Motion (240 fps)

- Use a phone in slow-motion mode (e.g. 240 fps).
- Perform a movement in real life and compare **when it finishes** (or starts) in the game.
- Need an **exact, reproducible** way to define “when” in both the real world and on screen.

This is a **video-based** approach: one camera (the phone) records both the real-world event and the display output, so you get a single timeline. It has been used in the literature and is suitable for your setup.

---

## 2. What Has Been Done Already (Literature)

### 2.1 Consumer camera, no specialised hardware — Feldstein & Ellis (2021)

- **Source:** Feldstein, I.T., Ellis, S.R. (2021). “A simple video-based technique for measuring latency in virtual reality or teleoperation.” *IEEE Transactions on Visualization and Computer Graphics.*
- **Method:** A **human evaluator** and an **ordinary consumer camera (e.g. cell phone)** film a setup where both the **real motion** and the **system output** (e.g. VR display or teleoperation feedback) are visible in the same frame. By analysing the video (e.g. frame-by-frame), the time difference between the real event and the displayed event is obtained.
- **Advantages:** No specialised hardware/software; can measure the system in its **actual** hardware/software configuration and under real performance conditions (e.g. with your Python + Unity pipeline running).
- **Accuracy:** Measurement uncertainty **below 10 ms** in their trials; they discuss refinements that may reduce uncertainty to **about 1 ms**.
- **Relevance:** Your phone-at-240-fps idea is directly in line with this: 240 fps ≈ 4.17 ms per frame, so frame-counting gives you a resolution on the order of a few ms, consistent with “below 10 ms” uncertainty and room to improve with care.

### 2.2 High-speed camera + co-registration — Warburton et al. (2022/2023)

- **Source:** Warburton, M., Mon-Williams, M., Mushtaq, F., Morehead, J.R. (2023). “Measuring motion-to-photon latency for sensorimotor experiments with virtual reality systems.” *Behavior Research Methods*, 55, 3658–3678. (DOI: 10.3758/s13428-022-01983-5)
- **Method:** They use a **240 fps smartphone** (Google Pixel 4a) to record **simultaneously**: (1) the real controller position (e.g. LED on a moving assembly) and (2) the **colour of the VR headset screen**. A custom Unity program drives the HMD screen colour in a known pattern (e.g. cyan/red/magenta per frame) and logs **virtual** controller position and screen colour at each HMD frame. By **matching screen colours** between the video and the Unity log, they **co-register** real and virtual time: “this camera frame = that HMD frame.” Then they detect **movement onset** in the real video and in the virtual data; the time difference is motion-to-photon latency. They also measure latency at mid-movement (where prediction helps) and over the full trajectory.
- **Findings:** At **sudden movement onset**, mean latencies were 21–42 ms across headsets; once motion prediction engaged, effective latency dropped to 2–13 ms within ~25–58 ms of movement start.
- **Relevance:** You can adopt the same **core idea** without the HMD: (a) phone records **real body part** (or a marker) and **the screen** where the avatar is shown; (b) you need a **synchronisation link** between “real time” and “display time” — either a visible on-screen signal (e.g. colour flash or timestamp overlay written by Unity) or frame-accurate timestamps in a log file aligned to the video. Then you define a clear **real-world event** (e.g. “hand passes a line”) and **display event** (e.g. “avatar hand passes the same line” or “first frame where avatar pose changes”) and count frames at 240 fps to get delay.

### 2.3 Summary: Can we inspire ourselves?

- **Yes.** Both approaches are directly relevant:
  - **Feldstein & Ellis:** Justifies using a **consumer phone camera** and a video-based method; gives expected accuracy (below 10 ms, possibly ~1 ms with refinements).
  - **Warburton et al.:** Shows a **concrete protocol** with 240 fps phone, co-registration via a **known visual pattern** (screen colour) tied to the application’s frame timeline, and **automated or semi-automated** detection of movement onset. You can simplify their setup (no HMD colour pattern; instead, e.g. a clear on-screen event or timestamp overlay + one visible real-world marker).

---

## 3. How to Execute Your Experiment (Concrete Options)

### 3.1 What you need

1. **Single timeline:** The phone video must show **both** (a) the real-world motion and (b) the screen (or part of it) where the avatar is displayed, so one frame index = one moment in time.
2. **Defined “real” event:** A moment in the real movement that you can detect in the video (e.g. “finger passes a line,” “wrist reaches highest point,” “LED on wrist passes a ruler mark”).
3. **Defined “display” event:** The corresponding moment on the display (e.g. “first frame where the avatar’s hand passes the same line,” or “first frame where avatar pose clearly changes”).
4. **Frame rate:** 240 fps ⇒ 1 frame ≈ 4.17 ms. So you get ~4 ms resolution before any refinement; with sub-frame interpolation or multiple trials you can approach the “below 10 ms” or “~1 ms” range discussed by Feldstein & Ellis.

### 3.2 Option A: Simple and robust (recommended to start)

- **Setup:** Phone fixed on a tripod, framing (1) you (or your hand/arm with a bright marker or LED) and (2) the monitor/screen showing the Architect avatar.
- **Sync link:** Have Unity **draw a visible indicator** that changes every frame or every N frames (e.g. a small coloured square that cycles R→G→B, or a number that increments each frame). Record that same indicator in the corner of the screen in the phone video. When you analyse the video, you can match “phone frame X” to “Unity frame Y” by reading the indicator, so you know the exact Unity frame time for each phone frame.
- **Real event:** Do a **single, sudden movement** (e.g. raise arm quickly). Define “real onset” as the first frame where your hand (or marker) clearly moves (you can do this manually or with simple motion detection in a ROI).
- **Display event:** Define “display onset” as the first Unity frame (identified via the indicator in the video) where the avatar’s pose visibly responds (e.g. arm starts moving). Then:  
  **Latency = (display onset frame − real onset frame) / 240 s** (or use actual fps if you measure it).
- **Exactness:** Use a clear, sudden movement; repeat many times (e.g. 20–40); report mean and SD or median and IQR. Optionally validate phone fps (e.g. with a 1 Hz blinking LED and frame count, as in Warburton et al.).

### 3.3 Option B: Even simpler (no Unity overlay)

- **Sync link:** You don’t have a frame-accurate overlay; instead you rely on **simultaneous visibility**. You perform a movement that has a **sharp, visible end** in both real and on screen (e.g. “hand hits table” in real life and “avatar hand hits virtual table” on screen). You count frames from “real impact” to “avatar impact” in the same video. This is easier to set up but usually less precise than Option A (sync tied to application frame).
- **Refinement:** Use a clear physical marker (e.g. LED) for the real event and a clear on-screen element (e.g. avatar hand crossing a line) for the display event; repeat and average.

### 3.4 Recommendation

- **Start with Option A:** Implement a small **Unity overlay** (e.g. frame counter or colour cycle) so every phone frame can be mapped to a Unity frame. Define **movement onset** (real + display) and compute latency as frame difference / 240 (or measured fps). This gives you an **exact, reproducible** procedure and aligns with established methods (Feldstein & Ellis; Warburton et al.).
- **Document in thesis:** “We measured motion-to-photon latency using a video-based method: a 240 fps smartphone recorded the user and the display; real and display movement onsets were identified and co-registered using an on-screen frame indicator; latency was computed as the frame difference at 240 fps (≈4.17 ms per frame).”

---

## 4. Camera for Capture Stage (Optimising the “Initial Part”)

Your supervisor suggested: **Edmund Optics**, and brands like **Point Grey**, **FLIR** — with **large sensor** and **large pixels** so the sensor “illuminates quickly” (short exposure, fast readout).

### 4.1 Why large sensor and large pixels?

- **Exposure time:** Larger pixels collect more light per unit time → you can use **shorter exposure** for the same scene brightness → less motion blur and **lower “capture” latency** (the moment the scene is sampled is closer to when the frame is used).
- **Readout:** Smaller sensors / fewer pixels often mean **faster readout** (less data to shift off the sensor). So there’s a trade-off: very high resolution can increase readout time; for pose estimation you often only need moderate resolution (e.g. 720p–1080p), so a sensor with **larger pixels** at moderate resolution can give both good light capture and fast readout.
- **Global shutter:** Industrial/machine vision cameras often offer **global shutter** (all pixels exposed at once), avoiding the rolling-shutter skew you get with many consumer cameras. That gives a **well-defined** capture instant and avoids motion artefacts that can affect pose quality and perceived latency.

### 4.2 Where to look (Edmund Optics, Point Grey, FLIR)

- **Edmund Optics:** They carry **machine vision cameras** (e.g. IDS Imaging USB3 models). Examples relevant to low latency:
  - **IDS U3-3864LE-M-GL-VU:** Monochrome, ~135 fps, 2.12 MP, Sony IMX290, USB 3.0, GenICam/USB3 Vision.
  - **IDS U3-3560XCP-M-GL:** Monochrome, ~102 fps, 2.3 MP, ON Semi AR0234 **global shutter**, USB 3.0, compact.
  - **IDS U3-3880CP-M-GL:** 1/1.8" sensor, USB 3, global shutter options.
- **Point Grey (now Teledyne FLIR):** Industrial USB3 Vision cameras; many with **global shutter**.
  - **Flea3 (e.g. FL3-U3-13E4C/M, FL3-U3-20E4):** 60 fps or ~59 fps, global shutter, 1.3–2 MP, 4.5 µm pixels (e.g. 20E4). Good for low-latency, controlled lighting.
- **FLIR (Teledyne FLIR):** Sony Pregius / Pregius S **global shutter** CMOS in many of their machine vision cameras; various interfaces (USB3, GigE). Higher-end models (e.g. 24 MP) are more for inspection than for minimal latency; look for **USB3**, **moderate resolution**, **high frame rate** (e.g. 60–120+ fps) for your use case.

### 4.3 What to specify for the thesis / lab

- **Interface:** USB 3.0 (UVC or USB3 Vision) for low transfer latency and minimal buffering.
- **Shutter:** Prefer **global shutter** for a well-defined capture time and no rolling-shutter artefacts.
- **Frame rate:** At least 60 fps; 90–120 fps or higher if budget allows, to reduce capture interval and improve perceived responsiveness.
- **Pixel size / sensor:** Prefer **larger pixels** (e.g. 4–5 µm or more where available) and **moderate resolution** (e.g. 1–2 MP for pose) so exposure can be short and readout fast.
- **Vendors:** Edmund Optics (IDS), Point Grey / Teledyne FLIR (Flea3, Blackfly, etc.), and FLIR’s machine vision range. Request specs for **exposure delay**, **readout time**, and **end-to-end frame latency** if available.

---

## 5. Where This Goes in the Thesis

- **Theory (Related Work):**
  - Add a short subsection on **measuring motion-to-photon latency**: cite Feldstein & Ellis (video-based, consumer camera, &lt;10 ms uncertainty) and Warburton et al. (240 fps phone, co-registration, movement onset). This supports your choice of a **video-based** experiment.
  - Add a **latency composition** diagram (timeline/scheme): **Capture → Python (inference) → UDP → Unity (parse, drive avatar, render) → Display**, with brief labels on how you optimise each (camera choice, buffer=1, model/det-frequency, no smoothing, etc.). This belongs in the **Motion Tracking and Latency** section (theory).
  - Expand **Sensing / camera** to include: **capture latency** (exposure, readout, transfer), and **industrial cameras** (Edmund Optics, Point Grey/FLIR, large sensor, large pixels, global shutter) as the next optimisation step after pose estimation.

- **Methodology:**
  - Describe **your** measurement protocol: e.g. 240 fps phone, what is in frame (user + display), how you co-register (e.g. Unity frame indicator), how you define real and display onset, and how you compute latency (frame count / fps). Optionally, how you validate phone fps.

- **Implementation / Evaluation:**
  - Report the hardware used (current webcam vs. any new industrial camera), and the measured **tracking-loop** (Python) and **motion-to-photon** (video-based) latencies.

---

*Doc prepared for thesis experiment design and Related Work updates. Literature: Feldstein & Ellis 2021 (IEEE TVCG); Warburton et al. 2023 (Behavior Research Methods).*
