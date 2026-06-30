"""AI-powered interview report generation using Claude."""

import json

from anthropic import Anthropic

SYSTEM_PROMPT = """你是一位资深 HR 顾问和技术面试官。你需要根据候选人在模拟面试中的表现，生成一份全面、有深度、可操作的面试评估报告。

## 报告要求
1. **客观公正**：基于真实表现，不夸大不贬低
2. **数据支撑**：引用具体分数和题目表现
3. **可操作**：每一条改进建议都是候选人明天就能开始做的事
4. **建设性**：语气积极，帮助候选人看到成长路径

## 报告结构
1. **总体评分**（百分制）
2. **优势**（3-5条，具体到题目表现）
3. **待改进**（3-5条，具体到题目表现）
4. **岗位匹配度评估**（用百分比，并解释原因）
5. **针对性提升建议**（按优先级排序，每条建议包含具体行动步骤）
6. **总结**（一段话，鼓励但真诚）

## 输出格式
必须以 JSON 格式输出：
```json
{
  "overall_score": 78,
  "strengths": "候选人展示了...",
  "weaknesses": "需要加强...",
  "recommendations": "1. ...\n2. ...\n3. ...",
  "role_fit": "70% - 具备基本的技术基础，但...",
  "summary": "一段真诚的总结评价"
}
```

注意：只输出 JSON，不要输出其他内容。"""


def generate_report(
    client: Anthropic,
    role: str,
    difficulty: str,
    questions_and_answers: list[dict],
) -> dict:
    """Generate a comprehensive interview report.

    Args:
        client: Anthropic client instance.
        role: Target job role.
        difficulty: Interview difficulty level.
        questions_and_answers: List of dicts with keys:
            - question: str
            - category: str
            - user_answer: str
            - score: int
            - feedback: str

    Returns:
        Dict with keys: overall_score, strengths, weaknesses, recommendations, role_fit, summary.
    """
    # Build the performance summary for the prompt
    qa_text_parts = []
    for i, qa in enumerate(questions_and_answers, 1):
        qa_text_parts.append(
            f"### 第{i}题 ({qa.get('category', '未知')})\n"
            f"题目：{qa['question']}\n"
            f"回答：{qa.get('user_answer', '(未作答)')}\n"
            f"评分：{qa.get('score', 0)}/100\n"
            f"评语：{qa.get('feedback', '')}"
        )

    qa_text = "\n\n".join(qa_text_parts)

    user_message = f"""请根据以下模拟面试的完整记录，生成一份面试评估报告。

## 目标岗位
{role}

## 面试难度
{difficulty}

## 面试记录
{qa_text}

请严格按照 JSON 格式输出评估报告。"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    content = response.content[0].text
    return _parse_report(content)


def _parse_report(raw: str) -> dict:
    """Parse report JSON from Claude's response."""
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    import re

    match = re.search(r"\s*\{.*\}\s*", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {
        "overall_score": 0,
        "strengths": "报告生成失败，请重试。",
        "weaknesses": "",
        "recommendations": "",
        "role_fit": "",
        "summary": "API 返回格式异常，请重新生成报告。",
    }
