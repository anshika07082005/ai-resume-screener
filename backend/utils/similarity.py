def skill_similarity(resume_skills, jd_skills):
    resume = set(resume_skills)
    jd = set(jd_skills)

    matched = list(resume & jd)
    missing = list(jd - resume)

    return matched, missing
