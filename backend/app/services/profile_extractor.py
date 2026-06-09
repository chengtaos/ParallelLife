"""LLM 解析人生自由文本 → 结构化画像 + 决策节点"""

from typing import Dict, Any, List
from ..utils.llm_client import LLMClient
from ..utils.locale import get_language_instruction
from ..utils.logger import get_logger

logger = get_logger('parallel-life.extractor')

PROFILE_EXTRACTOR_SYSTEM = """你是一位人生分析专家。你的任务是从用户的个人经历描述中提取结构化信息。

请输出以下JSON结构：
{
    "basic_info": {
        "name": "姓名",
        "age": 年龄数字,
        "gender": "男/女",
        "education": [{"level": "本科", "school": "学校名", "major": "专业", "year": "年份"}],
        "career": [{"company": "公司名", "role": "职位", "years": "年份范围"}],
        "location": {"current": "当前城市", "history": [{"city": "城市", "years": "年份范围"}]}
    },
    "entities": [
        {"name": "人物/组织名", "type": "Person/Organization/Location", "description": "简短描述", "attributes": {"role": "父亲/导师/朋友", "importance": "high/medium/low"}}
    ],
    "relationships": [
        {"source": "实体A名称", "target": "实体B名称", "type": "FAMILY/COLLEAGUE/MENTOR/FRIEND/ACQUAINTANCE", "description": "关系描述"}
    ],
    "decisions": [
        {
            "timestamp": "年份或具体时间",
            "life_stage": "high_school/college/early_career/mid_career",
            "scenario": "当时面临的场景和选择",
            "branches": [
                {"label": "选择A的描述", "pros": ["优点1"], "cons": ["缺点1"], "is_actual": true},
                {"label": "选择B的描述", "pros": ["优点1"], "cons": ["缺点1"], "is_actual": false}
            ]
        }
    ],
    "analysis_summary": "对该人生命运的简要总结（2-3句话）"
}

重要规则：
1. entities 必须是真实存在的具体人物/组织/地点，不能是抽象概念
2. 只提取用户明确提到的实体和关系
3. decisions 只提取用户描述中体现的重大人生选择（至少2个选项）
4. is_actual 标记用户实际做出的选择
"""


class ProfileExtractor:
    def __init__(self):
        self.llm = LLMClient()

    def extract(self, text: str) -> Dict[str, Any]:
        lang_instr = get_language_instruction()
        messages = [
            {"role": "system", "content": PROFILE_EXTRACTOR_SYSTEM},
            {"role": "user", "content": f"{lang_instr}\n\n以下是一位用户的人生经历描述，请提取结构化信息：\n\n{text}"}
        ]
        logger.info("开始 LLM 解析人生画像...")
        result = self.llm.chat_json(messages, temperature=0.3, max_tokens=8192)
        logger.info(f"解析完成: {len(result.get('entities', []))} 个实体, {len(result.get('decisions', []))} 个决策点")
        return result
