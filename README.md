# Job Mail Generator (Streamlit)

Generate custom internship/job application emails using AI, with automatic job description and portfolio extraction from URLs.

## Features
- Enter any job or internship posting URL and receive tailored draft emails for outreach.
- Uses LangChain and Groq API for role extraction and context-aware generation.
- Connects your own portfolio/CV links for personalization.
- Built with Streamlit (easy to run and deploy on cloud or locally).

## How it works
1. Paste a job/internship URL into the app.
2. LangChain + Groq automatically extract job responsibilities and role requirements.
3. Your pre-configured portfolio links are loaded from `my_portfolio.csv`.
4. Personalized cold/internship mails are generated for each role.

## Usage
1. Clone this repo and install requirements (`pip install -r requirements.txt`).
2. Prepare a `.env` file with your API key (`GROQ_API_KEY=...`). __Do not upload `.env` to GitHub!__
3. Fill or replace `my_portfolio.csv` with your portfolio/profile links.
4. Run `streamlit run main.py`.

## Tech Stack
- Python 3.X
- Streamlit
- LangChain
- Groq API
- Pandas/CSV for easy portfolio import

## Security Note
Your `.env` file holds your secret API key and must always be kept private (see `.gitignore`). Never commit it to GitHub or share it publicly.

## Example
1. You paste this internship URL: `https://internshala.com/job/detail/data-scientist-internship-at-acme-corp`
2. The app extracts key requirements like "Python, data analysis, machine learning..."
3. Generates emails with your work samples and skills pre-inserted for every matching role.

---
Final-year Electronics & Communication student project. For any queries, open an Issue or contact [VK-learner](https://github.com/VK-learner).
