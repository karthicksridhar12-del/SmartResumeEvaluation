from flask import Flask, render_template, request
import re
from PyPDF2 import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

SKILLS = [
    "python",
    "flask",
    "django",
    "sql",
    "html",
    "css",
    "javascript",
    "java",
    "git",
    "github",
    "rest api",
    "machine learning",
    "artificial intelligence",
    "data analysis",
    "mysql",
    "mongodb",
    "c",
    "c++"
]
EDUCATION = [
    "b.sc",
    "b.tech",
    "b.e",
    "m.sc",
    "m.tech",
    "m.e",
    "mca",
    "mba",
    "bca",
    "computer science",
    "information technology"
]
EXPERIENCE_KEYWORDS = [
    "fresher",
    "internship",
    "intern",
    "experience",
    "work experience",
    "years of experience",
    "software developer",
    "python developer",
    "web developer"
]


def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def extract_text_from_docx(file):
    document = Document(file)
    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def find_skills(text):
    text = text.lower()
    found_skills = []

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills

def find_experience(text):
    text = text.lower()
    found_experience = []

    for keyword in EXPERIENCE_KEYWORDS:
        pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"

        if re.search(pattern, text):
            found_experience.append(keyword)

    return found_experience
def calculate_similarity(resume_text, job_description):
    documents = [resume_text, job_description]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    return round(similarity * 100)


def find_education(text):
    text = text.lower()
    found_education = []

    for education in EDUCATION:
        pattern = r"(?<!\w)" + re.escape(education) + r"(?!\w)"

        if re.search(pattern, text):
            found_education.append(education)

    return found_education

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():
    resume = request.files.get("resume")
    job_description = request.form.get("job_description")

    if not resume:
        return "Please upload a resume."

    filename = resume.filename.lower()

    if filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(resume)
    elif filename.endswith(".docx"):
        resume_text = extract_text_from_docx(resume)
    else:
        return "Please upload a PDF or DOCX file."

    resume_skills = find_skills(resume_text)
    resume_education = find_education(resume_text)
    resume_experience = find_experience(resume_text)

    similarity_score = calculate_similarity(
        resume_text,
        job_description
    )

    job_skills = find_skills(job_description)

    matched_skills = [
        skill for skill in job_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill for skill in job_skills
        if skill not in resume_skills
    ]

    if len(job_skills) > 0:
        total_points = len(job_skills) * 10
        earned_points = len(matched_skills) * 10
        score = round((earned_points / total_points) * 100)
    else:
        score = 0
    if missing_skills:
        recommendation = (
            "To improve your match, consider adding these skills if you have knowledge of them: "
            + ", ".join(missing_skills) + "."
        )
    else:
        recommendation = "Excellent! Your resume matches all the required skills."

    return render_template(
        "result.html",
        score=score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        education=resume_education,
        experience=resume_experience,
        similarity_score=similarity_score,
        recommendation=recommendation
    )


if __name__ == "__main__":
    app.run(debug=True)