# Email draft: Camera setup summary for supervisor

---

**Subject:** Camera setup for thesis – FLIR Blackfly S and full parts list

---

Hi [Supervisor name],

I am getting back to you after our discussion on Monday. Here is research and a summary that I have done (with AI assistance) on the camera setup for the thesis.

---

**Choice: FLIR (Point Grey) Blackfly S**

I'll most likely stick with **FLIR**, as you recommended. The specific model is the **Teledyne FLIR Blackfly S BFS-U3-16S2M-CS**: monochrome, USB 3.1, global shutter, 1.6 MP (1440×1080), 226 fps, Sony IMX273 1/2.9" sensor. It fits the thesis requirements (low capture latency, high frame rate, USB3 Vision) and is available from Edmund Optics EU at a lower price than the equivalent IDS option.

**Why this camera and these parameters**

- **Full body at 3–5 m:** The use case is lab/clinic: patient standing 3–5 m in front of the camera with full body (or at least lower body + trunk) in frame. The lens (8 mm, 1/2" format) is chosen to give enough field of view for that distance.
- **Sensor size (1/2.9"):** Keeps the setup within the ~600 EUR camera budget while still giving enough resolution for pose. The camera's 1440×1080 output is more than enough for our pipeline: we currently use **640×480 capture** and **lightweight RTMPose** with **detector input 416×416** and **pose input 192×256**, so 1.6 MP is sufficient. Larger sensors (e.g. 1/1.2") would save another ~1–3 ms at capture but cost roughly €880 extra (diminishing returns).
- **Monochrome:** For lowest capture latency we prefer monochrome: no Bayer demosaicing (faster readout), higher sensitivity so we can use shorter exposure. Estimated **~1–4 ms** lower capture latency vs a comparable RGB camera. The pipeline already supports mono (replicate to 3 channels before pose inference); no retraining needed.
- **Time saved vs webcam:** Switching from a webcam to this industrial setup saves on the order of **~12–27 ms** at the capture stage (exposure + readout + transfer), which helps keep motion-to-photon below the 63 ms cybersickness threshold. With the current app and Unity, a rough end-to-end estimate is **~26–30 ms** motion-to-photon.

**Full setup (all from Edmund Optics EU, excl. VAT)**

| Item | Description | Price (excl. VAT) | Link |
|------|-------------|-------------------|------|
| **Camera** | FLIR BFS-U3-16S2M-CS — 1.6 MP, 226 fps, global shutter, monochrome, CS-mount | €371 | https://www.edmundoptics.eu/p/bfs-u3-16s2m-cs-usb3-blackflyreg-s-monochrome-camera/40163/ |
| **C/CS spacer** | 5 mm spacer to use C-mount lenses on this CS-mount camera (part #03-618) | €29 | https://www.edmundoptics.eu/search/?criteria=03-618 |
| **Lens** | 8 mm UC Series Fixed Focal Length, 1/2" format, C-mount (#33-307) — for 3–5 m full body | €260 | https://www.edmundoptics.eu/p/8mm-uc-series-fixed-focal-length-lens/41864/ |
| **Mount** | ¼-20 tripod adapter for Blackfly S 29×29×30 mm (#88-210) | €12 | https://www.edmundoptics.eu/search/?criteria=88-210 |
| **Cable** | USB 3.1 Type-A to Micro-B locking cable, 3 m (#86-770) | €25 | https://www.edmundoptics.eu/search/?criteria=86-770 |

**Total:** ~€697 (all items above). The camera is **USB bus powered** (no separate power supply needed). Edmund Optics also has an [Educational Discount Programme](https://www.edmundoptics.eu/promotions/your-university-partner/) — I can request a quote through the university if that would help.

**Software and compatibility (already set up)**

I have already installed the FLIR **Spinnaker SDK 4.3** and the Python bindings (**PySpin**) in a dedicated Python 3.10 environment with all dependencies verified (NumPy 1.26, OpenCV, rtmlib, onnxruntime). The environment is ready to integrate with the existing pose pipeline (monochrome → replicate to 3 channels → RTMPose, single-buffer / "newest only" grab for minimal latency). Once the camera arrives, I can start capturing frames immediately.

If you'd like any changes to this setup or more detail on any part, I'm happy to adjust.

Does the setup like this make sense?

Best regards,  
[Your name]

---

## Plain-text version (for simple email clients)

Copy the block below into your school email.

-------- BEGIN PLAIN-TEXT EMAIL (copy from here) --------

Subject: Camera setup for thesis – FLIR Blackfly S and full parts list

Hi [Supervisor name],

I am getting back to you after our discussion on Monday. Here is research and a summary that I have done (with AI assistance) on the camera setup for the thesis.

Choice: FLIR (Point Grey) Blackfly S

I will most likely stick with FLIR, as you recommended. The specific model is the Teledyne FLIR Blackfly S BFS-U3-16S2M-CS: monochrome, USB 3.1, global shutter, 1.6 MP (1440x1080), 226 fps, Sony IMX273 1/2.9" sensor. It fits the thesis requirements (low capture latency, high frame rate, USB3 Vision) and is available from Edmund Optics EU at a lower price than the equivalent IDS option.

Why this camera and these parameters:

- Full body at 3-5 m: The use case is lab/clinic: patient standing 3-5 m in front of the camera with full body (or at least lower body and trunk) in frame. The lens (8 mm, 1/2" format) is chosen to give enough field of view for that distance.

- Sensor size (1/2.9"): Keeps the setup within the ~600 EUR camera budget while still giving enough resolution for pose. The camera's 1440x1080 output is more than enough for our pipeline: we currently use 640x480 capture and lightweight RTMPose with detector input 416x416 and pose input 192x256, so 1.6 MP is sufficient. Larger sensors (e.g. 1/1.2") would save another ~1-3 ms at capture but cost roughly 880 EUR extra (diminishing returns).

- Monochrome: For lowest capture latency we prefer monochrome: no Bayer demosaicing (faster readout), higher sensitivity so we can use shorter exposure. Estimated ~1-4 ms lower capture latency vs a comparable RGB camera. The pipeline already supports mono (replicate to 3 channels before pose inference); no retraining needed.

- Time saved vs webcam: Switching from a webcam to this industrial setup saves on the order of ~12-27 ms at the capture stage, which helps keep motion-to-photon below the 63 ms cybersickness threshold. With the current app and Unity, a rough end-to-end estimate is ~26-30 ms motion-to-photon.

Full setup (all from Edmund Optics EU, excl. VAT):

  Camera - FLIR BFS-U3-16S2M-CS, 1.6 MP, 226 fps, global shutter, monochrome, CS-mount - 371 EUR
  https://www.edmundoptics.eu/p/bfs-u3-16s2m-cs-usb3-blackflyreg-s-monochrome-camera/40163/

  C/CS spacer - 5 mm spacer for C-mount lenses on CS-mount camera (#03-618) - 29 EUR
  https://www.edmundoptics.eu/search/?criteria=03-618

  Lens - 8 mm UC Series Fixed Focal Length, 1/2" format, C-mount (#33-307), for 3-5 m full body - 260 EUR
  https://www.edmundoptics.eu/p/8mm-uc-series-fixed-focal-length-lens/41864/

  Mount - 1/4-20 tripod adapter for Blackfly S 29x29x30 mm (#88-210) - 12 EUR
  https://www.edmundoptics.eu/search/?criteria=88-210

  Cable - USB 3.1 Type-A to Micro-B locking cable, 3 m (#86-770) - 25 EUR
  https://www.edmundoptics.eu/search/?criteria=86-770

Total: ~697 EUR. The camera is USB bus powered (no separate power supply needed). Edmund Optics also has an Educational Discount Programme - I can request a quote through the university:
https://www.edmundoptics.eu/promotions/your-university-partner/

Software and compatibility (already set up):
I have already installed the FLIR Spinnaker SDK 4.3 and the Python bindings (PySpin) in a dedicated Python 3.10 environment with all dependencies verified (NumPy 1.26, OpenCV, rtmlib, onnxruntime). The environment is ready to integrate with the existing pose pipeline (monochrome to 3 channels, then RTMPose, single-buffer / "newest only" grab for minimal latency). Once the camera arrives, I can start capturing frames immediately.

If you would like any changes to this setup or more detail on any part, I am happy to adjust.

Does the setup like this make sense?

Best regards,
[Your name]

-------- END PLAIN-TEXT EMAIL --------
