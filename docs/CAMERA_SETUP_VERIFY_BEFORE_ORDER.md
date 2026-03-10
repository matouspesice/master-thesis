# Verify before sending camera proposal (and before ordering)

Run through this **before** you send the email to your supervisor, so you can either confirm the setup or adjust it.

---

## Python and SDK compatibility – test results

*Ran: Python/NumPy/PySpin check on this machine.*

| Item | Result |
|------|--------|
| **Default Python** | 3.14.2 (`python` / `py -3`) |
| **Other Python** | 3.11 available via `py -3.11` |
| **NumPy (default env)** | 2.2.6 |
| **PySpin** | Not installed (`ModuleNotFoundError: No module named 'PySpin'`) |
| **Pose app deps (rtmlib, OpenCV)** | OK on Python 3.14 |

**Conclusion:** Spinnaker PySpin officially supports **Python up to 3.10** on Windows and typically requires **NumPy 1.x** (not 2.x). Your default environment is **Python 3.14 + NumPy 2.2**, which PySpin does not support. You do **not** have Python 3.10 installed (`py -0p` shows only 3.14 and 3.11).

**Recommendation before ordering the camera:**

1. **Install Python 3.10** (e.g. from [python.org](https://www.python.org/downloads/) or Windows Store) so that `py -3.10` works.
2. **Create a dedicated venv for the FLIR camera workflow**, e.g.:
   - `py -3.10 -m venv .venv_flir`
   - Activate it and install: `pip install numpy==1.26.* opencv-python rtmlib onnxruntime` (and other deps from `app/requirements.txt`).
   - After the camera arrives: install the Spinnaker SDK, then `pip install <path-to-Spinnaker>/python/dist/PySpin-*.whl` in that venv.
3. When using the **FLIR camera**, run the pose app from this venv (`py -3.10` + venv). When using a **webcam**, you can keep using your default Python 3.14.

Alternatively, after the camera arrives you can try the **latest Spinnaker** installer and see if it provides a PySpin wheel for **Python 3.11** (your other installed version); if yes, you could use a 3.11 venv instead of installing 3.10.

---

## 1. Python and SDK compatibility

**Goal:** Ensure your environment can run both the current pose app (rtmlib) and FLIR Spinnaker PySpin.

| Check | How |
|-------|-----|
| **Python version** | Run `python --version` (or `py -3 --version` on Windows). Spinnaker PySpin officially supports **Python up to 3.10** on Windows. If you have 3.11 or 3.12, you may need a separate virtual environment with Python 3.10 for the camera integration, or check [Spinnaker release notes](https://www.flir.com/support-center/iis/machine-vision/downloads/spinnaker-sdk-flycapture-and-firmware-download/) for newer PySpin builds. |
| **NumPy** | PySpin has strict NumPy requirements (e.g. NumPy 1.23 with Python 3.10; often not compatible with NumPy 2.x). Run `pip show numpy` and note the version. After installing Spinnaker, install the PySpin `.whl` from the SDK’s `python/dist` folder; use a venv if you need to pin NumPy. |
| **Pose app** | Your app works with `python pose_webcam.py` and `requirements.txt` (rtmlib, opencv, onnxruntime). MMPose (optional) needs Python 3.10 or 3.11 per README. So **Python 3.10** is a safe choice for both pose and PySpin. |

**Action:** If you are already on 3.11/3.12, either (a) plan a dedicated venv with Python 3.10 for the camera + pose pipeline, or (b) download the latest Spinnaker SDK and check the release notes for supported Python versions, then note in the email that you’ve confirmed compatibility.

---

## 2. Capture path (Spinnaker → pipeline)

**Goal:** No extra latency from buffering or format conversion.

| Check | How |
|-------|-----|
| **Buffer** | In Spinnaker, set the number of buffers to the minimum (e.g. 1) and use “newest only” or equivalent so each grab returns the latest frame. Avoid multi-frame queues. |
| **Format** | Camera outputs monochrome. You need to convert to the format your pipeline expects (numpy array, then `cv2.cvtColor(..., cv2.COLOR_GRAY2BGR)` before pose). No heavy processing in between. |
| **Where to implement** | Plan a small wrapper: Spinnaker grab → numpy (mono) → BGR → same path as current `pose_webcam.py` (e.g. replace `cap.read()` with this when the FLIR is selected). |

**Action:** You can’t test Spinnaker without the camera. Before ordering, just **document** in the email that you will use single-buffer / newest-only and mono→BGR with minimal processing. After delivery, implement and measure with `--log-latency`.

---

## 3. Driver / USB

**Goal:** No conflicts; pose app and Unity run on the same machine with the camera connected.

| Check | How |
|-------|-----|
| **Port** | Camera is USB 3.1 (Micro-B on camera side). Your PC has USB4 (Type-C) and USB 3.2 (Type-A). Either works; the camera only needs 5 Gbps. Use a **Type-A to Micro-B** cable (as in the list) on a Type-A port, or a **USB-C to Micro-B** cable if you want to plug into the USB4/Type-C port (see cable note below). |
| **Driver** | After installing Spinnaker, the SDK installs/uses the FLIR USB driver. Ensure no other application exclusively holds the camera (e.g. another FLIR tool or a generic UVC app). Your pose app will use Spinnaker only. |
| **Unity** | Unity and the Python pose app run on the same machine; camera is only used by Python. No conflict expected. |

**Action:** Note in the email that you’ll use a dedicated USB port and the official Spinnaker driver. If you have other USB3 vision devices, mention testing with the camera connected alone first.

---

## 4. Power and cable (for the email)

**Power:** The FLIR Blackfly S BFS-U3-16S2M-CS is **USB bus powered** (5 V via USB, ~3 W). **No separate power supply or power cable** — the USB cable provides both power and data. Nothing else to order for power.

**Cable (Type-A vs USB-C):**  
The **camera** has a **Micro-B** socket (fixed). So you need a cable with **Micro-B at the camera end**. The **PC end** can be:

- **Type-A:** Use the listed **Type-A to Micro-B** USB 3.1 locking cable (3 m). Plugs into your USB 3.2 Type-A port. Fully sufficient (camera is USB 3.1, 5 Gbps).
- **USB-C:** If you prefer to use your **USB4 / Type-C** port: use a **USB-C to Micro-B** USB 3.1 (or 3.2) cable. Edmund Optics does not list a USB-C–to–Micro-B locking cable; you can (1) ask Edmund if they have one, or (2) use a **quality third-party** USB 3.1/3.2 **USB-C to Micro-B** cable (e.g. 3 m, with locking or good strain relief). Data rate and power will be the same; USB-C is mainly convenience and using the modern port.

So: **either cable type is fine.** If you want to plug into USB-C, get a USB-C–to–Micro-B cable (and optionally mention in the email that you’ll use the USB4 port with a USB-C–to–Micro-B cable if you already have or will order one).

---

## 5. What to say in the email

- **Power:** “The camera is USB bus powered (no separate power cable); the USB cable provides power and data.”
- **Compatibility:** Either “I have confirmed Python 3.10 and will use a dedicated env for Spinnaker” or “I will verify Python/NumPy against the Spinnaker release notes before integration and use a separate venv if needed.”
- **Capture path:** “I will use single-buffer / newest-only grab and convert mono to BGR with minimal processing to avoid added latency.”
- **Cable:** “I’ll use the listed Type-A to Micro-B 3 m cable (or a USB-C to Micro-B cable to connect to my USB4 port).”

After you run through sections 1–3, you can send the proposal with these points included or adjusted.
