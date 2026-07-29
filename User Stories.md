# User Stories — Inspection Workflow

## The Problem

Before this project, inspection requests and results at a plant like this typically live in scattered, unstructured places — a WhatsApp message to the quality team, a note left on a machine, a verbal handoff during shift change, or at best a shared Excel sheet that nobody updates consistently. This creates a few recurring problems:

- **No single source of truth.** A machine in-charge can't easily check whether their request was even received, let alone where it stands.
- **No traceability.** When a machine fails again a few months later, there's no structured record of what was found, what was done, or who inspected it last time.
- **No visibility for management.** Without structured data, questions like "which cell has the most recurring defects?" or "how long does inspection actually take?" can't be answered — only guessed at.
- **Inconsistent detail.** A handwritten note might skip the root cause, or a verbal report might leave out whether a second inspection was needed — details get lost between the person who found the issue and the person who has to report on it later.

This project addresses that gap directly: it replaces ad hoc, unstructured reporting with a **structured, two-sided digital workflow** — a defined form for raising a request, a defined form for logging a result, and a real data pipeline underneath so that every inspection is captured consistently and can be analyzed, not just remembered.

---

## Personas & Stories

### 1. Machine In-Charge (Requester)

*Someone on the shop floor who notices a problem and needs it inspected, but has no reliable way to log it or track what happens next.*

- As a machine in-charge, I want a simple form to log an inspection request with the machine, cell, and reason, so that I don't have to rely on a verbal handoff or a note that might get lost.
- As a machine in-charge, I want to indicate the priority and whether I think the issue needs deeper investigation, so that urgent issues are flagged from the start rather than waiting to be discovered later.
- As a machine in-charge, I want my request to exist as a permanent record, so that if the same machine has a repeat issue, there's a history to refer back to.

### 2. Quality Inspector

*Responsible for physically inspecting flagged machines and reporting results — previously done with no consistent format, making results hard to compare or trust.*

- As a quality inspector, I want to see a queue of only open requests, so that I'm not sifting through a messy, undifferentiated list of everything ever reported.
- As a quality inspector, I want a structured form to log Pass/Fail, remarks, and whether a second inspection is required, so that my findings are captured the same way every time, regardless of who's inspecting.
- As a quality inspector, I want a separate queue for Stage 2 follow-ups, so that flagged issues don't get buried among first-time requests.

### 3. Plant Manager / Quality Lead

*Responsible for spotting patterns and improving the process — previously unable to do this at all without structured data.*

- As a plant manager, I want to see request volume and turnaround time by cell, so that I can identify which parts of the plant need more inspection resources.
- As a plant manager, I want to see first-pass yield and recurring defect categories, so that I can distinguish one-off failures from systemic problems worth investigating.
- As a plant manager, I want to compare what requesters predicted (priority, Stage 2 need) against what inspectors actually confirmed, so that I can judge how reliable front-line severity assessments are and where extra training or clearer guidelines might help.
- As a plant manager, I want a single dashboard rather than piecing together notes and spreadsheets, so that decisions are based on consistent, structured data rather than fragmented anecdotes.

---

## From Problem to Pipeline

| Unstructured reality | What this project provides |
|---|---|
| Verbal/note-based requests | A structured Power App request form |
| No consistent inspection format | A structured Stage 1 / Stage 2 inspection form |
| No historical record | Persistent, relational data (Requests → Stage 1 → Stage 2) |
| No way to spot patterns | Python-computed KPIs: yield, turnaround, defect trends |
| No visibility for leadership | A multi-page Power BI dashboard, filterable by cell, priority, and time |
