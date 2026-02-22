# BaguetteBot-French-Study-Organizer
(aka: “I had 1000+ screenshots and chose chaos… with AI”)

# Why This Exists
I was taking a French course.

The material was:
- Long
- Scattered
- Spread across 100+ PDFs
- Screenshotted into 1000+ images
At some point I had two choices:
1. Go through them manually like a normal human.
2. Build an LLM-powered processing pipeline.
I chose option 2.

# What This Project Actually Does
This is a side project that:
- Takes raw French screenshots
- Uses Vision models (image → text)
- Converts them into structured .txt
- Auto-generates categories
- Re-buckets everything into structured folders
Because manually organizing 1000+ screenshots is not my life’s calling.

# Architecture Overview
Pipeline = 3 stages:
Screenshots
    ↓
[extract.py] → Text files
    ↓
[category.py] → Category definitions
    ↓
[bucket.py] → Structured folder buckets

# Stage 1 — Extract (Vision → Structured Text)
File: extract.py 

# What it does:
- Reads all screenshot images (.png/.jpg/.webp)
- Base64 encodes them
- Sends them to gpt-4o-mini
- Uses structured JSON schema outputs
- Validates responses
- Writes clean .txt files
Key Concepts:
- Vision input
- JSON Schema enforcement
- Structured flashcard extraction
- Conversation extraction
- Response validation layer
- Rate limiting (sleep control)

Example Output:
```text
bonjour    hello
merci      thank you
```

Or for conversations:
```text
A: Bonjour, comment ça va ?
B: Ça va bien, merci.
```

Because yes, we respect clean data.

# Stage 2 — Categorization
File: category.py 
Now that we have structured text, we:
- Send full .txt files to LLM
- Ask it to generate categories
- Clean and normalize output
- Save structured category files
- This creates a semantic layer on top of raw extraction.

Example:
- Food
- Travel
- Grammar
- Daily Conversation

No more scrolling through chaos.

# Stage 3 — Bucketing (Line-Level Intelligence)
File: bucket.py 
This is where it gets fun.
We:
- Load category list
- Number every line in the source text
- Force the LLM to assign line numbers to specific categories
- Validate JSON strictly
- Write categorized lines into separate folder buckets

Example:
```text
output/
├── vocab/
│   └── A1.txt
└── bucket/
    └── vocab/
        ├── Food.txt
        ├── Travel.txt
        └── Grammar.txt
```

Basically: “You go here. You go there. You? Definitely grammar.”

# Tech Stack
- Python 3
- OpenAI Responses API
- Vision model (gpt-4o-mini)
- JSON Schema enforcement
- Base64 image encoding
- File system orchestration
- Structured LLM outputs
- Deterministic validation
- Folder bootstrapping & cleanup
Low budget.
High automation.
Zero manual suffering.

# Environment Setup
Set your API key:
```text
export OPENAI_API_KEY=your_key_here
```

Then run:
- python extract.py
- python category.py
- python bucket.py
Or selectively enable runners inside each script.

# Why This Is Interesting (Technically)
This project explores:
- Vision-based OCR using LLMs (instead of classical OCR)
- Structured schema enforcement
- Multi-stage semantic processing
- LLM as data pipeline engine
- Automated dataset normalization
- LLM-driven taxonomy creation
- Deterministic JSON validation to prevent hallucination chaos

It’s basically: “LLM as a data engineer.”

# Was This Necessary?
Absolutely not.
But:
- It saved hours of manual work.
- It made my French learning structured.
- It turned chaos into hierarchy.
- It let me experiment with multi-stage LLM workflows.
And honestly? Building this was more fun than studying French.

# Possible Future Improvements
- Async batching
- Token usage tracking
- Confidence scoring
- Embedding-based clustering
- Auto flashcard export (Anki-ready)
- Vector search layer
- CLI interface
- Web dashboard
Or I might just pass B2 and retire this repo forever.

Final Note
- This is a side project.
- Built because scrolling through 1000+ screenshots felt illegal.

If you're drowning in messy study material: Just let an LLM suffer for you.
