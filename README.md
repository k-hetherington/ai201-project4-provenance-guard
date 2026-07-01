# AI201 Project 4 – Provenance Guard

Provenance Guard is a Flask backend that analyzes submitted text and estimates whether it was likely written by a human or generated using AI. The system combines multiple detection signals, produces a confidence score, displays a transparency label, allows creators to appeal classifications, and records every decision in a structured audit log.

---

# Architecture Overview

When a user submits text, the system follows this workflow:

```
POST /submit
      │
      ▼
Validate Request
      │
      ▼
Groq LLM Detection
      │
      ▼
Stylometric Heuristics
      │
      ▼
Confidence Scoring
      │
      ▼
Transparency Label
      │
      ▼
Audit Log
      │
      ▼
JSON Response
```

If a creator disagrees with the classification, they may submit an appeal.

```
POST /appeal
      │
      ▼
Validate Input
      │
      ▼
Update Status → under_review
      │
      ▼
Record Appeal
      │
      ▼
Audit Log
```

---

# Detection Signals

## Signal 1 – Groq LLM

Uses the **llama-3.3-70b-versatile** model to estimate whether writing appears AI-generated or human-written.

This signal evaluates:

- writing style
- overall tone
- semantic consistency
- organization

### Limitations

- Formal human writing may resemble AI writing.
- Edited AI writing may appear human.
- Very short text may not provide enough context.

---

## Signal 2 – Stylometric Heuristics

Uses pure Python to measure structural writing characteristics.

Metrics include:

- sentence length variance
- vocabulary diversity (type-token ratio)
- punctuation density

### Limitations

- Poems
- Academic writing
- Very short submissions
- Non-native English writing

---

# Confidence Scoring

The final confidence score combines both detection signals.

```
confidence =
(LLM Score × 0.60)
+
(Stylometric Score × 0.40)
```

Score ranges:

| Confidence | Attribution |
|------------|-------------|
| 0.00–0.39 | Likely Human |
| 0.40–0.69 | Uncertain |
| 0.70–1.00 | Likely AI |

The system intentionally includes an **uncertain** range because false positives can unfairly impact human creators.

---

# Example Results

## Example 1

Input:

> Artificial intelligence represents a transformative paradigm shift in modern society...

Output

- LLM Score: **0.80**
- Stylometric Score: **0.55**
- Final Confidence: **0.70**
- Classification: **Likely AI**

---

## Example 2

Input:

> ok so i finally tried that new ramen place downtown and honestly? underwhelming...

Output

- LLM Score: **0.00**
- Stylometric Score: **0.40**
- Final Confidence: **0.16**
- Classification: **Likely Human**

---

# Transparency Labels

### High-confidence AI

> **Likely AI-generated:** Our system found strong evidence that this content may have been generated using AI. Confidence: XX%. Creators may appeal this decision if they believe it is incorrect.

---

### High-confidence Human

> **Likely human-written:** Our system found strong evidence that this content was written by a person. Confidence: XX%.

---

### Uncertain

> **Uncertain attribution:** Our system could not confidently determine whether this content was written by a human or generated using AI. Confidence: XX%. This label is not a final judgment.

---

# Appeals Workflow

Creators may submit an appeal using:

```
POST /appeal
```

Required fields:

- content_id
- creator_reasoning

When an appeal is received, the system:

1. Records the creator's reasoning.
2. Updates the submission status to `under_review`.
3. Logs the appeal in the audit log.
4. Returns a confirmation response.

---

# Rate Limiting

The `/submit` endpoint is protected using **Flask-Limiter**.

Limits:

- **10 requests per minute**
- **100 requests per day**

These limits allow normal users to submit content while preventing automated abuse.

### Test Results

```
200
200
200
200
200
200
200
200
200
200
429
429
```

The final two requests exceeded the configured rate limit and correctly returned HTTP **429 Too Many Requests**.

---

# Audit Log

Every submission records:

- timestamp
- content ID
- creator ID
- attribution
- confidence score
- LLM score
- stylometric score
- transparency label
- status

Appeals are also recorded with:

- content ID
- creator reasoning
- updated status
- timestamp

---

# Known Limitations

This project is intended as a transparency tool rather than a definitive AI detector.

Examples where it may struggle include:

- poetry
- academic papers
- non-native English writing
- very short submissions
- heavily edited AI-generated text

These cases may produce uncertain or incorrect classifications.

---

# Spec Reflection

Creating the planning document before implementation made it easier to organize the project into separate modules and define each API endpoint before writing code.

One area where the implementation differed from the original plan was the audit log. Rather than using SQLite, I implemented a structured JSON audit log because it required less setup while still satisfying the project requirements.

---

# AI Usage

## Example 1

I used AI as a planning assistant while designing the project architecture. It helped me think through the API endpoints and project organization before I began implementation. I wrote the final planning document and adjusted the design decisions to match the project requirements.

## Example 2

I primarily used AI for debugging and troubleshooting rather than code generation. When I encountered issues with Flask setup, virtual environments, PowerShell commands, and API testing, I asked AI for possible solutions, tested them myself, and incorporated only the changes that fit my project.

---

# Technologies Used

- Python
- Flask
- Flask-Limiter
- Groq API
- python-dotenv

---

# Running the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

The server will start on:

```
http://127.0.0.1:5000
```

# Stretch Feature: Analytics Dashboard
  "appeal_rate":  0.5,
    "average_confidence":  0.43,
    "detection_pattern":  {
                              "likely_ai":  1,
                              "likely_human":  1,
                              "uncertain":  0
                          },
    "total_appeals":  1,
    "total_submissions":  2