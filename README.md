# Pitch Perfect
<img width="1400" height="1019" alt="image" src="https://github.com/user-attachments/assets/205fb225-3dc2-4222-aad1-71199a7c268e" />

Pitch Perfect is an AI-powered resume and cover letter tailoring application. It helps job seekers automatically tailor their base LaTeX resume and generate customized cover letters based on specific job descriptions. 

Built with a Streamlit frontend and powered by LangGraph, it provides a seamless workflow from saving your base resume to generating ATS-optimized, high-quality application documents.

## Features

- **User Authentication**: Secure sign-up/log-in powered by Supabase.
- **Base Resume Storage**: Save your standard LaTeX resume to your account to be reused across applications.
- **Live PDF Preview**: Compiles your LaTeX resume using Tectonic on the fly with syntax error detection and suggestions.
- **Job Description Analysis**: Paste any job description to extract required skills, keywords, role titles, and expected tone.
- **ATS Precheck**: Before tailoring, the app compares your base resume against the JD to show baseline ATS fit, matched keywords, and missing keywords.
- **Resume Augmentation Walkthrough**: If your base resume is missing keywords from the JD, Pitch Perfect asks if you have the experience and appends short descriptions to your base resume.
- **AI Tailoring**: Generates a newly optimized LaTeX resume and/or cover letter specifically targeted to the role using OpenAI and LangGraph.
- **Quality Evaluation**: Reviews generated documents for divergence from base, ATS keyword match rate, and professional tone.
- **Document Generation**: Download the final tailored resume and cover letter as ready-to-send PDF files.

## Tech Stack

- **Frontend**: Streamlit
- **AI/Agents**: LangGraph, LangChain, OpenAI
- **Database/Auth**: Supabase
- **Compilation**: Tectonic (LaTeX to PDF)

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.9+
- [Tectonic](https://tectonic-typesetting.github.io/en-US/) for LaTeX compilation

You will also need:
- An [OpenAI API Key](https://platform.openai.com/)
- A [Supabase](https://supabase.com/) project (URL and Anon/Service Keys)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/pitchperfect.git
   cd pitchperfect
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\\Scripts\\activate`
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key

   LANGSMITH_TRACING=true
   LANGSMITH_ENDPOINT=your_langsmith_endpoint
   LANGSMITH_API_KEY=your_langsmith_api_key
   LANGSMITH_PROJECT="your_langsmith_project_name"
   ```

## Usage

Start the Streamlit application:

```bash
streamlit run app.py
```

1. **Sign Up/Log In**: Create an account or log in.
2. **My Resume (Sidebar)**: Paste your base LaTeX code and save it. You can preview the compiled PDF to ensure it's error-free.
3. **New Application**: Paste a job description and select whether you want a tailored resume, a cover letter, or both.
4. **Pre-Tailoring Review**: Review the ATS match. Add missing experience if applicable, or just click "Proceed to Tailoring".
5. **Review**: Check the evaluation summary, look at added content, and download your newly tailored PDF application materials.

## License

This project is licensed under the terms of the LICENSE file included in the repository.
