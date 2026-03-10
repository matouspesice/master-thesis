# Camera and Lens Research: RGB vs Monochrome, Requirements, and Product Links

## 1. Is the PDF updated?

The thesis PDF is built from `thesis/` with `.\build.ps1` (pdflatex → bibtex → pdflatex ×2). After the recent edits to `related_work.tex` and `bibliography.bib`, **you need to run the build** to get an updated PDF. If you already ran it (e.g. via LaTeX Workshop or `.\build.ps1`), the last run did write `main.pdf` (34 pages). A small fix was applied to `methodology.tex` (TikZ node `align=center` for the system-architecture figure) so the build no longer hits “Not allowed in LR mode” errors. **Run the build again** after pulling the latest changes to be sure the PDF includes the new Related Work content and compiles cleanly.

---

## 2. RGB vs monochrome: research and decision

### 2.1 Does the pipeline require RGB?

- **RTMPose / MMPose** are trained and used with **3-channel (RGB) input** by default. Preprocessing uses RGB normalisation (mean/std).
- **Using monochrome:** You can feed a **single-channel (grayscale) image** by **replicating it to three channels** (G, G, G) before passing to the model. No retraining is required. Pose estimation relies mainly on shape and contrast, not colour, so this is standard practice and accuracy remains acceptable for skeleton keypoints.

**Conclusion:** RGB is **not** strictly required. A **monochrome camera is compatible** with the existing Python pipeline: capture one channel, duplicate to 3 in code, then pass to RTMPose/MMPose.

### 2.2 Is monochrome faster?

- **Readout:** Monochrome sensors have **no Bayer colour filter**. Every pixel captures full intensity, so there is **no demosaicing** step. Readout can be simpler and **faster** (less data or simpler processing in the camera/API).
- **Sensitivity:** Without a colour filter, more light reaches each pixel (**higher quantum efficiency**). For the same exposure time you get a brighter image, or you can use **shorter exposure** for the same brightness → **lower capture latency** and less motion blur.
- **Data path:** Delivering one channel instead of three can reduce bandwidth and buffer size, which can help with **minimum latency** when grabbing “newest frame only.”

**Conclusion:** For a **low-latency** capture stage, **monochrome is preferable**: it can be faster (readout, no demosaicing) and allows shorter exposure (better sensitivity), which aligns with the thesis goal of optimising the capture stage.

### 2.2.1 Estimated time saved: monochrome vs RGB

The exact gain depends on the sensor, whether an RGB camera outputs raw Bayer (demosaic on host) or already-demosaiced RGB, and on lighting. A reasonable **ballpark for capture-stage latency reduction** when switching from a comparable RGB camera to monochrome:

| Factor | Effect |
|--------|--------|
| **No demosaicing** | If RGB path does Bayer→RGB (in camera or on host), removing it saves on the order of **~0.5–2 ms** (sensor-dependent; can be more for higher resolution). |
| **Shorter exposure** | Monochrome typically has ~1.3–2× higher sensitivity (no colour filter). For the same scene brightness you can use **~30–50% shorter exposure**; e.g. 2–3 ms saved if RGB needed 4–6 ms. |
| **Readout** | Mono readout can be simpler/faster; often **~0.5–1.5 ms** difference for 1–2 MP. |

**Overall:** A conservative **total estimate is on the order of 1–4 ms** lower capture latency with monochrome vs a comparable RGB setup (same resolution, same scene). The replication of one channel to three (e.g. `COLOR_GRAY2BGR`) adds only microseconds and is negligible. For a motion-to-photon budget of tens of milliseconds, saving 1–4 ms at capture is meaningful; exact numbers can be measured in your setup (e.g. with frame timestamps or the latency experiment in Methodology).

### 2.3 Decision

- **Monochrome is sufficient and can be faster.** Use a **monochrome, global-shutter** industrial camera for the lab/clinic capture stage when minimising latency is the priority.
- **Pipeline change:** In `pose_webcam.py` (or equivalent), when the source is monochrome, convert the single channel to 3-channel before inference, e.g. `cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)`. No other pipeline changes are required.
- **If colour is needed later** (e.g. for other experiments or overlays), you would need an RGB camera; for pose-only, monochrome is the better choice.

---

## 3. Requirements (from thesis and pipeline)

From the thesis and the existing Python pipeline, the camera must satisfy:

| Requirement | Rationale |
|-------------|-----------|
| **Low capture latency** | Target: minimise motion-to-photon; capture is the first stage (see latency pipeline in Related Work). |
| **Global shutter** | Single, well-defined capture instant; no rolling-shutter artefacts on moving subjects. |
| **High frame rate** | ≥60 fps (prefer 90–120+ if available) so the “newest frame” is as fresh as possible. |
| **Large pixels / good sensitivity** | Shorter exposure for given scene brightness → lower latency, less blur. |
| **USB 3.0 (UVC or USB3 Vision)** | Standard host interface; minimal buffering; direct frame access from the host. |
| **Python access to frames** | Must be able to grab frames in the **fastest possible way** from Python (e.g. via vendor SDK or UVC/OpenCV), with **buffer size 1** or equivalent so the app uses the newest frame. |
| **Compatible with pose pipeline** | Resolution sufficient for pose (e.g. 720p–1080p equivalent); monochrome OK (convert to 3-channel before inference). |
| **Lab/clinic use** | Patient standing **3–5 m** in front of the camera; **full body** (or at least lower body + trunk) in frame. |
| **Lens** | C-mount (or as required by camera); focal length and focus chosen so that at **3–5 m** the subject fits and is sharp. |

---

## 4. Concrete camera options (with links)

All links were valid at the time of research; vendor sites may change URLs.

### 4.1 Edmund Optics (IDS Imaging)

- **IDS U3-3060CP-M-GL** — Monochrome, USB 3.0, 1/1.2" Sony IMX174, **global shutter**, **161 fps**, 2.3 MP (1936×1216), C-mount.  
  - **Link (Edmund Optics US):**  
    https://www.edmundoptics.com/p/ids-imaging-u3-3060cp-m-gl-112-monochrome-usb3-camera/43941/  
  - **Link (Edmund Optics EU):**  
    https://www.edmundoptics.de/p/u3-3060cp-112-monochrome-usb3-camera/43941/  
  - **Link (1stVision, alternative):**  
    https://www.1stvision.com/cameras/models/IDS-Imaging/U3-3060CP-M/C  
  - **Python:** IDS provides **PyuEye** (Python bindings for uEye API). You can grab frames and pass them to OpenCV or duplicate to 3-channel for the pose pipeline.  
  - **Note:** Requires C-mount lens (sold separately).

- **IDS U3-3160CP-M-GL** — Monochrome, 2/3", **169 fps**, 2.3 MP, global shutter, USB 3.0.  
  - **Link (Edmund UK):**  
    https://www.edmundoptics.co.uk/p/ids-imaging-u3-3160cp-m-gl-23-monochrome-usb3-camera/49790/

- **IDS U3-3270LE-M-GL** — Monochrome, 1/1.8", USB 3.0, global shutter.  
  - **Link (Edmund UK):**  
    https://www.edmundoptics.co.uk/p/ids-imaging-u3-3270le-m-gl-118-monochrome-usb3-camera/49738/

### 4.2 Teledyne FLIR / Teledyne Vision Solutions (Point Grey)

*Point Grey was acquired by FLIR and is now part of Teledyne FLIR / Teledyne Vision Solutions. The Blackfly S USB3 line is the current successor; Flea3 is legacy.*

- **Blackfly S USB3** — Current USB3 Vision line; multiple **monochrome global-shutter** models. **Python:** FLIR **Spinnaker SDK** supports Python; you can grab frames and integrate with your pipeline (e.g. convert to numpy/OpenCV, then 3-channel for pose).  
  - **Product family:**  
    https://www.teledynevisionsolutions.com/products/blackfly-s-usb3?vertical=machine+vision&segment=iis  

  **Suitable models on Edmund Optics EU (monochrome, global shutter, USB 3):**

  | Model | Resolution | FPS | Sensor | Mount | Price (Edmund EU, excl. VAT) | Link |
  |-------|------------|-----|--------|-------|------------------------------|------|
  | **BFS-U3-16S2M-CS** | 1.6 MP (1440×1080) | 226 | Sony IMX273, 1/2.9" | **CS-mount** | **€371** | [BFS-U3-16S2M-CS](https://www.edmundoptics.eu/p/bfs-u3-16s2m-cs-usb3-blackflyreg-s-monochrome-camera/40163/) |
  | **BFS-U3-04S2M-C** | 0.4 MP (720×540) | 522 | Sony IMX287, 1/2.9", 6.9 µm pixels | C-mount | **€361** | [BFS-U3-04S2M-C](https://www.edmundoptics.eu/p/bfs-u3-04s2m-c-usb-31-blackflyr-s-monochrome-camera/49867/) |

  - **BFS-U3-16S2M-CS** is the **same sensor** (Sony IMX273) as the IDS U3-3040CP-M-GL and **cheaper** (€371 vs €540). It is **CS-mount**; use a **5 mm C/CS spacer** (Edmund #03-618) to attach standard **C-mount** lenses. Tripod adapter for Blackfly S 29×29×30 mm: [#88-210](https://www.edmundoptics.eu/search/?criteria=88-210).  
  - **BFS-U3-04S2M-C** is even cheaper and has **larger pixels** (6.9 µm) and 522 fps, but only **0.4 MP** — likely too low for reliable full-body pose at 3–5 m; use only if you prioritise cost and accept lower resolution.

- **Flea3 USB3** — Legacy (Point Grey); some monochrome global-shutter models. Many models are discontinued or obsoleted; prefer **Blackfly S** for new purchases.  
  - **Link:**  
    https://www.teledynevisionsolutions.com/en-au/products/flea3-usb3/?segment=iis&vertical=machine+vision  

### 4.3 Basler (alternative)

- **Basler** offers USB3 monochrome global-shutter cameras with **pypylon** (official Python API) for direct frame capture.  
  - **pypylon:**  
    https://www.baslerweb.com/en-us/software/pylon/pypylon/  
  - You can search their product finder for “USB3, monochrome, global shutter, 60+ fps” and match sensor size to your lens.

---

## 5. Lenses and focus for 3–5 m (lab/clinic)

### 5.1 Working distance 3–5 m

- **3–5 m** is a reasonable and common choice for a lab/clinic: enough space for the patient to stand and move (e.g. single-leg balance), while the camera sees full body without being too far. So **3–5 m is a good assumption** for focus and FOV.

### 5.2 Field of view (full body at 3–5 m)

- Assume subject height **~1.8 m**; we need the full body (or at least from hip down + trunk) in frame.
- **Vertical FOV:** At distance \(d\), to see height \(H\): half-angle \(\theta = \arctan((H/2)/d)\). For \(H=1.8\) m:  
  - \(d=3\) m → \(\theta \approx 16.7°\) → vertical FOV ≈ **33°**  
  - \(d=5\) m → \(\theta \approx 10.2°\) → vertical FOV ≈ **20°**  
- So we need **at least ~20–35° vertical FOV** (depending on distance and how much margin you want). A typical choice is to design for **~25–40° vertical** so both 3 m and 5 m are usable.

### 5.3 Focal length vs sensor

- For a **1/1.2"** sensor (e.g. IDS U3-3060CP-M-GL), vertical size is ~8.8 mm.  
  - FOV (deg) ≈ \(2 \arctan(\frac{\text{sensor\_size}/2}{f})\).  
  - For 30° vertical: \(f \approx 8.8/(2 \tan(15°)) \approx 16.4\) mm.  
  - For 40° vertical: \(f \approx 8.8/(2 \tan(20°)) \approx 12\) mm.  
- So for **full body at 3–5 m** with a 1/1.2" sensor, **roughly 8–16 mm** focal length is in the right range; **8–12 mm** gives a good compromise (wider FOV at 3 m, still adequate at 5 m).

### 5.4 Lens links (C-mount, suitable for 3–5 m)

- **Edmund Optics – C-mount fixed focal length:**  
  - **6 mm** (very wide; good for 3 m, plenty of margin at 5 m):  
    https://www.edmundoptics.com/p/6mm-focal-length-lens-1-sensor-format/41743/  
  - **8 mm** (good middle ground for 3–5 m):  
    https://www.edmundoptics.com/p/8mm-focal-length-lens-1quot-sensor-format/17859/  
  - **C Series fixed focal length (various FL):**  
    https://www.edmundoptics.com/f/c-series-fixed-focal-length-lenses/13679  
  - **Note:** Check “sensor format” or “image circle” for each lens so it covers your sensor (e.g. 1/1.2" or 1").

- **Kowa (example):**  
  - **6 mm, 1/1.8" C-mount:**  
    https://www.kowa-lenses.com/LM6NCL-1-1-8-6mm-C-Mount-wide-angle-lens/10098  

- **VA Imaging (lens calculator useful for FOV):**  
  - **Lens calculator (FOV vs focal length and sensor):**  
    https://va-imaging.com/en-us/collections/lens-calculator  
  - **12 mm C-mount example:**  
    https://va-imaging.com/products/va-lcm-6mp-12mm-f1-8-018-ic-lens-c-mount-6mp-12mm-f1-8-1-1-8-inch-non-distortion  

### 5.5 Recommended focus

- **Set focus for the main working distance.** A practical choice is **4 m** (centre of 3–5 m). With a typical machine-vision lens (e.g. f/2 or f/1.4), depth of field at 4 m will usually cover 3–5 m with acceptable sharpness. If the lens has a focus ring, set it once at 4 m and fix the camera position for the protocol.

---

## 6. Python integration (fastest frame access)

- **IDS (Edmund):** Use **PyuEye** or IDS Software Suite Python API; allocate a single buffer or use “newest only” mode if supported; in the loop: grab → get image array → convert to 3-channel if monochrome → feed to pose.  
- **FLIR (Spinnaker):** Use Spinnaker Python bindings; configure for **continuous grab**, **one buffer** or “latest only”; convert each frame to numpy (and to 3-channel) for your pipeline.  
- **Basler (pypylon):** Same idea: minimal buffer count, grab latest, convert to 3-channel for pose.  
- **UVC webcams (current):** `cv2.VideoCapture` with `CAP_PROP_BUFFERSIZE = 1` already gives “newest frame” behaviour; industrial cameras should be configured analogously (single or minimal buffer, read only when a new frame is needed).

---

## 7. Summary

- **PDF:** Rebuild with `.\build.ps1` in `thesis/` to get the latest PDF; methodology figure fix is in place.
- **RGB vs monochrome:** **Monochrome is enough** (replicate to 3 channels for pose) and **can be faster** (readout, sensitivity, shorter exposure). Prefer **monochrome + global shutter** for the capture stage.
- **Requirements:** Low latency, global shutter, ≥60 fps, USB 3, Python access with minimal buffering, 3–5 m full-body FOV.
- **Cameras:** IDS U3-3060CP-M-GL (Edmund), Blackfly S USB3 mono (Teledyne), and similar IDS/FLIR/Basler models with the above specs.
- **Lenses:** C-mount, **8–12 mm** (or 6 mm for wider FOV) for 3–5 m full body on 1/1.2" or similar sensor; **focus at ~4 m** as a default.
- **Pipeline:** Keep `pose_webcam.py` compatible by converting monochrome frames to 3-channel (e.g. `cv2.cvtColor(..., cv2.COLOR_GRAY2BGR)`) before inference.

---

## 8. Full setup: camera + lens + cable + mount (Edmund Optics)

Recommended setup that stays within the **~600 EUR camera** budget and includes lens, cable, and mount. All prices below are **excl. VAT**; add your local VAT for final cost.

### 8.1 Recommended setup (within budget)

| Item | Description | Price (excl. VAT) | Link (Edmund Optics EU) |
|------|-------------|-------------------|--------------------------|
| **Camera** | IDS U3-3040CP-M-GL — 1/2.9" monochrome, **251 fps**, global shutter, USB 3.0, C-mount | **€540** | [IDS U3-3040CP-M-GL](https://www.edmundoptics.eu/p/u3-3040cp-13-monochrome-usb3-camera/43937/) |
| **Lens** | 8mm UC Series Fixed Focal Length, 1/2" format, C-mount, f/1.8–f/11, suitable for 3–5 m full body (#33-307) | **€260** | [8mm UC Series Lens](https://www.edmundoptics.eu/p/8mm-uc-series-fixed-focal-length-lens/41864/) |
| **Mount** | ¼-20 tripod adapter for IDS uEye+ CP/XCP/SE cameras (#35-088) | **€45** | [¼-20 Mounting Adapter for IDS](https://www.edmundoptics.eu/search/?criteria=35-088) |
| **Cable** | Type-A to Micro-B, USB 3.1 locking cable, 3 m (#86-770) | **€25** | [USB 3.1 Locking Cable 3 m](https://www.edmundoptics.eu/search/?criteria=86-770) |
| **Total** | | **~€870** | |

- **Why this camera:** Fits the **600 EUR camera budget**; 251 fps (excellent for latency), global shutter, monochrome, USB3 Vision. Sensor 1/2.9" is smaller than the lens’s 1/2" max format, so the 8 mm UC lens is compatible and gives a wide FOV for full body at 3–5 m.

- **Why 1/2.9" and is it too small?** The 1/2.9" choice was **budget-driven**: on Edmund Optics (USB 3, C-mount, monochrome, global shutter), the U3-3040CP-M-GL was the only model that stayed at or under ~600 EUR; the larger-sensor option (1/1.2", U3-3060CP-M-GL) is ~€970. A **larger sensor** (e.g. 1/1.2") would be preferable for the thesis goals: larger pixels (5.86 µm vs 3.45 µm) mean better sensitivity and shorter exposure for a given light level, hence lower capture latency and less motion blur. That said, **1/2.9" is not too small for the application**: (1) Pose models typically use modest input resolution (e.g. 256×256 or 384×384); 1.58 MP (1448×1086) is sufficient for keypoint detection at 3–5 m. (2) You still get 251 fps and global shutter. The trade-off is that in dimmer conditions you may need slightly longer exposure than with a 1/1.2" camera. If budget or educational discount allows, the 1/1.2" setup (section 8.2) is the better choice for minimal capture latency; otherwise the 1/2.9" setup is a valid, cost-effective option.
- **Optional:** If you need a filter (e.g. M43) on the 8 mm UC, Edmund lists adapter [#89-940](https://www.edmundoptics.eu/p/filter-adapter-m43-x-075-from-m34-x-05-female/32375/); not required for basic operation.
- **Educational discount:** Edmund Optics has an [Educational Discount Program](https://www.edmundoptics.eu/promotions/your-university-partner/). Ask for a quote through your institution to reduce the total.

### 8.2 Alternative: higher-end camera (if budget allows)

If the supervisor approves a higher total and you want a **larger sensor** (1/1.2") and **larger pixels** (5.86 µm) for even lower capture latency and better low-light behaviour:

| Item | Description | Price (excl. VAT) | Link |
|------|-------------|-------------------|------|
| **Camera** | IDS U3-3060CP-M-GL — 1/1.2" monochrome, **161 fps**, global shutter, 2.3 MP, C-mount | ~£828 (UK) / ~€970 (check Edmund EU) | [Edmund UK: U3-3060CP-M-GL](https://www.edmundoptics.co.uk/p/ids-imaging-u3-3060cp-m-gl-112-monochrome-usb3-camera/43941/) |
| **Lens** | 8 mm, 1" sensor format (#63-243) — covers 1/1.2" sensor; 79.7° HFOV | £710 (UK) | [Edmund UK: 8 mm 1" lens](https://www.edmundoptics.co.uk/p/8mm-focal-length-lens-1-sensor-format/17859/) |
| **Mount** | Same as above (#35-088) | €45 | Same as above |
| **Cable** | Same as above (#86-770) | €25 | Same as above |

Total for this alternative is **~€1,750+** (excl. VAT). Prefer the **recommended setup (8.1)** unless you specifically need the larger sensor and have budget/approval.

### 8.3 FLIR Blackfly S alternative (Point Grey / supervisor-recommended brand)

If you prefer **FLIR (Point Grey)** as recommended by your supervisor, the following setup is **equivalent in specs** to the IDS setup (8.1) and **cheaper** (same Sony IMX273 1/2.9" sensor, 226 fps, global shutter, monochrome). The only extra is a **C/CS 5 mm spacer** because this model is CS-mount.

| Item | Description | Price (excl. VAT) | Link (Edmund EU) |
|------|-------------|-------------------|------------------|
| **Camera** | FLIR BFS-U3-16S2M-CS — 1.6 MP (1440×1080), **226 fps**, global shutter, monochrome, **CS-mount** | **€371** | [BFS-U3-16S2M-CS](https://www.edmundoptics.eu/p/bfs-u3-16s2m-cs-usb3-blackflyreg-s-monochrome-camera/40163/) |
| **C/CS spacer** | 5 mm spacer to use C-mount lenses on CS-mount camera (#03-618) | (check Edmund) | [Search 03-618](https://www.edmundoptics.eu/search/?criteria=03-618) |
| **Lens** | Same 8 mm UC Series (#33-307), 1/2" format, C-mount | **€260** | [8 mm UC](https://www.edmundoptics.eu/p/8mm-uc-series-fixed-focal-length-lens/41864/) |
| **Mount** | ¼-20 tripod adapter for Blackfly S 29×29×30 mm (#88-210) | (check Edmund) | [88-210](https://www.edmundoptics.eu/search/?criteria=88-210) |
| **Cable** | Same USB 3.1 Type-A to Micro-B, 3 m (#86-770) | **€25** | [Cable](https://www.edmundoptics.eu/search/?criteria=86-770) |

**Total (camera + lens + cable; spacer and mount TBD):** ~**€656** + spacer + mount — **noticeably cheaper** than the IDS setup (~€870). Software: **Spinnaker SDK** (Python supported); pipeline change: same as for IDS (monochrome → replicate to 3 channels before pose).

### 8.4 Why IDS was chosen in this doc (and when to pick FLIR instead)

- **Why IDS appeared as the “recommended” option:** The initial search on Edmund Optics was filtered for **USB 3, C-mount, monochrome** (and budget ~600 EUR for the camera). The **IDS U3-3040CP-M-GL** came up as a **native C-mount** camera with 1.58 MP and 251 fps, so it was documented first and used for the full setup (lens, cable, mount) without needing a C/CS spacer. So the choice was partly **discovery order** and **simplicity** (C-mount native).
- **FLIR (Point Grey) is fully suitable and supervisor-recommended.** The **BFS-U3-16S2M-CS** uses the **same sensor** (Sony IMX273) as the IDS, at **lower price** (€371 vs €540). You only need to add a **5 mm C/CS spacer** to use standard C-mount lenses. If your supervisor prefers FLIR/Point Grey, the **FLIR setup (8.3)** is a better fit: same image quality and frame rate, cheaper, and Spinnaker SDK is well supported.
- **Summary:** Both **IDS** and **FLIR (Point Grey) Blackfly S** are suitable. Choose **FLIR** for supervisor preference and lower cost; choose **IDS** if you want native C-mount and the exact part numbers already listed in 8.1.

---

## 9. Price vs time saved, and rough motion-to-photon estimate

### 9.1 Cost per millisecond saved (capture stage)

Comparison is on **capture-stage latency** only (exposure + readout + transfer; buffer = 1). Inference, Unity, and display are the same across options. All monetary values excl. VAT.

| Setup | Total cost (camera + lens + cable + mount) | Est. capture latency | vs webcam: time saved | Extra cost vs previous | Cost per ms saved (vs previous) |
|-------|------------------------------------------|---------------------|------------------------|------------------------|----------------------------------|
| **Webcam (baseline)** | €0 (already owned) | ~20–35 ms | — | — | — |
| **1/2.9" industrial** (U3-3040CP-M-GL + 8 mm UC + mount + cable) | **~€870** | ~5–8 ms | **~12–27 ms** | €870 vs webcam | **~€32–72 / ms** (€870 ÷ 12–27 ms) |
| **1/1.2" industrial** (U3-3060CP-M-GL + 1" 8 mm + mount + cable) | **~€1,750** | ~3–6 ms | **~14–32 ms** vs webcam; **~1–3 ms** vs 1/2.9" | ~€880 vs 1/2.9" | **~€290–880 / ms** (€880 ÷ 1–3 ms) |

**Interpretation:**

- **Webcam → 1/2.9" industrial:** You pay **~€870** and save on the order of **12–27 ms** at capture. That is **~€32–72 per millisecond saved** (using the midpoint, about **€50/ms**). This is the most cost-effective step: you get global shutter, 251 fps, monochrome, and a large capture improvement.
- **1/2.9" → 1/1.2" (larger sensor):** You pay **~€880 extra** and save only **about 1–3 ms** at capture. So **~€290–880 per additional millisecond**. Diminishing returns: only worth it if budget allows and every millisecond is critical.

Capture estimates are conservative; actual values depend on lighting, driver buffer behaviour (webcam), and USB host. You can measure capture-to-pose with `--log-latency` and compare webcam vs industrial in your environment.

### 9.2 Rough motion-to-photon latency (current camera option + app + Unity)

Pipeline: **capture → pose inference (Python) → UDP → Unity (parse, avatar, render) → display.**  
Assumptions: **recommended 1/2.9" industrial camera** (section 8.1), **current app config** (lightweight rtmlib, 640×480, `det_frequency` 10, CUDA, buffer 1, no smoothing), **Unity Architect** (parse JSON, drive avatar, render one frame).

| Stage | Low estimate | Mid (typical) | High estimate | Notes |
|-------|--------------|---------------|---------------|--------|
| **Capture** | 5 ms | 6–7 ms | 8 ms | Exposure ~2–4 ms, readout ~2–3 ms, USB ~0.5–1 ms (251 fps, mono, global shutter). |
| **Pose inference** | 5 ms | 8–10 ms | 12 ms | Lightweight rtmlib, 192×256 pose input; GPU-dependent (7–10 ms on high-end GPU per thesis; mid-range GPU ~8–10 ms). |
| **UDP (Python → Unity)** | 0.2 ms | 0.5 ms | 1 ms | Localhost; negligible. |
| **Unity (parse + avatar + 1 frame)** | 2 ms | 3–4 ms | 5 ms | Simple scene; one frame render. |
| **Display (next refresh)** | 0 ms | ~8 ms | 16.7 ms | At 60 Hz, up to 16.7 ms; often taken as half-frame average ~8 ms. |
| **Total (motion-to-photon)** | **~12 ms** | **~26–30 ms** | **~42 ms** | |

**Point estimate:** **~26–30 ms** end-to-end with the 1/2.9" camera and current app + Unity. That is **below the 63 ms cybersickness threshold** and **below 50 ms** “ideal” range cited in the thesis, with margin.

**If you keep a webcam** (no industrial camera): capture ~20–35 ms → total motion-to-photon roughly **~40–60 ms** (still under 63 ms in typical conditions, but closer to the threshold and more variable).

**If you upgrade to 1/1.2"** (section 8.2): capture ~3–6 ms → total **~24–28 ms** (about 2–3 ms lower than 1/2.9" end-to-end).

These are **rough estimates** for planning and discussion with your supervisor. The methodology (e.g. 240 fps video or frame-indicator method) should be used to **measure** actual motion-to-photon latency in your setup.
