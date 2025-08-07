from pathlib import Path
import json
import math

# ✅ 模块顶层定义权重表，可供其他模块（如 gap_analysis）引用
USER_TOPIC_WEIGHTS = {
    "social_user": {
        "Password management": 1.0, "2FA authentication": 1.2, "Phishing Awareness": 1.3,
        "Security Attitude": 1.2, "Privacy Control": 1.5, "Content Visibility Awareness": 1.3
    },
    "content_creator": {
        "Password management": 1.0, "2FA authentication": 1.2, "Phishing Awareness": 1.2,
        "Content Backup": 1.3, "Copyright Protection": 1.5, "Content Sharing Permissions": 1.2
    },
    "remote_worker": {
        "Password management": 1.3, "2FA authentication": 1.2, "Phishing Awareness": 1.2,
        "Cloud Collaboration Permissions": 1.3, "Sensitive Document Handling": 1.5, "Device Login Security": 1.3
    },
    "passive_browser": {
        "Password management": 1.0, "Phishing Awareness": 1.5, "Ad Tracking Protection": 1.3,
        "Source Evaluation": 1.2, "Data Breach Awareness": 1.2, "Security Attitude": 1.2
    },
    "hybrid_user": {
        "Password management": 1.2, "2FA authentication": 1.2, "Phishing Awareness": 1.2,
        "Cloud Collaboration Permissions": 1.2, "Content Sharing Permissions": 1.2,
        "Data Breach Awareness": 1.2, "Security Attitude": 1.2
    }
}


def load_question_bank(user_type):
    QUIZ_FILE_MAP = {
        "social_user": "social_user_quiz_bank.json",
        "content_creator": "content_creator_quiz_bank.json",
        "remote_worker": "cloud_worker_quiz_bank.json",
        "passive_browser": "browser_user_quiz_bank.json",
        "hybrid_user": "mixed_user_quiz_bank.json"
    }

    filename = QUIZ_FILE_MAP.get(user_type)
    if not filename:
        return []
    path = Path("data/processed") / filename
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return list(data.values())[0]


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def evaluate_knowledge(answers, questions, user_type):
    topic_scores = {}
    topic_weights = {}

    for q in questions:
        qid = q.get("id")
        topic = q.get("topic")
        correct = q.get("answer")
        qtype = q.get("type")
        weight = float(q.get("weight", 1.0))

        if not all([qid, topic, correct, qtype]):
            continue

        if qtype == "single":
            user_answer = answers.get(qid)
            score = 1.0 if user_answer == correct else 0.0

        elif qtype == "multi":
            correct_set = set(correct)
            user_set = set(answers.getlist(qid)) if qid in answers else set()
            tp = len(user_set & correct_set)
            fp = len(user_set - correct_set)
            score = max((tp - fp) / len(correct_set), 0.0)

        else:
            score = 0.0

        topic_scores[topic] = topic_scores.get(topic, 0.0) + score * weight
        topic_weights[topic] = topic_weights.get(topic, 0.0) + weight

    # 平滑参数
    PRIOR_SCORE = 0.6
    PRIOR_WEIGHT = 2.0

    final_scores = {}
    raw_scores = {}

    from .knowledge_assessment import USER_TOPIC_WEIGHTS
    user_weights = USER_TOPIC_WEIGHTS.get(user_type, {})

    for topic in topic_scores:
        # 平滑平均
        avg_score = (topic_scores[topic] + PRIOR_SCORE * PRIOR_WEIGHT) / (topic_weights[topic] + PRIOR_WEIGHT)

        # 乘权系数
        multiplier = user_weights.get(topic, 1.0)

        raw = avg_score * multiplier

        # ✅ 改进点：不再用 sigmoid，而是 capped = 1.0 的真实分
        final_scores[topic] = round(min(raw, 1.0), 3)
        raw_scores[topic] = round(raw, 3)

    return final_scores, raw_scores

def get_user_topics(user_type):
    return list(set(q['topic'] for q in load_question_bank(user_type)))
