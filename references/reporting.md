# Reporting

Shared by `debloat-scan` and `debloat-file`. Governs the output only. Every check and its severity default lives in [checks.md](checks.md).

Lead with the headline where there is something substantial to recover: estimated tokens, the whole surface for a scan or the one file for a file audit, and that as a percentage of a 200k reference window. Skip it silently, without announcing that it was skipped, where the target is already lean or the recoverable total is trivial. Never invent a 0-100 score.

Then the findings, under `Issues`, `Warnings` and `Nice to have`, in that order, omitting any band that is empty and ordered within a band by estimated token impact. The four check-section names from checks.md tag a finding, they do not group it. Give each finding the room its evidence needs rather than a fixed shape: the file and line range, what is wrong, the evidence for it (for duplication, every location it appears in and the wording that actually overlaps, not just the claim that it does), whether the cost is paid every session or only when that item runs, and the concrete fix. A finding the reader can check for themselves is worth several they have to take on trust.

Close in a sentence or two, separate from the findings: name the Issues and what fixing them recovers, then ask which of the lower bands to include. Nothing before the report, no preamble and no narrating this file. Where the target is already lean say so plainly rather than padding the list, three findings that matter beat twenty that don't, and where no band has anything the whole report is one sentence saying there is nothing worth changing, with no bands and no closing question.
