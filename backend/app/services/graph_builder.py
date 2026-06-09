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
        """构建人生画像的知识图谱

        Zep SDK 3.13 API:
        - graph.create(graph_id, name) → 显式创建图谱
        - graph.add(data, type, graph_id, source_description) → 添加 Episodic 数据
        """
        graph_id = profile_id  # 用 profile_id 作为 graph_id，保持一致
        logger.info(f"创建 Zep 图谱: graph_id={graph_id}, name={profile_name}")

        # Step 1: 显式创建图谱
        graph = self.client.graph.create(
            graph_id=graph_id,
            name=f"ParallelLife - {profile_name}",
            description=f"人生画像图谱：{profile_name}"
        )
        logger.info(f"图谱创建成功: {graph.graph_id}")

        # Step 2: 添加主文本数据（触发 Zep 自动提取实体）
        self.client.graph.add(
            data=input_text[:10000],
            type="text",
            graph_id=graph_id,
            source_description="用户人生描述主文本"
        )
        logger.info("主文本数据已添加")

        # Step 3: 注入明确指定的实体信息
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
            self.client.graph.add(
                data=entity_episode,
                type="text",
                graph_id=graph_id,
                source_description="用户人生中的关键实体"
            )
            logger.info(f"已注入 {len(entities)} 个实体")

        # Step 4: 注入关系信息
        if relationships:
            rel_texts = []
            for r in relationships:
                rel_texts.append(
                    f"{r['source']} 与 {r['target']} 的关系：{r['type']}。{r.get('description', '')}"
                )
            rel_episode = "以下是实体之间的关系：\n\n" + "\n".join(rel_texts)
            self.client.graph.add(
                data=rel_episode,
                type="text",
                graph_id=graph_id,
                source_description="实体关系信息"
            )
            logger.info(f"已注入 {len(relationships)} 个关系")

        logger.info(f"图谱构建完成: {graph_id}")
        return graph_id
