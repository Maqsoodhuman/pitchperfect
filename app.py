"""
Pitch Perfect — Streamlit entry point.

Single-file app that handles auth state and page routing.
Each page is a function called based on st.session_state.
"""

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from app.auth import sign_up, sign_in, sign_out
from app.storage import get_resume, save_resume
from app.pdf import compile_latex
from app.latex_errors import parse_tectonic_error


# ============================================================
# Page config
# ============================================================

st.set_page_config(
    page_title="Pitch Perfect",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ============================================================
# Session state initialization
# ============================================================

def _init_session_state() -> None:
    """Ensure all required session keys exist with safe defaults."""
    defaults = {
        "user_id": None,
        "access_token": None,
        "email": None,
        "current_page": "new_application",  # default page after login
        "last_result": None,  # final state from the most recent graph run
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_init_session_state()


# ============================================================
# Helpers
# ============================================================

def is_logged_in() -> bool:
    return st.session_state["user_id"] is not None


def logout() -> None:
    sign_out()
    for key in ("user_id", "access_token", "email", "last_result"):
        st.session_state[key] = None
    st.session_state["current_page"] = "new_application"
    st.rerun()


# ============================================================
# Page: Auth (login / signup)
# ============================================================

def page_auth() -> None:
    st.title("🎯 Pitch Perfect")
    st.caption("AI-powered resume and cover letter tailoring")

    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        st.subheader("Log in to your account")
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pw")
            submitted = st.form_submit_button("Log in", type="primary")

        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
                return
            result = sign_in(email, password)
            if result.success:
                st.session_state["user_id"] = result.user_id
                st.session_state["access_token"] = result.access_token
                st.session_state["email"] = email
                st.rerun()
            else:
                st.error(result.error)

    with tab_signup:
        st.subheader("Create a new account")
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input(
                "Password (min 6 characters)", type="password", key="signup_pw"
            )
            submitted = st.form_submit_button("Sign up", type="primary")

        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
                return
            if len(password) < 6:
                st.error("Password must be at least 6 characters.")
                return
            result = sign_up(email, password)
            if result.success:
                st.session_state["user_id"] = result.user_id
                st.session_state["access_token"] = result.access_token
                st.session_state["email"] = email
                st.success("Account created! Redirecting...")
                st.rerun()
            else:
                st.error(result.error)


# ============================================================
# Page: My Resume (placeholder for next step)
# ============================================================

def page_my_resume() -> None:
    st.title("My Resume")
    st.caption("Paste your base LaTeX resume here. It's saved to your account and reused for every job application.")

    # Load the existing resume if any
    existing = get_resume(st.session_state["user_id"])

    if existing is None:
        st.warning(
            "⚠️ You don't have a saved resume yet. "
            "Paste your LaTeX resume below and click Save."
        )
    else:
        st.success(f"✅ Resume saved ({len(existing)} characters)")

    # Textarea pre-filled with existing content (or empty)
    resume_text = st.text_area(
        label="LaTeX source",
        value=existing or "",
        height=500,
        placeholder=r"\documentclass{article}\begin{document}...\end{document}",
        help="Must be a complete, compilable LaTeX document starting with \\documentclass and ending with \\end{document}.",
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("💾 Save resume", type="primary", use_container_width=True):
            if not resume_text.strip():
                st.error("Resume cannot be empty.")
                return
            if "\\documentclass" not in resume_text or "\\end{document}" not in resume_text:
                st.error(
                    "This doesn't look like a complete LaTeX document. "
                    "It must contain \\documentclass and \\end{document}."
                )
                return
            save_resume(st.session_state["user_id"], resume_text)
            st.success("Resume saved!")
            st.rerun()

    with col2:
        if st.button("🔍 Preview PDF", use_container_width=True):
            if not resume_text.strip():
                st.error("Nothing to preview.")
                return
            with st.spinner("Compiling with Tectonic..."):
                try:
                    pdf_bytes = compile_latex(resume_text)
                    st.session_state["_resume_preview_pdf"] = pdf_bytes
                    st.session_state["_resume_preview_error"] = None
                    st.success("✅ Compiled successfully")
                except Exception as e:
                    parsed = parse_tectonic_error(str(e), resume_text)
                    st.session_state["_resume_preview_pdf"] = None
                    st.session_state["_resume_preview_error"] = parsed

    # Render compile error below the buttons if one exists
    err = st.session_state.get("_resume_preview_error")
    if err:
        st.divider()
        st.error(f"**LaTeX compilation failed**\n\n{err.explanation}")

        if err.line_number and err.offending_line:
            st.markdown(f"**Line {err.line_number}:**")
            st.code(err.offending_line, language="latex")

        if err.suggested_fix:
            st.markdown("**Suggested fix:**")
            st.markdown(err.suggested_fix)

        with st.expander("Show raw Tectonic output"):
            st.code(err.raw, language="text")
    # Show preview PDF if one was just compiled
    preview = st.session_state.get("_resume_preview_pdf")
    if preview:
        st.divider()
        st.subheader("Preview")
        st.download_button(
            label="⬇️ Download preview PDF",
            data=preview,
            file_name="resume_preview.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        # Try inline PDF display
        import base64
        b64 = base64.b64encode(preview).decode()
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{b64}" '
            f'width="100%" height="600" style="border:1px solid #ddd;border-radius:8px;"></iframe>',
            unsafe_allow_html=True,
        )

# ============================================================
# Page: New Application (placeholder)
# ============================================================
def page_new_application() -> None:
    st.title("New Application")
    st.caption("Paste a job description below and generate a tailored resume and/or cover letter.")

    # Gate: user must have a saved resume first
    existing_resume = get_resume(st.session_state["user_id"])
    if existing_resume is None:
        st.warning(
            "⚠️ You need to save a base resume first before generating an application. "
            "Go to **My Resume** in the sidebar."
        )
        if st.button("Go to My Resume", type="primary"):
            st.session_state["current_page"] = "my_resume"
            st.rerun()
        return

    # JD input
    jd_text = st.text_area(
        label="Job description",
        value=st.session_state.get("_last_jd_text", ""),
        height=350,
        placeholder="Paste the full job description here, including requirements, responsibilities, and any nice-to-haves...",
        help="The more complete the JD, the better the tailoring. Include requirements, responsibilities, and company context.",
    )

    # Request type
    request_type_label = st.radio(
        "What do you want to generate?",
        options=["Both resume and cover letter", "Tailored resume only", "Cover letter only"],
        index=0,
        horizontal=False,
    )

    # Map friendly label to state value
    request_type_map = {
        "Both resume and cover letter": "both",
        "Tailored resume only": "resume",
        "Cover letter only": "cover_letter",
    }
    request_type = request_type_map[request_type_label]

    # Generate button
    if st.button("🚀 Generate", type="primary", use_container_width=True):
        if not jd_text.strip():
            st.error("Please paste a job description.")
            return
        if len(jd_text.strip()) < 100:
            st.error(
                "That job description looks very short. "
                "Please paste the complete JD (typically 300+ characters)."
            )
            return

        # Stash the JD so the user doesn't lose it if generation fails
        st.session_state["_last_jd_text"] = jd_text

        _run_graph_and_redirect(jd_text, request_type)


def _run_graph_and_redirect(jd_text: str, request_type: str) -> None:
    """
    Invoke the LangGraph pipeline, store the result in session state,
    and navigate to the Review page.
    """
    from app.graph import graph

    initial_state = {
        "user_id": st.session_state["user_id"],
        "jd_text": jd_text,
        "request_type": request_type,
        "retry_count": 0,
        # base_resume is loaded from the DB by the intake node
    }

    with st.spinner("Generating your application... this usually takes 20-40 seconds."):
        try:
            final_state = graph.invoke(initial_state)
        except Exception as e:
            st.error(
                f"**Generation failed**\n\n"
                f"Something went wrong while running the agent pipeline.\n\n"
                f"```\n{str(e)[:800]}\n```\n\n"
                f"Your JD and resume are still saved. Try again, or check that your resume compiles in the My Resume page."
            )
            return

    # Save result to session state and navigate
    st.session_state["last_result"] = final_state
    st.session_state["current_page"] = "review"
    st.rerun()

# ============================================================
# Page: Review (placeholder)
# ============================================================

def page_review() -> None:
    st.title("Review")

    result = st.session_state.get("last_result")
    if result is None:
        st.info(
            "No application to review yet. "
            "Go to **New Application** to generate a tailored resume and cover letter."
        )
        if st.button("New Application", type="primary"):
            st.session_state["current_page"] = "new_application"
            st.rerun()
        return

    _render_evaluation_summary(result)
    st.divider()
    _render_added_items(result)
    st.divider()
    _render_keyword_coverage(result)
    st.divider()
    _render_generated_outputs(result)
    st.divider()
    _render_next_actions()


# ============================================================
# Review page sections
# ============================================================

def _render_evaluation_summary(result: dict) -> None:
    """Top banner with pass/fail and scores."""
    report = result.get("eval_report") or {}
    passed = report.get("passed", False)

    if passed:
        st.success("✅ Your application passed all quality checks")
    else:
        st.warning("⚠️ Your application has quality issues — see below")

    # Three score cards side by side
    col1, col2, col3 = st.columns(3)

    divergence = report.get("divergence_score", 0)
    ats = report.get("ats_score", 0)
    tone = report.get("tone_score", 0)

    with col1:
        st.metric(
            label="Divergence from base",
            value=f"{divergence:.0%}",
            help="1.0 = no changes from base. Lower = more aggressive rewriting. Informational only.",
        )
    with col2:
        st.metric(
            label="ATS keyword match",
            value=f"{ats:.0%}",
            help="Fraction of JD keywords present in your tailored output. Minimum is 60%.",
        )
    with col3:
        st.metric(
            label="Tone",
            value=f"{tone:.0%}",
            help="Clarity and professionalism. Minimum is 60%.",
        )

    retries = result.get("retry_count", 0)
    st.caption(f"Generated in {retries} attempt{'s' if retries != 1 else ''}.")

    # Blocking issues (rare — only shown if something is truly broken)
    issues = report.get("issues", [])
    if issues:
        st.warning("**Issues found:**")
        for issue in issues:
            st.markdown(f"- {issue}")


def _render_added_items(result: dict) -> None:
    """Transparency panel: what the tailor added vs base resume."""
    report = result.get("eval_report") or {}
    added = report.get("added_items", [])

    st.subheader("Added Content")
    if not added:
        st.caption("The tailored output uses only content from your base resume. Nothing new was added.")
        return

    st.caption(
        "These items appear in the tailored output but are NOT in your base resume. "
        "They were added to improve JD relevance. Review them and decide if you want to keep them."
    )
    for item in added:
        st.markdown(f"- **{item}**")

    st.info(
        "💡 In a future update, you'll be able to confirm each item individually — "
        "add it to your base resume if you have the experience, or remove it from this application."
    )


def _render_keyword_coverage(result: dict) -> None:
    """Matched and missing JD keywords."""
    report = result.get("eval_report") or {}
    matched = report.get("matched_keywords", [])
    missing = report.get("missing_keywords", [])

    st.subheader("Keyword Coverage")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**✅ Matched ({len(matched)})**")
        if matched:
            st.markdown("\n".join(f"- {kw}" for kw in matched))
        else:
            st.caption("(none)")

    with col2:
        st.markdown(f"**❌ Missing ({len(missing)})**")
        if missing:
            st.markdown("\n".join(f"- {kw}" for kw in missing))
            st.caption(
                "Missing keywords weren't added because they're not in your base resume. "
                "If you have genuine experience with any of them, add them to your base resume."
            )
        else:
            st.caption("All JD keywords are covered.")


def _render_generated_outputs(result: dict) -> None:
    """Compile and display the tailored resume and cover letter PDFs."""
    st.subheader("Generated Documents")

    tailored = result.get("tailored_resume_tex")
    cover = result.get("cover_letter_tex")

    if not tailored and not cover:
        st.warning("No documents were generated.")
        return

    # Use tabs so both documents are accessible without huge scroll
    tabs = []
    if tailored:
        tabs.append("📄 Tailored Resume")
    if cover:
        tabs.append("✉️ Cover Letter")

    tab_objects = st.tabs(tabs)
    idx = 0

    if tailored:
        with tab_objects[idx]:
            _render_document_tab(tailored, filename="tailored_resume.pdf", key="resume")
        idx += 1

    if cover:
        with tab_objects[idx]:
            _render_document_tab(cover, filename="cover_letter.pdf", key="cover")


def _render_document_tab(tex: str, filename: str, key: str) -> None:
    """Compile LaTeX, show download button, and render inline PDF preview."""
    try:
        pdf_bytes = compile_latex(tex)
    except Exception as e:
        parsed = parse_tectonic_error(str(e), tex)
        st.error(f"**PDF generation failed**\n\n{parsed.explanation}")
        if parsed.line_number and parsed.offending_line:
            st.markdown(f"**Line {parsed.line_number}:**")
            st.code(parsed.offending_line, language="latex")
        if parsed.suggested_fix:
            st.markdown("**Suggested fix:**")
            st.markdown(parsed.suggested_fix)
        with st.expander("Show raw Tectonic output"):
            st.code(parsed.raw, language="text")

        # Still offer the raw .tex as a fallback download
        st.download_button(
            label="⬇️ Download .tex source",
            data=tex,
            file_name=filename.replace(".pdf", ".tex"),
            mime="text/plain",
            use_container_width=True,
            key=f"tex_dl_{key}",
        )
        return

    # Download button
    st.download_button(
        label="⬇️ Download PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        use_container_width=True,
        type="primary",
        key=f"pdf_dl_{key}",
    )

    # Inline preview via base64 iframe
    import base64
    b64 = base64.b64encode(pdf_bytes).decode()
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{b64}" '
        f'width="100%" height="700" style="border:1px solid #ddd;border-radius:8px;"></iframe>',
        unsafe_allow_html=True,
    )


def _render_next_actions() -> None:
    """Buttons to start a new run or go back."""
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Application", use_container_width=True, type="primary"):
            st.session_state["last_result"] = None
            st.session_state["_last_jd_text"] = ""
            st.session_state["current_page"] = "new_application"
            st.rerun()
    with col2:
        if st.button("✏️ Edit My Resume", use_container_width=True):
            st.session_state["current_page"] = "my_resume"
            st.rerun()

# ============================================================
# Sidebar + routing
# ============================================================

def render_sidebar() -> None:
    st.sidebar.title("Pitch Perfect")

    if is_logged_in():
        st.sidebar.caption(f"Logged in as **{st.session_state['email']}**")
        st.sidebar.divider()

        pages = {
            "New Application": "new_application",
            "My Resume": "my_resume",
            "Review": "review",
        }
        for label, key in pages.items():
            if st.sidebar.button(label, use_container_width=True):
                st.session_state["current_page"] = key
                st.rerun()

        st.sidebar.divider()
        if st.sidebar.button("Log out", use_container_width=True):
            logout()
    else:
        st.sidebar.info("Please log in to continue.")


def render_current_page() -> None:
    if not is_logged_in():
        page_auth()
        return

    page = st.session_state["current_page"]
    if page == "my_resume":
        page_my_resume()
    elif page == "new_application":
        page_new_application()
    elif page == "review":
        page_review()
    else:
        st.error(f"Unknown page: {page}")


# ============================================================
# Main
# ============================================================

render_sidebar()
render_current_page()