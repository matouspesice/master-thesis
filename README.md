# Master Thesis Project

**Development of a Low-Latency ML-Based Motion Tracking System for Gamified Knee Rehabilitation in Virtual Reality**  
MCI Health Tech — MA I · Matouš Pešice (52006687)

---

## Structure

| Folder        | Purpose |
|---------------|--------|
| **thesis/**   | LaTeX source: `main.tex`, `chapters/`. Build PDF from here (e.g. LaTeX Workshop in Cursor). |
| **references/** | Citavi BibTeX export → `bibliography.bib`. All citations in the thesis use this file. |
| **app/**      | VR/ML source code (Unity, Python, C++). |
| **data/**     | Pilot study data (CSV, logs). |

- **.cursorrules** — Instructions for the AI when helping with thesis vs code (tone, citations, latency focus).

## Workflow

1. **Citavi → LaTeX:** In Citavi, export to BibTeX and save into `references/bibliography.bib` (overwrite).  
2. **Build thesis:** Open `thesis/main.tex` and use “Build” (LaTeX Workshop) to generate the PDF. After updating `references/bibliography.bib`, run a full build so the PDF shows updated references.  
3. **Code ↔ thesis:** Use Cursor to generate LaTeX/TikZ from code in `app/` and to keep names/constants consistent.

## Tools

- **Cursor** — Editing, LaTeX, code; AI help for structure and technical description.  
- **Citavi** — Literature; export `.bib` into `references/`.  
- **Git** — Commit thesis and code regularly (e.g. GitHub/GitLab).  
- **Mathpix Snip** — Formula screenshots → LaTeX.  
- **TikZ / Mermaid** — Diagrams for methodology and architecture.
