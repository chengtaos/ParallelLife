"""分支对比分析服务 — LLM 比较多条人生路径的差异"""

from typing import Dict, Any, List
from ..utils.llm_client import LLMClient
from ..utils.locale import get_language_instruction
from ..utils.logger import get_logger

logger = get_logger('parallel-life.compare')

COMPARISON_SYSTEM = """你是一位人生分析专家，擅长对比不同人生选择带来的后果。你需要分析 2-3 条不同的人生路径，找出它们的核心差异和关键转折点。

输出严格的JSON格式：
{
    "diff_summary": "整体对比摘要，200-300字，概括各路径的核心差异",
    "dimension_diff": {
        "career_achievement": {
            "analysis": "该维度在各路径的对比分析",
            "best_path": "最佳路径的标签"
        },
        "wealth": { "同上格式" },
        "social_density": { "同上格式" },
        "happiness": { "同上格式" },
        "location_stability": { "同上格式" },
        "health": { "同上格式" },
        "self_fulfillment": { "同上格式" }
    },
    "key_turning_points": [
        {
            "time": "时间节点",
            "event": "该节点发生的关键分歧",
            "impact": "这个分歧如何导致了后续的不同走向"
        }
    ],
    "insight": "深度洞察，300-500字。分析用户的决策模式、价值观倾向、以及这些对比能带来什么人生启示"
}

规则：
- 每个维度的 analysis 需要具体说明各路径在该维度的表现差异
- best_path 必须是输入中给出的路径标签之一
- key_turning_points 找出 2-4 个最关键的分歧点
- insight 要有人文深度，不只是数据对比
"""


class ComparisonAgent:
    def __init__(self):
        self.llm = LLMClient()

    def compare(
        self,
        branches: List[Dict[str, Any]],
        decision_scenario: str = ""
    ) -> Dict[str, Any]:
        """对比多条分支"""
        lang_instr = get_language_instruction()

        branch_descriptions = []
        for i, b in enumerate(branches):
            label = b.get('branch_label', f'路径{i+1}')
            narrative = b.get('narrative', '')
            dims = b.get('dimensional_trajectory', {})
            last_timepoint = list(dims.keys())[-1] if dims else '未知'
            final_scores = dims.get(last_timepoint, {}) if dims else {}

            desc = f"路径 {i+1}：{label}\n"
            desc += f"叙事摘要：{narrative[:300]}\n"
            if final_scores:
                scores_text = ", ".join(
                    f"{k}={v.get('score', '?')}"
                    for k, v in final_scores.items()
                )
                desc += f"终局评分：{scores_text}\n"
            branch_descriptions.append(desc)

        user_prompt = f"""{lang_instr}

决策场景：{decision_scenario if decision_scenario else '未指定'}

以下是需要对比的人生路径：

{chr(10).join(f'--- 路径 {i+1} ---{chr(10)}{desc}' for i, desc in enumerate(branch_descriptions))}

请全面对比分析这些路径的差异。"""

        messages = [
            {"role": "system", "content": COMPARISON_SYSTEM},
            {"role": "user", "content": user_prompt}
        ]

        logger.info(f"开始对比 {len(branches)} 条分支...")
        result = self.llm.chat_json(messages, temperature=0.5, max_tokens=4096)
        logger.info("对比分析完成")
        return result
