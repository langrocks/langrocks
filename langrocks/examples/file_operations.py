from langrocks.client.files import FileOperations
from langrocks.common.models.files import FileMimeType

DATA = r"""
\documentclass[a4paper,10pt]{article}
\usepackage[a4paper,margin=0.75in]{geometry}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{hyperref}
\usepackage{multicol}

% Define a custom title format for each section
\titleformat{\section}{\large\bfseries}{}{0em}{}[\titlerule]
\setlength{\parindent}{0pt}
\setlength{\parskip}{1em}

\begin{document}

% Contact Information
\begin{center}
    {\LARGE John Doe} \\
    \href{mailto:johndoe@example.com}{johndoe@example.com} \\
    (123) 456-7890 \\
    \href{https://linkedin.com/in/johndoe}{linkedin.com/in/johndoe} \\
    \href{https://github.com/johndoe}{github.com/johndoe} \\
    123 Main Street, Anytown, USA
\end{center}

% Education
\section*{Education}

\textbf{Bachelor of Science in Computer Science} \\
University of Anytown \\
Graduated: May 2024 \\
\begin{itemize}[leftmargin=*, itemsep=0pt]
    \item GPA: 3.8/4.0
    \item Relevant Coursework: Data Structures, Algorithms, Databases, Machine Learning
\end{itemize}

% Experience
\section*{Experience}

\textbf{Software Engineer Intern} \\
Tech Solutions Inc., Anytown, USA \\
June 2023 - August 2023
\begin{itemize}[leftmargin=*, itemsep=0pt]
    \item Developed a web application using React and Node.js that improved user engagement by 20\%.
    \item Collaborated with a team of 5 engineers to design and implement new features.
    \item Conducted code reviews and provided feedback to peers.
\end{itemize}

\textbf{Research Assistant} \\
Department of Computer Science, University of Anytown \\
January 2023 - May 2023
\begin{itemize}[leftmargin=*, itemsep=0pt]
    \item Assisted in research on machine learning algorithms for natural language processing.
    \item Co-authored a paper published in the International Journal of AI Research.
    \item Presented findings at the annual Computer Science Research Conference.
\end{itemize}

% Skills
\section*{Skills}
\begin{multicols}{2}
\begin{itemize}[leftmargin=*, itemsep=0pt]
    \item Programming Languages: Python, Java, C++
    \item Web Development: HTML, CSS, JavaScript, React, Node.js
    \item Tools: Git, Docker, Jenkins
    \item Data Analysis: SQL, Pandas, NumPy
\end{itemize}
\end{multicols}

% Projects
\section*{Projects}

\textbf{Personal Portfolio Website} \\
\begin{itemize}[leftmargin=*, itemsep=0pt]
    \item Developed a responsive website using HTML, CSS, and JavaScript to showcase my projects and skills.
    \item Integrated a contact form that allows visitors to send messages directly to my email.
\end{itemize}

\textbf{Machine Learning Model for Predicting Housing Prices} \\
\begin{itemize}[leftmargin=*, itemsep=0pt]
    \item Built a regression model using Python and scikit-learn to predict housing prices based on historical data.
    \item Achieved an accuracy of 92\% on the test dataset.
    \item Visualized data and results using Matplotlib and Seaborn.
\end{itemize}

\end{document}
"""


with FileOperations("localhost:50051") as fops:
    print("\nRunning file converter")

    # Convert file
    print("Converting file")
    response = fops.convert_file(
        data=DATA.encode(),
        filename="resume.tex",
        input_mime_type=FileMimeType.LATEX,
        output_mime_type=FileMimeType.PDF,
    )

    # with open(response.name, "wb") as f:
    #     f.write(response.data)
    print("Response", response)
