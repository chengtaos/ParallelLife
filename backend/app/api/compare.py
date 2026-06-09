"""分支对比 API"""

import traceback
import threading
from flask import request, jsonify, Blueprint
from ..models.profile import ProfileManager
from ..models.decision import DecisionManager, DecisionNode
from ..models.task import TaskManager, TaskStatus
from ..services.comparison_agent import ComparisonAgent
from ..utils.logger import get_logger
from ..utils.locale import set_locale, get_locale

compare_bp = Blueprint('compare', __name__)
logger = get_logger('parallel-life.api.compare')


@compare_bp.route('/<profile_id>', methods=['POST'])
def compare_branches(profile_id: str):
    """对比多条分支（异步）"""
    try:
        data = request.get_json() or {}
        branch_ids = data.get('branch_ids', [])

        if not branch_ids or len(branch_ids) < 2:
            return jsonify({"success": False, "error": "请至少选择 2 条分支进行对比"}), 400
        if len(branch_ids) > 3:
            return jsonify({"success": False, "error": "最多对比 3 条分支"}), 400

        profile = ProfileManager.get(profile_id)
        if not profile:
            return jsonify({"success": False, "error": f"画像不存在: {profile_id}"}), 404

        # 加载所有分支
        branches = []
        for bid in branch_ids:
            b = DecisionManager.get_branch(profile_id, bid)
            if not b:
                return jsonify({"success": False, "error": f"分支不存在: {bid}"}), 404
            if b.status.value != 'completed':
                return jsonify({"success": False, "error": f"分支 {bid} 尚未推演完成"}), 400
            branches.append(b.to_dict())

        # 获取决策场景（从第一个分支关联的决策节点获取）
        decision_scenario = ""
        if branches:
            dec = DecisionManager.get_decision(profile_id, branches[0].get('decision_id', ''))
            if dec:
                decision_scenario = dec.scenario

        task_manager = TaskManager()
        task_id = task_manager.create_task("branch_compare", {
            "profile_id": profile_id,
            "branch_ids": branch_ids,
        })

        current_locale = get_locale()

        def run_compare():
            set_locale(current_locale)
            try:
                task_manager.update_task(task_id, status=TaskStatus.PROCESSING, progress=20,
                                         message="正在分析各路径差异...")

                agent = ComparisonAgent()
                result = agent.compare(branches, decision_scenario)

                task_manager.complete_task(task_id, result={
                    "profile_id": profile_id,
                    "branch_ids": branch_ids,
                    "comparison": result,
                })

            except Exception as e:
                logger.error(f"对比分析失败: {str(e)}")
                task_manager.fail_task(task_id, str(e))

        thread = threading.Thread(target=run_compare, daemon=True)
        thread.start()

        return jsonify({
            "success": True,
            "data": {
                "task_id": task_id,
                "status": "processing",
                "message": "对比分析已启动",
            }
        })

    except Exception as e:
        logger.error(f"启动对比失败: {str(e)}")
        return jsonify({"success": False, "error": str(e), "traceback": traceback.format_exc()}), 500


@compare_bp.route('/task/<task_id>/status', methods=['GET'])
def get_compare_status(task_id: str):
    """查询对比任务进度"""
    task = TaskManager().get_task(task_id)
    if not task:
        return jsonify({"success": False, "error": f"任务不存在: {task_id}"}), 404
    return jsonify({"success": True, "data": task.to_dict()})
