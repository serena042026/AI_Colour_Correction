# 02_TEST_RECORD.md

The observations below are from **programmatic requests to the running local HTTP server** on 2026-10-29, not from a human visually inspecting the browser. The page JavaScript includes the required result rendering, but **you must check the actual browser display and update this record before submission**. The corpus is supplied mock teaching material, not a verified real coursework timetable.

| question | type | what the local HTTP response actually returned | supported? | what I would change |
|---|---|---|---|---|
| `when is coursework 1 due` | grounded | `Coursework 1 is due on 14 November at 12:00...`; evidence includes `Module Handbook 2026–27`, `3 Assessment`, updated `2026-09-12`, score `1.056`, with the quoted passage. | Yes, by supplied mock corpus | Verify the browser shows full text, source, date and score beside the answer. |
| `late submission policy` | stale | Retriever ranked superseded `handbook_2024.md` first (score `0.821`); response instead used newer `handbook_late.md` passage (score `0.489`): `Work submitted after the deadline loses five marks per working day...`; stale warning returned. | Yes, with explicit supersession warning | Consider preferring current documents in retrieval ranking instead of detecting supersession afterward. |
| `what is the library wifi password` | unanswerable | `The supplied corpus does not give a reliable answer. Ask the module lead about anything it does not cover.` No positive-score evidence returned. | Correctly withheld unsupported answer | Suggest a more specific official source or support contact when available. |

## Other checks

## Clothing Colour Correction Interaction Tests

The main prototype is an AI-assisted clothing colour correction system developed from the Lab 3 interaction design.

The following observations are based on manual interaction with the local browser interface.

| Test scenario | Observed behaviour | Status |
|---|---|---|
| Image upload | A photograph was successfully uploaded and displayed in the original-image panel. | Passed |
| Colour correction preview | The application generated and displayed an adjusted preview. | Passed |
| Manual adjustments | Brightness, saturation and additional colour controls produced visible changes. | Passed |
| Natural-language feedback | Feedback such as "Too grey" and "Too yellow" was tested as part of the interactive adjustment workflow. | Passed in basic testing |
| Iterative correction | The user was able to continue adjusting the preview through multiple interactions. | Passed in basic testing |
| User control | The application provides confirmation and undo functionality, tested during the interaction workflow. | Passed in basic testing |
| Reference reliability | The interface supports reference selection and assessment, but the behaviour for overexposed or shadowed reference regions requires separate verification. | Not fully verified |

### Human–AI Interaction

The prototype supports an iterative interaction process:

1. The user uploads a clothing photograph.
2. The system generates an initial colour correction preview.
3. The user evaluates the result and provides feedback.
4. The system interprets recognised feedback using predefined rules.
5. The application generates a revised preview.
6. The user can continue adjusting, undo changes or confirm the result.

This workflow demonstrates user participation in the correction process rather than relying entirely on automatic image adjustment.

### Limitations and Improvements

The current prototype uses rule-based feedback interpretation and conventional image processing. It does not use a fully integrated multimodal AI model.

Colour adjustments may affect the entire image rather than only the garment. The prototype also cannot guarantee that the corrected colours accurately match the physical clothing item.

Future improvements would include garment segmentation, more flexible natural-language understanding, improved reference-region assessment and stronger integration between retrieval evidence and the colour correction workflow.

### Testing Scope

The clothing correction tests and the supplied Lab 4 technical checks were conducted through separate application workflows.

Passing the clothing correction interaction tests does not independently demonstrate that retrieval, tool calling and image question answering have been integrated into the clothing correction workflow.

## Clothing Colour Correction Tool Validation

### Valid confirmation
- Test: User adjusted the clothing colour preview and clicked "Confirm & log preview".
- Result: The application displayed "Preview accepted and logged locally".
- Evidence: `colour_tool_log.jsonl` recorded `accept_colour_preview`, the adjustment settings, `confirmed_by: user`, and `accepted_preview_only`.
- Status: Passed.

### Invalid parameter
- Test: Submitted a confirmation request with `saturation = 900`.
- Expected: The application should reject the request because the allowed saturation range is 0.5–1.5.
- Actual result: The server returned `Invalid saturation: 900. Allowed range is 0.5 to 1.5`.
- Status: Passed.

### Remaining verification
- Confirm that the invalid request did not append a successful entry to `colour_tool_log.jsonl`.

## Clothing Colour Correction — Additional Prototype Tests

### Test 1: Image Upload and Colour Correction

**Input:** A clothing photograph uploaded through the web interface.

**Observed result:** The original image was displayed, and the system generated a correction preview. Brightness, saturation, warmth and contrast could be adjusted manually.

**Supported:** Yes.

**Limitation:** The current prototype applies adjustments to the whole image rather than automatically segmenting the garment.

### Test 2: White-Paper Reference Assessment

**Input:** A clothing photograph and a white-paper reference photograph, using the separate-reference upload option.

**Observed result:** The separate-reference workflow was exercised in the browser. The system provides reference-region selection and generates a correction preview using the reference assessment.

**Supported:** Partially.

**Limitation:** A separately photographed white reference may not share the same lighting or camera settings as the clothing photograph. The resulting correction is approximate and cannot establish true colour accuracy.

### Test 3: Natural-Language Feedback

**Input:** User feedback including “too grey” and “too yellow”.

**Observed result:** The system interpreted the feedback using predefined rules and proposed bounded adjustments to saturation or warmth. The user could review the updated preview and undo an adjustment.

**Supported:** Yes, for the supported feedback categories.

**Limitation:** Feedback interpretation is rule-based rather than powered by a large language model. Complex or ambiguous descriptions may not be understood.

### Test 4: User Confirmation and Tool Logging

**Input:** A user-approved colour correction preview.

**Observed result:** After confirmation, the interface displayed:

“Preview accepted and logged locally. This does not establish true colour accuracy.”

The file `colour_tool_log.jsonl` contained records with the tool name `accept_colour_preview`, adjustment arguments, `confirmed_by: user`, and the result status `accepted_preview_only`.

**Supported:** Yes.

**Limitation:** Confirmation records acceptance of a preview, not verification of the garment's real-world colour.

### Test 5: Invalid Tool Parameters

**Input:** An HTTP request containing `saturation = 900`.

**Observed result:** The server rejected the request with:

“Invalid saturation: 900. Allowed range is 0.5 to 1.5”

The existing log contained two successful confirmation records, with no additional successful record created by the invalid request.

**Supported:** Yes.

**Improvement:** Continue validating all adjustment parameters before any confirmed action is logged.

### Overall Evaluation

The prototype demonstrates a human-in-the-loop colour correction workflow. Users can upload photographs, assess a reference, generate previews, provide feedback, manually adjust settings, undo changes and explicitly confirm a proposed result.

The system prioritises user control and transparent limitations. However, it does not perform calibrated colour measurement, automatic garment segmentation or general-purpose natural-language understanding. Future improvements could include more reliable reference validation, garment-specific correction and more flexible feedback interpretation.

## Final Verification

The clothing colour correction prototype was tested through the browser.

The implemented workflow includes image upload, reference selection,
colour correction preview, natural-language feedback, manual adjustment,
undo, and explicit user confirmation.

The confirmation endpoint was tested with valid and invalid parameters.
An out-of-range saturation value was rejected.

Python syntax checks were performed on the main application modules.

The prototype remains limited to approximate colour correction and
does not guarantee calibrated garment colour accuracy.