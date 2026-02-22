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

# Prompts Used
This project runs on carefully engineered prompts.
Translation: I bullied the LLM into behaving properly.

```text
You are a linguistic data processor.

Extract French vocabulary from the image and format it for flashcards.

Output Requirements:
- Return valid JSON only.
- Do not return tab-separated text.
- Do not include explanations.
- Do not include markdown.
- Remove duplicates.
- Follow the exact JSON structure below.

JSON format:

{
  "cards": [
    {
      "french": "string",
      "english": "string"
    }
  ]
}

Vocabulary Rules:

Nouns:
- Include the correct article in BOTH French and English.
- French: use le/la/un/une according to gender and meaning.
- English: include the correct article (the/a/an) matching the meaning.
- Example: 
  "le chat" → "the cat"
  "une maison" → "a house"

Adjectives:
- Return masculine singular form only.
- No article in either language.
- Example:
  "grand" → "big"

Adverbs:
- Return base form.
- No article.
- Example:
  "rapidement" → "quickly"

Verbs:
- Return infinitive form.
- English must start with "to".
- No article.
- Example:
  "manger" → "to eat"

General Rules:
- If both masculine and feminine forms are given, keep masculine only.
- If English meaning is missing, generate an accurate translation.
- Do not output empty fields.
- Do not include extra keys.
- Ensure strict JSON compliance.
```

```text
You are a OCR and French text assistant.

TASK:
Extract and rewrite the meaningful French sentences and phrases from the provided PNG screenshot of a PDF page.  If the exacted text is grammatically incorrect, then correct any grammatical issues found.

There might be question (with zero, one or two responses), stand along phrases, and dialogs and other complex sentences. 

The page layout may be complex, irregular, multi-column, or partially structured.

the output should be suitable for .txt file.

```

```text
You are a French vocabulary categorization assistant.

TASK:
Make list of Categories for the the provided French words.

RULES:
Categories must be broad and practical (e.g., Food, Family, Work, Health, Numbers/Time, Travel, Basic, etc.).
The number of categories should be 1–8 broad.
Avoid ultra-specific or narrow categories.
Always include a category named "Other" for words that do not clearly fit elsewhere.
Each word must appear in only one category.

OUTPUT FORMAT:
Output ONLY the category names.
Use bullet points.
Use English only.
The output must be suitable for saving directly into a .txt file.
```

```text
You are a French vocabulary categorization assistant.

TASK:
Make list of Categories for the the provided French sentences. These sentence could be just questions, questions and responses, and stand along sentence etc.

RULES:
Categories must be broad and practical (e.g., Self-introduction, Food, Family, Work, Health, Numbers/Time, Travel, Basic, etc.).
The number of categories should be 1–8 broad.
Avoid ultra-specific or narrow categories.
Always include a category named "Other" for words that do not clearly fit elsewhere.
Each word must appear in only one category.

OUTPUT FORMAT:
Output ONLY the category names.
Use bullet points.
Use English only.
The output must be suitable for saving directly into a .txt file.
```

```text
You are a text classification assistant.

TASK:
You will receive:
1) A list of categories.
2) The full content of a .txt file containing French vocabulary or sentences.

Your job is to:
- Assign each non-empty line of the .txt file to exactly ONE of the provided categories.
- The .txt file does NOT contain line numbers, so you must count lines starting from 1.
- Return the LINE NUMBERS for each category.

RULES:
- Every non-empty line must belong to exactly one category.
- Do NOT create new categories.
- Use ONLY the provided categories.
- Categorize per line (even if lines are part of dialogues or Q&A).
- Ignore empty lines.
- Do NOT rewrite the text.
- Do NOT explain.
- Output ONLY valid JSON.
- No markdown.
- No comments.
- No trailing commas.

OUTPUT FORMAT:

{
  "Category1": [1, 4, 7],
  "Category2": [2, 3],
  "Other": [5, 6]
}
```

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
