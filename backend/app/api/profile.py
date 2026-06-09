"""画像相关API — 创建、查询、列表、删除"""

import traceback
import threading
from flask import request, jsonify
from . import profile_bp
from ..config import Config
from ..models.profile import ProfileManager, ProfileStatus
from ..models.task import TaskManager, TaskStatus
from ..services.profile_extractor import ProfileExtractor
from ..services.graph_builder import GraphBuilderService
from ..utils.logger import get_logger
from ..utils.locale import t, get_locale, set_locale

logger = get_logger('parallel-life.api.profile')


@profile_bp.route('/create', methods=['POST'])
def create_profile():
    """创建人生画像（异步 — LLM 解析 + 图谱构建）"""
    try:
        data = request.get_json() or {}
        text = data.get('text', '').strip()
        name = data.get('name', 'Unnamed')

        if not text:
            return jsonify({"success": False, "error": "请输入人生描述文本"}), 400

        profile = ProfileManager.create(name=name)
        ProfileManager.save_input_text(profile.profile_id, text)
        profile.extracted_text = text
        ProfileManager.save(profile)

        task_manager = TaskManager()
        task_id = task_manager.create_task("profile_extract", {"profile_id": profile.profile_id})

        current_locale = get_locale()

        def run_extract():
            set_locale(current_locale)
            try:
                task_manager.update_task(task_id, status=TaskStatus.PROCESSING, progress=10,
                                         message="正在解析人生经历...")

                extractor = ProfileExtractor()
                result = extractor.extract(text)

                task_manager.update_task(task_id, progress=40, message="解析完成，正在构建知识图谱...")

                profile.basic_info = result.get('basic_info', {})
                profile.status = ProfileStatus.CREATED
                ProfileManager.save(profile)

                builder = GraphBuilderService(api_key=Config.ZEP_API_KEY)
                graph_id = builder.build_profile_graph(
                    profile_id=profile.profile_id,
                    profile_name=name,
                    basic_info=profile.basic_info,
                    entities=result.get('entities', []),
                    relationships=result.get('relationships', []),
                    input_text=text
                )

                profile.graph_id = graph_id
                profile.status = ProfileStatus.GRAPH_BUILT
                ProfileManager.save(profile)

                task_manager.update_task(task_id, progress=70, message="正在保存决策节点...")

                from ..models.decision import DecisionManager, DecisionNode
                decisions = result.get('decisions', [])
                decision_ids = []
                for d in decisions:
                    node = DecisionNode(
                        decision_id=f"dec_{profile.profile_id}_{len(decision_ids)}",
                        profile_id=profile.profile_id,
                        timestamp=d.get('timestamp', ''),
                        life_stage=d.get('life_stage', ''),
                        scenario=d.get('scenario', ''),
                        branches=d.get('branches', []),
                    )
                    DecisionManager.save_decision(node)
                    decision_ids.append(node.decision_id)

                profile.decision_ids = decision_ids
                profile.status = ProfileStatus.READY
                ProfileManager.save(profile)

                task_manager.complete_task(task_id, result={
                    "profile_id": profile.profile_id,
                    "graph_id": graph_id,
                    "basic_info": profile.basic_info,
                    "decision_count": len(decision_ids),
                    "analysis_summary": result.get('analysis_summary', ''),
                })

            except Exception as e:
                logger.error(f"画像创建失败: {str(e)}")
                profile.status = ProfileStatus.FAILED
                profile.error = str(e)
                ProfileManager.save(profile)
                task_manager.fail_task(task_id, str(e))

        thread = threading.Thread(target=run_extract, daemon=True)
        thread.start()

        return jsonify({
            "success": True,
            "data": {
                "profile_id": profile.profile_id,
                "task_id": task_id,
                "status": "processing",
                "message": "画像创建任务已启动",
            }
        })

    except Exception as e:
        logger.error(f"创建画像失败: {str(e)}")
        return jsonify({"success": False, "error": str(e), "traceback": traceback.format_exc()}), 500


@profile_bp.route('/<profile_id>', methods=['GET'])
def get_profile(profile_id: str):
    """获取画像详情"""
    profile = ProfileManager.get(profile_id)
    if not profile:
        return jsonify({"success": False, "error": f"画像不存在: {profile_id}"}), 404

    result = profile.to_dict()
    result["input_text"] = ProfileManager.get_input_text(profile_id)

    return jsonify({"success": True, "data": result})


@profile_bp.route('/list', methods=['GET'])
def list_profiles():
    """列出所有画像"""
    limit = request.args.get('limit', 50, type=int)
    profiles = ProfileManager.list_all(limit=limit)
    return jsonify({
        "success": True,
        "data": [p.to_dict() for p in profiles],
        "count": len(profiles)
    })


@profile_bp.route('/<profile_id>', methods=['DELETE'])
def delete_profile(profile_id: str):
    """删除画像"""
    ok = ProfileManager.delete(profile_id)
    if not ok:
        return jsonify({"success": False, "error": f"画像不存在: {profile_id}"}), 404
    return jsonify({"success": True, "message": f"画像已删除: {profile_id}"})


@profile_bp.route('/task/<task_id>/status', methods=['GET'])
def get_task_status(task_id: str):
    """查询任务状态"""
    task = TaskManager().get_task(task_id)
    if not task:
        return jsonify({"success": False, "error": f"任务不存在: {task_id}"}), 404
    return jsonify({"success": True, "data": task.to_dict()})
