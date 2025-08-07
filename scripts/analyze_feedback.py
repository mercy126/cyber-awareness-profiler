import json
import os
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Paths
FEEDBACK_PATH = "data/feedback_log.json"
CHART_DIR = "static/charts"
os.makedirs(CHART_DIR, exist_ok=True)

# Load feedback data
with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

feedback_counter = {}
comments = []

for entry in data:
    comments.append(entry.get("comment", ""))
    for f in entry["feedback"]:
        text = f["recommendation"]
        rating = f["user_rating"]
        if text not in feedback_counter:
            feedback_counter[text] = Counter()
        feedback_counter[text][rating] += 1

# Generate bar charts
for rec_text, rating_counts in feedback_counter.items():
    labels = list(rating_counts.keys())
    counts = [rating_counts[l] for l in labels]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, counts, color="lightgreen")
    plt.title(f"Feedback Stats: {rec_text[:30]}")
    plt.ylabel("Count")
    plt.tight_layout()
    filename = os.path.join(CHART_DIR, f"rec_{hash(rec_text)}.png")
    plt.savefig(filename)
    plt.close()

# WordCloud for comments（安全处理版本）
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

all_text = " ".join(comments).strip()

if not all_text:
    print("⚠️ No comments found, skipping word cloud.")
else:
    words = all_text.split()
    filtered = [w.lower() for w in words if w.lower() not in ENGLISH_STOP_WORDS and len(w) > 2]
    word_freq = Counter(filtered)

    if not word_freq:
        print("⚠️ All words removed after filtering. Skipping word cloud.")
    else:
        wc = WordCloud(
            background_color="white",
            width=800,
            height=400
        )
        wc.generate_from_frequencies(word_freq)
        wc.to_file(os.path.join(CHART_DIR, "comment_wordcloud.png"))
        print("✅ Word cloud generated.")
