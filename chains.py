import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


class Chain:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in environment or Streamlit secrets.")

        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=api_key,
            # llama-3.1-8b-instant was deprecated by Groq and shut down on 08/16/2026.
            # openai/gpt-oss-20b is Groq's recommended 1:1 replacement.
            model_name="openai/gpt-oss-20b",
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
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

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
        return res.content


if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))