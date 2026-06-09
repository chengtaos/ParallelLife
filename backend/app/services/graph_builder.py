"""Zep 知识图谱构建服务 — 将画像实体写入图谱"""

from typing import Dict, Any, List, Optional
from zep_cloud.client import Zep
from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('parallel-life.graph')


class GraphBuilderService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.ZEP_API_KEY
        if not self.api_key:
            raise ValueError("ZEP_API_KEY 未配置")
        self.client = Zep(api_key=self.api_key)

    def build_profile_graph(
        self,
        profile_id: str,
        profile_name: str,
        basic_info: Dict[str, Any],
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        input_text: str
    ) -> str:
        """构建人生画像的知识图谱"""
        graph_name = f"ParallelLife - {profile_name} ({profile_id})"
        logger.info(f"创建 Zep 图谱: {graph_name}")

        graph = self.client.graph.add(
            user_id=profile_id,
            name=graph_name,
            data_type="text",
            data=input_text[:10000],
            max_robots=1,
            auto_create_entities=True
        )
        graph_id = graph.user_id
        logger.info(f"图谱创建成功: {graph_id}")

        # 注入明确指定的实体
        if entities:
            entity_texts = []
            for e in entities:
                attrs = e.get('attributes', {})
                role = attrs.get('role', '')
                importance = attrs.get('importance', 'medium')
                entity_texts.append(
                    f"{e['name']}：{e.get('description', '')}。"
                    f"类型：{e['type']}。角色：{role}。重要性：{importance}。"
                )
            entity_episode = "以下是在用户人生中出现的所有关键人物和实体：\n\n" + "\n".join(entity_texts)
            self.client.graph.episodic.add(
                graph_id=graph_id,
                data=entity_episode,
                data_type="text",
                source_type="profile_entities"
            )

        # 注入关系信息
        if relationships:
            rel_texts = []
            for r in relationships:
                rel_texts.append(
                    f"{r['source']} 与 {r['target']} 的关系：{r['type']}。{r.get('description', '')}"
                )
            rel_episode = "以下是实体之间的关系：\n\n" + "\n".join(rel_texts)
            self.client.graph.episodic.add(
                graph_id=graph_id,
                data=rel_episode,
                data_type="text",
                source_type="profile_relationships"
            )

        logger.info(f"图谱构建完成: {graph_id}")
        return graph_id
