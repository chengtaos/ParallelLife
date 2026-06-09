"""决策引擎 — LLM 推理反事实分支的因果链 + 七维评分"""

from typing import Dict, Any, List, Callable, Optional
from ..utils.llm_client import LLMClient
from ..utils.locale import get_language_instruction
from ..utils.logger import get_logger

logger = get_logger('parallel-life.engine')

DECISION_ENGINE_SYSTEM = """你是一位人生推演专家，擅长基于已知信息推理不同人生选择可能带来的后果。

你需要为一个"反事实人生选择"生成推演结果。输出严格的JSON格式：

{
    "causal_chain": [
        {
            "step_no": 1,
            "time_offset": "3个月后",
            "event": "具体发生了什么事件",
            "consequence": "这个事件带来了什么结果",
            "affected_dimensions": ["career_achievement", "social_density"]
        }
    ],
    "dimensional_trajectory": {
        "baseline": {
            "career_achievement": {"score": 50, "reasoning": "决策时的状态描述"},
            "wealth": {"score": 50, "reasoning": "..."},
            "social_density": {"score": 50, "reasoning": "..."},
            "happiness": {"score": 50, "reasoning": "..."},
            "location_stability": {"score": 50, "reasoning": "..."},
            "health": {"score": 50, "reasoning": "..."},
            "self_fulfillment": {"score": 50, "reasoning": "..."}
        },
        "1y": { "同上格式，每个维度包含 score 和 reasoning" },
        "3y": { "同上" },
        "5y": { "同上" },
        "10y": { "同上" }
    },
    "narrative": "完整的叙事摘要，500-800字，以第一人称或第三人称讲述这条人生路径的故事"
}

评分规则：
- 0-100分，50分为普通平均水平
- 每个评分必须附带一句话理由
- baseline 是决策发生时的实际状态
- 后续各时间点反映选择产生的影响
- 评分需要合理：不会一夜之间从30跳到90，变化应该是渐进的
- 因果链的每一步应包含1-3个受影响的维度
"""


class DecisionEngine:
    def __init__(self):
        self.llm = LLMClient()

    def explore_branch(
        self,
        decision_scenario: str,
        branch_label: str,
        actual_path_context: str,
        related_entities: List[str],
        depth: str = "5y",
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """推演反事实分支"""
        lang_instr = get_language_instruction()

        depth_desc = {"1y": "1年", "3y": "3年", "5y": "5年", "10y": "10年"}
        depth_steps = {"1y": 3, "3y": 5, "5y": 8, "10y": 12}

        timeline_points = "baseline（决策时）"
        if depth in ("1y", "3y", "5y", "10y"):
            timeline_points += ", 1y（1年后）"
        if depth in ("3y", "5y", "10y"):
            timeline_points += ", 3y（3年后）"
        if depth in ("5y", "10y"):
            timeline_points += ", 5y（5年后）"

        user_prompt = f"""{lang_instr}

决策场景：{decision_scenario}

用户实际选择的路径是：{actual_path_context}

我们要推演的反事实选择是：{branch_label}

相关人物/实体：{', '.join(related_entities) if related_entities else '无特殊关联实体'}

推演深度：{depth_desc.get(depth, '5年')}
因果链步骤数：约 {depth_steps.get(depth, 8)} 步
需要评分的时间点：{timeline_points}

请基于人物的性格特征、关系网络和现实逻辑，推理如果TA选择了「{branch_label}」，人生会如何演变。"""

        messages = [
            {"role": "system", "content": DECISION_ENGINE_SYSTEM},
            {"role": "user", "content": user_prompt}
        ]

        logger.info(f"开始推演分支: {branch_label}, 深度={depth}")
        if progress_callback:
            progress_callback("reasoning", 0, "开始 LLM 推理...")

        result = self.llm.chat_json(messages, temperature=0.7, max_tokens=8192)

        if progress_callback:
            progress_callback("reasoning", 100, "推理完成")

        if "causal_chain" not in result:
            result["causal_chain"] = []
        if "dimensional_trajectory" not in result:
            result["dimensional_trajectory"] = {}
        if "narrative" not in result:
            result["narrative"] = ""

        logger.info(f"推演完成: {len(result.get('causal_chain', []))} 步因果链")
        return result
