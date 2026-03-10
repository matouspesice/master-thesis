# Master thesis and app plan — submission May 31

**Scope:** Thesis *Development of a Low-Latency ML-Based Motion Tracking System for Gamified Knee Rehabilitation in VR* (MCI Health Tech), Python pose app (app/), Unity Architect games (architect/), and pilot study.  
**Deadline:** Submit thesis by **31 May 2025**.  
**Start:** 3 March 2025.  
**Approach:** Define goals and milestones, weekly review and rescheduling, and Plan B for critical milestones (ethics, latency work, dependencies, waiting times).

---

## Goals

1. **Thesis:** Submit a complete, coherent thesis (all chapters filled, citations, appendices, abstract). Stay under **15,000 words** (body text; seminar maximum).
2. **App/system:** Add and document **latency measurement** (end-to-end or motion-to-display) so Implementation and Evaluation can report it.
3. **Pilot study:** Run a small pilot (system feel, engagement) and write up in Evaluation.
4. **Meetings:** Use **half-time** and **final** meeting dates as fixed milestones; schedule work so drafts and results are ready in time.

---

## Timeline overview (~13 weeks from 3 Mar 2025)

| Phase | Focus | Dates |
| ----- | ----- | ----- |
| **A** | Ethics + latency measurement | 3 Mar – 23 Mar |
| **B** | Thesis writing (Intro, Methodology, Implementation) + app doc | 10 Mar – 13 Apr |
| **C** | Pilot (run + analyze) | After ethics; aim 31 Mar – 27 Apr |
| **D** | Evaluation chapter + Discussion + Conclusion + polish | 21 Apr – 25 May |
| **E** | Final meeting, submission | 19 May – 31 May |

Your **half-time meeting** should fall around the end of Phase B / start of C (technical + methodology solid; pilot ready or started). Your **final meeting** should fall in Phase E (full draft, results in).

**Week calendar (from 3 Mar 2025):** W1 3–9 Mar · W2 10–16 Mar · W3 17–23 Mar · W4 24–30 Mar · W5 31 Mar–6 Apr · W6 7–13 Apr · W7 14–20 Apr · W8 21–27 Apr · W9 28 Apr–4 May · W10 5–11 May · W11 12–18 May · W12 19–25 May · W13 26–31 May.

---

## Milestones (with Plan B)

**M1 — Ethics submitted**
- **Target:** By 23 Mar (end of week 3).
- **Plan B:** If ethics takes longer: (1) lock protocol and participant info in Methodology/Evaluation so you can run as soon as approved; (2) keep a "planned vs actual" note for Discussion; (3) avoid blocking all writing on approval.

**M2 — Latency measurement in place**
- **Target:** By 30 Mar (end of week 4).
- **Deliverable:** Reproducible way to measure/record motion-to-display (or end-to-end) latency in app/ (and optionally in Unity); document in thesis/chapters/implementation.tex (e.g. "Latency Measurement" section).
- **Plan B:** If very difficult: define a minimal method (e.g. high-speed camera, or timestamp-based) and document limitations in Implementation and Discussion.

**M3 — Half-time meeting**
- **Target:** Your scheduled date.
- **Ready by then:** Introduction, Methodology, Implementation (incl. latency), Related Work (done); app + Architect feature-complete with latency; pilot protocol and ethics status clear.

**M4 — Pilot completed and data in**
- **Target:** By 4 May (end of week 9; allows time for analysis and Evaluation chapter).
- **Dependency:** Ethics approval.
- **Plan B:** If ethics is late: compress pilot window (fewer sessions or participants if agreed with supervisor) and protect time for Evaluation writing.

**M5 — Full thesis draft**
- **Target:** By 25 May (end of week 12).
- **Content:** All chapters drafted (Introduction through Conclusion, Abstract, appendices), figures/tables, bibliography.

**M6 — Final meeting + submission**
- **Target:** Final meeting as scheduled; submission by **31 May 2025**.
- **Buffer:** Reserve 26–31 May for formatting, PDF, and submission logistics.

---

## Weekly checkpoints (rescheduling)

Use a **weekly review** (e.g. same weekday every week) to:

- **Check progress:** Tick off which milestone steps were done (ethics, latency, pilot run, chapter drafts).
- **Plan next week:** Set 3–5 concrete tasks (e.g. "finish Methodology §3", "run 2 pilot sessions", "draft Evaluation §2"). Plan **small/tiny goals** so progress is visible and you notice if you slip the timeline (seminar: recommended Kanban).
- **Reschedule if needed:** If you slip (ethics delay, illness, etc.), move non-critical tasks and protect: (1) ethics submission, (2) latency measurement, (3) pilot execution, (4) Evaluation + Discussion + Conclusion + submission date.
- **Supervisor:** Keep in **regular touch** (seminar recommendation); half-time and final meetings are fixed; add short syncs every 1–2 weeks if useful.

Keep a short log (in docs/ or a `PLAN_WEEKLY.md`) so you can see patterns and adjust.

---

## Thesis writing order and dependencies

- **Already in good shape:** thesis/chapters/related_work.tex; thesis/chapters/abstract.tex.
- **Write early (10 Mar – 6 Apr):** Introduction, Methodology, Implementation (including latency method and system description from app/ and architect/ as in ARCHITECT_GAME.md).
- **Write after pilot (21 Apr – 18 May):** Evaluation (setup, quantitative/qualitative, threats), Discussion, Conclusion.
- **Ongoing:** Abbreviations, acknowledgements, appendices (e.g. protocol, screenshots, tables).

Flow: Introduction → Methodology → Implementation → (Pilot run) → Evaluation → Discussion → Conclusion. Latency measurement feeds Implementation.

---

## App / latency measurement (must-have)

- **Goal:** A defined, repeatable way to get a motion-to-display (or end-to-end) latency number for the thesis.
- **Options (to choose with supervisor):**
  - Timestamp-based: camera frame time → pose time → Unity display time; report mean/percentiles.
  - External validation: e.g. high-speed camera or known-motion event.
- **Where it lives:**
  - Code: extend app/ (and if needed architect/ scripts) to log timestamps or trigger measurement.
  - Text: thesis/chapters/implementation.tex section "Latency Measurement" and, if needed, thesis/chapters/evaluation.tex for reported values.

---

## Plan B summary (critical milestones)

| Risk | Mitigation |
| ---- | ---------- |
| **Ethics not yet submitted** | Submit by 16 Mar (3–16 Mar); in parallel, fix protocol and participant description so pilot can start as soon as approved. |
| **Very difficult: latency** | Agree minimal method with supervisor (e.g. timestamp pipeline); document method and limitations. |
| **Dependencies** | Pilot depends on ethics; keep Evaluation chapter outline and tables ready so you only fill numbers and quotes after data. |
| **Waiting times** | Don't block writing on ethics; use waiting time for Introduction, Methodology, Implementation, and latency implementation. |

---

## Suggested week-by-week focus (with dates)

- **3–16 Mar:** Ethics submission; start Introduction + Methodology; design latency measurement.
- **17–23 Mar:** Implement and test latency measurement; continue Methodology + start Implementation.
- **24–30 Mar:** Finish Implementation (incl. latency section); align with half-time meeting.
- **31 Mar – 13 Apr:** Half-time meeting; pilot recruitment/prep; start Evaluation outline.
- **7 Apr – 4 May:** Run pilot; analyze data; write Evaluation.
- **28 Apr – 18 May:** Discussion, Conclusion; integrate feedback; full draft.
- **12 May – 31 May:** Final meeting; revisions; abstract/appendices; submission by 31 May 2025.

Insert your **actual half-time and final meeting dates** into this grid and shift the ranges if needed so that "full draft" is ready before the final meeting and submission stays on 31 May 2025.

---

## Requirements from Master's Seminar (lecturer slides)

These points come from the MA Seminar slides (MA_Seminar_1.pdf, MA_Seminar_2.pdf) so that thesis structure, writing, and process align with the programme.

### Thesis structure (seminar order)

Seminar order: Cover pages → Preclusion → Oath → AI declaration → Abstract → Introduction (Motivation & background / State-of-the-art / Goal) → Material & Methods → Results → Discussion → Summary & Outlook → References, Lists → Appendices.

**Mapping to this project:** Introduction = motivation, background, goal; Related Work = state-of-the-art (intro can briefly point to it); Methodology + Implementation = Material & Methods; Evaluation = Results; Discussion + Conclusion = Discussion + Summary & Outlook. No need to rename files—keep the current structure; just be consistent in the text.

### Abstract (seminar rules)

- **No citations** in the abstract.
- **No abbreviations without explanation** (e.g. spell out "virtual reality" at first use if you use "VR", or explain in one phrase).
- **Length:** Min. 0.5 to max. 1 page. Can be structured or unstructured.

Before submission: double-check every abbreviation in the abstract is spelled out or explained.

### Introduction (seminar guidelines)

- **Shortest chapter** of the thesis; usually a few pages.
- **Many high-quality references**; use them to show relevance, what others did, and to lead into your problem/goal.
- **Start with WHY:** problem description → motivation. Funnel from broad ("X Mio people affected" / relevance) to specific ("Goal of this thesis is…").
- **State a clear hypothesis** (align wording with supervisor, e.g. Gerda).
- **Do not** talk about results or methods in the Introduction (keep those for later chapters).
- Keep "neighbouring work" short in the intro; detailed state-of-the-art stays in Related Work.

### Word count and references

- **Maximum 15,000 words** (body text). Plan a final check (e.g. texcount or word count from PDF) before submission.
- **One uniform citation style** throughout (e.g. IEEE, APA—match MCI/SAKAI template). Use references in Introduction/Related Work (relevance, state-of-the-art), in Methodology/Implementation (justify methods, document sources/code), and in Discussion (compare results, support findings). **No references in Abstract or Conclusion (Summary).**

### Literature review

- **Document your literature review well** (seminar recommendation). Related Work is already substantial; add a short note on **search and scope**: which databases/keywords you used and how you narrowed (e.g. in Methodology or at the start of Related Work). If literature feels scarce, widen scope (other fields, "cited by" from key papers, alternate keywords).

### Code and data (seminar)

- If code is not fully in the thesis or appendix: create a **permanent copy** with a **DOI** (e.g. Zenodo: link GitHub repo to Zenodo for automatic archiving). In the thesis (e.g. Implementation or Appendix), add one sentence and citation: e.g. "The pose pipeline and Unity project are available at [URL] and archived in Zenodo [X]."

### Guidelines and template

- **Check out:** Academic Walkthrough and Lab Report Guide (seminar). Note any formal or structural requirements and tick them off before submission.
- **LaTeX template:** Confirm the template in use (template/) is the current one from SAKAI (or approved by supervisor). Responsibility for your work lies with you; feedback on the template goes to Aitor.

### Project management (seminar)

- **"Boring structures win!"**—thesis structure is already in place; keep filling it systematically.
- **Define goals → Milestones → Weekly review** and rescheduling (already in this plan). **Plan B** for critical milestones: difficult tasks, dependencies, waiting times (already covered above).
- **Kanban recommended:** underlying project plan and milestones, weekly work planning, **small/tiny goals** so you feel progress and notice when you miss the timeline. Use your weekly checkpoints for this.
- **Find an excellent thesis as reference** (seminar recommendation)—one from your programme or field to mirror structure and tone.

### If things go wrong ("My project is a trainwreck…")

- Stay calm. **Negative results are okay in science.**
- Contact your supervisor; realign or redefine the project if needed.
- Document decisions and limitations (e.g. in Discussion); continue with a clear, adjusted scope rather than hiding problems.
