"""AI-powered interview question generation using Claude."""

import json

from anthropic import Anthropic

PROMPT_FILE = None  # We'll use inline prompts for reliability


SYSTEM_PROMPT = """你是一位资深技术面试官，拥有 10 年以上互联网行业面试经验。你需要根据候选人的简历和目标岗位，生成有针对性的面试题目。

## 你的任务
1. 仔细分析候选人的简历内容
2. 结合目标岗位的要求，生成 5 道面试题
3. 题目应该覆盖不同维度：基础知识、项目经验、系统设计、行为面试、技术深度

## 出题原则
- 题目必须与简历中提到的技术和经验相关
- 难度应该匹配候选人水平，不要过于简单或过于刁钻
- 每道题应该能考察候选人的真实能力，而非死记硬背
- 题目之间应该有不同的考察维度，形成互补
- 参考回答应该给出评分要点，而非唯一正确答案

## 输出格式
必须以 JSON 格式输出，包含 5 道题的数组：
```json
[
  {
    "question": "面试题目（中文，清晰明确）",
    "category": "基础知识 | 项目深挖 | 系统设计 | 行为面试 | 技术视野",
    "difficulty": "easy | medium | hard",
    "reference_answer": "评分要点和参考回答方向"
  }
]
```

注意：只输出 JSON，不要输出其他内容。"""


def generate_questions(
    client: Anthropic,
    resume_text: str,
    role: str,
    difficulty: str = "中级 (1-3年)",
    num_questions: int = 5,
) -> list[dict]:
    """Generate interview questions based on resume and target role.

    Args:
        client: Anthropic client instance.
        resume_text: Candidate's resume text.
        role: Target job role (Chinese).
        difficulty: Difficulty level string.
        num_questions: Number of questions to generate.

    Returns:
        List of question dicts with keys: question, category, difficulty, reference_answer.
    """
    user_message = f"""请为以下候选人生成 {num_questions} 道面试题。

## 目标岗位
{role}

## 难度要求
{difficulty}

## 候选人简历
{resume_text}

请严格按照 JSON 格式输出题目列表。"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    # Extract text from response (skip thinking blocks)
    content = "".join(b.text for b in response.content if b.type == "text")
    return _parse_questions(content)


def _parse_questions(raw: str) -> list[dict]:
    """Extract JSON questions from Claude's response, handling markdown code blocks."""
    # Remove markdown code block if present
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()

    try:
        questions = json.loads(raw)
        if isinstance(questions, list):
            return questions
    except json.JSONDecodeError:
        pass

    # Fallback: try to find JSON array in text
    import re

    match = re.search(r"\[\s*\{.*\}\s*\]", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Last resort: return empty list
    return []
