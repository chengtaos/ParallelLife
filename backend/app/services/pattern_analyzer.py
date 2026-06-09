"""决策模式分析 — LLM 分析用户的决策倾向和价值观"""

from typing import Dict, Any, List
from ..utils.llm_client import LLMClient
from ..utils.locale import get_language_instruction
from ..utils.logger import get_logger

logger = get_logger('parallel-life.pattern')

PATTERN_SYSTEM = """你是一位行为心理学家，擅长分析人们的决策模式。根据用户提供的人生决策记录和推演探索记录，分析其决策倾向。

输出严格的JSON格式：
{
    "decision_style": "一句话概括决策风格，如：稳健务实型/冒险进取型/情感驱动型/理性分析型",
    "risk_preference": {
        "level": "保守/平衡/冒险",
        "analysis": "100-150字分析"
    },
    "value_orientation": {
        "primary": "最看重的价值（如家庭/事业/自由/稳定）",
        "analysis": "100-150字分析"
    },
    "patterns": [
        {"pattern": "模式描述", "evidence": "具体的决策证据"}
    ],
    "insight": "200-300字的深度洞察，关于这些决策模式如何塑造了用户的人生轨迹，以及有什么可以反思的地方"
}
"""


class PatternAnalyzer:
    def __init__(self):
        self.llm = LLMClient()

    def analyze(
        self,
        actual_decisions: List[Dict[str, Any]],
        explored_branches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析决策模式"""
        lang_instr = get_language_instruction()

        # 汇总实际选择
        actual_lines = []
        for d in actual_decisions:
            actual_choice = next((b['label'] for b in d.get('branches', []) if b.get('is_actual')), '未知')
            actual_lines.append(f"- {d.get('life_stage', '')}阶段 | {d.get('scenario', '')[:80]} → 选择了「{actual_choice}」")

        # 汇总推演行为
        explore_lines = []
        for b in explored_branches:
            explore_lines.append(f"- 探索了「{b.get('branch_label', '')}」的{b.get('depth', '')}推演")

        user_prompt = f"""{lang_instr}

以下是用户的真实人生决策记录：
{chr(10).join(actual_lines) if actual_lines else '无记录'}

用户主动探索过的反事实路径（说明用户对这些选择有兴趣或遗憾）：
{chr(10).join(explore_lines) if explore_lines else '尚未探索'}

请分析这个人的决策模式、风险偏好、价值观取向，并给出深度洞察。"""

        messages = [
            {"role": "system", "content": PATTERN_SYSTEM},
            {"role": "user", "content": user_prompt}
        ]

        logger.info("开始决策模式分析...")
        result = self.llm.chat_json(messages, temperature=0.5, max_tokens=2048)
        logger.info("模式分析完成")
        return result
