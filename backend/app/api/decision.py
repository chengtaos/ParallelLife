"""决策相关API — 列出决策、推演分支、获取结果"""

import traceback
import threading
from flask import request, jsonify
from . import decision_bp
from ..models.profile import ProfileManager
from ..models.decision import DecisionManager, BranchTimeline, BranchStatus
from ..models.task import TaskManager, TaskStatus
from ..services.decision_engine import DecisionEngine
from ..utils.logger import get_logger
from ..utils.locale import t, get_locale, set_locale

logger = get_logger('parallel-life.api.decision')


@decision_bp.route('/<profile_id>/list', methods=['GET'])
def list_decisions(profile_id: str):
    """列出画像的所有决策节点"""
    profile = ProfileManager.get(profile_id)
    if not profile:
        return jsonify({"success": False, "error": f"画像不存在: {profile_id}"}), 404

    decisions = DecisionManager.list_decisions(profile_id)
    return jsonify({
        "success": True,
        "data": [d.to_dict() for d in decisions],
        "count": len(decisions)
    })


@decision_bp.route('/<profile_id>/explore', methods=['POST'])
def explore_branch(profile_id: str):
    """推演反事实分支（异步）"""
    try:
        data = request.get_json() or {}
        decision_id = data.get('decision_id')
        branch_label = data.get('branch_label')
        depth = data.get('depth', '5y')

        if not decision_id or not branch_label:
            return jsonify({"success": False, "error": "请提供 decision_id 和 branch_label"}), 400
        if depth not in ('1y', '3y', '5y', '10y'):
            return jsonify({"success": False, "error": "depth 必须是 1y/3y/5y/10y"}), 400

        profile = ProfileManager.get(profile_id)
        if not profile:
            return jsonify({"success": False, "error": f"画像不存在: {profile_id}"}), 404

        decision = DecisionManager.get_decision(profile_id, decision_id)
        if not decision:
            return jsonify({"success": False, "error": f"决策节点不存在: {decision_id}"}), 404

        actual_branch = next((b for b in decision.branches if b.get('is_actual')), None)
        actual_label = actual_branch['label'] if actual_branch else '未指定'

        branch = BranchTimeline(
            branch_id=f"branch_{profile_id}_{len(DecisionManager.list_branches(profile_id))}",
            decision_id=decision_id,
            profile_id=profile_id,
            branch_label=branch_label,
            status=BranchStatus.PENDING,
            depth=depth,
        )
        DecisionManager.save_branch(branch)

        task_manager = TaskManager()
        task_id = task_manager.create_task("branch_explore", {
            "profile_id": profile_id,
            "branch_id": branch.branch_id,
        })

        current_locale = get_locale()

        def run_explore():
            set_locale(current_locale)
            try:
                task_manager.update_task(task_id, status=TaskStatus.PROCESSING, progress=10,
                                         message="正在检索上下文...")

                actual_path_ctx = f"实际选择了「{actual_label}」"
                related = []
                for b in decision.branches:
                    if b.get('label') == branch_label:
                        related = b.get('related_entities', [])
                        break

                def progress_cb(stage, pct, msg):
                    task_manager.update_task(task_id, progress=10 + int(pct * 0.8),
                                             message=f"[{stage}] {msg}")

                engine = DecisionEngine()
                result = engine.explore_branch(
                    decision_scenario=decision.scenario,
                    branch_label=branch_label,
                    actual_path_context=actual_path_ctx,
                    related_entities=related,
                    depth=depth,
                    progress_callback=progress_cb,
                )

                branch.narrative = result.get('narrative', '')
                branch.causal_chain = result.get('causal_chain', [])
                branch.dimensional_trajectory = result.get('dimensional_trajectory', {})
                branch.status = BranchStatus.COMPLETED
                from datetime import datetime
                branch.completed_at = datetime.now().isoformat()
                DecisionManager.save_branch(branch)

                task_manager.complete_task(task_id, result={
                    "branch_id": branch.branch_id,
                    "status": "completed",
                })

            except Exception as e:
                logger.error(f"分支推演失败: {str(e)}")
                branch.status = BranchStatus.FAILED
                branch.error = str(e)
                DecisionManager.save_branch(branch)
                task_manager.fail_task(task_id, str(e))

        thread = threading.Thread(target=run_explore, daemon=True)
        thread.start()

        return jsonify({
            "success": True,
            "data": {
                "task_id": task_id,
                "branch_id": branch.branch_id,
                "status": "generating",
                "message": "分支推演已启动",
            }
        })

    except Exception as e:
        logger.error(f"启动推演失败: {str(e)}")
        return jsonify({"success": False, "error": str(e), "traceback": traceback.format_exc()}), 500


@decision_bp.route('/task/<task_id>/status', methods=['GET'])
def get_explore_status(task_id: str):
    """查询推演任务进度"""
    task = TaskManager().get_task(task_id)
    if not task:
        return jsonify({"success": False, "error": f"任务不存在: {task_id}"}), 404
    return jsonify({"success": True, "data": task.to_dict()})


@decision_bp.route('/branch/<profile_id>/<branch_id>', methods=['GET'])
def get_branch_result(profile_id: str, branch_id: str):
    """获取分支推演结果"""
    branch = DecisionManager.get_branch(profile_id, branch_id)
    if not branch:
        return jsonify({"success": False, "error": f"分支不存在: {branch_id}"}), 404
    return jsonify({"success": True, "data": branch.to_dict()})


@decision_bp.route('/branches/<profile_id>', methods=['GET'])
def list_branches(profile_id: str):
    """列出画像的所有分支"""
    branches = DecisionManager.list_branches(profile_id)
    return jsonify({
        "success": True,
        "data": [b.to_dict() for b in branches],
        "count": len(branches)
    })
