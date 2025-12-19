# 🧠 AI Resume Screener

AI Resume Screener is a full-stack web application that automates resume screening using AI. It helps recruiters and hiring teams quickly analyze resumes, 
extract key information, and evaluate candidates efficiently through an intuitive frontend and a robust backend API.


## 🚀 Project Overview
Manual resume screening is time-consuming and often inconsistent. AI Resume Screener solves this problem by using AI models to parse resumes, 
extract important candidate details, and evaluate resumes based on relevance.  

The project follows a **frontend–backend architecture**:
- **Frontend**: HTML, CSS, and JavaScript for user interaction  
- **Backend**: FastAPI (Python) for resume processing and AI integration


## ✨ Features
- 📄 Upload resumes for automated screening  
- 🤖 AI-based resume evaluation and analysis  
- 🧠 Automatic extraction of candidate details (name, email, skills, etc.)  
- 📊 Display of processed results in a user-friendly interface  
- ⚙️ Modular backend for easy AI model integration  
- 🔌 API-based design for scalability and future extensions
  

## 🏗️ Project Structure
```text

ai-resume-screener/
│
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── requirements.txt     # Backend dependencies
│   └── ...                  # API logic and utilities
│
├── frontend-html/
│   ├── index.html           # Frontend UI
│   ├── style.css            # Styling
│   ├── script.js            # Frontend logic
│
├── README.md                # Project documentation
└── .gitignore
