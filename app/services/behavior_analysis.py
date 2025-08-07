def analyze_behavior(form):
    scores = {
        '社交活跃者': 0,
        '内容创作者': 0,
        '云文档/远程办公者': 0,
        '被动信息浏览者': 0,
        '混合型用户': 0
    }

    f = form

    # Q1
    q1 = f.get('q1')
    if q1 == 'B': scores['社交活跃者'] += 1
    elif q1 == 'C': scores['社交活跃者'] += 2
    elif q1 == 'D':
        scores['社交活跃者'] += 3
        scores['混合型用户'] += 1

    # Q2
    for v in f.getlist('q2'):
        if v == 'browse': scores['被动信息浏览者'] += 1
        if v == 'like': scores['社交活跃者'] += 1
        if v == 'post': scores['社交活跃者'] += 2
        if v == 'add': scores['社交活跃者'] += 2

    # Q3-Q5
    if f.get('q3') == 'B': scores['社交活跃者'] += 1
    elif f.get('q3') == 'C': scores['社交活跃者'] += 2
    elif f.get('q3') == 'D': scores['社交活跃者'] += 3

    if f.get('q4') == 'B': scores['社交活跃者'] += 1
    elif f.get('q4') == 'C': scores['社交活跃者'] += 2

    if f.get('q5') == 'B': scores['社交活跃者'] += 1; scores['内容创作者'] += 1
    elif f.get('q5') == 'C': scores['社交活跃者'] += 2; scores['内容创作者'] += 2

    # Q6-Q10
    if f.get('q6') == 'B': scores['内容创作者'] += 1
    elif f.get('q6') == 'C': scores['内容创作者'] += 3

    for v in f.getlist('q7'):
        if v == 'ps': scores['内容创作者'] += 1
        if v == 'video': scores['内容创作者'] += 2
        if v == 'editor': scores['内容创作者'] += 2

    if f.get('q8') == 'B': scores['内容创作者'] += 1
    elif f.get('q8') == 'C': scores['内容创作者'] += 2

    if f.get('q9') == 'B': scores['内容创作者'] += 1
    elif f.get('q9') == 'C': scores['内容创作者'] += 2

    if f.get('q10') == 'yes': scores['内容创作者'] += 2

    # Q11-Q15
    if f.get('q11') == 'B': scores['云文档/远程办公者'] += 1
    elif f.get('q11') == 'C': scores['云文档/远程办公者'] += 2

    if f.get('q12') == 'yes': scores['云文档/远程办公者'] += 2

    if f.get('q13') == 'B': scores['云文档/远程办公者'] += 1
    elif f.get('q13') == 'C': scores['云文档/远程办公者'] += 2

    if f.get('q14') == 'A': scores['云文档/远程办公者'] += 1
    elif f.get('q14') == 'B': scores['云文档/远程办公者'] += 2
    elif f.get('q14') == 'C': scores['云文档/远程办公者'] += 3

    if f.get('q15') == 'yes': scores['云文档/远程办公者'] += 2

    # Q16-Q20
    for v in f.getlist('q16'):
        if v == 'read': scores['被动信息浏览者'] += 2
        if v == 'video': scores['被动信息浏览者'] += 1
        if v == 'learn': scores['被动信息浏览者'] += 2
        if v == 'chat': scores['社交活跃者'] += 1
        if v == 'work':
            scores['内容创作者'] += 1
            scores['云文档/远程办公者'] += 1

    if f.get('q17') == 'yes': scores['被动信息浏览者'] += 2

    if f.get('q18') == 'yes': scores['被动信息浏览者'] += 2
    elif f.get('q18') == 'no': scores['社交活跃者'] += 1

    if f.get('q19') == 'yes': scores['被动信息浏览者'] += 1

    if f.get('q20') == 'yes': scores['被动信息浏览者'] += 2

    # Q21-Q25 混合型识别
    try: scores['混合型用户'] += int(f.get('q21', 0))
    except: pass
    try: scores['混合型用户'] += int(f.get('q22', 0))
    except: pass

    q23 = f.get('q23')
    if q23 == 'B': scores['混合型用户'] += 1
    elif q23 == 'C': scores['混合型用户'] += 2

    try: scores['混合型用户'] += int(f.get('q24', 0))
    except: pass

    q25 = f.get('q25')
    if q25 == 'A': scores['云文档/远程办公者'] += 2
    elif q25 == 'B': scores['社交活跃者'] += 2
    elif q25 == 'C': scores['内容创作者'] += 2
    elif q25 == 'D': scores['被动信息浏览者'] += 2
    elif q25 == 'E': scores['混合型用户'] += 3

    max_score = max(scores.values())
    top_types = [k for k, v in scores.items() if v == max_score]
    
    USER_TYPE_MAP = {
    '社交活跃者': 'social_user',
    '内容创作者': 'content_creator',
    '云文档/远程办公者': 'remote_worker',
    '被动信息浏览者': 'passive_browser',
    '混合型用户': 'hybrid_user'
     }

    top_label = top_types[0] if len(top_types) == 1 else '混合型用户'
    return USER_TYPE_MAP.get(top_label, 'unknown')
