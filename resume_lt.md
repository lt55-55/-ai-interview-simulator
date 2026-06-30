# 兰添

**求职意向：AI 应用开发工程师** | 长沙 | 2026 届本科 | 计算机科学与技术

| | |
|---|---|
| 📧 3357895744@qq.com | 🐙 [github.com/lt55-55](https://github.com/lt55-55) |

---

## 💻 AI 相关项目

### AI 面试官（AI Interview Simulator）| 独立开发 | 2026.06

基于大语言模型的智能模拟面试系统。用户上传简历后，AI 自动分析并生成针对性面试题，评估答案质量，输出结构化报告。

- **AI 能力**: 使用 Anthropic Claude API 实现简历解析、智能出题、多维度评分（正确性/深度/表达）和报告生成，通过结构化 Prompt 保证输出一致性
- **技术栈**: Python · Streamlit · Anthropic SDK · SQLite
- **设计思路**: 将面试官的完整工作流拆解为「分析→出题→评估→报告」四个 AI 任务节点，每个节点有独立的 System Prompt 和输出格式约束
- 已开源至 GitHub，通过 SSH 部署

### 外网信息素材收集系统 | 独立开发 | 2026.06

从 28 个国际 RSS 源（TechCrunch、Reuters、ESPN 等）自动抓取前沿信息，利用 1-4 周信息差，转化为小红书图文笔记素材。

- **AI 能力**: 使用 Claude WebSearch 辅助翻译及润色，设计中文技术内容格式化模板
- **技术栈**: Python · feedparser · 异步爬虫 · Windows 计划任务
- **系统设计**: 5 个内容类别独立管道 → 自动去重/评分/格式化 → 每日定时输出，30 天自动归档

### CLI 多模型 AI 聊天机器人 | 独立开发 | 2026.05

终端交互式 AI 对话工具，支持 Claude 全系列模型（Haiku/Sonnet/Opus）实时切换。

- **AI 能力**: 集成 Anthropic SDK，实现流式输出、对话上下文管理、Token 用量实时统计和成本估算
- **技术栈**: Python · Anthropic SDK · asyncio
- **亮点**: 完整的 CLI 命令系统（/save /load /stats /model），对话持久化为 JSON

### Prompt 实验平台 | 独立开发 | 2026.05

5 种 Prompt 策略（专家型/创意型/教学型/简洁型/思维链）的 A/B 测试框架。

- **AI 能力**: Prompt Engineering 方法论实践，文件驱动模板管理，API 并排对比，SQLite 记录全部实验历史
- **技术栈**: Python · Anthropic SDK · SQLite

---

## 🛠️ 技能

| 类别 | 具体技能 |
|------|----------|
| **AI/LLM** | Anthropic Claude API、Prompt Engineering（4C 框架/A/B 测试）、RAG 概念、AI Agent 概念、Function Calling 概念 |
| **编程语言** | Python（主力，熟练 asyncio/aiohttp）、SQL |
| **框架/工具** | Streamlit、FastAPI、SQLite（含 FTS5 全文搜索）、Git |
| **AI 理论** | Transformer 原理、Token 经济学、Embedding、模型训练三阶段、MCP 协议概念 |

---

## 📚 系统学习

独立规划并完成 14 周 AI 应用开发学习路径，产出 12 篇技术笔记 + 4 个实战项目：

- **LLM 原理**: Token/Embedding/Transformer 架构/三阶段训练（预训练→SFT→RLHF）
- **Prompt Engineering**: 4C 框架（Context/Character/Command/Constraint）、少样本学习、思维链、结构化输出
- **API 集成**: Anthropic vs OpenAI SDK 对比、流式传输、错误重试、多提供商抽象层
- **Token 优化**: 计费模型、上下文窗口管理、Prompt Caching、模型路由策略

---

## 🎓 教育背景

**计算机科学与技术 本科** | 2026 届

- 英语：能阅读技术文档和 AI 论文
- 日语：初学
- 7 年篮球运动经历，院级比赛冠军（前锋）

---

## 🧠 自我评价

- **自驱力强**: 独立完成 4 个 AI 应用项目，从需求分析到代码实现到开源发布全流程自主推进
- **结构化思维**: 善于将复杂问题拆解为可执行的系统设计（见 AI 面试官的 4 节点工作流设计）
- **快速学习**: 3 个月内从零掌握 LLM API 集成、Prompt Engineering、Streamlit 全栈开发
- **心理素质过硬**: 长期自律（体重管理从 85kg 到 75kg、持续英语日语学习），在长期无反馈状态下保持学习节奏
