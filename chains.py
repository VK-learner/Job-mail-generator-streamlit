import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Gemini's free tier is far more generous than Groq's free-tier gpt-oss-20b
# (8000 TPM), so chunking is a safety net here rather than a hard requirement -
# but kept for very large pages. Check current limits at ai.google.dev/pricing,
# since Google updates model availability and quotas periodically.
CHARS_PER_TOKEN_ESTIMATE = 4
MAX_INPUT_TOKENS_PER_CALL = 40000
MAX_INPUT_CHARS_PER_CALL = MAX_INPUT_TOKENS_PER_CALL * CHARS_PER_TOKEN_ESTIMATE


def _chunk_text(text, max_chars=MAX_INPUT_CHARS_PER_CALL):
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)] or [text]


def _get_text_content(content):
    """Newer Gemini models (3.x) return content as a list of content blocks
    (e.g. [{"type": "text", "text": "...", "extras": {...}}]) instead of a
    plain string. Normalize either shape into plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
        return "".join(parts)
    return str(content)


def _clean_json_response(content):
    """Strip markdown code fences and leading/trailing stray text so
    JsonOutputParser gets pure JSON even if the model doesn't follow
    the 'no preamble' instruction exactly."""
    text = _get_text_content(content).strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


class Chain:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set in environment or Streamlit secrets.")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            temperature=0,
            google_api_key=api_key,
        )

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm

        chunks = _chunk_text(cleaned_text)
        all_jobs = []
        seen_roles = set()
        last_error_detail = None

        for i, chunk in enumerate(chunks):
            try:
                res = chain_extract.invoke(input={"page_data": chunk})
                raw = _get_text_content(res.content)
                json_parser = JsonOutputParser()
                parsed = json_parser.parse(_clean_json_response(res.content))
            except Exception as e:
                # Keep a snippet of what actually came back so the eventual
                # error message tells us why, instead of a generic failure.
                snippet = ""
                try:
                    snippet = _get_text_content(res.content)[:200]
                except Exception:
                    pass
                last_error_detail = f"{type(e).__name__}: {e} | response snippet: {snippet!r}"
                continue

            for job in (parsed if isinstance(parsed, list) else [parsed]):
                role = job.get("role")
                if role and role not in seen_roles:
                    seen_roles.add(role)
                    all_jobs.append(job)

            # Small pause between chunks as a courtesy against the 10 RPM limit;
            # rarely triggered since chunks are large relative to Gemini's budget.
            if i < len(chunks) - 1:
                time.sleep(2)

        if not all_jobs:
            raise OutputParserException(
                f"Context too big. Unable to parse jobs. Last failure: {last_error_detail}"
            )
        return all_jobs

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are Vaibhav Kulkarni, an Electronics & Communication Engineering graduate (PDA College of
            Engineering, Kalaburagi, 2022-2026) specializing in edge AI and intelligent systems. You bridge
            hardware and software, deploying optimized AI models to IoT/embedded devices and building
            LLM-powered applications. You recently completed an IoT & Robotics Engineering internship at Unlox.
            You are open to internships, freelance projects, and full-time roles in Python/AI development.

            In your email, highlight:
            - Your background and technical skills (Python, TensorFlow/TFLite, OpenCV, YOLO, LangChain, Streamlit,
              Raspberry Pi, Embedded C, Java, JavaScript) spanning computer vision, edge AI, IoT, and LLM applications.
            - Your enthusiasm for applying these skills to real-world projects in the company.
            - Your interest in contributing to the company's mission and learning from industry professionals.
            - The most relevant ones from the following links to showcase your portfolio or related work: {link_list}

            Write a professional internship application email addressed to the hiring team.
            Do not provide a preamble.
            ### EMAIL (NO PREAMBLE):
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return _get_text_content(res.content)


if __name__ == "__main__":
    print(os.getenv("GOOGLE_API_KEY"))