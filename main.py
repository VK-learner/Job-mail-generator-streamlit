import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from datetime import datetime
import json
import os

from chains import Chain
from portfolio import Portfolio
from utils import clean_text, export_to_pdf, export_to_docx

st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stTextArea textarea { font-size: 14px; }
    .email-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .history-item {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        cursor: pointer;
    }
    .badge {
        background: #667eea;
        color: white;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)


def init_session():
    if "email_history" not in st.session_state:
        st.session_state.email_history = []


def save_to_history(url, role, email):
    st.session_state.email_history.append({
        "timestamp": datetime.now().strftime("%b %d, %H:%M"),
        "url": url,
        "role": role,
        "email": email,
    })


def create_streamlit_app(llm, portfolio, clean_text):
    init_session()

    # ── Sidebar ─────────────────────────────────────────────────────────────
    with st.sidebar:
        st.title("📧 Cold Email Generator")
        st.markdown("---")
        st.subheader("⚙️ Settings")
        num_results = st.slider("Portfolio links per email", 1, 5, 2)
        st.markdown("---")

        # History panel
        st.subheader(f"📋 Email History ({len(st.session_state.email_history)})")
        if not st.session_state.email_history:
            st.info("No emails generated yet.")
        else:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.email_history = []
                st.rerun()
            for i, item in enumerate(reversed(st.session_state.email_history)):
                with st.expander(f"📄 {item['role']} · {item['timestamp']}"):
                    st.caption(item["url"])
                    st.code(item["email"], language="markdown")

    # ── Main area ────────────────────────────────────────────────────────────
    st.title("📧 Cold Email Generator")
    st.markdown("Generate personalized internship emails from any job posting URL.")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🔗 Job URLs")
        urls_input = st.text_area(
            "Enter one URL per line:",
            placeholder="https://jobs.nike.com/job/R-33460\nhttps://careers.google.com/...",
            height=120,
        )

    with col2:
        st.subheader("ℹ️ How it works")
        st.markdown("""
1. Paste one or more job URLs
2. Click **Generate Emails**
3. Emails are matched to your portfolio
4. Download as PDF or Word doc
        """)

    generate_btn = st.button("🚀 Generate Emails", type="primary", use_container_width=True)

    if generate_btn:
        urls = [u.strip() for u in urls_input.strip().splitlines() if u.strip()]
        if not urls:
            st.warning("Please enter at least one URL.")
            return

        portfolio.load_portfolio()
        progress = st.progress(0, text="Starting...")

        for idx, url in enumerate(urls):
            progress.progress((idx) / len(urls), text=f"Processing {idx+1}/{len(urls)}: {url[:60]}...")
            st.markdown(f"### 🔍 Job {idx+1}: `{url}`")

            try:
                with st.spinner("Scraping job page..."):
                    loader = WebBaseLoader([url])
                    data = clean_text(loader.load().pop().page_content)

                with st.spinner("Extracting job details..."):
                    jobs = llm.extract_jobs(data)

                for job_idx, job in enumerate(jobs):
                    role = job.get("role", "Unknown Role")
                    skills = job.get("skills", [])
                    description = job.get("description", "")

                    st.markdown(f"**Role:** {role}")
                    if skills:
                        st.markdown(f"**Skills:** {', '.join(skills) if isinstance(skills, list) else skills}")

                    with st.spinner("Writing your email..."):
                        links = portfolio.query_links(skills, n_results=num_results)
                        email = llm.write_mail(job, links)

                    save_to_history(url, role, email)

                    with st.expander(f"📧 Email for: {role}", expanded=True):
                        st.code(email, language="markdown")

                        dl_col1, dl_col2 = st.columns(2)
                        with dl_col1:
                            pdf_data = export_to_pdf(email, role)
                            st.download_button(
                                "⬇️ Download PDF",
                                data=pdf_data,
                                file_name=f"email_{role.replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                key=f"pdf_{idx}_{job_idx}",
                            )
                        with dl_col2:
                            docx_data = export_to_docx(email, role)
                            st.download_button(
                                "⬇️ Download Word",
                                data=docx_data,
                                file_name=f"email_{role.replace(' ', '_')}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True,
                                key=f"docx_{idx}_{job_idx}",
                            )

            except Exception as e:
                st.error(f"❌ Error processing `{url}`: {e}")

        progress.progress(1.0, text="✅ All done!")


if __name__ == "__main__":
    os.environ.setdefault("USER_AGENT", "cold-email-generator/1.0")
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)
