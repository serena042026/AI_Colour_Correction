# Lab 4 app route

If you have a working Lab 3 app, you can extend it with the Lab 4 support files and keep its app files.
Otherwise, copy this whole folder to your working location. Lab 3 is not required for this route.
Open a terminal there, run `python app.py`, then open <http://localhost:8000>. The mock model and sample
files run locally, without a key or network connection. Use the student handout for the task steps.

| file | what it is |
|---|---|
| `retrieve.py` | searches `corpus/`; each result includes its source, section, date, score and superseded status |
| `tools.py` | checks a revision-slot request, asks for confirmation, then logs the result |
| `vlm.py` | returns an answer with a confidence score or refuses with a reason |
| `app.py`, `index.html`, `model.py`, `mock_model.py`, `recorded_runs/` | the runnable app and its mock replies |
| `corpus/` | six sample course documents with source and date information |
| `sample_images/` | `sample_poster.png` supports the deadline answer; for the same question, the app should refuse to answer from `sample_noticeboard.png` |
| `01_CONTEXT_MAP.md` | record what your app sends to the model |
| `02_TEST_RECORD.md` | record the three retrieval cases you test |

## Check the support files

    python retrieve.py --selftest     # expect: ok: 6 documents, 14 passages
    python tools.py --selftest        # expect: valid call accepted, 900-minute call refused
    python vlm.py --selftest          # expect: ok: 2 sample images

The supplied mock is used for the checks in this lab. Do not put API keys in a file, screenshot or
commit. The course documents and sample images are provided for this exercise.
