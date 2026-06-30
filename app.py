"""AI Interview Simulator — Streamlit App.

A realistic mock interview experience powered by Claude.
Resume input → AI question generation → simulated interview → detailed report.
"""

import streamlit as st
from src.config import get_client, ROLES, DIFFICULTY_LEVELS
from src.question_generator import generate_questions
from src.evaluator import evaluate_answer
from src.report_writer import generate_report
from src.database import (
    create_session,
    save_questions,
    save_answer,
    update_evaluation,
    save_report,
    get_session_stats,
    get_recent_sessions,
)

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI 面试官",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .score-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-weight: 700;
        font-size: 1.1rem;
    }
    .score-high { background: #d4edda; color: #155724; }
    .score-mid { background: #fff3cd; color: #856404; }
    .score-low { background: #f8d7da; color: #721c24; }
    .question-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
    }
    .feedback-box {
        background: #f0f4ff;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ── Session State Init ───────────────────────────────────────────────────────
DEFAULTS = {
    "page": "home",
    "resume_text": "",
    "role": "",
    "difficulty": "初级 (实习/应届)",
    "questions": [],
    "session_id": None,
    "answers": [],
    "evaluations": [],
    "report": None,
}

for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 AI 面试官")
    st.markdown("基于 Claude 的智能模拟面试系统")
    st.markdown("---")

    # Stats
    try:
        stats = get_session_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("面试次数", stats["total_sessions"])
        col2.metric("答题数", stats["total_answers"])
        col3.metric("平均分", f"{stats['avg_score']}")
    except Exception:
        pass

    st.markdown("---")

    # Navigation
    st.markdown("### 📋 导航")
    if st.button("🏠 首页", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("📊 历史记录", use_container_width=True):
        st.session_state.page = "history"
        st.rerun()

    st.markdown("---")
    st.caption("Made with ❤️ by LT | Powered by Claude")


# ── Home Page ────────────────────────────────────────────────────────────────
def render_home():
    st.markdown(
        '<div class="main-header"><h1>🎯 AI 面试官</h1></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;font-size:1.2rem;color:#666;'>"
        "粘贴你的简历，选择目标岗位，AI 将为你生成真实的面试体验</p>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Step 1: Resume Input
    st.markdown("### 📄 第一步：输入简历")
    resume_text = st.text_area(
        "将你的简历内容粘贴到下方",
        value=st.session_state.resume_text,
        height=250,
        placeholder="在这里粘贴你的简历文本...\n\n例如：\n教育背景：XX大学 计算机科学 本科 2026届\n技能：Python, FastAPI, SQL, Docker\n项目经历：...\n实习经历：...",
        help="支持纯文本格式。AI 会从文本中提取关键信息。",
    )

    # Step 2: Role & Difficulty
    col1, col2 = st.columns(2)
    with col1:
        role = st.selectbox(
            "### 💼 目标岗位",
            options=[""] + list(ROLES.keys()),
            format_func=lambda x: "请选择..." if x == "" else x,
        )
        if role:
            st.caption(ROLES.get(role, ""))

    with col2:
        difficulty = st.selectbox(
            "### 📊 难度级别",
            options=DIFFICULTY_LEVELS,
        )

    # Step 3: Generate Questions
    st.markdown("---")
    st.markdown("### 🚀 第三步：开始面试")

    can_start = resume_text.strip() and role
    if not can_start:
        missing = []
        if not resume_text.strip():
            missing.append("简历内容")
        if not role:
            missing.append("目标岗位")
        st.warning(f"请先填写：{'、'.join(missing)}")
    else:
        st.info(f"准备就绪！将为 {role} 岗位生成 {difficulty} 难度的面试题。")

    if st.button(
        "🎯 生成面试题",
        type="primary",
        disabled=not can_start,
        use_container_width=True,
    ):
        with st.spinner("AI 正在分析你的简历并生成面试题..."):
            try:
                client = get_client()
                questions = generate_questions(
                    client, resume_text, role, difficulty
                )
                if not questions:
                    st.error("题目生成失败，请检查 API 配置后重试。")
                    return

                # Save to DB
                session_id = create_session(role, difficulty, resume_text)
                save_questions(session_id, questions)

                # Update session state
                st.session_state.resume_text = resume_text
                st.session_state.role = role
                st.session_state.difficulty = difficulty
                st.session_state.questions = questions
                st.session_state.session_id = session_id
                st.session_state.answers = [""] * len(questions)
                st.session_state.evaluations = []
                st.session_state.report = None
                st.session_state.page = "questions"

                st.rerun()
            except Exception as e:
                st.error(f"出错了：{e}")


# ── Questions Review Page ────────────────────────────────────────────────────
def render_questions():
    st.markdown("## 📋 面试题目预览")

    role = st.session_state.role
    difficulty = st.session_state.difficulty
    st.markdown(f"**岗位：** {role} | **难度：** {difficulty}")
    st.markdown("---")

    questions = st.session_state.questions
    for i, q in enumerate(questions, 1):
        cat = q.get("category", "未知")
        diff = q.get("difficulty", "medium")
        diff_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(diff, "⚪")

        with st.container():
            st.markdown(
                f'<div class="question-card">'
                f'<strong>第 {i} 题</strong> {diff_emoji} {diff} · {cat}<br>'
                f'{q["question"]}'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回修改", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    with col2:
        if st.button("开始面试 →", type="primary", use_container_width=True):
            st.session_state.page = "interview"
            st.rerun()


# ── Interview Page ───────────────────────────────────────────────────────────
def render_interview():
    st.markdown("## 🎤 模拟面试中...")

    questions = st.session_state.questions
    role = st.session_state.role

    st.markdown(f"**岗位：{role}** | 共 {len(questions)} 道题")
    progress = sum(1 for a in st.session_state.answers if a.strip())
    st.progress(progress / len(questions), text=f"已完成 {progress}/{len(questions)} 题")

    st.markdown("---")

    # Display all questions with answer inputs
    for i, q in enumerate(questions, 1):
        cat = q.get("category", "")
        diff = q.get("difficulty", "")
        diff_color = {"easy": "green", "medium": "orange", "hard": "red"}.get(diff, "grey")

        with st.container():
            st.markdown(
                f"### 第 {i} 题 "
                f":{diff_color}[{diff}] · *{cat}*"
            )
            st.markdown(f'<div class="question-card">{q["question"]}</div>', unsafe_allow_html=True)

            # Answer text area
            current_answer = st.text_area(
                f"你的回答 (第{i}题)",
                value=st.session_state.answers[i - 1],
                height=120,
                placeholder="在这里输入你的回答...\n\n建议：\n- 先概述你的理解\n- 再给出具体的技术细节\n- 最后补充实际经验或例子",
                key=f"answer_{i}",
                label_visibility="collapsed",
            )
            st.session_state.answers[i - 1] = current_answer

            # Show evaluation if already done
            if i <= len(st.session_state.evaluations):
                eval_data = st.session_state.evaluations[i - 1]
                if eval_data:
                    s = eval_data.get("score", 0)
                    score_class = "score-high" if s >= 75 else ("score-mid" if s >= 60 else "score-low")
                    st.markdown(f'<span class="score-badge {score_class}">得分: {s}/100</span>', unsafe_allow_html=True)
                    with st.expander("查看详细反馈"):
                        st.markdown(f'<div class="feedback-box">{eval_data.get("feedback", "")}</div>', unsafe_allow_html=True)
                        if eval_data.get("strengths"):
                            st.markdown("**✅ 优点：**")
                            for strength in eval_data["strengths"]:
                                st.markdown(f"- {strength}")
                        if eval_data.get("improvements"):
                            st.markdown("**📈 改进建议：**")
                            for imp in eval_data["improvements"]:
                                st.markdown(f"- {imp}")

            st.markdown("---")

    # Submit all answers
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 返回预览", use_container_width=True):
            st.session_state.page = "questions"
            st.rerun()
    with col2:
        if st.button("📤 提交全部答案并评估", type="primary", use_container_width=True):
            if not any(a.strip() for a in st.session_state.answers):
                st.warning("请至少回答一道题再提交。")
                return
            _evaluate_all()
    with col3:
        if st.button("查看报告 →", use_container_width=True, disabled=not st.session_state.report):
            st.session_state.page = "results"
            st.rerun()


def _evaluate_all():
    """Evaluate all answered questions."""
    client = get_client()
    evaluations = []

    for i, q in enumerate(st.session_state.questions):
        user_answer = st.session_state.answers[i]

        with st.spinner(f"正在评估第 {i+1} 题..."):
            eval_data = evaluate_answer(
                client,
                q["question"],
                q.get("reference_answer", ""),
                user_answer,
                q.get("category", ""),
            )

        # Save to DB
        try:
            answer_id = save_answer(
                st.session_state.session_id,
                i + 1,
                user_answer,
            )
            update_evaluation(
                answer_id,
                eval_data.get("score", 0),
                eval_data.get("feedback", ""),
            )
        except Exception:
            pass

        evaluations.append(eval_data)

    st.session_state.evaluations = evaluations

    # Generate overall report
    with st.spinner("正在生成综合评估报告..."):
        qa_pairs = []
        for i, q in enumerate(st.session_state.questions):
            qa_pairs.append({
                "question": q["question"],
                "category": q.get("category", ""),
                "user_answer": st.session_state.answers[i],
                "score": evaluations[i].get("score", 0) if i < len(evaluations) else 0,
                "feedback": evaluations[i].get("feedback", "") if i < len(evaluations) else "",
            })

        report = generate_report(
            client,
            st.session_state.role,
            st.session_state.difficulty,
            qa_pairs,
        )

        # Save report to DB
        try:
            save_report(
                st.session_state.session_id,
                report.get("overall_score", 0),
                report.get("strengths", ""),
                report.get("weaknesses", ""),
                report.get("recommendations", ""),
                report.get("role_fit", ""),
                report.get("summary", ""),
            )
        except Exception:
            pass

        st.session_state.report = report

    st.success("✅ 评估完成！点击右侧按钮查看报告。")
    st.rerun()


# ── Results Page ─────────────────────────────────────────────────────────────
def render_results():
    st.markdown("## 📊 面试评估报告")

    report = st.session_state.report
    if not report:
        st.warning("暂无报告，请先完成面试。")
        if st.button("返回首页"):
            st.session_state.page = "home"
            st.rerun()
        return

    overall = report.get("overall_score", 0)

    # Score gauge
    score_color = "green" if overall >= 75 else ("orange" if overall >= 60 else "red")
    st.markdown(
        f"<div style='text-align:center;padding:2rem;'>"
        f"<span style='font-size:4rem;font-weight:800;color:{score_color};'>{overall}</span>"
        f"<span style='font-size:1.5rem;color:#666;'> / 100</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Per-question breakdown
    st.markdown("### 📋 逐题得分")
    questions = st.session_state.questions
    evaluations = st.session_state.evaluations

    for i in range(len(questions)):
        q = questions[i]
        eval_data = evaluations[i] if i < len(evaluations) else {}
        score = eval_data.get("score", 0)

        cols = st.columns([1, 3, 1, 1])
        with cols[0]:
            st.markdown(f"**第{i+1}题**")
        with cols[1]:
            st.caption(q["question"][:80] + "...")
        with cols[2]:
            score_class = "score-high" if score >= 75 else ("score-mid" if score >= 60 else "score-low")
            st.markdown(f'<span class="score-badge {score_class}">{score}/100</span>', unsafe_allow_html=True)
        with cols[3]:
            with st.expander("详情"):
                st.markdown(f"**题目：** {q['question']}")
                st.markdown(f"**你的回答：** {st.session_state.answers[i] if i < len(st.session_state.answers) else '(无)'}")
                st.markdown(f"**反馈：** {eval_data.get('feedback', '')}")

    st.markdown("---")

    # Full report
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ 优势")
        st.markdown(report.get("strengths", "无"))

        st.markdown("### 📈 待改进")
        st.markdown(report.get("weaknesses", "无"))

    with col2:
        st.markdown("### 🎯 岗位匹配度")
        st.markdown(report.get("role_fit", ""))

        st.markdown("### 💡 提升建议")
        st.markdown(report.get("recommendations", ""))

    st.markdown("---")
    st.markdown("### 📝 总结")
    st.info(report.get("summary", ""))

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("🔄 重新面试", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.questions = []
            st.session_state.answers = []
            st.session_state.evaluations = []
            st.session_state.report = None
            st.rerun()
    with col2:
        if st.button("📋 查看历史记录", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()


# ── History Page ─────────────────────────────────────────────────────────────
def render_history():
    st.markdown("## 📊 历史记录")

    try:
        sessions = get_recent_sessions(20)
    except Exception:
        st.warning("暂无历史记录。完成一次面试后这里会有数据显示。")
        return

    if not sessions:
        st.info("还没有面试记录。去首页开始你的第一次模拟面试吧！")
        if st.button("🎯 开始面试", type="primary"):
            st.session_state.page = "home"
            st.rerun()
        return

    for s in sessions:
        score = s.get("overall_score")
        score_display = f"{score}/100" if score is not None else "未评估"
        with st.expander(
            f"{s['created_at']} | {s['role']} | {s['difficulty']} | 🏆 {score_display}"
        ):
            st.markdown(f"**岗位：** {s['role']}")
            st.markdown(f"**难度：** {s['difficulty']}")
            st.markdown(f"**时间：** {s['created_at']}")
            if score is not None:
                st.markdown(f"**总分：** {score}/100")


# ── Router ───────────────────────────────────────────────────────────────────
PAGES = {
    "home": render_home,
    "questions": render_questions,
    "interview": render_interview,
    "results": render_results,
    "history": render_history,
}

page_func = PAGES.get(st.session_state.page, render_home)
page_func()
