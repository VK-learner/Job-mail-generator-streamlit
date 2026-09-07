# 📧 Cold Email Generator

A Streamlit app that turns any job posting URL into a personalized, ready-to-send internship/application email — automatically matched against your own project portfolio.

🔗 **Live app:** https://job-mail-generator-app-bjsjoim2krdzniy8l6r9v4.streamlit.app/
📂 **Source:** https://github.com/VK-learner/Job-mail-generator-streamlit

---

## ✨ What it does

1. **Paste job URL(s)** — one or more, one per line.
2. **Scrapes** the job page and cleans the raw HTML into plain text.
3. **Extracts structured job data** (role, experience, skills, description) using **Gemini 3.6 Flash** via LangChain, returned as strict JSON. Large pages are automatically chunked to stay within API limits.
4. **Matches your portfolio** — the extracted required skills are embedded and queried against a Chroma vector store built from your own project links (`my_portfolio.csv`), so only the most relevant projects get pulled in.
5. **Generates a personalized email** written in your voice, referencing your real background and the most relevant portfolio links.
6. **Download or track** — export the email as PDF or DOCX, with a running history in the sidebar for the session.

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| LLM orchestration | LangChain |
| LLM inference | Google Gemini (`gemini-3.6-flash`) via `langchain-google-genai` |
| Web scraping | `langchain_community.WebBaseLoader` + BeautifulSoup |
| Vector search / RAG | ChromaDB |
| Data | Pandas |
| Exports | ReportLab (PDF), python-docx (Word) |

---

## 📁 Project Structure

```
├── main.py           # Streamlit UI + orchestration
├── chains.py         # LLM prompts: job extraction + email generation
├── portfolio.py       # Chroma-backed portfolio embedding & retrieval
├── utils.py           # Text cleaning + PDF/DOCX export
├── my_portfolio.csv   # Your projects: Techstack, Links (edit this!)
└── requirements.txt
```

---

## 🚀 Getting Started

### 1. Clone and install

```bash
git clone https://github.com/VK-learner/Job-mail-generator-streamlit.git
cd Job-mail-generator-streamlit
pip install -r requirements.txt
```

### 2. Add your Gemini API key

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

Get a free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey). Note: this is separate from any consumer Gemini app subscription (e.g. one bundled with a telecom plan) — API access is billed/limited through its own Cloud/AI Studio project, so a consumer subscription doesn't automatically raise your API rate limits.

Check current model availability and free-tier limits at [ai.google.dev/pricing](https://ai.google.dev/pricing) before deploying — Google updates the Gemini model lineup and quotas periodically, and older model IDs can be retired for new API keys.

### 3. Personalize your portfolio

Edit `my_portfolio.csv` with your **real** tech stacks and project links so the app can surface work that's actually relevant to the job it's emailing about:

```csv
Techstack,Links
"Python, automation, workflow scripting","https://github.com/yourname/automation-project"
"Embedded C, microcontrollers, PCB design","https://github.com/yourname/embedded-project"
"Java, JavaScript, system troubleshooting","https://github.com/yourname/your-repo"
```

> If you change this file after already running the app once, delete the `vectorstore/` folder first — the embeddings only rebuild when the Chroma collection is empty.

### 4. Update your bio

In `chains.py`, the `write_mail()` prompt describes who's applying (name, background, skills). Edit this block to match you exactly.

### 5. Run it

```bash
streamlit run main.py
```

---

## 📝 Example Usage

1. Paste a job posting URL (e.g. a careers page listing).
2. Click **Generate Emails**.
3. Review the extracted role/skills.
4. Read the generated email, download as PDF/Word, or copy it directly.

---

## ⚠️ Known limitations

- **Large career pages** (e.g. enterprise ATS platforms like Workday, Qualcomm's careers portal) can contain a lot of unrelated text (navigation, other job listings, footers). `chains.py` chunks oversized pages automatically, but very large pages take longer to process since each chunk is a separate API call with a small delay between them.
- **Model/vendor changes**: LLM providers periodically deprecate model IDs and change response formats. If generation suddenly breaks, check the provider's status/changelog page first — it's the most common cause of an otherwise-working app failing without any code changes on your end.

---

## 🙏 Acknowledgements

Built while following [this tutorial](https://youtu.be/CO4E_9V6li0), then extended with:
- Multi-URL batch processing
- PDF/DOCX export
- Session-based email history sidebar
- Progress tracking during generation
- Chunked extraction for large job pages
- Migrated from Groq to Gemini for LLM inference

---

## 📄 License

MIT