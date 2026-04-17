"""
Sample resume and job description used for Phase 1 agent testing.
Replace SAMPLE_RESUME_TEX with your own resume later.
"""


SAMPLE_RESUME_TEX = r"""\documentclass[11pt, letterpaper]{article}

% Packages:
\usepackage[
    ignoreheadfoot, % set margins without considering header and footer
    top=0.8 cm, % seperation between body and page edge from the top
    bottom=1.5 cm, % seperation between body and page edge from the bottom
    left=1.5 cm, % seperation between body and page edge from the left
    right=1.5 cm, % seperation between body and page edge from the right
    footskip=1.0 cm, % seperation between body and footer
    % showframe % for debugging 
]{geometry} % for adjusting page geometry
\usepackage{titlesec} % for customizing section titles
\usepackage{tabularx} % for making tables with fixed width columns
\usepackage{array} % tabularx requires this
\usepackage[dvipsnames]{xcolor} % for coloring text
\definecolor{primaryColor}{RGB}{0, 0, 0} % define primary color
\usepackage{enumitem} % for customizing lists
\usepackage{amsmath} % for math
\usepackage[
    pdftitle={Mohammed Maqsood Ahmed's CV},
    pdfauthor={Mohammed Maqsood Ahmed},
    pdfcreator={LaTeX with RenderCV},
    colorlinks=true,
    urlcolor=primaryColor
]{hyperref} % for links, metadata and bookmarks
\usepackage[pscoord]{eso-pic} % for floating text on the page
\usepackage{calc} % for calculating lengths
\usepackage{bookmark} % for bookmarks
\usepackage{lastpage} % for getting the total number of pages
\usepackage{changepage} % for one column entries (adjustwidth environment)
\usepackage{paracol} % for two and three column entries
\usepackage{ifthen} % for conditional statements
\usepackage{needspace} % for avoiding page brake right after the section title
\usepackage{iftex} % check if engine is pdflatex, xetex or luatex

% Ensure that generate pdf is machine readable/ATS parsable:
\ifPDFTeX
    \input{glyphtounicode}
    \pdfgentounicode=1
    \usepackage[T1]{fontenc}
    \usepackage[utf8]{inputenc}
\fi

\usepackage{helvet}
\usepackage{ragged2e}
% Some settings:
\justifying
\AtBeginEnvironment{adjustwidth}{\partopsep0pt} % remove space before adjustwidth environment
\pagestyle{empty} % no header or footer
\setcounter{secnumdepth}{0} % no section numbering
\setlength{\parindent}{0pt} % no indentation
\setlength{\topskip}{0pt} % no top skip
\setlength{\columnsep}{0.15cm} % set column seperation
\pagenumbering{gobble} % no page numbering

\titleformat{\section}{\needspace{4\baselineskip}\bfseries\large}{}{0pt}{}[\vspace{1pt}\titlerule]

\titlespacing{\section}{
    % left space:
    -1pt
}{
    % top space:
    0.3 cm
}{
    % bottom space:
    0.2 cm
} % section title spacing

\renewcommand\labelitemi{$\vcenter{\hbox{\small$\bullet$}}$} % custom bullet points
\newenvironment{highlights}{
    \begin{itemize}[
        topsep=0.01 cm,
        parsep=0.01 cm,
        partopsep=0pt,
        itemsep=0pt,
        leftmargin=0 cm + 10pt
    ]
}{
    \end{itemize}
} % new environment for highlights


\newenvironment{highlightsforbulletentries}{
    \begin{itemize}[
        topsep=0.05 cm,
        parsep=0.10 cm,
        partopsep=0pt,
        itemsep=0pt,
        leftmargin=5pt
    ]
}{
    \end{itemize}
} % new environment for highlights for bullet entries

\newenvironment{onecolentry}{
    \begin{adjustwidth}{
        0 cm + 0.00001 cm
    }{
        0 cm + 0.00001 cm
    }
}{
    \end{adjustwidth}
} % new environment for one column entries

\newenvironment{twocolentry}[2][]{
    \onecolentry
    \def\secondColumn{#2}
    \setcolumnwidth{\fill, 4.5 cm}
    \begin{paracol}{2}
}{
    \switchcolumn \raggedleft \secondColumn
    \end{paracol}
    \endonecolentry
} % new environment for two column entries

\newenvironment{threecolentry}[3][]{
    \onecolentry
    \def\thirdColumn{#3}
    \setcolumnwidth{, \fill, 4.5 cm}
    \begin{paracol}{3}
    {\raggedright #2} \switchcolumn
}{
    \switchcolumn \raggedleft \thirdColumn
    \end{paracol}
    \endonecolentry
} % new environment for three column entries

\newenvironment{header}{
    \setlength{\topsep}{0pt}\par\kern\topsep\centering\linespread{1.5}
}{
    \par\kern\topsep
} % new environment for the header

\newcommand{\placelastupdatedtext}{% \placetextbox{<horizontal pos>}{<vertical pos>}{<stuff>}
  \AddToShipoutPictureFG*{% Add <stuff> to current page foreground
    \put(
        \LenToUnit{\paperwidth-2 cm-0 cm+0.05cm},
        \LenToUnit{\paperheight-1.0 cm}
    ){\vtop{{\null}\makebox[0pt][c]{     
        \small\color{gray}\textit{Last updated in January 2025}\hspace{\widthof{Last updated in January 2025}}
    }}}%
  }%
}%

% save the original href command in a new command:
\let\hrefWithoutArrow\href

% new command for external links:


\begin{document}
    \newcommand{\AND}{\unskip
        \cleaders\copy\ANDbox\hskip\wd\ANDbox
        \ignorespaces
    }
    \newsavebox\ANDbox
    \sbox\ANDbox{$|$}

\begin{header}98
    \fontsize{25 pt}{25 pt}\selectfont Mohammed Maqsood Ahmed

    \vspace{5 pt}

    \normalsize
    \mbox{Buffalo, NY }%
    \AND%
    \kern 5.0 pt%
    \mbox{\hrefWithoutArrow{mailto:maqsoodhuman@gmail.com}{maqsoodhuman@gmail.com}}%
    \kern 5.0 pt%
    \AND%
    \kern 5.0 pt%
    \mbox{\hrefWithoutArrow{tel:+1-716-812-9130}{(716) 812-9130}}%
    \kern 5.0 pt%
    \AND%
    \kern 5.0 pt%
    \mbox{\hrefWithoutArrow{https://linkedin.com/in/maqsoodhuman}{linkedin.com/in/maqsoodhuman}}%
    \kern 5.0 pt%
    \AND%
    \kern 5.0 pt%
    \mbox{\hrefWithoutArrow{https://maqsoodhuman.com}{maqsoodhuman.com}}%
    
\end{header}

    \vspace{7 pt - 0.3 cm}


\section{Summary}

\begin{onecolentry}
AI/ML Engineer with 4+ years of industry experience building scalable cloud-native systems, ML pipelines, and intelligent automation. Pursuing an MS in Computer Science (AI/ML) at the University at Buffalo (4.0 GPA). Active researcher in computer vision, deep learning, NLP, and distributed systems across two university labs, with hands-on experience shipping generative AI and workflow automation at enterprise scale.
\end{onecolentry}
\vspace{0.1 cm}

    \section{Education}

\begin{twocolentry}{
    Aug 2025 – May 2027
}
    \textbf{Master of Science in Computer Science (AI/ML)}, University at Buffalo - NY
    
    \textit{GPA: 4.0/4.0}
\end{twocolentry}

\vspace{0.20 cm}

\begin{twocolentry}{
    Aug 2016 – May 2020
}
    \textbf{B.Tech in Computer Science}, Mahatma Gandhi Institute of Technology - India
\end{twocolentry}


  \section{Experience}

\vspace{0.10 cm}

        \begin{twocolentry}{
            Feb 2026 – Present
        }
            \textbf{AI Research Assistant},Under Prof Wenyao Xu, University at Buffalo - NY\end{twocolentry}

\vspace{0.10 cm}
\begin{onecolentry}
    \begin{highlights}
        \item Conducting multi-modal research on AI-driven clinical sensing, spanning wound infection detection and intelligent ICU monitoring systems.
    \end{highlights}
\end{onecolentry}

\vspace{0.10 cm}

        \begin{twocolentry}{
            Jan 2026 – Present
        }
            \textbf{Research Assistant}, CAVAS Lab, University at Buffalo - NY\end{twocolentry}

\vspace{0.10 cm}
\begin{onecolentry}
    \begin{highlights}
        \item Developing a multi-client distributed simulation framework for Digital Twin–based autonomous vehicle testing using CARLA and ROS 2, synchronizing vehicle state and sensor streams across networked server instances.
        \item Implementing containerized CARLA deployments using Docker for multi-node simulation orchestration and building telemetry ingestion pipelines for offline analysis and model training..
        \item Integrating LiDAR and camera sensor fusion pipelines within the ROS 2 middleware stack, supporting perception modules for connected autonomous vehicle evaluation.
    \end{highlights}
\end{onecolentry}

\vspace{0.10 cm}
        \begin{twocolentry}{
            Jan 2021 – June 2025
        }
            \textbf{Senior Cloud Engineer (ML)}, LTIMindtree | Portland General Electric - India\end{twocolentry}

\vspace{0.10 cm}
\begin{onecolentry}
    \begin{highlights}
        \item Designed and deployed cloud-native solutions across multiple enterprise projects, replacing legacy systems with scalable, event-driven architectures on AWS, achieving 30\% cost reduction and 99.9\% uptime.
        \item Built more than 100 high-performance APIs and serverless ETL pipelines, improving outage detection and customer alerting speed by $\sim$40\% for over 500K+ customers.
        \item Designed and maintained ELT pipelines using Matillion to efficiently ingest and transform large-scale data into Snowflake, supporting analytics and operational reporting.
        \item Developed distributed data pipelines on Databricks leveraging Apache Spark and Delta Lake, optimizing query performance by 50\% through adaptive query execution and Z-ordering techniques.
        \item Implemented anomaly detection and real-time alerting in the energy trading platform, reducing trading risks by 25\% through early detection of pricing anomalies.
        \item Collaborated with data science teams to automate hydro and budget forecasting models, reducing report time from 3 hours to 20 minutes.
        \item Developed and deployed smart meter–based proactive outage alert system using AWS and Twilio, with fault-tolerant pipelines (DLQ, SQS, SNS) handling $\sim$2M daily events and reducing storm-time calls by 35\% while minimizing data loss by 80\%.
        \item Architected real time Socket APIs and integrated Amazon Kendra with AWS Bedrock (Claude); delivered a Generative AI assistant for natural language queries
        \item Automated CI/CD pipelines (Jenkins) across all the environments, reducing deployment time by 60\%.
    \end{highlights}
\end{onecolentry}


        \vspace{0.4 cm}

        \begin{twocolentry}{
            March 2019 – Oct 2019
        }
            \textbf{Cloud Intern}, Grepthor Software Solutions -- Hyderabad, India\end{twocolentry}

        \vspace{0.10 cm}
        \begin{onecolentry}
            \begin{highlights}
            \item Collaborated with cross functional teams to execute cloud migration initiatives on AWS, enhancing scalability and performance.
            \item Implemented and maintained AWS CloudWatch monitoring alarms and dashboards tracking 15+ key metrics, reducing incident response time by 30\% and improving application uptime.
            \item Engineered event-driven, serverless architectures leveraging AWS Lambda, Amazon S3, and Amazon SNS, enabling modular, scalable, and cost-efficient cloud solutions.
            \end{highlights}
        \end{onecolentry}


\section{Projects}

\vspace{0.1 cm}
\vspace{0.1 cm}

\begin{samepage}
    \begin{twocolentry}{
        2026
    }
        \textbf{PriceWatch}, AI-Powered Amazon Price Intelligence Agent - \href{https://github.com/maqsoodhuman/pricewatch}{GitHub}
    \end{twocolentry}

    \vspace{0.10 cm}
    \begin{onecolentry}
Developed an AI-powered Amazon price monitor using Playwright, GPT-4o-mini, and ChromaDB; deployed a scalable, fault-tolerant system via Docker Compose with n8n orchestration and a real-time webhook dashboard.
    \end{onecolentry}
\end{samepage}

\begin{samepage}
    \begin{twocolentry}{
        2026
    }
        \textbf{Hybrid KG Augmented Question Answering System}
    \end{twocolentry}

    \vspace{0.10 cm}
    \begin{onecolentry}
Developed a question answering system that combines retrieval-augmented generation with knowledge graph reasoning, using a confidence-weighted router to dynamically select the optimal knowledge source. Leveraged dense retrieval, vector search, and a transformer-based reader for accurate answer extraction across diverse query types.
    \end{onecolentry}
\end{samepage}
\begin{samepage}
    \begin{twocolentry}{
        2025
    }
        \textbf{RefFlag}, AI-Powered Chrome Extension - \href{https://bit.ly/4iDcACq}{GitHub} 
        
    \end{twocolentry}

    \vspace{0.10 cm}
    \begin{onecolentry}
Built browser extension using Chrome Extension API (Manifest V3) with background service workers for DOM manipulation and text extraction. Integrated LLM inference endpoints for real-time privacy policy analysis using prompt engineering and semantic chunking. Implemented asynchronous content script injection with MutationObserver for dynamic page monitoring 
    \end{onecolentry}
\end{samepage}
\vspace{0.10 cm}
\begin{samepage}
    \begin{twocolentry}{
        2025
    }
        \textbf{ClearThinker AI}, Serverless AI Decision Coach - \href{https://astonishing-kangaroo-7d3e26.netlify.app} {Demo}
    \end{twocolentry}

    \vspace{0.10 cm}
    \begin{onecolentry}
Built a scalable serverless cognitive bias detection system (1,000+ sessions) using React, AWS Lambda, API Gateway, DynamoDB, and CloudWatch, integrating Anthropic Claude via AWS Bedrock for real-time Socratic dialogue and bias analysis.
    \end{onecolentry}
\end{samepage}

\vspace{0.1 cm}

\section{Awards and Publications}

\begin{samepage}
    \begin{twocolentry}{
        2025
    }
        \textbf{MolFM-Lite: Multi-Modal Molecular Property Prediction}
    \end{twocolentry}

    \vspace{0.10 cm}
    \begin{onecolentry}
        Developed a lightweight multi-modal deep learning model integrating 1D, 2D, and 3D molecular representations using cross-attention and FiLM conditioning. - \href{https://arxiv.org/abs/2602.22405}{arxiv.org/abs/2602.22405}
        
    \end{onecolentry}
\end{samepage}

\begin{samepage}
    \begin{twocolentry}{
        2024
    }
        \textbf{Shooting Star Award}, LTIMindtree
    \end{twocolentry}

    \vspace{0.10 cm}
    \begin{onecolentry}
        Recipient of the Shooting Star Award for key contributions in the Cloud Pillar at LTIMindtree.
    \end{onecolentry}
\end{samepage}




\begin{samepage}
    \begin{twocolentry}{
        2022
    }
        \textbf{An Approach to Translate Human Gestures into Telugu}
    \end{twocolentry}

    \begin{onecolentry}
        Published in \textit{International Journal of Scientific and Technology Research (IJSTR)}.  
        \href{https://bit.ly/4nTIJHY}{IJSTR Link}
    \end{onecolentry}
\end{samepage}

\begin{samepage}
    \begin{twocolentry}{
        2021
    }
        \textbf{Question Answering System using Deep Learning}
    \end{twocolentry}

    \vspace{0.10 cm}
    \begin{onecolentry}
        Published in \textit{Journal of Xidian University}.  
        \href{https://bit.ly/44RHArw}{Journal Link}
    \end{onecolentry}
\end{samepage}
    
\section{Technical Skills}

\begin{onecolentry}

\textbf{Languages:} Python, Java, JavaScript, TypeScript, SQL, Bash/Shell

\textbf{AI/ML \& Data Science:} PyTorch, Hugging Face Transformers, LangChain, RAG, PySpark, Pandas, NumPy, Optuna, OpenClaw

\textbf{Databases:} PostgreSQL, MySQL, Snowflake, DynamoDB, Pinecone, ChromaDB

\textbf{Frameworks \& Tools:} FastAPI, Spring, React, REST APIs, Postman, JMeter

\textbf{Cloud (AWS):} EC2, Lambda, API Gateway, S3, RDS,
Step Functions, EventBridge, SNS, SQS,
Glue, SageMaker, Bedrock, Kendra, OpenSearch,
IAM, VPC, CloudWatch, CloudFormation

\textbf{Data Platforms:} Databricks, Delta Lake, Apache Spark, Data Lakes, Matillion


\textbf{DevOps \& Infrastructure:} Docker, Kubernetes, Terraform, CI/CD (Jenkins), Git, Playwright, n8n
\end{onecolentry}

\section{Certifications}

\begin{onecolentry}
    \small % Optional: adjust size to fit
    \begin{tabular}{@{} p{0.5\textwidth} p{0.5\textwidth} @{}}
        $\bullet$ Oracle Generative AI Professional & $\bullet$ AWS Solutions Architect \\
        $\bullet$ AWS Developer Associate & $\bullet$ Deep Learning (IIT Madras) \\
        $\bullet$ Oracle AI Fundamentals Associate & $\bullet$ AWS Databricks Platform Architect \\
        $\bullet$ Databricks AI Agent & \\
    \end{tabular}
\end{onecolentry}

\end{document}
"""


SAMPLE_JD = """Senior Python Developer — CloudScale Inc.

About the Role
CloudScale is hiring a Senior Python Developer to join our platform team.
You'll design and build scalable microservices that power our core product,
used by thousands of engineering teams worldwide.

Requirements
- 4+ years of Python experience
- Strong experience with FastAPI or Flask
- Solid knowledge of PostgreSQL, including query optimization
- Experience deploying services to AWS (ECS, Lambda, or EKS)
- Comfortable with Docker and container-based workflows

Nice to Have
- Kubernetes experience
- Redis or other caching technologies
- Experience mentoring junior engineers
- Contributions to open-source projects

Responsibilities
- Design, build, and maintain Python microservices
- Optimize database queries and API performance
- Review code and mentor junior developers
- Collaborate with product and design on new features

We value clear writing, thoughtful engineering, and a bias for shipping.
"""