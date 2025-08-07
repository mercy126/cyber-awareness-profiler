# ✅ gap_analysis.py
from scipy.spatial.distance import cosine
from scipy.stats import pearsonr
import numpy as np
from .knowledge_assessment import USER_TOPIC_WEIGHTS

def analyze_similarity(raw_scores: dict, user_weights: dict):
    """
    计算用户得分向量与权重向量（归一化）之间的相似度：
    - 余弦相似度衡量结构是否一致
    - 皮尔逊相关性衡量掌握重点是否正确
    """
    keys = sorted(raw_scores.keys())
    user_vec = np.array([raw_scores[k] for k in keys])
    ideal_vec = np.array([user_weights.get(k, 1.0) for k in keys])
    ideal_vec = ideal_vec / np.max(ideal_vec)  # 归一化处理

    cos_sim = 1 - cosine(user_vec, ideal_vec)
    pearson_corr, _ = pearsonr(user_vec, ideal_vec)

    return {
        "cosine_similarity": round(cos_sim, 3),
        "pearson_correlation": round(pearson_corr, 3)
    }

def identify_blind_spots(topic_scores, threshold=0.6):
    return [topic for topic, score in topic_scores.items() if score < threshold]

def build_user_profile(topic_scores, raw_scores, user_type):
    user_weights = USER_TOPIC_WEIGHTS.get(user_type, {})
    similarity = analyze_similarity(raw_scores, user_weights)
    blind_spots = identify_blind_spots(topic_scores)

    return {
    "user_type": user_type,
    "scores": topic_scores,
    "raw_scores": raw_scores,
    "profile_weights": user_weights,
    "blind_spots": blind_spots,
    "cosine_similarity": similarity["cosine_similarity"],
    "pearson_correlation": similarity["pearson_correlation"],
    "summary": "",
    "recommendations": []
}

def compute_priority_scores(raw_scores, weights, blind_spots, alpha=1.0, beta=1.0, gamma=1.0):
    """
    根据三个因素计算每个主题的推荐优先级分数 priority_score：
    priority_score = α × (1 - raw_score) + β × weight + γ × 盲区标志
    """
    scores = {}
    for topic in raw_scores:
        raw = raw_scores.get(topic, 0)
        w = weights.get(topic, 1.0)
        is_blind = topic in blind_spots
        score = alpha * (1 - raw) + beta * w + gamma * (1 if is_blind else 0)
        scores[topic] = round(score, 3)
    return scores

def map_score_to_priority(score):
    """
    将 priority_score 分数映射为 priority 级别（1~5）
    """
    if score >= 3.5:
        return 1
    elif score >= 2.5:
        return 2
    elif score >= 1.5:
        return 3
    elif score >= 1.0:
        return 4
    else:
        return 5


