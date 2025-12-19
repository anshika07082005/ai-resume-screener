import re

# SKILL CATEGORIES
SKILL_CATEGORIES = {

    "programming_languages": [
        "python", "java", "c", "c++", "c#", "go", "rust",
        "javascript", "typescript", "r", "matlab", "kotlin", "swift"
    ],

    "web_frontend": [
        "html", "css", "sass", "tailwind", "bootstrap",
        "react", "angular", "vue", "next.js"
    ],

    "web_backend": [
        "node", "express", "fastapi", "flask", "django",
        "spring", "spring boot", "graphql", "rest api"
    ],

    "databases": [
        "sql", "mysql", "postgresql", "sqlite", "oracle",
        "mongodb", "redis", "cassandra", "nosql"
    ],

    "data_science_ml": [
        "machine learning", "deep learning", "artificial intelligence",
        "nlp", "computer vision",
        "pandas", "numpy", "scikit-learn",
        "tensorflow", "keras", "pytorch"
    ],

    "big_data": [
        "spark", "hadoop", "kafka", "airflow", "hive"
    ],

    "cloud_devops": [
        "aws", "azure", "gcp",
        "docker", "kubernetes", "terraform",
        "jenkins", "ci/cd"
    ],

    "version_control_os": [
        "git", "github", "gitlab",
        "linux", "bash", "powershell"
    ],

    "testing_quality": [
        "unit testing", "pytest", "selenium", "jest", "cypress"
    ],

    "software_engineering": [
        "oop", "design patterns", "data structures",
        "algorithms", "system design", "microservices"
    ],

    "ai_nlp_tools": [
        "spacy", "nltk", "huggingface",
        "transformers", "bert", "llm"
    ],

    "data_visualization": [
        "matplotlib", "seaborn", "plotly", "power bi", "tableau"
    ],

    "mobile_development": [
    "react native", "expo", "android", "ios",
    "flutter", "swift", "kotlin"
    ],

    "misc": [
        "streamlit", "opencv", "postman", "jira", "figma"
    ]
}

# ALIASES (FUZZY MATCHING)
ALIASES = {
    "python3": "python",
    "js": "javascript",
    "nodejs": "node",
    "postgres": "postgresql",
    "ci cd": "ci/cd",
    "restful api": "rest api",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "cv": "computer vision",
    "expo cli": "react native",
    "android ios": "react native"
}

# CATEGORY WEIGHTS
CATEGORY_WEIGHTS = {
    "programming_languages": 2.0,
    "web_backend": 1.8,
    "data_science_ml": 2.0,
    "cloud_devops": 1.7,
    "databases": 1.6,
    "software_engineering": 1.5,
    "web_frontend": 1.2,
    "big_data": 1.4,
    "testing_quality": 1.0,
    "version_control_os": 0.8,
    "ai_nlp_tools": 1.3,
    "data_visualization": 0.9,
    "mobile_development": 2.0,
    "misc": 0.7
}

#FLATTEN SKILLS
ALL_SKILLS = {}
for category, skills in SKILL_CATEGORIES.items():
    for skill in skills:
        ALL_SKILLS[skill] = category

# 5️⃣ NORMALIZATION

def normalize_text(text: str) -> str:
    text = text.lower()
    for alias, actual in ALIASES.items():
        text = text.replace(alias, actual)
    return text

#SKILL EXTRACTION
def extract_skills(text: str) -> list:
    text = normalize_text(text)
    found = set()

    for skill in ALL_SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            found.add(skill)

    return list(found)

# SKILL WEIGHT LOOKUP
def get_skill_weight(skill: str) -> float:
    category = ALL_SKILLS.get(skill)
    return CATEGORY_WEIGHTS.get(category, 1.0)
