"""决策节点 + 分支时间线 数据模型"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from ..config import Config


class BranchStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DecisionNode:
    decision_id: str
    profile_id: str
    timestamp: str
    life_stage: str
    scenario: str
    branches: List[Dict[str, Any]] = field(default_factory=list)
    context_text: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "profile_id": self.profile_id,
            "timestamp": self.timestamp,
            "life_stage": self.life_stage,
            "scenario": self.scenario,
            "branches": self.branches,
            "context_text": self.context_text,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecisionNode':
        return cls(
            decision_id=data['decision_id'],
            profile_id=data['profile_id'],
            timestamp=data.get('timestamp', ''),
            life_stage=data.get('life_stage', ''),
            scenario=data.get('scenario', ''),
            branches=data.get('branches', []),
            context_text=data.get('context_text', ''),
            created_at=data.get('created_at', ''),
        )


@dataclass
class BranchTimeline:
    branch_id: str
    decision_id: str
    profile_id: str
    branch_label: str
    status: BranchStatus
    depth: str
    narrative: str = ""
    causal_chain: List[Dict[str, Any]] = field(default_factory=list)
    dimensional_trajectory: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "branch_id": self.branch_id,
            "decision_id": self.decision_id,
            "profile_id": self.profile_id,
            "branch_label": self.branch_label,
            "status": self.status.value if isinstance(self.status, BranchStatus) else self.status,
            "depth": self.depth,
            "narrative": self.narrative,
            "causal_chain": self.causal_chain,
            "dimensional_trajectory": self.dimensional_trajectory,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BranchTimeline':
        status = data.get('status', 'pending')
        if isinstance(status, str):
            status = BranchStatus(status)
        return cls(
            branch_id=data['branch_id'],
            decision_id=data['decision_id'],
            profile_id=data['profile_id'],
            branch_label=data.get('branch_label', ''),
            status=status,
            depth=data.get('depth', '5y'),
            narrative=data.get('narrative', ''),
            causal_chain=data.get('causal_chain', []),
            dimensional_trajectory=data.get('dimensional_trajectory', {}),
            created_at=data.get('created_at', ''),
            completed_at=data.get('completed_at'),
            error=data.get('error'),
        )


class DecisionManager:
    """决策/分支持久化管理器"""

    @classmethod
    def _get_decisions_dir(cls, profile_id: str) -> str:
        return os.path.join(Config.PROFILES_DIR, profile_id, 'decisions')

    @classmethod
    def _get_branches_dir(cls, profile_id: str) -> str:
        return os.path.join(Config.PROFILES_DIR, profile_id, 'branches')

    @classmethod
    def _ensure_dirs(cls, profile_id: str):
        os.makedirs(cls._get_decisions_dir(profile_id), exist_ok=True)
        os.makedirs(cls._get_branches_dir(profile_id), exist_ok=True)

    @classmethod
    def save_decision(cls, node: DecisionNode):
        cls._ensure_dirs(node.profile_id)
        p = os.path.join(cls._get_decisions_dir(node.profile_id), f"{node.decision_id}.json")
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(node.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def get_decision(cls, profile_id: str, decision_id: str) -> Optional[DecisionNode]:
        p = os.path.join(cls._get_decisions_dir(profile_id), f"{decision_id}.json")
        if not os.path.exists(p):
            return None
        with open(p, 'r', encoding='utf-8') as f:
            return DecisionNode.from_dict(json.load(f))

    @classmethod
    def list_decisions(cls, profile_id: str) -> List[DecisionNode]:
        d = cls._get_decisions_dir(profile_id)
        if not os.path.exists(d):
            return []
        nodes = []
        for fn in os.listdir(d):
            if fn.endswith('.json'):
                with open(os.path.join(d, fn), 'r', encoding='utf-8') as f:
                    nodes.append(DecisionNode.from_dict(json.load(f)))
        nodes.sort(key=lambda n: n.timestamp or '')
        return nodes

    @classmethod
    def save_branch(cls, branch: BranchTimeline):
        cls._ensure_dirs(branch.profile_id)
        p = os.path.join(cls._get_branches_dir(branch.profile_id), f"{branch.branch_id}.json")
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(branch.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def get_branch(cls, profile_id: str, branch_id: str) -> Optional[BranchTimeline]:
        p = os.path.join(cls._get_branches_dir(profile_id), f"{branch_id}.json")
        if not os.path.exists(p):
            return None
        with open(p, 'r', encoding='utf-8') as f:
            return BranchTimeline.from_dict(json.load(f))

    @classmethod
    def list_branches(cls, profile_id: str) -> List[BranchTimeline]:
        d = cls._get_branches_dir(profile_id)
        if not os.path.exists(d):
            return []
        branches = []
        for fn in os.listdir(d):
            if fn.endswith('.json'):
                with open(os.path.join(d, fn), 'r', encoding='utf-8') as f:
                    branches.append(BranchTimeline.from_dict(json.load(f)))
        branches.sort(key=lambda b: b.created_at, reverse=True)
        return branches
