from flask import Blueprint, render_template, make_response,request
from app.services.behavior_analysis import analyze_behavior  # 引入分析函数
from flask import session  # ← 解决 session 未定义
from app.services.knowledge_assessment import evaluate_knowledge, load_question_bank
from app.services.gap_analysis import identify_blind_spots
from app.services.gap_analysis import build_user_profile
from datetime import datetime
import pdfkit
import json
import os


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('base.html')

def evaluate_attitude(form):
    try:
        values = [int(form.get(f"q{i}", 0)) for i in range(26, 31)]
        score = sum(values) / 5
    except:
        score = 0
    level = "relatively low" if score < 3 else "generally" if score < 4 else "higher"
    bias = "low vigilance type" if score < 3 else "moderately defensive"
    return score, level, bias

@main.route('/submit', methods=['POST'])
def submit():
    form = request.form

    user_type = analyze_behavior(form)

    attitude_score, attitude_level, risk_bias = evaluate_attitude(form)

    # ✅ 保存到 session 中，供后续使用
    session["attitude_score"] = attitude_score
    session["attitude_level"] = attitude_level
    session["risk_bias"] = risk_bias

    return render_template('result.html',
                           result=user_type,
                           attitude_score=attitude_score,
                           attitude_level=attitude_level,
                           risk_bias=risk_bias)

@main.route('/quiz', methods=['POST'])
def quiz():
    user_type = request.form.get("user_type")
    session['user_type'] = user_type
    questions = load_question_bank(user_type)
    return render_template("quiz.html", questions=questions, user_type=user_type)


@main.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    from flask import request, session
    from app.services.knowledge_assessment import evaluate_knowledge, load_question_bank
    from app.services.gap_analysis import build_user_profile
    from app.services.ai_helper import (
        build_prompt_for_ai,
        generate_feedback_from_gpt,
        update_profile_with_feedback
    )
    from app.services.gap_analysis import compute_priority_scores

    user_type = session.get("user_type", "default_user")
    questions = load_question_bank(user_type)
    answers = request.form

    # ✅ 分析分数 + 构建用户画像
    topic_scores, raw_scores = evaluate_knowledge(answers, questions, user_type)
    profile = build_user_profile(topic_scores, raw_scores, user_type)
    priority_scores = compute_priority_scores(
    raw_scores=profile["raw_scores"],
    weights=profile["profile_weights"],
    blind_spots=profile["blind_spots"],
    alpha=1.0, beta=1.0, gamma=1.0 )# 可以调节这三个权重

    profile["priority_scores"] = priority_scores


    # ✅ 加入态度评分
    profile["attitude_score"] = session.get("attitude_score", 0)
    profile["attitude_level"] = session.get("attitude_level", "未知")
    profile["risk_tendency"] = session.get("risk_bias", "未分类")

    # ✅ AI 推荐生成（结构化 JSON：含 text + reason + link）
    try:
        prompt = build_prompt_for_ai(profile)
        feedback = generate_feedback_from_gpt(prompt)
        profile = update_profile_with_feedback(profile, feedback)
    except Exception as e:
        profile["summary"] = "Generation failed, please try again later."
        profile["recommendations"] = [{
            "text": "Unable to generate personalised suggestions",
            "reason": f"Error message:{str(e)}",
            "link": ""
        }]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = "data/profiles"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"profile_{timestamp}.json")

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    return render_template("profile.html", profile=profile)

@main.route('/export_pdf', methods=['POST'])
def export_pdf():
    profile_json = request.form.get("profile_json")
    chart_data_url = request.form.get("chart_img")

    if not profile_json:
        return "Missing profile data", 400

    profile = json.loads(profile_json)

    # ✅ 格式化时间
    generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rendered = render_template(
        "profile_pdf.html",
        profile=profile,
        chart_data=chart_data_url,
        generated_time=generated_time  # ✅ 传入模板变量
    )

    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    pdf = pdfkit.from_string(rendered, configuration=config)

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=cyber_profile.pdf"
    return response

@main.route('/feedback', methods=['POST'])
def feedback_page():
    from flask import request
    profile_json = request.form.get("profile_json")
    if not profile_json:
        return "⚠️ The feedback page cannot be loaded and user data is missing"

    profile = json.loads(profile_json)
    return render_template("feedback.html", profile=profile)

@main.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    form = request.form
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    num_recs = int(form.get("num_recs", 0))
    feedback_list = []

    for i in range(1, num_recs + 1):
        rec_text = form.get(f"recommendation_text_{i}")
        rating = form.get(f"feedback_{i}")
        feedback_list.append({
            "recommendation": rec_text,
            "user_rating": rating
        })

    entry = {
        "submitted_at": timestamp,
        "user_type": form.get("user_type"),
        "blind_spots": form.get("blind_spots"),
        "comment": form.get("comment", ""),
        "feedback": feedback_list
    }

    feedback_file = "data/feedback_log.json"
    os.makedirs("data", exist_ok=True)

    if os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = []
    else:
        data = []

    data.append(entry)

    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return "✅ Thank you for your feedback!<br><a href='/'>Back to Home</a>"

@main.route("/view_feedback_analysis")
def view_feedback_analysis():
    chart_dir = "static/charts"
    if not os.path.exists(chart_dir):
        return "❌ No charts generated yet. Please run analysis script."

    chart_files = [f for f in os.listdir(chart_dir) if f.endswith(".png")]
    chart_files.sort()

    html = "<h2>📊 Feedback Visual Analysis</h2>"
    for img in chart_files:
        html += f"<div><img src='/static/charts/{img}' width='600'><br><hr></div>"
    return html






