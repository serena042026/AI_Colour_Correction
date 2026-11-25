# The demonstrations

Every demonstration in the lab is written out here with its before and after, so students can review
the sequence and tutors can prepare the live demonstration.

## 1. Printing the context  (slide 5)

**Before** — in the supplied starting app, `turn(message)` passes one user message to the mock model.
There is no conversation history, tool definition or retrieved passage in that request.

Add the `log_context(parts)` helper and replace the inline list with a named `parts` variable as shown
in the student handout. Run `python app.py`, make one ordinary browser request, and read the actual
terminal output:

    CONTEXT: {'role': 'user', 'content': 'your test request'}

Fill one row in `01_CONTEXT_MAP.md` for the user message. Mark history, tools and retrieved passages as
`not present`. There is nothing safe to cut from this starting request. Revisit that decision after
retrieval is added in Phase 2; do not report a change that was not made.

## 2. Retrieval, on its own then wired in  (slide 7)

    $ python retrieve.py "when is coursework 1 due"
    1.06  handbook.md 3 Assessment  2026-09-12
          "Coursework 1 is due on 14 November at 12:00 and is worth 40%..."
    0.95  handbook.md 3 Assessment  2026-09-12
    0.76  handbook.md 3 Assessment  2026-09-12

Then the stale question, which is the one worth showing twice:

    $ python retrieve.py "what is the late-submission penalty"
    0.82  handbook_2024.md 5.2 Late submission  2024-10-03 [SUPERSEDED]  <- still ranks first
    0.49  handbook_late.md 5.2 Late submission  2026-09-12     <- the current rule

Then wire the result into the existing project:

    hits = retrieve(question, k=3)
    ctx  = format_passages(hits)
    # and in the reply: show(hit["text"], hit["source"], hit["date"], hit["score"])

**The mistake to show:** paste `hit["text"]` alone into the context and ask the room how the page is
supposed to print a citation afterwards. It cannot: the source was thrown away at the only moment it
was available. The app keeps a superseded result visible but selects the current passage for its answer
and warns the user, so the ranking failure is not presented as current policy.

## 3. The tool, refused and then confirmed  (slide 9)

**Break it first.** Propose 900 minutes:

    {"name": "book_slot", "arguments": {"date": "2026-11-14", "minutes": 900}}
    -> refused: minutes must be between 15 and 180      (nothing ran)

Say: "that is check one doing its job, and notice the reason is in words a person could be shown."

**Then the real one.** 90 minutes, and the confirmation shows the arguments:

    Add a 90-minute revision slot on Sat 14 Nov 2026?      [ Confirm ]  [ Cancel ]

Press confirm, then:

    $ tail -1 tool_log.jsonl
    {"t": "...", "tool": "book_slot", "args": {"date": "2026-11-14", "minutes": 90},
     "confirmed_by": "user", "result": {"status": "ok", "id": "slot_1", "total_slots": 1}}

## 4. The image, and the refusal  (slide 11)

    $ python vlm.py sample_images/sample_poster.png "what deadline is shown?"
    14 November, 12:00  (confidence 0.86 — the sheet reads 'Due: 14 November, 12:00')

    $ python vlm.py sample_images/sample_noticeboard.png "what deadline is shown?"
    I cannot answer that from this image: no deadline is visible in this image, and it shows a
    named person's mark, which I will not read out

Two reasons, and say both: the picture does not contain the answer, and it contains somebody else's
personal data. Both images are drawn for teaching; no photograph of a real person is used anywhere.

## 5. The stale row, written live  (slide 13)

Ask "what is the late-submission penalty?" in the project. The top hit is the 2024
handbook. The page warns about it and answers from the current 2026 passage while showing both results.
Write the row live:

    | "What is the late-submission penalty?" | stale | 2024 result ranks first; warning shown; answer uses 2026 passage | yes, with warning |
      keep the warning and current answer; improve retrieval ranking |

Say: "a row that says no, with a fix beside it, is worth more than three that say yes."
