# Parallel Life · 平行人生

> 如果当初选了另一条路，人生会怎样？

**Parallel Life** 是一款 AI 驱动的平行人生推演引擎。输入你的人生经历，AI 解析你的关键决策点，构建知识图谱，推演不同选择下的平行人生走向——以叙事 + 七维量化评分的方式呈现。

---

## ✨ 功能

- **人生画像** — 自由文本输入，AI 自动提取人物、关系、重大决策，构建知识图谱
- **人物关系网** — D3 力导向图可视化你的关键人物网络
- **决策时间线** — 按人生阶段排列所有岔路口，标注实际选择
- **平行推演** — 选择一条未走过的路，AI 推理因果链 + 七维评分 + 叙事故事
- **次级决策** — 推演路径中自动识别新的岔路口，可继续深入探索
- **多分支对比** — 选 2-3 条路径并排分析，AI 指出维度差异和关键转折点
- **决策模式分析** — AI 总结你的决策风格、风险偏好、核心价值观
- **报告导出** — 一键下载 Markdown 格式的推演报告
- **中英双语** — 完整的中文 / English 界面切换

## 🚀 快速开始

### 前提条件

- Python 3.11+
- Node.js 18+
- [DeepSeek API Key](https://platform.deepseek.com/) 或其他 OpenAI 兼容的 LLM API
- [Zep Cloud API Key](https://app.getzep.com/)（每月有免费额度）

### 安装

```bash
# 克隆项目
git clone https://github.com/yourname/ParallelLife.git
cd ParallelLife

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY 和 ZEP_API_KEY

# 安装后端依赖
pip install -r backend/requirements.txt

# 安装前端依赖
cd frontend && npm install && cd ..
```

### 启动

```bash
# 终端 1：启动后端
python backend/run.py

# 终端 2：启动前端
cd frontend && npm run dev
```

打开 `http://localhost:3000`

## 🏗️ 架构

```
ParallelLife/
├── backend/                  # Flask 后端
│   ├── app/
│   │   ├── api/              # REST API（profile / decision / compare）
│   │   ├── models/           # 数据模型 + JSON 文件持久化
│   │   ├── services/         # 核心业务逻辑
│   │   │   ├── profile_extractor.py   # LLM 解析文本 → 结构化画像
│   │   │   ├── graph_builder.py       # Zep 知识图谱构建
│   │   │   ├── decision_engine.py     # 因果链 + 七维评分推理
│   │   │   ├── comparison_agent.py    # 多分支对比分析
│   │   │   └── pattern_analyzer.py    # 决策模式分析
│   │   └── utils/            # LLM 客户端 / 日志 / i18n / 错误处理
│   └── run.py                # 启动入口
├── frontend/                 # Vue 3 + Vite 前端
│   └── src/
│       ├── views/            # Home / Profile / Branch / Compare
│       ├── components/       # DecisionCard / BranchResult / DimRadar / NetworkGraph / Toast
│       ├── api/              # Axios 封装
│       ├── store/            # 跨页面状态管理
│       └── i18n/             # 多语言
└── locales/                  # 翻译文件（zh / en）
```

## 🛠️ 技术栈

| 层 | 技术 |
|---|---|
| 后端框架 | Flask 3 |
| LLM | DeepSeek / OpenAI 兼容 API |
| 知识图谱 | Zep Cloud |
| 前端 | Vue 3 + Vite |
| 可视化 | D3.js（雷达图 + 力导向图） |
| 国际化 | Vue I18n |
| 字体 | JetBrains Mono / Space Grotesk / Noto Sans SC |

## 📄 许可证

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 🙏 致谢

本项目灵感来源于 **[MiroFish](https://github.com/666ghj/MiroFish)** —— 一个简洁通用的群体智能引擎。Parallel Life 复用了 MiroFish 的架构设计思想（知识图谱 + Agent + LLM 推理），将其应用于个人人生决策推演领域。
