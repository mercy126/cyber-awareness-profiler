
# 🔐 Cybersecurity Literacy Profiler

A behavior-driven, personalized recommendation system for cybersecurity awareness.  
Built with **Flask**, powered by **GPT**, and enhanced with user feedback and visual analytics.

---

## 🚀 Overview

This system helps users understand their cybersecurity weaknesses by:

1. **Classifying their behavior patterns** (e.g., social user, remote worker)  
2. **Delivering a customized knowledge assessment**  
3. **Identifying blind spots** through weighted scoring  
4. **Generating personalized recommendations** with traceable explanations  
5. **Collecting structured feedback** and visualizing it for evaluation

---

## 📌 Key Features

- ✅ Behavior-based user classification  
- ✅ Custom question set loading based on user type  
- ✅ Weighted scoring + blind spot detection  
- ✅ Priority-controlled recommendation generation  
- ✅ Explainable recommendations with reasoning  
- ✅ Structured user feedback (Likert-scale + comments)  
- ✅ Automatic feedback visualization (bar charts + word cloud)  
- ✅ Export personalized report as PDF  
- ✅ JSON-based result storage for reproducibility

---

## 🧭 System Workflow

```text
1. User completes behavior questionnaire → system determines user type
2. Loads matching question bank → user completes knowledge test
3. Scores are calculated → low-performing topics (blind spots) identified
4. Each topic is assigned a priority_score for recommendation ordering
5. GPT (or local logic) generates suggestions + explanations
6. User rates each suggestion + optional comments
7. All feedback is saved and visualized
```

---

## 🧱 Tech Stack

| Layer         | Technology                    |
|---------------|-------------------------------|
| Backend       | Python + Flask                |
| Frontend      | HTML + Jinja2 templates       |
| AI Integration| OpenAI GPT-4 (optional)       |
| Data Storage  | JSON (lightweight, editable)  |
| Visualization | `matplotlib`, `wordcloud`     |

---

## 📁 Project Structure

```
├── app/
│   ├── routes.py                  # Flask routes (main logic)
│   ├── ai_helper.py               # GPT interaction + prompt builder
│   ├── knowledge_assessment.py    # Quiz scoring and logic
│   ├── gap_analysis.py            # Profile generation + blind spot logic
│   ├── behavior_analysis.py       # Behavior classification rules
│   └── templates/
│       ├── profile.html           # Result display
│       ├── feedback.html          # User feedback form
│
├── scripts/
│   └── analyze_feedback.py        # Feedback analysis & visualization
│
├── static/
│   └── charts/                    # Generated graphs (bar, word cloud)
│
├── data/
│   ├── feedback_log.json          # Collected user feedback
│   ├── questions_social.json      # Sample question banks
│   └── ...
```

---

## 📊 Feedback Visualization

Run the following script to generate visual feedback summaries:

```bash
python scripts/analyze_feedback.py
```

This will generate:

- 📊 Bar charts showing how users rated each suggestion  
- ☁️ Word cloud summarizing keywords from user comments  
- 📁 Output saved to `static/charts/`, viewable via `/view_feedback_analysis`

---

## 📄 PDF Export

After completing the quiz and receiving personalized recommendations, users can **export a formatted PDF report** containing:

- Their scores  
- Identified blind spots  
- Personalized suggestions + reasoning

---

## 🛠️ Run Locally

1. Clone the repository:

```bash
git clone https://github.com/yourusername/cybersecurity-profiler.git
cd cybersecurity-profiler
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python app.py
```

4. Visit in browser:

```
http://localhost:5000/
```

---
