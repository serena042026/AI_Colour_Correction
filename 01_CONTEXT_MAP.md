# 01_CONTEXT_MAP.md — Lab 4 Context Inspection

## 1. Observed Model Context

The model context was inspected by examining the `turn(message)` function in `app.py`.

The relevant code is:

```python
parts = [{"role": "user", "content": message}]
log_context(parts)
data = model.call_json(parts, SCHEMA)
```

The `log_context(parts)` function prints each message component immediately before the model call:

```python
def log_context(parts):
    for part in parts:
        print("CONTEXT:", part, flush=True)
```

This confirms that the inspected model call receives a single user message.

For example, when the input is `when is coursework 1 due`, the expected context is:

```text
CONTEXT: {'role': 'user', 'content': 'when is coursework 1 due'}
```

This example illustrates the inspected code path. It should not be treated as a new execution record unless reproduced in the terminal.

## 2. Context Map

| Context component | Source / Trust boundary | Type | Size |
|---|---|---|---|
| Current user message | Browser input; untrusted user-provided text | User input | Short |
| System instructions | Not present in the inspected model request | Not present | N/A |
| Conversation history | Not included in `parts` | Not present | N/A |
| Retrieved passages | Not included in the inspected model request | Not present | N/A |
| Tool definitions | Handled separately by the application | Not present | N/A |
| Uploaded clothing image | Processed through the clothing workflow; not included in this model request | Not present | N/A |
| Reference selection | Application input; not included in this model request | Not present | N/A |
| Previous colour adjustments | Application state; not included in this model request | Not present | N/A |

## 3. Clothing Colour Correction Workflow

The main application is an AI-assisted clothing colour correction prototype developed from the Lab 3 interaction design.

Its workflow includes:

1. Uploading a clothing photograph.
2. Selecting a reference type: no reference, white paper, or colour chart.
3. Choosing whether the reference is in the clothing photograph (same-photo mode) or in a separately uploaded photograph (separate-photo mode).
4. Selecting a reference region and assessing whether it is suitable for approximate correction.
5. Generating a colour correction preview for the clothing photograph.
6. Receiving user feedback, such as "Too grey" or "Too yellow", and proposing bounded adjustments.
7. Reviewing the preview, undoing adjustments if needed, and explicitly confirming an accepted preview for local logging.

The current prototype uses rule-based feedback interpretation and local image processing. A separate reference photograph, when selected, is application input used by the colour-processing workflow; it is not a separate message in the inspected `model.call_json()` request. The prototype does not establish calibrated real-world garment colour accuracy.

The inspected `model.call_json()` request does not include the uploaded clothing photograph, optional separate reference photograph, selected reference region, reference mode, colour parameters or previous adjustments.

Therefore, the clothing correction application's state should not be described as model context.

## 4. Context Removal Decision

The inspected model request contains only one user message.

No redundant message, duplicated instruction or unnecessary conversation history was identified in this request.

Removing the only user message would eliminate the information required to interpret the request.

Therefore, no context component was removed from this call.

**Limitation:** This documents the inspection and removal decision, but does not constitute a completed removal-and-retest experiment. If the Lab 4 marking criteria require actually removing a context component and comparing outputs, that requirement remains outstanding and should be tested separately rather than claimed as completed.

## 5. Context Removal and Retest

The current user message was inspected before the model call.

The original implementation passed the raw user message to the model.
The revised implementation applies `message.strip()` before constructing
the model context, removing unnecessary leading and trailing whitespace.

The model still receives the current user request, but redundant whitespace
is excluded.

Retest input: `  when is coursework 1 due  `

Observed context:
`CONTEXT: {'role': 'user', 'content': 'when is coursework 1 due'}`

This change reduces unnecessary input without removing information
required to answer the user's question.