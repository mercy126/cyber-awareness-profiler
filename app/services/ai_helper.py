import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from app.services.gap_analysis import map_score_to_priority

load_dotenv()

def build_prompt_for_ai(profile: dict) -> str:
    user_type = profile.get("user_type", "未知类型")
    attitude = profile.get("attitude_level", "未知")
    risk_pref = profile.get("risk_tendency", "未标明")
    scores = profile.get("scores", {})
    blind_spots = profile.get("blind_spots", [])
    cosine_sim = profile.get("cosine_similarity", "N/A")
    pearson_sim = profile.get("pearson_correlation", "N/A")

    score_str = "\n".join([f"- {k}: {v:.2f}" for k, v in scores.items()])
    blind_spot_str = "、".join(blind_spots) if blind_spots else "无明显盲区"
    raw_score_str = "\n".join([f"- {k}: {v:.2f}" for k, v in profile.get("raw_scores", {}).items()])
    weight_str = "\n".join([f"- {k}: {v:.1f}" for k, v in profile.get("profile_weights", {}).items()])
    priority_lines = []
    for topic, score in profile.get("priority_scores", {}).items():
     pr = map_score_to_priority(score)
    priority_lines.append(f"- {topic}: score={score:.2f} → priority={pr}")
    priority_str = "\n".join(priority_lines)


    prompt = f"""
你是一位网络安全教育专家，请根据以下用户画像，提供结构化安全建议（带推荐理由）。
注意，建议要个性化，语言要能让普通用户能够理解。
同时原因解释也通俗一点，但是一定要让用户能够清晰的知道他在哪些安全知识方面的欠缺。

👤 用户类型：{user_type}
🧠 安全态度等级：{attitude}
⚠️ 风险偏向：{risk_pref}
📊 各维度得分（压缩后）：
{score_str}

📉 原始分数（未压缩，反映掌握强度）：
{raw_score_str}

🎯 用户应优先掌握的主题（权重）：
{weight_str}

🚩 知识盲区：
{blind_spot_str}
🚦 推荐优先级评分（越高越优先）：
- Phishing Awareness: score=3.9 → priority=1
- 2FA Authentication: score=2.6 → priority=2
- Data Breach Awareness: score=1.4 → priority=4
📐 
- 结构一致性（余弦相似度）: {cosine_sim}
- 重点掌握趋势（皮尔逊相关）: {pearson_sim}

请生成 JSON 结构，格式如下（不要添加说明文字）：

{{
  "summary": "一句话总结用户网络安全能力",
  "recommendations": [
    {{
      "text": "建议内容",
      "reason": "为什么给出这个建议",
      "link": "https://推荐网站"
      "priority": 1
    }}
  ]
}}

⚠️ 注意：
- `priority` 范围为 1~5，1 表示最高优先级
- 1 表示“非常紧急”（如：分数低 + 重要）
- 3 表示“一般建议”
- 5 表示“次要建议或已有掌握”；
- 建议数量建议 2~5 条；
- 用英文生成。
"""
    return prompt.strip()


def generate_feedback_from_gpt(prompt: str, model="gpt-4o") -> dict:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    content = response.choices[0].message.content.strip()

    print("🔍 GPT 返回内容：")
    print(content)

    try:
        json_part = re.search(r"\{[\s\S]*\}", content).group()
        parsed = json.loads(json_part)
        return parsed
    except Exception as e:
        return {
            "summary": "生成失败，请稍后重试。",
            "recommendations": [{"text": "无法生成建议", "reason": f"⚠️ GPT 返回无效 JSON：{str(e)}", "link": ""}]
        }


def update_profile_with_feedback(profile: dict, feedback: dict) -> dict:
    recs = feedback.get("recommendations", [])
    recs_sorted = sorted(recs, key=lambda r: r.get("priority", 3))  # 默认 priority=3
    profile["summary"] = feedback.get("summary", "")
    profile["recommendations"] = recs_sorted

    return profile


