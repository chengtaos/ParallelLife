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
    "narrative": "完整的叙事摘要，500-800字，以第一人称或第三人称讲述这条人生路径的故事",
    "sub_decisions": [
        {
            "time_offset": "3年后",
            "scenario": "此时你面临一个新的重大选择（场景描述）",
            "branches": [
                {"label": "选项A的描述", "pros": ["优点"], "cons": ["缺点"]},
                {"label": "选项B的描述", "pros": ["优点"], "cons": ["缺点"]}
            ]
        }
    ]
}

评分规则：
- 0-100分，50分为普通平均水平
- 每个评分必须附带一句话理由
- baseline 是决策发生时的实际状态
- 后续各时间点反映选择产生的影响
- 评分需要合理：不会一夜之间从30跳到90，变化应该是渐进的
- 因果链的每一步应包含1-3个受影响的维度
- sub_decisions：在这条路径演变过程中，自然会遇到的 0-2 个新的重大人生决策点
- sub_decisions 必须是路径演变中合理出现的新岔路口，不要硬凑

重要：如果用户提示中包含"此前已经发生的事件"，说明这是嵌套次级决策。此时：
- baseline 评分必须反映这些已发生事件带来的影响，而非原始人生决策时的状态
- 因果链从当前时间点继续推演，不要重复此前已经发生的事件
- narrative 的写法至关重要：开头用 2-3 句话简要回顾此前路径的关键事件（自然融入，不要用"此前/回顾/上文提到"等生硬词汇），然后 用"于是/就这样/在这个节点上"等自然过渡词引入当前的岔路口选择，再展开推演后续故事。整体读起来应该像一篇连贯的人生叙事，而非两段拼接的文字。
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
        progress_callback: Optional[Callable] = None,
        parent_context: str = "",
    ) -> Dict[str, Any]:
        """推演反事实分支

        parent_context: 次级决策时，父分支在此决策点之前已发生的事件上下文
        """
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

        prefix = ""
        if parent_context:
            prefix = f"""

⚠️ 这是一个嵌套在已有推演路径中的次级决策。在此决策之前，这条人生路径中已经发生的事件如下：
{parent_context}

请务必：
1. baseline 评分反映这些已发生事件后的状态
2. 因果链从当前时间点继续，不重复之前事件
3. narrative 开头先自然融入此前事件作为背景（2-3句话），再用自然过渡引出当前决策和后续推演，
   确保全文读起来是一篇连贯的人生故事。"""


        user_prompt = f"""{lang_instr}

{prefix}
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
