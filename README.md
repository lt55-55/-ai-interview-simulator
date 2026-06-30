# 🎯 AI 面试官 — AI Interview Simulator

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58-red.svg)](https://streamlit.io)
[![Claude](https://img.shields.io/badge/Anthropic-Claude-purple.svg)](https://anthropic.com)

基于 **Anthropic Claude API** 的智能模拟面试系统。粘贴你的简历，AI 自动生成针对性面试题，进行模拟面试，并给出详细的评估报告。

> **不只是"调个 API"** — 完整的系统设计：智能出题 → 多维度评估 → 结构化报告 → 历史追踪。

## ✨ 功能

- 📄 **简历解析** — 粘贴简历文本，AI 自动提取关键信息
- 🎯 **智能出题** — 根据简历和目标岗位生成 5 道针对性面试题（基础/项目/系统设计/行为/视野）
- 🎤 **模拟面试** — 逐题作答，真实还原面试场景
- 📊 **多维评估** — 从正确性(40)、深度(30)、表达(30) 三个维度评分
- 📝 **综合报告** — 优势/待改进/岗位匹配度/针对性提升建议
- 📋 **历史记录** — SQLite 存储所有面试数据，支持回顾和追踪进步

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 Anthropic API Key
```

### 3. 启动

```bash
streamlit run app.py
```

浏览器访问 `http://localhost:8501` 即可使用。

## 🏗️ 项目结构

```
project3/
├── app.py                      # Streamlit 主应用
├── src/
│   ├── config.py               # 配置与 API 客户端
│   ├── question_generator.py   # AI 出题模块
│   ├── evaluator.py            # 答案评估模块
│   ├── report_writer.py        # 报告生成模块
│   └── database.py             # SQLite 数据层
├── requirements.txt
├── .env.example
└── README.md
```

## 🧠 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Streamlit (Python 原生) |
| AI | Anthropic Claude API (Sonnet 4.6) |
| 存储 | SQLite (WAL 模式) |
| 部署 | 支持 Streamlit Cloud / Railway / 任意云服务器 |

## 📊 评估维度

每题从三个维度评分（总分 100）：

| 维度 | 占比 | 说明 |
|------|:----:|------|
| 正确性 | 40% | 技术理解是否准确 |
| 深度 | 30% | 是否展示深入理解 |
| 表达 | 30% | 逻辑清晰度与结构化程度 |

## 🔮 路线图

- [ ] 语音输入支持 (Whisper API)
- [ ] 支持自定义出题数量
- [ ] 导出 PDF 报告
- [ ] 多语言简历解析
- [ ] 面试数据可视化面板

## 📄 License

MIT
