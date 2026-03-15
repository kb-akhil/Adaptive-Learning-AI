# 🎓 AgenticLearn – Adaptive Learning Path Generator

> A multi-agent AI system that analyzes a student's prior knowledge through syllabus analysis and generates a personalized, adaptive learning path.

---

## 🏗️ System Architecture

```
Student → Upload Syllabus PDF
       → [PDF Extractor] → Text
       → [TF-IDF Agent] → Topics
       → [Question Generator Agent (FLAN-T5 + RAG)] → MCQ/TF Questions
       → Student Answers Questions
       → [Performance Analysis Agent] → Weak/Strong Topics + Accuracy
       → [Learning Path Agent] → Ordered Modules (Priority-Based + Cognitive Map)
       → [AI Tutor Agent (Gemini)] → Explanations on demand
```

---

## 🤖 Multi-Agent Architecture

| Agent | Technology | Purpose |
|---|---|---|
| **Question Generator Agent** | Fine-tuned FLAN-T5 + RAG | Generates MCQ and True/False questions |
| **Performance Analysis Agent** | Python logic | Calculates accuracy, weak/strong topics |
| **Learning Path Agent** | Priority algorithm + Cognitive Map | Generates ordered learning modules |
| **AI Tutor Agent** | Gemini API | Answers student questions |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Python |
| Frontend | React (Vite) + Tailwind CSS |
| AI Model | FLAN-T5 Base (fine-tuned) |
| Database | SQLite + SQLAlchemy |
| PDF Extraction | PyMuPDF (fitz) |
| Keyword Extraction | TF-IDF (scikit-learn) |
| AI Tutor | Gemini 1.5 Flash API |
| Auth | JWT (python-jose) |

---

## 📁 Project Structure

```
AgenticLearn/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration
│   ├── requirements.txt
│   ├── agents/
│   │   ├── question_agent.py      # FLAN-T5 question generator
│   │   ├── performance_agent.py   # Performance analyzer
│   │   ├── path_agent.py          # Learning path generator
│   │   └── tutor_agent.py         # Gemini AI tutor
│   ├── services/
│   │   ├── pdf_extractor.py       # PyMuPDF text extraction
│   │   ├── keyword_extractor.py   # TF-IDF keyword extraction
│   │   └── rag_engine.py          # RAG for question retrieval
│   ├── models/
│   │   ├── user.py
│   │   ├── syllabus.py
│   │   └── assessment.py
│   ├── routes/
│   │   ├── auth.py                # POST /auth/login, /auth/register
│   │   ├── upload.py              # POST /upload/syllabus
│   │   ├── assessment.py          # GET /assessment/generate, POST /submit
│   │   ├── learning_path.py       # GET /learning-path/{id}
│   │   └── tutor.py               # POST /tutor/ask
│   ├── database/
│   │   └── db.py
│   └── model_training/
│       ├── train_model.py         # FLAN-T5 fine-tuning script
│       └── dataset_loader.py      # 150+ CN Q&A dataset
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── pages/
        │   ├── Login.jsx
        │   ├── Upload.jsx
        │   ├── Assessment.jsx
        │   ├── LearningPath.jsx
        │   └── Tutor.jsx
        ├── components/
        │   ├── Navbar.jsx
        │   ├── QuestionCard.jsx
        │   └── ModuleCard.jsx
        └── services/
            └── api.js
```

---

## 🚀 Setup & Running

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) NVIDIA GPU with CUDA (RTX 3050 recommended)

---

### 1. Clone / Extract Project
```bash
cd AgenticLearn
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt



# Run the backend
uvicorn main:app --reload
```

Backend runs at: **http://localhost:8000**
API Docs at: **http://localhost:8000/docs**

---

### 3. Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

### 4. (Optional) Train FLAN-T5 Model

```bash
cd backend
python model_training/train_model.py

# Test after training:
python model_training/train_model.py --test
```

> Training takes ~10-20 minutes on RTX 3050.
> If you skip training, the system uses the FLAN-T5 base model with rule-based fallback.

---

## 🔑 Getting a Gemini API Key

1. Go to [https://aistudio.google.com/](https://aistudio.google.com/)
2. Sign in with Google
3. Click "Get API Key"
4. Copy the key and set it as `GEMINI_API_KEY` environment variable

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, get JWT token |
| POST | `/upload/syllabus` | Upload PDF syllabus |
| GET | `/upload/syllabi` | List user's syllabi |
| GET | `/assessment/generate/{id}` | Generate questions from syllabus |
| POST | `/assessment/submit` | Submit answers, get analysis |
| GET | `/assessment/result/{id}` | Get assessment result |
| GET | `/learning-path/{id}` | Get learning path |
| GET | `/learning-path/latest/me` | Get latest learning path |
| POST | `/tutor/ask` | Ask AI Tutor |

---

## 🧠 Algorithms Used

| Algorithm | Where Used |
|---|---|
| **TF-IDF** | Keyword extraction from syllabus |
| **RAG (TF-IDF cosine similarity)** | Retrieve relevant question prompts |
| **Priority-Based Algorithm** | Order topics in learning path (weak first) |
| **Cognitive Mapping** | Map topics to subtopics and resources |

---

## 💻 Hardware Requirements

| Component | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| GPU | None (CPU mode) | RTX 3050 4GB |
| Storage | 5 GB | 10 GB |
| Python | 3.10 | 3.11 |

---

## 👨‍💻 User Flow

```
1. Register / Login
2. Upload Course Syllabus PDF
3. System extracts topics using TF-IDF
4. Take AI-generated assessment (MCQ + T/F)
5. View performance: accuracy, weak/strong topics
6. Receive personalized learning path
7. Study modules (weak topics first)
8. Ask AI Tutor for explanations anytime
```

---

## 📝 Notes

- The AI model is trained on Computer Networks but works for any subject via rule-based fallback
- Gemini API is used only for the AI Tutor chat feature
- All other AI (question generation) uses local FLAN-T5
- SQLite database requires no separate server
