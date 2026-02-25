# Bibliography import for Citavi

## Source: Literature search document

References were extracted from **VR Knee Rehab Motion Tracking Literature Search.docx** (10 main papers + works cited). Use **`from_literature_search.bib`** for a BibTeX file containing only those 10 articles with DOIs where available.

---

## Is the literature search document enough for the theoretical part?

**Yes, as a base.** A focused “VR Knee Rehab Motion Tracking” literature search is a good foundation for your Related Work chapter. For a strong theoretical part you should:

- **Use it as the core** for VR rehab, motion tracking, and gamification.
- **Synthesize and critique** (compare methods, limitations, gaps), not only summarize.
- **Add a few recent papers** (2023–2025) so the state of the art is up to date.
- **Tie everything to your gap**: low-latency ML tracking for gamified knee rehab in VR.

The PDF is binary in the repo, so references could not be extracted from it. Use the files below to build your Citavi project.

---

## Bulk import (recommended)

1. In **Citavi**: **File → Import → BibTeX file**.
2. Select: **`citavi_literature_import.bib`**.
3. Map fields if asked (Citavi usually does this automatically).
4. Duplicates with your existing project (e.g. MediaPipe, RTMPose) can be merged or skipped.

---

## One-by-one import by DOI

1. In **Citavi**: **References → Add → Add Reference by Identifier** (or “Add by DOI”).
2. Paste one DOI from **`DOI_list_for_Citavi.txt`** (lines without `#`).
3. Citavi will fetch metadata; confirm and add.
4. Repeat for each DOI you need.

---

## Your main bibliography file

Your thesis uses **`bibliography.bib`**. Keep that as the main .bib for LaTeX. After importing into Citavi you can:

- Add new references in Citavi and **export** (or sync) to `bibliography.bib`, or  
- Maintain `bibliography.bib` and re-import into Citavi when needed.

Citavi 7 can use the same .bib as LaTeX; check **Citavi → Project properties → Word / LaTeX** for export path to `references/bibliography.bib`.
