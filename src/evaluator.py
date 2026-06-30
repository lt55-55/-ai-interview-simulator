"""AI-powered answer evaluation using Claude."""

import json

from anthropic import Anthropic

SYSTEM_PROMPT = """你是一位严格但公正的技术面试官。你需要评估候选人对每道面试题的回答质量。

## 评分维度（每题满分 100 分）
- **正确性 (40分)**：技术理解是否准确，事实是否正确
- **深度 (30分)**：是否展示了深入理解，而非停留在表面
- **表达 (30分)**：逻辑是否清晰，结构是否合理，是否举例说明

## 评分标准
- 90-100：优秀，超出预期，展示了深刻理解和实践经验
- 75-89：良好，回答基本正确，有一定深度
- 60-74：及格，方向对但不够深入或表述不清
- 40-59：较差，有明显错误或缺乏基本理解
- 0-39：很差，完全跑题或拒绝回答

## 反馈原则
- 先肯定优点（哪怕很少），再指出不足
- 每一个扣分点都要给出具体原因和改进建议
- 语气要建设性，而非批评
- 反馈要具体，不要说"回答不够深入"，要说"缺少对XX机制的解释"

## 输出格式
必须以 JSON 格式输出：
```json
{
  "score": 85,
  "correctness": 34,
  "depth": 24,
  "clarity": 27,
  "feedback": "详细的评估反馈，包含优点和改进建议",
  "strengths": ["优点1", "优点2"],
  "improvements": ["改进建议1", "改进建议2"]
}
```

注意：只输出 JSON，不要输出其他内容。"""


def evaluate_answer(
    client: Anthropic,
    question: str,
    reference_answer: str,
    user_answer: str,
    category: str = "",
) -> dict:
    """Evaluate a single interview answer.

    Args:
        client: Anthropic client instance.
        question: The interview question.
        reference_answer: Reference answer / scoring guide.
        user_answer: Candidate's actual answer.
        category: Question category for context.

    Returns:
        Dict with keys: score, correctness, depth, clarity, feedback, strengths, improvements.
    """
    if not user_answer.strip():
        return {
            "score": 0,
            "correctness": 0,
            "depth": 0,
            "clarity": 0,
            "feedback": "未作答。面试中保持沉默比给出不准确的回答更糟——至少应该尝试表达自己的思考过程。",
            "strengths": [],
            "improvements": ["下次遇到不会的问题，尝试说出你知道的相关知识和思考逻辑"],
        }

    user_message = f"""请评估以下面试回答：

## 题目类型
{category}

## 面试题目
{question}

## 参考回答/评分要点
{reference_answer}

## 候选人回答
{user_answer}

请严格按照 JSON 格式输出评估结果。"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    content = response.content[0].text
    return _parse_evaluation(content)


def _parse_evaluation(raw: str) -> dict:
    """Parse evaluation JSON from Claude's response."""
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

    # Fallback: return a default evaluation
    return {
        "score": 50,
        "correctness": 20,
        "depth": 15,
        "clarity": 15,
        "feedback": "评估解析出错，请重试。技术原因：API 返回格式异常。",
        "strengths": ["无法判断"],
        "improvements": ["请重新提交回答"],
    }
