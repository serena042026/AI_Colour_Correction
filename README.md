# Lab 4 app route


# AI-Assisted Clothing Colour Correction System

**Module:** Intelligent Interactive Systems  
**Submission:** Assignment 2 – Project Report  
**Word count:** Approximately 760 words

## 1. Project Status

This project develops an intelligent interactive system to help online clothing sellers reduce colour differences between product photographs and physical garments without requiring professional photo-editing skills.

The system follows a human-in-the-loop approach. It generates an approximate colour correction preview, communicates limitations, and allows users to refine, reject or confirm adjustments.

| Feature | Status |
|---|---|
| Clothing photograph upload and original/preview comparison | Implemented |
| Same-photo and separate-photo reference selection | Implemented |
| Manual reference-region selection | Implemented |
| Reference assessment for overexposure, shadows and uneven colour distribution | Implemented |
| Approximate white-paper-based colour correction | Implemented |
| Brightness, saturation, warmth and contrast adjustment | Implemented |
| Natural-language feedback using predefined rules | Implemented |
| Adjustment explanations, undo and user confirmation | Implemented |
| Parameter validation and local confirmation logging | Implemented |
| Retrieval, structured model responses and visual question answering | Separate Lab 4 technical demonstrations using mock responses |
| Automatic reference detection and garment segmentation | Planned; simulated in earlier design work |
| Calibrated colour-chart correction | Not implemented |
| Personalised learning from previous user feedback | Planned |
| General-purpose LLM/VLM-based colour reasoning | Not implemented |

The current prototype applies adjustments to the whole photograph rather than an automatically segmented garment. It does not guarantee calibrated or objectively accurate garment colours.

## 2. Technology Stack

- **Python:** Local application server, image-processing logic, feedback interpretation and parameter validation.
- **Pillow:** Image decoding, reference-region analysis, approximate RGB correction and image enhancement.
- **HTML and CSS:** Interactive interface and visual presentation.
- **JavaScript:** Image upload, reference-region selection, preview updates, adjustment controls and interaction state.
- **JSON and JSONL:** Structured application requests, responses and local confirmation records.
- **Rule-based feedback interpretation:** Maps supported user expressions to bounded colour adjustments.
- **Recorded mock model:** Supports the separate Lab 4 technical demonstrations without requiring an external API or network connection.

ChatGPT was used as a development assistant. It is not a runtime model within the clothing correction workflow.

Future choices concerning garment segmentation, calibrated colour transformations and language-model integration remain undecided.

## 3. Running or Inspecting the Work

### Requirements

- Python 3
- Pillow
- A modern web browser

### Installation and execution

Download or clone this repository:

```bash
git clone https://github.com/serena042026/AI-Clothing-Colour-Correction.git
cd AI-Clothing-Colour-Correction
```

Install the required dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Start the local application:

```bash
python3 app.py
```

Open the following address in a web browser:

http://localhost:8000

No external AI API key is required.

### Using the prototype

1. Upload a clothing photograph.
2. Select the available reference type.
3. If using a reference, choose the same-photo or separate-photo option and select a suitable reference region.
4. Generate and inspect the correction preview.
5. Review the reference assessment and reliability warnings.
6. Provide feedback such as "too grey" or "too yellow", or adjust the parameters manually.
7. Undo unsatisfactory adjustments if necessary.
8. Explicitly confirm the accepted preview.

Confirmation records the user's acceptance, not verified colour accuracy.

## 4. Development Record

### Stage 1 — Problem identification and literature exploration (Lab 1)

The project initially investigated colour differences between digital photographs and physical garments.

Literature exploration covered interactive white balancing, camera colour processing and human-machine colour descriptions. Search queries were refined to improve relevance, and AI-generated literature summaries were checked against original abstracts.

This established the initial direction of combining colour correction with understandable user interaction.

### Stage 2 — Interaction design (Lab 2)

The design developed into an interactive correction workflow involving sensing, inference, action and feedback.

Original/preview comparison, reference confirmation, semantic feedback, manual controls and undo were introduced to support user agency.

Storyboards explored normal correction, unreliable references and recovery from unsatisfactory adjustments.

### Stage 3 — System specification and simulated testing (Lab 3)

The proposed system distinguished calibrated colour charts, ordinary white paper and photographs without references.

A structured simulation examined a normal reference case and a partially overexposed white-paper case.

The design was revised to distinguish reference identification from reference-quality validation and make the selected reference region visible.

These were designed simulation traces rather than executed image-processing experiments.

### Stage 4 — Runnable prototype and technical validation (Lab 4)

The interaction design was developed into a local web application.

Manual reference-region selection, approximate white balancing, separate-reference photographs, rule-based feedback and bounded adjustment controls were implemented.

Automatic garment segmentation and calibrated chart correction were excluded from the current implementation.

Recorded browser tests covered image upload, preview generation, reference assessment, feedback interpretation, undo and explicit confirmation.

An invalid saturation value of 900 was rejected by the confirmation endpoint. The recorded test also checked that the invalid request did not create an additional successful confirmation entry.

The separate Lab 4 demonstrations examined context inspection, retrieval, structured responses and tool validation.

Development evidence:

- [Context inspection and system boundaries](01_CONTEXT_MAP.md)
- [Prototype testing and technical validation](02_TEST_RECORD.md)

## 5. AI Assistance

ChatGPT was used during literature exploration, interaction design, prototype implementation, debugging and documentation preparation.

Examples include:

- Generating literature-search queries and preliminary paper summaries. Summary claims were checked against original abstracts, and unsupported interpretations were identified.
- Assisting with interaction scenarios and storyboard development. The project retained user confirmation, visible feedback and recovery mechanisms.
- Generating and revising Python and JavaScript code for reference assessment, preview generation and feedback interpretation.
- Assisting with parameter-validation logic and test preparation.

The implemented behaviour was inspected through browser interaction and recorded technical tests, including valid and invalid confirmation requests.

AI assistance also supported the preparation of this README. The documented implementation scope distinguishes actual functionality, simulated behaviour and planned improvements.

## 6. Additional Files

| File or directory | Purpose |
|---|---|
| `app.py` | Local application server and request handling |
| `colour.py` | Reference assessment, image correction, feedback rules and confirmation validation |
| `index.html` | Main clothing colour correction interface |
| `requirements.txt` | Python dependencies |
| `01_CONTEXT_MAP.md` | Context inspection and system boundaries |
| `02_TEST_RECORD.md` | Recorded tests, observations and limitations |
| `lab4_checks.html` | Separate Lab 4 technical demonstration interface |
| `demo_walkthrough.md` | Supporting Lab 4 demonstration instructions |
| `model.py`, `mock_model.py` | Supplied model interface and recorded mock responses |
| `retrieve.py`, `tools.py`, `vlm.py` | Supporting Lab 4 technical components |
| `corpus/` | Sample documents for retrieval demonstrations |
| `sample_images/` | Sample images for technical demonstrations |
| `recorded_runs/` | Recorded responses required by the mock model |
| `reference/` | Supporting reference materials |

The repository retains course-provided Lab 4 support components alongside the developed clothing colour correction prototype. These supporting demonstrations should not be interpreted as fully integrated colour correction capabilities.

The main application can be inspected through `index.html`, `app.py` and `colour.py`.

Local runtime logs are generated during confirmed operations and are not required as uploaded submission files.
